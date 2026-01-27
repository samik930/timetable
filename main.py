from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import io
import models
import schemas
from database import get_db, engine
from schedule_generator import ScheduleGenerator
from credit_validator import CreditValidator
from automated_timetable_generator import AutomatedTimetableGenerator
from auth import authenticate_admin, create_access_token, get_current_admin, timedelta, verify_password, get_password_hash
from attendance_service import AttendanceService
from pydantic import BaseModel
from datetime import datetime

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Timetable Creator API", version="1.0.0")

@app.get("/")
def read_root():
    return {
        "message": "Timetable Creator API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication schemas
class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: str  # "admin", "student", "faculty"

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_info: dict

# Automated Timetable Generation schemas
class SubjectFacultyAssignment(BaseModel):
    section: str
    subject_code: str
    faculty_initials: str

class AutomatedTimetableRequest(BaseModel):
    assignments: List[SubjectFacultyAssignment]

# Authentication endpoints
@app.post("/auth/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user_type_lower = credentials.user_type.lower() if credentials.user_type else ""
    
    if user_type_lower == "admin":
        print(f"DEBUG: Admin login attempt - username: '{credentials.username}', password: '{credentials.password}'")
        if authenticate_admin(credentials.username, credentials.password):
            access_token = create_access_token(data={"sub": credentials.username, "user_type": "admin"})
            return {"access_token": access_token, "token_type": "bearer", "user_type": "admin", "user_info": {"username": credentials.username}}
        else:
            print(f"DEBUG: Admin authentication failed")
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    elif user_type_lower == "student":
        student = db.query(models.STUDENT).filter(models.STUDENT.id == credentials.username).first()
        if not student:
            raise HTTPException(status_code=401, detail="Student not found")
        if verify_password(credentials.password, student.password):
            access_token = create_access_token(data={"sub": credentials.username, "user_type": "student"})
            return {
                "access_token": access_token, 
                "token_type": "bearer", 
                "user_type": "student",
                "user_info": {
                    "id": student.id,
                    "name": student.name,
                    "section": student.section,
                    "roll_number": student.roll_number
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    
    elif user_type_lower == "faculty":
        faculty = db.query(models.FACULTY).filter(models.FACULTY.email == credentials.username).first()
        if not faculty:
            raise HTTPException(status_code=401, detail="Faculty not found")
        if verify_password(credentials.password, faculty.password):
            access_token = create_access_token(data={"sub": credentials.username, "user_type": "faculty"})
            return {
                "access_token": access_token, 
                "token_type": "bearer", 
                "user_type": "faculty",
                "user_info": {
                    "id": faculty.id,
                    "name": faculty.name,
                    "initials": faculty.initials,
                    "email": faculty.email
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/auth/me")
def get_current_user(current_user: str = Depends(get_current_admin)):
    return {"username": current_user}

# SUBJECTS endpoints
@app.post("/subjects/", response_model=schemas.Subjects)
def create_subject(subject: schemas.SubjectsCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    db_subject = models.SUBJECTS(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.get("/subjects/", response_model=List[schemas.Subjects])
def get_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subjects = db.query(models.SUBJECTS).offset(skip).limit(limit).all()
    return subjects

@app.get("/subjects/{subject_code}", response_model=schemas.Subjects)
def get_subject(subject_code: str, db: Session = Depends(get_db)):
    subject = db.query(models.SUBJECTS).filter(models.SUBJECTS.code == subject_code).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@app.put("/subjects/{subject_code}", response_model=schemas.Subjects)
def update_subject(subject_code: str, subject: schemas.SubjectsCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    db_subject = db.query(models.SUBJECTS).filter(models.SUBJECTS.code == subject_code).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    for key, value in subject.dict().items():
        setattr(db_subject, key, value)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.delete("/subjects/{subject_code}")
def delete_subject(subject_code: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    db_subject = db.query(models.SUBJECTS).filter(models.SUBJECTS.code == subject_code).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(db_subject)
    db.commit()
    return {"message": "Subject deleted successfully"}

# FACULTY endpoints
@app.post("/faculty/", response_model=schemas.Faculty)
def create_faculty(faculty: schemas.FacultyCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    # Hash the password before storing
    faculty_data = faculty.dict()
    faculty_data['password'] = get_password_hash(faculty_data['password'])
    db_faculty = models.FACULTY(**faculty_data)
    db.add(db_faculty)
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@app.get("/faculty/", response_model=List[schemas.Faculty])
def get_faculty(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    faculty = db.query(models.FACULTY).offset(skip).limit(limit).all()
    return faculty

@app.get("/faculty/{faculty_id}", response_model=schemas.Faculty)
def get_faculty_member(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(models.FACULTY).filter(models.FACULTY.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty

@app.put("/faculty/{faculty_id}", response_model=schemas.Faculty)
def update_faculty(faculty_id: int, faculty: schemas.FacultyCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    db_faculty = db.query(models.FACULTY).filter(models.FACULTY.id == faculty_id).first()
    if not db_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Hash password if it's being updated
    faculty_data = faculty.dict()
    if 'password' in faculty_data and faculty_data['password']:
        faculty_data['password'] = get_password_hash(faculty_data['password'])
    
    for key, value in faculty_data.items():
        setattr(db_faculty, key, value)
    
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@app.delete("/faculty/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    db_faculty = db.query(models.FACULTY).filter(models.FACULTY.id == faculty_id).first()
    if not db_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    db.delete(db_faculty)
    db.commit()
    return {"message": "Faculty deleted successfully"}

# STUDENT endpoints
@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    # Hash the password before storing
    student_data = student.dict()
    student_data['password'] = get_password_hash(student_data['password'])
    db_student = models.STUDENT(**student_data)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[schemas.Student])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(models.STUDENT).offset(skip).limit(limit).all()
    return students

@app.get("/students/{student_id}", response_model=schemas.Student)
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(models.STUDENT).filter(models.STUDENT.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: str, student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    db_student = db.query(models.STUDENT).filter(models.STUDENT.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Hash password if it's being updated
    student_data = student.dict()
    if 'password' in student_data and student_data['password']:
        student_data['password'] = get_password_hash(student_data['password'])
    
    for key, value in student_data.items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    db_student = db.query(models.STUDENT).filter(models.STUDENT.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}

# SCHEDULE endpoints
@app.post("/schedule/", response_model=schemas.Schedule)
def create_schedule_entry(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    """Create a schedule entry with credit validation"""
    validator = CreditValidator(db)
    
    # Validate the schedule entry first
    validation_result = validator.validate_schedule_entry(
        schedule.subcode, 
        schedule.section, 
        schedule.day_id, 
        schedule.period_id
    )
    
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])
    
    # If validation passes, create the entry
    generator = ScheduleGenerator(db)
    
    try:
        entry = generator.create_schedule_entry(
            day_id=schedule.day_id,
            period_id=schedule.period_id,
            subcode=schedule.subcode,
            section=schedule.section,
            fini=schedule.fini
        )
        
        # Set the ID if provided
        if schedule.id:
            entry.id = schedule.id
            db.commit()
            
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/schedule/", response_model=List[schemas.Schedule])
def get_all_schedule(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    schedule = db.query(models.SCHEDULE).offset(skip).limit(limit).all()
    return schedule

@app.get("/schedule/{entry_id}", response_model=schemas.Schedule)
def get_schedule_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = db.query(models.SCHEDULE).filter(models.SCHEDULE.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Schedule entry not found")
    return entry

@app.put("/schedule/{entry_id}", response_model=schemas.Schedule)
def update_schedule_entry(entry_id: str, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    generator = ScheduleGenerator(db)
    
    try:
        entry = generator.update_schedule_entry(
            entry_id=entry_id,
            day_id=schedule.day_id,
            period_id=schedule.period_id,
            subcode=schedule.subcode,
            section=schedule.section,
            fini=schedule.fini
        )
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/schedule/{entry_id}")
def delete_schedule_entry(entry_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    generator = ScheduleGenerator(db)
    
    success = generator.delete_schedule_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule entry not found")
    
    return {"message": "Schedule entry deleted successfully"}

# Schedule view endpoints
@app.get("/schedule/section/{section}", response_model=schemas.ScheduleResponse)
def get_schedule_by_section(section: str, db: Session = Depends(get_db)):
    generator = ScheduleGenerator(db)
    schedule = generator.get_schedule_by_section(section)
    
    return schemas.ScheduleResponse(
        section=section,
        schedule=schedule
    )

@app.get("/schedule/faculty/{fini}", response_model=schemas.FacultyScheduleResponse)
def get_schedule_by_faculty(fini: str, db: Session = Depends(get_db)):
    generator = ScheduleGenerator(db)
    schedule = generator.get_schedule_by_teacher(fini)
    
    # Get faculty name
    faculty = db.query(models.FACULTY).filter(models.FACULTY.initials == fini).first()
    faculty_name = faculty.name if faculty else "Unknown"
    
    return schemas.FacultyScheduleResponse(
        faculty_name=faculty_name,
        schedule=schedule
    )

@app.get("/schedule/full", response_model=List[schemas.ScheduleEntry])
def get_full_schedule(db: Session = Depends(get_db)):
    generator = ScheduleGenerator(db)
    schedule = generator.get_full_schedule()
    return schedule

@app.get("/schedule/conflicts", response_model=List[schemas.Conflict])
def get_conflicts(db: Session = Depends(get_db)):
    generator = ScheduleGenerator(db)
    conflicts = generator.detect_conflicts()
    return conflicts

@app.delete("/schedule/section/{section}")
def clear_section_schedule(section: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    deleted_count = db.query(models.SCHEDULE).filter(
        models.SCHEDULE.section == section
    ).delete()
    
    db.commit()
    return {"message": f"Deleted {deleted_count} schedule entries for section {section}"}

# Student and Faculty timetable endpoints
@app.get("/student/timetable/{section}")
def get_student_timetable(section: str, db: Session = Depends(get_db)):
    """Get timetable for a student's section"""
    generator = ScheduleGenerator(db)
    schedule = generator.get_schedule_by_section(section)
    
    return {
        "section": section,
        "schedule": schedule
    }

@app.get("/faculty/timetable/{fini}")
def get_faculty_timetable(fini: str, db: Session = Depends(get_db)):
    """Get timetable for a faculty member by their initials"""
    generator = ScheduleGenerator(db)
    schedule = generator.get_schedule_by_teacher(fini)
    
    return {
        "faculty_initials": fini,
        "schedule": schedule
    }

# Automated Timetable Generation endpoints
@app.get("/automated/subjects")
def get_available_subjects(db: Session = Depends(get_db)):
    """Get all available subjects for automated timetable generation"""
    generator = AutomatedTimetableGenerator(db)
    subjects = generator.get_available_subjects()
    return {"subjects": subjects}

@app.get("/automated/faculty")
def get_available_faculty(db: Session = Depends(get_db)):
    """Get all available faculty for automated timetable generation"""
    generator = AutomatedTimetableGenerator(db)
    faculty = generator.get_available_faculty()
    return {"faculty": faculty}

@app.post("/automated/generate")
def generate_automated_timetable(request: AutomatedTimetableRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_admin)):
    """Generate automated timetable for all sections based on subject-faculty assignments"""
    
    # Convert assignments to the format expected by the generator
    subject_faculty_assignments = {}
    for assignment in request.assignments:
        section = assignment.section.upper()
        if section not in subject_faculty_assignments:
            subject_faculty_assignments[section] = {}
        subject_faculty_assignments[section][assignment.subject_code] = assignment.faculty_initials
    
    # Generate timetable
    generator = AutomatedTimetableGenerator(db)
    results = generator.generate_automated_timetable(subject_faculty_assignments)
    
    return {
        "message": "Automated timetable generation completed",
        "results": results
    }

@app.get("/automated/preview/{section}")
def preview_section_timetable(section: str, db: Session = Depends(get_db)):
    """Preview the generated timetable for a specific section"""
    generator = ScheduleGenerator(db)
    schedule = generator.get_schedule_by_section(section)
    
    return {
        "section": section,
        "schedule": schedule
    }

# Initialize attendance service
attendance_service = AttendanceService()

# Attendance endpoints
@app.post("/attendance/generate-qr", response_model=schemas.QRCodeResponse)
def generate_attendance_qr(request: schemas.QRCodeRequest, db: Session = Depends(get_db)):
    """Generate QR code for attendance marking"""
    # Verify schedule exists
    schedule = db.query(models.SCHEDULE).filter(models.SCHEDULE.id == request.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Generate QR code
    qr_image, qr_hash, expires_at = attendance_service.generate_qr_code(request.schedule_id)
    
    return schemas.QRCodeResponse(
        qr_code=qr_image,
        qr_hash=qr_hash,
        schedule_id=request.schedule_id,
        expires_at=expires_at
    )

@app.post("/attendance/mark", response_model=schemas.AttendanceResponse)
def mark_attendance(request: schemas.AttendanceMarkRequest, db: Session = Depends(get_db)):
    """Mark attendance using QR code"""
    # Validate QR code
    is_valid, message = attendance_service.validate_qr_code(request.qr_hash, request.schedule_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Verify student exists
    student = db.query(models.STUDENT).filter(models.STUDENT.id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Verify schedule exists
    schedule = db.query(models.SCHEDULE).filter(models.SCHEDULE.id == request.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if student section matches schedule section
    if student.section != schedule.section:
        raise HTTPException(
            status_code=403, 
            detail=f"Section mismatch: Student is in section {student.section} but this class is for section {schedule.section}"
        )
    
    # Check if attendance already marked
    existing_attendance = db.query(models.ATTENDANCE).filter(
        models.ATTENDANCE.student_id == request.student_id,
        models.ATTENDANCE.schedule_id == request.schedule_id
    ).first()
    
    if existing_attendance:
        return schemas.AttendanceResponse(
            success=False,
            message="Attendance already marked for this class",
            attendance=existing_attendance
        )
    
    # Create attendance record
    attendance_data = {
        "student_id": request.student_id,
        "schedule_id": request.schedule_id,
        "qr_code_hash": request.qr_hash,
        "status": attendance_service.determine_attendance_status(datetime.utcnow(), datetime.utcnow()),
        "verification_method": "QR"
    }
    
    db_attendance = models.ATTENDANCE(**attendance_data)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    # Check if this is a lab subject and mark attendance for consecutive lab periods
    try:
        # Check if the subject is a lab (typically lab subjects have 'L' in subtype or specific naming)
        from models import SUBJECTS
        subject = db.query(SUBJECTS).filter(SUBJECTS.code == schedule.subcode).first()
        
        if subject and (subject.subtype == 'L' or 'LAB' in subject.name.upper()):
            # Find all consecutive lab periods for this subject
            consecutive_schedules = attendance_service.find_consecutive_lab_periods(db, schedule)
            
            # Mark attendance for all consecutive lab periods (excluding the one already marked)
            additional_attendances = []
            for lab_schedule in consecutive_schedules:
                if lab_schedule.id != request.schedule_id:  # Skip the already marked one
                    # Check if attendance already exists for this period
                    existing = db.query(models.ATTENDANCE).filter(
                        models.ATTENDANCE.student_id == request.student_id,
                        models.ATTENDANCE.schedule_id == lab_schedule.id
                    ).first()
                    
                    if not existing:
                        # Create attendance for consecutive lab period
                        lab_attendance_data = {
                            "student_id": request.student_id,
                            "schedule_id": lab_schedule.id,
                            "qr_code_hash": request.qr_hash,  # Use same QR hash
                            "status": attendance_service.determine_attendance_status(datetime.utcnow(), datetime.utcnow()),
                            "verification_method": "QR (Auto-marked for consecutive lab)"
                        }
                        
                        lab_attendance = models.ATTENDANCE(**lab_attendance_data)
                        db.add(lab_attendance)
                        additional_attendances.append(lab_attendance)
            
            if additional_attendances:
                db.commit()
                for attendance in additional_attendances:
                    db.refresh(attendance)
                
                return schemas.AttendanceResponse(
                    success=True,
                    message=f"Attendance marked successfully for {len(additional_attendances) + 1} consecutive lab periods",
                    attendance=db_attendance
                )
    except Exception as e:
        # Log error but don't fail the main attendance marking
        print(f"Error marking consecutive lab attendance: {e}")
        db.rollback()
        # Continue with original attendance response
    
    return schemas.AttendanceResponse(
        success=True,
        message="Attendance marked successfully",
        attendance=db_attendance
    )

@app.get("/attendance/schedule/{schedule_id}", response_model=List[schemas.Attendance])
def get_attendance_by_schedule(schedule_id: str, db: Session = Depends(get_db)):
    """Get all attendance records for a specific schedule"""
    attendance_records = db.query(models.ATTENDANCE).filter(
        models.ATTENDANCE.schedule_id == schedule_id
    ).all()
    return attendance_records

@app.get("/attendance/student/{student_id}", response_model=List[schemas.Attendance])
def get_attendance_by_student(student_id: str, db: Session = Depends(get_db)):
    """Get all attendance records for a specific student"""
    attendance_records = db.query(models.ATTENDANCE).filter(
        models.ATTENDANCE.student_id == student_id
    ).all()
    return attendance_records

@app.get("/attendance/stats/{schedule_id}", response_model=schemas.AttendanceStatsResponse)
def get_attendance_stats(schedule_id: str, db: Session = Depends(get_db)):
    """Get attendance statistics for a specific schedule"""
    # Get schedule info
    schedule = db.query(models.SCHEDULE).filter(models.SCHEDULE.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Get total students in the section
    total_students = db.query(models.STUDENT).filter(models.STUDENT.section == schedule.section).count()
    
    # Get attendance records
    attendance_records = db.query(models.ATTENDANCE).filter(
        models.ATTENDANCE.schedule_id == schedule_id
    ).all()
    
    # Generate statistics
    stats = attendance_service.generate_attendance_report_data(attendance_records, total_students)
    
    return schemas.AttendanceStatsResponse(**stats)

@app.post("/attendance/manual", response_model=schemas.AttendanceResponse)
def mark_manual_attendance(
    student_id: str,
    schedule_id: str,
    status: str = "Present",
    db: Session = Depends(get_db)
):
    """Manually mark attendance (for faculty/admin use)"""
    # Verify student exists
    student = db.query(models.STUDENT).filter(models.STUDENT.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Verify schedule exists
    schedule = db.query(models.SCHEDULE).filter(models.SCHEDULE.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if attendance already exists
    existing_attendance = db.query(models.ATTENDANCE).filter(
        models.ATTENDANCE.student_id == student_id,
        models.ATTENDANCE.schedule_id == schedule_id
    ).first()
    
    if existing_attendance:
        # Update existing attendance
        existing_attendance.status = status
        existing_attendance.verification_method = "Manual"
        db.commit()
        db.refresh(existing_attendance)
        return schemas.AttendanceResponse(
            success=True,
            message="Attendance updated successfully",
            attendance=existing_attendance
        )
    else:
        # Create new attendance record
        attendance_data = {
            "student_id": student_id,
            "schedule_id": schedule_id,
            "status": status,
            "verification_method": "Manual",
            "qr_code_hash": f"manual_{student_id}_{schedule_id}_{datetime.utcnow().timestamp()}"
        }
        
        db_attendance = models.ATTENDANCE(**attendance_data)
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)
        
        return schemas.AttendanceResponse(
            success=True,
            message="Attendance marked manually successfully",
            attendance=db_attendance
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)