import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import FACULTY, STUDENT

# Check all users in database
db = SessionLocal()
try:
    students = db.query(STUDENT).all()
    print(f'Found {len(students)} students:')
    for student in students:
        print(f'  - ID: {student.id}, Name: {student.name}, Section: {student.section}')
    
    faculty = db.query(FACULTY).all()
    print(f'Found {len(faculty)} faculty:')
    for fac in faculty:
        print(f'  - ID: {fac.id}, Name: {fac.name}, Email: {fac.email}')
            
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
