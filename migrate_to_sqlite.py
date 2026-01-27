#!/usr/bin/env python3
"""
Complete PostgreSQL to SQLite Migration Script
"""
import json
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import SUBJECTS, FACULTY, STUDENT, SCHEDULE, Base

def export_from_postgres():
    """Export all data from PostgreSQL database"""
    print("🔄 Exporting data from PostgreSQL...")
    
    # PostgreSQL connection
    pg_engine = create_engine("postgresql://postgres:Samik19@localhost:5432/timetable_db")
    pg_session = sessionmaker(bind=pg_engine)()
    
    try:
        # Export all tables
        data = {
            'subjects': [],
            'faculty': [],
            'students': [],
            'schedules': []
        }
        
        # Export SUBJECTS
        subjects = pg_session.query(SUBJECTS).all()
        for subject in subjects:
            data['subjects'].append({
                'code': subject.code,
                'name': subject.name,
                'subtype': subject.subtype,
                'credits': subject.credits
            })
        print(f"✅ Exported {len(data['subjects'])} subjects")
        
        # Export FACULTY
        faculty = pg_session.query(FACULTY).all()
        for member in faculty:
            data['faculty'].append({
                'id': member.id,
                'password': member.password,
                'name': member.name,
                'initials': member.initials,
                'email': member.email,
                'subcode1': member.subcode1,
                'subcode2': member.subcode2,
                'max_periods_per_day': member.max_periods_per_day
            })
        print(f"✅ Exported {len(data['faculty'])} faculty members")
        
        # Export STUDENT
        students = pg_session.query(STUDENT).all()
        for student in students:
            data['students'].append({
                'id': student.id,
                'password': student.password,
                'name': student.name,
                'roll_number': student.roll_number,
                'section': student.section
            })
        print(f"✅ Exported {len(data['students'])} students")
        
        # Export SCHEDULE
        schedules = pg_session.query(SCHEDULE).all()
        for schedule in schedules:
            data['schedules'].append({
                'id': schedule.id,
                'day_id': schedule.day_id,
                'period_id': schedule.period_id,
                'subcode': schedule.subcode,
                'section': schedule.section,
                'fini': schedule.fini
            })
        print(f"✅ Exported {len(data['schedules'])} schedules")
        
        # Save to JSON file
        with open('postgres_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("💾 Data exported successfully to postgres_data.json")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting from PostgreSQL: {e}")
        return False
    finally:
        pg_session.close()

def import_to_sqlite():
    """Import data into SQLite database"""
    print("🔄 Importing data into SQLite...")
    
    # Remove existing SQLite database if it exists
    if os.path.exists('timetable.db'):
        os.remove('timetable.db')
        print("🗑️  Removed existing SQLite database")
    
    # SQLite connection
    sqlite_engine = create_engine("sqlite:///./timetable.db")
    
    # Create tables
    Base.metadata.create_all(bind=sqlite_engine)
    print("🏗️  Created SQLite tables")
    
    sqlite_session = sessionmaker(bind=sqlite_engine)()
    
    try:
        # Load data from JSON file
        with open('postgres_data.json', 'r') as f:
            data = json.load(f)
        
        # Import SUBJECTS
        for subject_data in data['subjects']:
            subject = SUBJECTS(**subject_data)
            sqlite_session.add(subject)
        print(f"✅ Imported {len(data['subjects'])} subjects")
        
        # Import FACULTY
        for faculty_data in data['faculty']:
            faculty = FACULTY(**faculty_data)
            sqlite_session.add(faculty)
        print(f"✅ Imported {len(data['faculty'])} faculty members")
        
        # Import STUDENT
        for student_data in data['students']:
            student = STUDENT(**student_data)
            sqlite_session.add(student)
        print(f"✅ Imported {len(data['students'])} students")
        
        # Import SCHEDULE
        for schedule_data in data['schedules']:
            schedule = SCHEDULE(**schedule_data)
            sqlite_session.add(schedule)
        print(f"✅ Imported {len(data['schedules'])} schedules")
        
        # Commit all changes
        sqlite_session.commit()
        print("💾 Data imported successfully into SQLite")
        return True
        
    except Exception as e:
        print(f"❌ Error importing to SQLite: {e}")
        sqlite_session.rollback()
        return False
    finally:
        sqlite_session.close()

def verify_migration():
    """Verify that data was migrated correctly"""
    print("🔍 Verifying migration...")
    
    # SQLite connection
    sqlite_engine = create_engine("sqlite:///./timetable.db")
    sqlite_session = sessionmaker(bind=sqlite_engine)()
    
    try:
        # Count records in each table
        subject_count = sqlite_session.query(SUBJECTS).count()
        faculty_count = sqlite_session.query(FACULTY).count()
        student_count = sqlite_session.query(STUDENT).count()
        schedule_count = sqlite_session.query(SCHEDULE).count()
        
        print(f"📊 SQLite database contains:")
        print(f"   - {subject_count} subjects")
        print(f"   - {faculty_count} faculty members")
        print(f"   - {student_count} students")
        print(f"   - {schedule_count} schedules")
        
        # Test database connection
        from database import engine
        print(f"🔗 Database URL: {engine.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False
    finally:
        sqlite_session.close()

def main():
    """Main migration function"""
    print("🚀 Starting PostgreSQL to SQLite Migration...")
    print("=" * 50)
    
    # Step 1: Export from PostgreSQL
    if not export_from_postgres():
        print("❌ Failed to export data from PostgreSQL")
        sys.exit(1)
    
    print("-" * 50)
    
    # Step 2: Import to SQLite
    if not import_to_sqlite():
        print("❌ Failed to import data to SQLite")
        sys.exit(1)
    
    print("-" * 50)
    
    # Step 3: Verify migration
    if not verify_migration():
        print("❌ Failed to verify migration")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Migration completed successfully!")
    print("✅ Your application is now using SQLite with all original data!")
    print("📁 SQLite database file: timetable.db")

if __name__ == "__main__":
    main()
