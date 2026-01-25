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
        {"code": "CSE2101", "name": "DATA STRUCTURES & ALGORITHMS", "subtype": "T","credits":4.0},
        {"code": "CSE2102", "name": "OPERATING SYSTEMS", "subtype": "T","credits":3.0},
        {"code": "ECE2004", "name": "DIGITAL ELECTRONICS", "subtype": "T","credits":3.0},
        {"code": "MTH2101", "name": "DISCRETE MATHEMATICS", "subtype": "T","credits":4.0},
        {"code": "MTH2102", "name": "PROBABILITY & STATISTICS", "subtype": "T","credits":4.0},
        {"code": "CSE2151", "name": "DATA STRUCTURES & ALGORITHMS LAB", "subtype": "P","credits":1.5},
        {"code": "CSE2152", "name": "OPERATING SYSTEMS LAB", "subtype": "P","credits":1.5},
        {"code": "ECE2054", "name": "DIGITAL ELECTRONICS LAB", "subtype": "P","credits":1.0},
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
   #faculty_data = [
   #     {"id": 1, "password": "pass1", "name": "Sudeshna Goswami", "initials": "SDG", "email": "goswamisudeshna@heritageit.edu", "subcode1": "CSE", "subcode2": "PCCCS403P"},
  #      {"id": 2, "password": "pass2", "name": "Sarah Johnson", "initials": "SJ", "email": "sarah.j@school.edu", "subcode1": "PCCCS404", "subcode2": "PCCCS404P"},
  #      {"id": 4, "password": "pass4", "name": "Emily Davis", "initials": "ED", "email": "emily.d@school.edu", "subcode1": "PCCCS405", "subcode2": "PCCCS405P"},
   #     {"id": 5, "password": "pass5", "name": "Robert Wilson", "initials": "RW", "email": "robert.w@school.edu", "subcode1": "BSC491", "subcode2": "BSC491P"},
    #    {"id": 6, "password": "pass6", "name": "Lisa Anderson", "initials": "LA", "email": "lisa.a@school.edu", "subcode1": "HSMC402", "subcode2": "PCCCS403"},
     #   {"id": 7, "password": "pass7", "name": "David Martinez", "initials": "DM", "email": "david.m@school.edu", "subcode1": "PCCCS404", "subcode2": "PLT401"},
      #  {"id": 8, "password": "pass8", "name": "Jennifer Taylor", "initials": "JT", "email": "jennifer.t@school.edu", "subcode1": "PCCCS405", "subcode2": "BSC491"},
       # {"id": 9, "password": "pass9", "name": "James Thomas", "initials": "JMT", "email": "james.t@school.edu", "subcode1": "HSMC402", "subcode2": "PCCCS403"},
        #{"id": 10, "password": "pass10", "name": "Maria Garcia", "initials": "MG", "email": "maria.g@school.edu", "subcode1": "PLT401", "subcode2": "PCCCS404"},
       # {"id": 11, "password": "pass11", "name": "William Jones", "initials": "WJ", "email": "william.j@school.edu", "subcode1": "BSC491", "subcode2": "PCCCS405"},
        #{"id": 12, "password": "pass12", "name": "Patricia Miller", "initials": "PM", "email": "patricia.m@school.edu", "subcode1": "PCCCS403P", "subcode2": "PCCCS404P"},
       # {"id": 13, "password": "pass13", "name": "Christopher Davis", "initials": "CD", "email": "chris.d@school.edu", "subcode1": "PLT401P", "subcode2": "BSC491P"},
    #]
    
    # Clear existing data
    db.query(models.FACULTY).delete()
    db.commit()
    
    # Insert new data
    #print(f"✅ Created {len(faculty_data)} faculty records")

def setup_students(db):
    """Setup STUDENT table with data"""
 #   student_data = [
  #      {"id": "STU001", "password": "pass1", "name": "Alice Johnson", "roll_number": 101, "section": "A"},
   #     {"id": "STU002", "password": "pass2", "name": "Bob Smith", "roll_number": 102, "section": "A"},
    #    {"id": "STU003", "password": "pass3", "name": "Charlie Brown", "roll_number": 103, "section": "B"},
     #   {"id": "STU004", "password": "pass4", "name": "Diana Prince", "roll_number": 104, "section": "B"},
      #  {"id": "STU005", "password": "pass5", "name": "Edward Norton", "roll_number": 105, "section": "A"},
      #  {"id": "STU006", "password": "pass6", "name": "Fiona Green", "roll_number": 106, "section": "C"},
      #  {"id": "STU007", "password": "pass7", "name": "George Wilson", "roll_number": 107, "section": "C"},
      #  {"id": "STU008", "password": "pass8", "name": "Hannah Lee", "roll_number": 108, "section": "B"},
       # {"id": "STU009", "password": "pass9", "name": "Ian Miller", "roll_number": 109, "section": "A"},
       # {"id": "STU010", "password": "pass10", "name": "Julia Roberts", "roll_number": 110, "section": "C"},
       # {"id": "STU011", "password": "pass11", "name": "Kevin Hart", "roll_number": 111, "section": "B"},
       # {"id": "STU012", "password": "pass12", "name": "Laura Palmer", "roll_number": 112, "section": "A"},
   # ]
    
    # Clear existing data
    db.query(models.STUDENT).delete()
    db.commit()
    
    # Insert new data
    #for student_info in student_data:
    #    student = models.STUDENT(**student_info)
    #    db.add(student)
    
    #print(f"✅ Created {len(student_data)} student records")

def setup_schedule(db):
    """Setup SCHEDULE table with data"""
    
    
    # Clear existing data
    db.query(models.SCHEDULE).delete()
    db.commit()
    
    # Insert new data

if __name__ == "__main__":
    setup_database()
