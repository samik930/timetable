from sqlalchemy import Column, Integer, String,Float ,ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class SUBJECTS(Base):
    __tablename__ = "SUBJECTS"
    
    code = Column(String, primary_key=True, index=True)  # SUBCODE - Primary key
    name = Column(String, index=True)  # SUBNAME
    subtype = Column(String)  # SUBTYPE
    credits = Column(Float)
    
    timetables = relationship("SCHEDULE", back_populates="subject")

class FACULTY(Base):
    __tablename__ = "FACULTY"
    
    id = Column(Integer, primary_key=True, index=True)  # FID
    password = Column(String)  # PASSW
    name = Column(String, index=True)  # NAME
    initials = Column(String, unique=True, index=True)  # INI
    email = Column(String, unique=True, index=True)  # EMAIL
    subcode1 = Column(String)  # SUBCODE1
    subcode2 = Column(String)  # SUBCODE2
    max_periods_per_day = Column(Integer, default=6)  # Additional field for scheduling
    
    timetables = relationship("SCHEDULE", back_populates="teacher")

class STUDENT(Base):
    __tablename__ = "STUDENT"
    
    id = Column(String, primary_key=True, index=True)  # SID
    password = Column(String)  # PASSW
    name = Column(String, index=True)  # NAME
    roll_number = Column(Integer)  # ROLL
    section = Column(String)  # SECTION

class SCHEDULE(Base):
    __tablename__ = "SCHEDULE"
    
    id = Column(String, primary_key=True, index=True)  # ID
    day_id = Column(Integer)  # DAYID
    period_id = Column(Integer)  # PERIODID
    subcode = Column(String, ForeignKey("SUBJECTS.code"))  # SUBCODE
    section = Column(String)  # SECTION
    fini = Column(String, ForeignKey("FACULTY.initials"))  # FINI
    
    subject = relationship("SUBJECTS", back_populates="timetables")
    teacher = relationship("FACULTY", back_populates="timetables")

class ATTENDANCE(Base):
    __tablename__ = "ATTENDANCE"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("STUDENT.id"), index=True)
    schedule_id = Column(String, ForeignKey("SCHEDULE.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Present")  # Present, Absent, Late, Excused
    qr_code_hash = Column(String, unique=True, index=True)
    verification_method = Column(String, default="QR")  # QR, Manual, Biometric
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("STUDENT")
    schedule = relationship("SCHEDULE")
