import pandas as pd
import os
from sqlalchemy.orm import Session
from app.models.models import AttendanceLog, AttendanceSession

def generate_excel_report(session_id: int, db: Session) -> str:
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise Exception("Session not found")

    logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()

    data = []
    for log in logs:
        data.append({
            "Registration No": log.student.reg_no,
            "Student Name": log.student.name,
            "Department": log.student.department,
            "Year": log.student.year,
            "Section": log.student.section,
            "Status": log.status,
            "Date/Time": session.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    df = pd.DataFrame(data)
    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/attendance_session_{session_id}.xlsx"
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance Report')

    return file_path