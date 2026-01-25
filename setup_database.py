"""
Complete Database Setup Script
This script creates all tables and populates them with initial data
"""

import models
from database import SessionLocal, engine
from sqlalchemy import inspect

def setup_database():
    """
    Complete database setup: create tables and populate with initial data
    """
    print("🚀 Starting Timetable Database Setup...")
    
    # Create all tables
    print("\n📋 Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Verify tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables created: {', '.join(tables)}")
    
    db = SessionLocal()
    
    try:
        # 1. Setup SUBJECTS table
        print("\n📚 Setting up SUBJECTS table...")
        setup_subjects(db)
        
        # 2. Setup FACULTY table
        print("\n👥 Setting up FACULTY table...")
        setup_faculty(db)
        
        # 3. Setup STUDENT table
        print("\n🎓 Setting up STUDENT table...")
        setup_students(db)
        
        # 4. Setup SCHEDULE table
        print("\n📅 Setting up SCHEDULE table...")
        setup_schedule(db)
        
        # Final status
        print("\n🎉 Database Setup Complete!")
        print("=" * 50)
        print("📊 Final Database Status:")
        print(f"   SUBJECTS: {db.query(models.SUBJECTS).count()} records")
        print(f"   FACULTY:  {db.query(models.FACULTY).count()} records")
        print(f"   STUDENT:  {db.query(models.STUDENT).count()} records")
        print(f"   SCHEDULE: {db.query(models.SCHEDULE).count()} records")
        print("=" * 50)
        print("✅ You can now start the API server with: uvicorn main:app --reload")
        print("🌐 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def setup_subjects(db):
    """Setup SUBJECTS table with data"""
    subjects_data = [
        {"code": "PCCCS403", "name": "COMPUTER ORGANIZATION AND ARCHITECTURE", "subtype": "T"},
        {"code": "PLT401", "name": "FORMAL LANGUAGE & AUTOMATA THEORY", "subtype": "T"},
        {"code": "HSMC402", "name": "PRE PLACEMENT TRAINING", "subtype": "T"},
        {"code": "BSC491", "name": "NUMERICAL METHODS", "subtype": "T"},
        {"code": "PCCCS404", "name": "DATABASE MANAGEMENT SYSTEMS", "subtype": "T"},
        {"code": "PCCCS405", "name": "COMPUTER NETWORKS", "subtype": "T"},
        {"code": "PCCCS403P", "name": "COMPUTER ORGANIZATION AND ARCHITECTURE LAB", "subtype": "P"},
        {"code": "PLT401P", "name": "FORMAL LANGUAGE & AUTOMATA THEORY LAB", "subtype": "P"},
        {"code": "BSC491P", "name": "NUMERICAL METHODS LAB", "subtype": "P"},
        {"code": "PCCCS404P", "name": "DATABASE MANAGEMENT SYSTEMS LAB", "subtype": "P"},
        {"code": "PCCCS405P", "name": "COMPUTER NETWORKS LAB", "subtype": "P"},
    ]
    
    # Clear existing data
    db.query(models.SUBJECTS).delete()
    db.commit()
    
    # Insert new data
    for subject_info in subjects_data:
        subject = models.SUBJECTS(**subject_info)
        db.add(subject)
    
    db.commit()
    print(f"✅ Created {len(subjects_data)} subject records")

def setup_faculty(db):
    """Setup FACULTY table with data"""
    faculty_data = [
        {"id": 1, "password": "pass1", "name": "John Smith", "initials": "JS", "email": "john.smith@school.edu", "subcode1": "PCCCS403", "subcode2": "PCCCS403P"},
        {"id": 2, "password": "pass2", "name": "Sarah Johnson", "initials": "SJ", "email": "sarah.j@school.edu", "subcode1": "PCCCS404", "subcode2": "PCCCS404P"},
        {"id": 3, "password": "pass3", "name": "Michael Brown", "initials": "MB", "email": "michael.b@school.edu", "subcode1": "PLT401", "subcode2": "PLT401P"},
        {"id": 4, "password": "pass4", "name": "Emily Davis", "initials": "ED", "email": "emily.d@school.edu", "subcode1": "PCCCS405", "subcode2": "PCCCS405P"},
        {"id": 5, "password": "pass5", "name": "Robert Wilson", "initials": "RW", "email": "robert.w@school.edu", "subcode1": "BSC491", "subcode2": "BSC491P"},
        {"id": 6, "password": "pass6", "name": "Lisa Anderson", "initials": "LA", "email": "lisa.a@school.edu", "subcode1": "HSMC402", "subcode2": "PCCCS403"},
        {"id": 7, "password": "pass7", "name": "David Martinez", "initials": "DM", "email": "david.m@school.edu", "subcode1": "PCCCS404", "subcode2": "PLT401"},
        {"id": 8, "password": "pass8", "name": "Jennifer Taylor", "initials": "JT", "email": "jennifer.t@school.edu", "subcode1": "PCCCS405", "subcode2": "BSC491"},
        {"id": 9, "password": "pass9", "name": "James Thomas", "initials": "JMT", "email": "james.t@school.edu", "subcode1": "HSMC402", "subcode2": "PCCCS403"},
        {"id": 10, "password": "pass10", "name": "Maria Garcia", "initials": "MG", "email": "maria.g@school.edu", "subcode1": "PLT401", "subcode2": "PCCCS404"},
        {"id": 11, "password": "pass11", "name": "William Jones", "initials": "WJ", "email": "william.j@school.edu", "subcode1": "BSC491", "subcode2": "PCCCS405"},
        {"id": 12, "password": "pass12", "name": "Patricia Miller", "initials": "PM", "email": "patricia.m@school.edu", "subcode1": "PCCCS403P", "subcode2": "PCCCS404P"},
        {"id": 13, "password": "pass13", "name": "Christopher Davis", "initials": "CD", "email": "chris.d@school.edu", "subcode1": "PLT401P", "subcode2": "BSC491P"},
    ]
    
    # Clear existing data
    db.query(models.FACULTY).delete()
    db.commit()
    
    # Insert new data
    for faculty_info in faculty_data:
        faculty = models.FACULTY(**faculty_info)
        db.add(faculty)
    
    db.commit()
    print(f"✅ Created {len(faculty_data)} faculty records")

def setup_students(db):
    """Setup STUDENT table with data"""
    student_data = [
        {"id": "STU001", "password": "pass1", "name": "Alice Johnson", "roll_number": 101, "section": "A"},
        {"id": "STU002", "password": "pass2", "name": "Bob Smith", "roll_number": 102, "section": "A"},
        {"id": "STU003", "password": "pass3", "name": "Charlie Brown", "roll_number": 103, "section": "B"},
        {"id": "STU004", "password": "pass4", "name": "Diana Prince", "roll_number": 104, "section": "B"},
        {"id": "STU005", "password": "pass5", "name": "Edward Norton", "roll_number": 105, "section": "A"},
        {"id": "STU006", "password": "pass6", "name": "Fiona Green", "roll_number": 106, "section": "C"},
        {"id": "STU007", "password": "pass7", "name": "George Wilson", "roll_number": 107, "section": "C"},
        {"id": "STU008", "password": "pass8", "name": "Hannah Lee", "roll_number": 108, "section": "B"},
        {"id": "STU009", "password": "pass9", "name": "Ian Miller", "roll_number": 109, "section": "A"},
        {"id": "STU010", "password": "pass10", "name": "Julia Roberts", "roll_number": 110, "section": "C"},
        {"id": "STU011", "password": "pass11", "name": "Kevin Hart", "roll_number": 111, "section": "B"},
        {"id": "STU012", "password": "pass12", "name": "Laura Palmer", "roll_number": 112, "section": "A"},
    ]
    
    # Clear existing data
    db.query(models.STUDENT).delete()
    db.commit()
    
    # Insert new data
    for student_info in student_data:
        student = models.STUDENT(**student_info)
        db.add(student)
    
    db.commit()
    print(f"✅ Created {len(student_data)} student records")

def setup_schedule(db):
    """Setup SCHEDULE table with data"""
    schedule_data = [
        {"id": "SCH001", "day_id": 1, "period_id": 1, "subcode": "PCCCS403", "section": "A", "fini": "JS"},
        {"id": "SCH002", "day_id": 1, "period_id": 2, "subcode": "PCCCS405", "section": "A", "fini": "RW"},
        {"id": "SCH003", "day_id": 1, "period_id": 3, "subcode": "BSC491", "section": "B", "fini": "WJ"},
        {"id": "SCH004", "day_id": 1, "period_id": 4, "subcode": "HSMC402", "section": "C", "fini": "MB"},
        {"id": "SCH005", "day_id": 2, "period_id": 1, "subcode": "PCCCS404", "section": "A", "fini": "ED"},
        {"id": "SCH006", "day_id": 2, "period_id": 2, "subcode": "BSC491", "section": "B", "fini": "SJ"},
        {"id": "SCH007", "day_id": 2, "period_id": 3, "subcode": "PLT401", "section": "C", "fini": "MB"},
        {"id": "SCH008", "day_id": 2, "period_id": 4, "subcode": "PCCCS403", "section": "B", "fini": "JT"},
        {"id": "SCH009", "day_id": 3, "period_id": 1, "subcode": "PCCCS405", "section": "C", "fini": "CD"},
        {"id": "SCH010", "day_id": 3, "period_id": 2, "subcode": "HSMC402", "section": "A", "fini": "MG"},
        {"id": "SCH011", "day_id": 3, "period_id": 3, "subcode": "PCCCS404", "section": "B", "fini": "JMT"},
        {"id": "SCH012", "day_id": 3, "period_id": 4, "subcode": "PLT401", "section": "C", "fini": "DM"},
        {"id": "SCH013", "day_id": 4, "period_id": 1, "subcode": "BSC491", "section": "A", "fini": "WJ"},
        {"id": "SCH014", "day_id": 4, "period_id": 2, "subcode": "PCCCS403", "section": "C", "fini": "LA"},
        {"id": "SCH015", "day_id": 4, "period_id": 3, "subcode": "PCCCS403", "section": "B", "fini": "JS"},
        {"id": "SCH016", "day_id": 4, "period_id": 4, "subcode": "PCCCS405", "section": "A", "fini": "RW"},
        {"id": "SCH017", "day_id": 5, "period_id": 1, "subcode": "HSMC402", "section": "B", "fini": "MB"},
        {"id": "SCH018", "day_id": 5, "period_id": 2, "subcode": "PCCCS404", "section": "C", "fini": "ED"},
        {"id": "SCH019", "day_id": 5, "period_id": 3, "subcode": "PLT401", "section": "A", "fini": "DM"},
        {"id": "SCH020", "day_id": 5, "period_id": 4, "subcode": "BSC491", "section": "B", "fini": "PM"},
    ]
    
    # Clear existing data
    db.query(models.SCHEDULE).delete()
    db.commit()
    
    # Insert new data
    for schedule_info in schedule_data:
        schedule = models.SCHEDULE(**schedule_info)
        db.add(schedule)
    
    db.commit()
    print(f"✅ Created {len(schedule_data)} schedule records")

if __name__ == "__main__":
    setup_database()
