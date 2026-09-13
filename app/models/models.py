from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    reg_no = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String)
    year = Column(String)
    section = Column(String)
    embedding = Column(JSON, nullable=True) # Stores face embeddings from AI module

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_students = Column(Integer)
    present_count = Column(Integer)
    absent_count = Column(Integer)

    logs = relationship("AttendanceLog", back_populates="session")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    status = Column(String) # 'Present' or 'Absent'
    confidence = Column(Float, nullable=True)

    session = relationship("AttendanceSession", back_populates="logs")
    student = relationship("Student")