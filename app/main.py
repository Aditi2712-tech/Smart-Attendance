from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import requests

from app.database import engine, get_db, Base
from app.models import models
from app.schemas import schemas
from app.services.excel_service import generate_excel_report

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Attendance System Backend")

# Student Registration
@app.post("/students/", response_model=schemas.StudentResponse)
def register_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.reg_no == student.reg_no).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Student already registered")
    
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.get("/students/", response_model=List[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

#Image Processing, Face Recognition & Attendance Generation
@app.post("/recognize-and-mark/")
async def process_attendance(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Mocking communication with Member 1's AI Module Endpoint (http://localhost:8001/ai-recognize)
    # Returns recognized registration numbers and confidence scores
    # Example format: [{"reg_no": "24BCB7105", "confidence": 0.95}]
    
    recognized_faces = [
        {"reg_no": "24BCB7105", "confidence": 0.92}  # Simulated response for demo
    ]

    all_students = db.query(models.Student).all()
    if not all_students:
        raise HTTPException(status_code=400, detail="No students registered in database")

    recognized_reg_nos = {f["reg_no"]: f["confidence"] for f in recognized_faces}

    present_count = 0
    absent_count = 0

    session = models.AttendanceSession(
        total_students=len(all_students),
        present_count=0,
        absent_count=0
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    log_responses = []
    for student in all_students:
        if student.reg_no in recognized_reg_nos:
            status = "Present"
            conf = recognized_reg_nos[student.reg_no]
            present_count += 1
        else:
            status = "Absent"
            conf = None
            absent_count += 1

        log = models.AttendanceLog(
            session_id=session.id,
            student_id=student.id,
            status=status,
            confidence=conf
        )
        db.add(log)
        log_responses.append({
            "reg_no": student.reg_no,
            "name": student.name,
            "status": status,
            "confidence": conf
        })

    session.present_count = present_count
    session.absent_count = absent_count
    db.commit()

    return {
        "session_id": session.id,
        "total": len(all_students),
        "present": present_count,
        "absent": absent_count,
        "logs": log_responses
    }

# History & Report Generation
@app.get("/history/")
def get_attendance_history(db: Session = Depends(get_db)):
    sessions = db.query(models.AttendanceSession).all()
    return sessions

@app.get("/export-excel/{session_id}")
def export_excel(session_id: int, db: Session = Depends(get_db)):
    try:
        file_path = generate_excel_report(session_id, db)
        return FileResponse(
            path=file_path, 
            filename=f"attendance_session_{session_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 1. Delete a Student by Registration Number
@app.delete("/students/{reg_no}")
def delete_student(reg_no: str, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.reg_no == reg_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Delete associated logs first to preserve foreign key constraints
    db.query(models.AttendanceLog).filter(models.AttendanceLog.student_id == student.id).delete()
    
    db.delete(student)
    db.commit()
    return {"message": f"Student with registration number {reg_no} deleted successfully"}

# 2. Delete an Attendance Session by Session ID
@app.delete("/history/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.AttendanceSession).filter(models.AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")
    
    # Delete all associated attendance logs for this session
    db.query(models.AttendanceLog).filter(models.AttendanceLog.session_id == session_id).delete()
    
    db.delete(session)
    db.commit()
    return {"message": f"Attendance session {session_id} deleted successfully"}