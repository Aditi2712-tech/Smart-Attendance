# from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# from typing import List
# import requests

# from app.database import engine, get_db, Base
# from app.models import models
# from app.schemas import schemas
# from app.services.excel_service import generate_excel_report

# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Attendance System Backend")

# # Student Registration
# @app.post("/students/", response_model=schemas.StudentResponse)
# def register_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
#     db_student = db.query(models.Student).filter(models.Student.reg_no == student.reg_no).first()
#     if db_student:
#         raise HTTPException(status_code=400, detail="Student already registered")
    
#     new_student = models.Student(**student.dict())
#     db.add(new_student)
#     db.commit()
#     db.refresh(new_student)
#     return new_student

# @app.get("/students/", response_model=List[schemas.StudentResponse])
# def get_students(db: Session = Depends(get_db)):
#     return db.query(models.Student).all()

# #Image Processing, Face Recognition & Attendance Generation
# @app.post("/recognize-and-mark/")
# async def process_attendance(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     # Mocking communication with Member 1's AI Module Endpoint (http://localhost:8001/ai-recognize)
#     # Returns recognized registration numbers and confidence scores
#     # Example format: [{"reg_no": "24BCB7105", "confidence": 0.95}]
    
#     recognized_faces = [
#         {"reg_no": "24BCB7105", "confidence": 0.92}  # Simulated response for demo
#     ]

#     all_students = db.query(models.Student).all()
#     if not all_students:
#         raise HTTPException(status_code=400, detail="No students registered in database")

#     recognized_reg_nos = {f["reg_no"]: f["confidence"] for f in recognized_faces}

#     present_count = 0
#     absent_count = 0

#     session = models.AttendanceSession(
#         total_students=len(all_students),
#         present_count=0,
#         absent_count=0
#     )
#     db.add(session)
#     db.commit()
#     db.refresh(session)

#     log_responses = []
#     for student in all_students:
#         if student.reg_no in recognized_reg_nos:
#             status = "Present"
#             conf = recognized_reg_nos[student.reg_no]
#             present_count += 1
#         else:
#             status = "Absent"
#             conf = None
#             absent_count += 1

#         log = models.AttendanceLog(
#             session_id=session.id,
#             student_id=student.id,
#             status=status,
#             confidence=conf
#         )
#         db.add(log)
#         log_responses.append({
#             "reg_no": student.reg_no,
#             "name": student.name,
#             "status": status,
#             "confidence": conf
#         })

#     session.present_count = present_count
#     session.absent_count = absent_count
#     db.commit()

#     return {
#         "session_id": session.id,
#         "total": len(all_students),
#         "present": present_count,
#         "absent": absent_count,
#         "logs": log_responses
#     }

# # History & Report Generation
# @app.get("/history/")
# def get_attendance_history(db: Session = Depends(get_db)):
#     sessions = db.query(models.AttendanceSession).all()
#     return sessions

# @app.get("/export-excel/{session_id}")
# def export_excel(session_id: int, db: Session = Depends(get_db)):
#     try:
#         file_path = generate_excel_report(session_id, db)
#         return FileResponse(
#             path=file_path, 
#             filename=f"attendance_session_{session_id}.xlsx",
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))

#     # 1. Delete a Student by Registration Number
# @app.delete("/students/{reg_no}")
# def delete_student(reg_no: str, db: Session = Depends(get_db)):
#     student = db.query(models.Student).filter(models.Student.reg_no == reg_no).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Student not found")
    
#     # Delete associated logs first to preserve foreign key constraints
#     db.query(models.AttendanceLog).filter(models.AttendanceLog.student_id == student.id).delete()
    
#     db.delete(student)
#     db.commit()
#     return {"message": f"Student with registration number {reg_no} deleted successfully"}

# # 2. Delete an Attendance Session by Session ID
# @app.delete("/history/{session_id}")
# def delete_session(session_id: int, db: Session = Depends(get_db)):
#     session = db.query(models.AttendanceSession).filter(models.AttendanceSession.id == session_id).first()
#     if not session:
#         raise HTTPException(status_code=404, detail="Attendance session not found")
    
#     # Delete all associated attendance logs for this session
#     db.query(models.AttendanceLog).filter(models.AttendanceLog.session_id == session_id).delete()
    
#     db.delete(session)
#     db.commit()
#     return {"message": f"Attendance session {session_id} deleted successfully"}

