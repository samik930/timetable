import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import STUDENT
from auth import verify_password

# Test student password verification
db = SessionLocal()
try:
    student = db.query(STUDENT).filter(STUDENT.id == '1').first()
    if student:
        print(f'Student found: {student.name}')
        print(f'Stored password (first 20 chars): {student.password[:20]}...')
        print(f'Password length: {len(student.password)}')
        
        # Test with common passwords
        test_passwords = ['password123', 'admin', 'test', 'student123', '123456']
        for pwd in test_passwords:
            result = verify_password(pwd, student.password)
            print(f'Password "{pwd}": {result}')
            
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
