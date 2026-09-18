"""
Main FastAPI application.

Wired to Member 1's real ai/engine.py (FaceEngine class), which does its own
face detection AND matching internally (reads registered embeddings from
embeddings/*.npy on disk and returns registration numbers directly).
This backend's job is: receive the image, call the engine, translate its
result into attendance records, and persist them.
"""

import json
import logging
import datetime
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db, engine
from app import models
from app.schemas import AttendanceResponse, AttendanceRecordOut, StudentOut
from app.services.ai_service import recognize_classroom_image, register_student_face
from app.services.excel_service import generate_attendance_excel
# for deletion of data
from app.services.ai_service import recognize_classroom_image, register_student_face, delete_student_embedding


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("attendance_backend")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Attendance Backend")


# ----------------------------------------------------------------------
# Student registration
# ----------------------------------------------------------------------
@app.post("/students/")
def register_student(
    registration_number: str = Form(...),
    name: str = Form(...),
    department: str = Form(None),
    year: str = Form(None),
    section: str = Form(None),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if photo.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=415, detail="Upload a JPEG or PNG image")

    existing = db.query(models.Student).filter(
        models.Student.registration_number == registration_number
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Student already registered")

    image_bytes = photo.file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    temp_path = f"/tmp/{registration_number}.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    try:
        result = register_student_face(registration_number, temp_path)
    except ValueError as e:
        # No face / multiple faces / bad image - client's fault, not a 500
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"AI registration failed for {registration_number}: {e}")
        raise HTTPException(status_code=500, detail="Face registration failed")

    try:
        student = models.Student(
            registration_number=registration_number,
            name=name,
            department=department,
            year=year,
            section=section,
            # Embedding is kept here too for reference/portability, even though
            # the real matching source of truth is the .npy file on disk
            # written by register_student_face() -> engine.save_embedding().
            embedding=json.dumps(np.asarray(result["embedding"]).tolist()),
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error during registration: {e}")
        raise HTTPException(status_code=500, detail="Database error during registration")

    logger.info(f"Registered student {registration_number}")
    return StudentOut.model_validate(student)


# ----------------------------------------------------------------------
# Core workflow: image -> AI recognition -> attendance
# ----------------------------------------------------------------------
@app.post("/recognize-and-mark/", response_model=AttendanceResponse)
def recognize_and_mark(
    class_name: str = Form(...),
    section: str = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # --- Validate the upload first ---
    if image.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=415, detail="Upload a JPEG or PNG image")

    image_bytes = image.file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    temp_path = f"/tmp/classroom_{datetime.datetime.utcnow().timestamp()}.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    # --- Run real recognition ---
    try:
        result = recognize_classroom_image(temp_path)
    except Exception as e:
        logger.error(f"AI recognition failed: {e}")
        raise HTTPException(status_code=422, detail="Could not process image - ensure it's a valid photo")

    recognized_reg_numbers = {r["registration_number"] for r in result["recognized_students"]}
    confidence_by_reg = {r["registration_number"]: r["confidence"] for r in result["recognized_students"]}
    unknown_count = len(result["unknown_faces"])

    # --- Save attendance ---
    try:
        all_students = db.query(models.Student).all()
        if section:
            all_students = [s for s in all_students if s.section == section]

        session = models.ClassSession(class_name=class_name, section=section)
        db.add(session)
        db.flush()  # get session.id without committing yet

        records = []
        for student in all_students:
            if student.registration_number in recognized_reg_numbers:
                record = models.AttendanceRecord(
                    student_id=student.id,
                    class_session_id=session.id,
                    status=models.AttendanceStatus.PRESENT,
                    similarity_score=confidence_by_reg[student.registration_number],
                )
            else:
                record = models.AttendanceRecord(
                    student_id=student.id,
                    class_session_id=session.id,
                    status=models.AttendanceStatus.ABSENT,
                )
            db.add(record)
            records.append(record)

        db.commit()
        db.refresh(session)

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error during attendance marking: {e}")
        raise HTTPException(status_code=500, detail="Database error while saving attendance")

    present_count = len(recognized_reg_numbers)
    absent_count = len(all_students) - present_count
    logger.info(
        f"Session {session.id}: {present_count} present, {absent_count} absent, "
        f"{unknown_count} unknown faces (of {result['face_count']} detected)"
    )

    return AttendanceResponse(
        class_session_id=session.id,
        session_date=session.session_date,
        present_count=present_count,
        absent_count=absent_count,
        unknown_faces_detected=unknown_count,
        records=[AttendanceRecordOut.model_validate(r) for r in records],
    )


# ----------------------------------------------------------------------
# History
# ----------------------------------------------------------------------
@app.get("/attendance/history/{class_session_id}", response_model=AttendanceResponse)
def get_attendance_history(class_session_id: int, db: Session = Depends(get_db)):
    session = db.get(models.ClassSession, class_session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Class session not found")

    records = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.class_session_id == class_session_id
    ).all()

    present_count = sum(1 for r in records if r.status == models.AttendanceStatus.PRESENT)
    absent_count = sum(1 for r in records if r.status == models.AttendanceStatus.ABSENT)

    return AttendanceResponse(
        class_session_id=session.id,
        session_date=session.session_date,
        present_count=present_count,
        absent_count=absent_count,
        unknown_faces_detected=0,  # not persisted per-session; add a column if needed later
        records=[AttendanceRecordOut.model_validate(r) for r in records],
    )


# ----------------------------------------------------------------------
# Excel export
# ----------------------------------------------------------------------
@app.get("/attendance/report/{class_session_id}")
def download_attendance_report(class_session_id: int, db: Session = Depends(get_db)):
    try:
        buffer = generate_attendance_excel(db, class_session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Excel generation failed: {e}")
        raise HTTPException(status_code=500, detail="Could not generate report")

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=attendance_{class_session_id}.xlsx"},
    )

# deletion of student data
@app.delete("/students/{registration_number}")
def delete_student(registration_number: str, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(
        models.Student.registration_number == registration_number
    ).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    try:
        # Remove attendance records first - required by the FK relationship,
        # otherwise the DELETE on students fails with an integrity error.
        db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.student_id == student.id
        ).delete()

        db.delete(student)
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error while deleting student {registration_number}: {e}")
        raise HTTPException(status_code=500, detail="Database error while deleting student")

    # Also remove the .npy embedding file - this is the real source of truth
    # the recognition engine reads from, not just the DB row.
    embedding_deleted = delete_student_embedding(registration_number)
    if not embedding_deleted:
        logger.warning(f"No embedding file found on disk for {registration_number} (DB row still deleted)")

    logger.info(f"Deleted student {registration_number}")
    return {"message": f"Student {registration_number} deleted successfully"}