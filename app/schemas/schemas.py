# from pydantic import BaseModel
# from typing import List, Optional
# from datetime import datetime

# class StudentCreate(BaseModel):
#     reg_no: str
#     name: str
#     department: str
#     year: str
#     section: str
#     embedding: Optional[List[float]] = None

# class StudentResponse(StudentCreate):
#     id: int
#     class Config:
#         from_attributes = True

# class AttendanceLogResponse(BaseModel):
#     reg_no: str
#     name: str
#     status: str
#     confidence: Optional[float]

#     class Config:
#         from_attributes = True

# class SessionResponse(BaseModel):
#     session_id: int
#     timestamp: datetime
#     present_count: int
#     absent_count: int
#     logs: List[AttendanceLogResponse]

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class StudentOut(BaseModel):
    id: int
    registration_number: str
    name: str
    department: Optional[str] = None
    year: Optional[str] = None
    section: Optional[str] = None

    model_config = {"from_attributes": True}

class AttendanceRecordOut(BaseModel):
    student: StudentOut
    status: str
    similarity_score: Optional[float] = None

    model_config = {"from_attributes": True}
    

class AttendanceResponse(BaseModel):
    class_session_id: int
    session_date: datetime
    present_count: int
    absent_count: int
    unknown_faces_detected: int
    records: List[AttendanceRecordOut]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None