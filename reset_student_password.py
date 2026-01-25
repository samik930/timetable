import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import STUDENT
from auth import get_password_hash

# Reset student password to a known value
db = SessionLocal()
try:
    student = db.query(STUDENT).filter(STUDENT.id == '1').first()
    if student:
        print(f'Student found: {student.name}')
        # Reset password to 'student123'
        new_password = 'student123'
        hashed_password = get_password_hash(new_password)
        student.password = hashed_password
        db.commit()
        print(f'Password reset successfully for student {student.id}')
        print(f'New password is: {new_password}')
        
        # Test the new password
        from auth import verify_password
        if verify_password(new_password, hashed_password):
            print('Password verification test passed!')
        else:
            print('Password verification test failed!')
            
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
