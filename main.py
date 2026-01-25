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
from auth import authenticate_admin, create_access_token, get_current_admin, timedelta, verify_password, get_password_hash
from pydantic import BaseModel

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Timetable Creator API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
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

@app.get("/subjects/periods-info")
def get_all_subjects_periods_info(db: Session = Depends(get_db)):
    """Get periods needed info for all subjects"""
    try:
        generator = ScheduleGenerator(db)
        subjects = db.query(models.SUBJECTS).all()
        
        periods_info = []
        for subject in subjects:
            try:
                periods_needed = generator.calculate_periods_needed(subject.code)
                periods_info.append({
                    "code": subject.code,
                    "name": subject.name,
                    "subtype": subject.subtype,
                    "credits": subject.credits,
                    "periods_needed": periods_needed
                })
            except ValueError as e:
                periods_info.append({
                    "code": subject.code,
                    "name": subject.name,
                    "subtype": subject.subtype,
                    "credits": subject.credits,
                    "periods_needed": None,
                    "error": str(e)
                })
            except Exception as e:
                periods_info.append({
                    "code": subject.code,
                    "name": subject.name,
                    "subtype": subject.subtype,
                    "credits": subject.credits,
                    "periods_needed": None,
                    "error": f"Unexpected error: {str(e)}"
                })
        
        return periods_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/subjects/{subcode}/periods-needed")
def get_periods_needed(subcode: str, db: Session = Depends(get_db)):
    """Get the number of periods needed per week for a subject based on credits"""
    generator = ScheduleGenerator(db)
    try:
        periods_needed = generator.calculate_periods_needed(subcode)
        return {
            "subcode": subcode,
            "periods_needed": periods_needed
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)