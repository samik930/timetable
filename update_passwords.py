import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import STUDENT, FACULTY
from auth import get_password_hash

def update_existing_passwords():
    """Update existing plain text passwords to hashed passwords"""
    db = SessionLocal()
    try:
        # Update student passwords
        students = db.query(STUDENT).all()
        for student in students:
            if student.password and not student.password.startswith('$2b$'):
                print(f"Updating password for student: {student.id}")
                try:
                    student.password = get_password_hash(student.password)
                except Exception as e:
                    print(f"Error hashing student {student.id} password: {e}")
                    # Set a default hashed password if hashing fails
                    student.password = get_password_hash("default123")
        
        # Update faculty passwords
        faculty = db.query(FACULTY).all()
        for fac in faculty:
            if fac.password and not fac.password.startswith('$2b$'):
                print(f"Updating password for faculty: {fac.name} ({fac.email})")
                try:
                    fac.password = get_password_hash(fac.password)
                except Exception as e:
                    print(f"Error hashing faculty {fac.email} password: {e}")
                    # Set a default hashed password if hashing fails
                    fac.password = get_password_hash("default123")
        
        db.commit()
        print("Password hashing completed successfully!")
        
    except Exception as e:
        print(f"Error updating passwords: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_existing_passwords()
