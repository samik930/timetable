from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# SUBJECTS schemas
class SubjectsBase(BaseModel):
    code: str
    name: str
    subtype: str
    credits: float

class SubjectsCreate(SubjectsBase):
    pass

class Subjects(SubjectsBase):
    code: str
    
    class Config:
        from_attributes = True

# FACULTY schemas
class FacultyBase(BaseModel):
    password: str
    name: str
    initials: str
    email: str
    subcode1: str
    subcode2: str
    max_periods_per_day: int = 6

class FacultyCreate(FacultyBase):
    pass

class Faculty(FacultyBase):
    id: int
    
    class Config:
        from_attributes = True

# STUDENT schemas
class StudentBase(BaseModel):
    password: str
    name: str
    roll_number: int
    section: str

class StudentCreate(StudentBase):
    id: str

class Student(StudentBase):
    id: str
    
    class Config:
        from_attributes = True

# SCHEDULE schemas
class ScheduleBase(BaseModel):
    id: str
    day_id: int
    period_id: int
    subcode: str
    section: str
    fini: str

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: str
    
    class Config:
        from_attributes = True

# Schedule display schemas
class ScheduleEntry(BaseModel):
    id: str
    day_id: int
    period_id: int
    subcode: Optional[str] = None
    subject_name: str
    section: str
    fini: Optional[str] = None
    teacher_name: str

class Conflict(BaseModel):
    type: str
    day_id: Optional[int] = None
    period_id: Optional[int] = None
    section: Optional[str] = None
    fini: Optional[str] = None
    entries: Optional[List[str]] = None

# Response schemas
class ScheduleGenerationResponse(BaseModel):
    success: bool
    message: str
    schedule_entries: List[Schedule]
    conflicts: List[Conflict]

class ScheduleResponse(BaseModel):
    section: str
    schedule: List[ScheduleEntry]

class FacultyScheduleResponse(BaseModel):
    faculty_name: str
    schedule: List[ScheduleEntry]

# ATTENDANCE schemas
class AttendanceBase(BaseModel):
    student_id: str
    schedule_id: str
    status: str = "Present"
    verification_method: str = "QR"

class AttendanceCreate(AttendanceBase):
    qr_code_hash: str

class Attendance(AttendanceBase):
    id: int
    timestamp: datetime
    qr_code_hash: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class QRCodeRequest(BaseModel):
    schedule_id: str

class QRCodeResponse(BaseModel):
    qr_code: str
    qr_hash: str
    schedule_id: str
    expires_at: datetime

class AttendanceMarkRequest(BaseModel):
    qr_hash: str
    student_id: str
    schedule_id: str

class AttendanceResponse(BaseModel):
    success: bool
    message: str
    attendance: Optional[Attendance] = None

class AttendanceStatsResponse(BaseModel):
    total_students: int
    present_count: int
    absent_count: int
    attendance_percentage: float