"""
Main FastAPI application.

Endpoints covered here (merge with whatever you already have from Days 1-6):
  POST /students/                registration (Day 2, kept minimal here)
  POST /recognize-and-mark/       Day 3-5 core workflow, real AI plugged in Day 7
  GET  /attendance/history/{id}   Day 6
  GET  /attendance/report/{id}    Day 6 - Excel download

Logging is used instead of print() (Day 9 cleanup requirement) from the start,
so you don't have to hunt for debug prints later.
"""

import json
import logging
import datetime
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db, engine
from app import models
from app.schemas import AttendanceResponse, AttendanceRecordOut, StudentOut
from app.services.recognition_service import match_faces_to_students, dedupe_matches
from app.services.excel_service import generate_attendance_excel



# --- AI module import -------------------------------------------------
# ASSUMPTION: Member 1 exposes ai/recognize.py with:
#     def recognize_classroom_faces(image_path: str) -> list[dict]
# Adjust this import to match their actual module path/name.
try:
    from ai.recognize import recognize_classroom_faces
except ImportError:
    recognize_classroom_faces = None  # allows backend to boot even if ai/ isn't wired yet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("attendance_backend")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Attendance Backend")


# ----------------------------------------------------------------------
# Student registration (minimal - merge with your Day 2 implementation)
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
    if recognize_classroom_faces is None:
        raise HTTPException(status_code=503, detail="AI module not available")

    try:
        existing = db.query(models.Student).filter(
            models.Student.registration_number == registration_number
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Student already registered")

        image_bytes = photo.file.read()
        temp_path = f"/tmp/{registration_number}.jpg"
        with open(temp_path, "wb") as f:
            f.write(image_bytes)

        faces = recognize_classroom_faces(temp_path)
        if not faces:
            raise HTTPException(status_code=422, detail="No face detected in registration photo")
        if len(faces) > 1:
            raise HTTPException(status_code=422, detail="Multiple faces found - upload a single, clear face photo")

        embedding = faces[0]["embedding"]

        student = models.Student(
            registration_number=registration_number,
            name=name,
            department=department,
            year=year,
            section=section,
            embedding=json.dumps(embedding),
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        logger.info(f"Registered student {registration_number}")
        return StudentOut.from_orm(student)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error during registration: {e}")
        raise HTTPException(status_code=500, detail="Database error during registration")


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
    if recognize_classroom_faces is None:
        raise HTTPException(status_code=503, detail="AI module not available")

    # --- Validate the upload before touching the AI module ---
    if image.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=415, detail="Upload a JPEG or PNG image")

    image_bytes = image.file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    temp_path = f"/tmp/classroom_{datetime.datetime.utcnow().timestamp()}.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    try:
        detected_faces = recognize_classroom_faces(temp_path)
    except Exception as e:
        logger.error(f"AI recognition failed: {e}")
        raise HTTPException(status_code=422, detail="Could not process image - ensure it's a valid photo")

    if not detected_faces:
        logger.info("No faces detected in classroom image")

    try:
        matches = match_faces_to_students(detected_faces, db)
        best_by_student = dedupe_matches(matches)
        unknown_count = sum(1 for m in matches if m.student_id is None)

        all_students = db.query(models.Student).all()
        # Filter by section if your Student model tracks it per-class.
        if section:
            all_students = [s for s in all_students if s.section == section]

        session = models.ClassSession(class_name=class_name, section=section)
        db.add(session)
        db.flush()  # get session.id without committing yet

        records = []
        for student in all_students:
            match = best_by_student.get(student.id)
            if match:
                record = models.AttendanceRecord(
                    student_id=student.id,
                    class_session_id=session.id,
                    status=models.AttendanceStatus.PRESENT,
                    similarity_score=match.similarity,
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

    present_count = len(best_by_student)
    absent_count = len(all_students) - present_count
    logger.info(
        f"Session {session.id}: {present_count} present, {absent_count} absent, "
        f"{unknown_count} unknown faces"
    )

    return AttendanceResponse(
        class_session_id=session.id,
        session_date=session.session_date,
        present_count=present_count,
        absent_count=absent_count,
        unknown_faces_detected=unknown_count,
        records=[AttendanceRecordOut.from_orm(r) for r in records],
    )


# ----------------------------------------------------------------------
# History (Day 6)
# ----------------------------------------------------------------------
@app.get("/attendance/history/{class_session_id}", response_model=AttendanceResponse)
def get_attendance_history(class_session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ClassSession).get(class_session_id)
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
        unknown_faces_detected=0,  # not stored per-session; add a column if you need history on this
        records=[AttendanceRecordOut.from_orm(r) for r in records],
    )


# ----------------------------------------------------------------------
# Excel export (Day 6)
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