from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StudentCreate(BaseModel):
    reg_no: str
    name: str
    department: str
    year: str
    section: str
    embedding: Optional[List[float]] = None

class StudentResponse(StudentCreate):
    id: int
    class Config:
        from_attributes = True

class AttendanceLogResponse(BaseModel):
    reg_no: str
    name: str
    status: str
    confidence: Optional[float]

    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    session_id: int
    timestamp: datetime
    present_count: int
    absent_count: int
    logs: List[AttendanceLogResponse]