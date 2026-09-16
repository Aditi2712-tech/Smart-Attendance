# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.database import Base

# class Student(Base):
#     __tablename__ = "students"

#     id = Column(Integer, primary_key=True, index=True)
#     reg_no = Column(String, unique=True, index=True, nullable=False)
#     name = Column(String, nullable=False)
#     department = Column(String)
#     year = Column(String)
#     section = Column(String)
#     embedding = Column(JSON, nullable=True) # Stores face embeddings from AI module

# class AttendanceSession(Base):
#     __tablename__ = "attendance_sessions"

#     id = Column(Integer, primary_key=True, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     total_students = Column(Integer)
#     present_count = Column(Integer)
#     absent_count = Column(Integer)

#     logs = relationship("AttendanceLog", back_populates="session")

# class AttendanceLog(Base):
#     __tablename__ = "attendance_logs"

#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(Integer, ForeignKey("attendance_sessions.id"))
#     student_id = Column(Integer, ForeignKey("students.id"))
#     status = Column(String) # 'Present' or 'Absent'
#     confidence = Column(Float, nullable=True)

#     session = relationship("AttendanceSession", back_populates="logs")
#     student = relationship("Student")

"""
SQLAlchemy models for the Attendance system.

ASSUMPTION: adapt field names here to match whatever you already built
in Days 1-2. The important parts for Day 7+ are:
  - Student.embedding stores the 512-d InsightFace vector (as JSON/bytes)
  - AttendanceRecord has a unique constraint on (student_id, class_session_id)
    to guarantee duplicate prevention at the DB level, not just in app code.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
import datetime

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    year = Column(String, nullable=True)
    section = Column(String, nullable=True)

    # 512-d InsightFace embedding, stored as JSON list of floats.
    # (For larger scale you'd use pgvector, but JSON is fine for an MVP.)
    embedding = Column(String, nullable=False)  # json.dumps(list[float])

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    attendance_records = relationship("AttendanceRecord", back_populates="student")


class ClassSession(Base):
    """One attendance-taking event: a class, on a date, at a time."""
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String, nullable=False)
    section = Column(String, nullable=True)
    session_date = Column(DateTime, default=datetime.datetime.utcnow)

    attendance_records = relationship("AttendanceRecord", back_populates="class_session")


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        # This is what actually guarantees no duplicate attendance rows,
        # even if the API is called twice for the same session.
        UniqueConstraint("student_id", "class_session_id", name="uq_student_session"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    status = Column(SAEnum(AttendanceStatus), nullable=False)
    similarity_score = Column(Float, nullable=True)  # null for absent students
    marked_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="attendance_records")
    class_session = relationship("ClassSession", back_populates="attendance_records")