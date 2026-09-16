# import pandas as pd
# import os
# from sqlalchemy.orm import Session
# from app.models.models import AttendanceLog, AttendanceSession

# def generate_excel_report(session_id: int, db: Session) -> str:
#     session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
#     if not session:
#         raise Exception("Session not found")

#     logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).all()

#     data = []
#     for log in logs:
#         data.append({
#             "Registration No": log.student.reg_no,
#             "Student Name": log.student.name,
#             "Department": log.student.department,
#             "Year": log.student.year,
#             "Section": log.student.section,
#             "Status": log.status,
#             "Date/Time": session.timestamp.strftime("%Y-%m-%d %H:%M:%S")
#         })

#     df = pd.DataFrame(data)
#     os.makedirs("exports", exist_ok=True)
#     file_path = f"exports/attendance_session_{session_id}.xlsx"
    
#     with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Attendance Report')

#     return file_path

"""
Excel report generation using pandas + openpyxl.
Handles the "large class" edge case from Day 8 by writing in one pass
rather than row-by-row cell writes (much faster for 100+ students).
"""

import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session

from app.models import AttendanceRecord, ClassSession


def generate_attendance_excel(db: Session, class_session_id: int) -> BytesIO:
    session = db.query(ClassSession).get(class_session_id)
    if session is None:
        raise ValueError(f"No class session with id {class_session_id}")

    records = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.class_session_id == class_session_id)
        .all()
    )

    rows = []
    for r in records:
        rows.append({
            "Registration Number": r.student.registration_number,
            "Name": r.student.name,
            "Department": r.student.department,
            "Status": r.status.value.capitalize(),
            "Similarity": round(r.similarity_score, 3) if r.similarity_score else "",
            "Date": session.session_date.strftime("%Y-%m-%d"),
            "Time": session.marked_at.strftime("%H:%M:%S") if hasattr(session, "marked_at") else "",
        })

    df = pd.DataFrame(rows)
    # Present students first, then absent - easier for faculty to scan.
    df["_sort"] = df["Status"].map({"Present": 0, "Absent": 1})
    df = df.sort_values(["_sort", "Registration Number"]).drop(columns="_sort")

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
        worksheet = writer.sheets["Attendance"]
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells if cell.value is not None)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 4

    buffer.seek(0)
    return buffer