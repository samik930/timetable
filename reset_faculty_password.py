import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import FACULTY
from auth import get_password_hash

# Reset faculty password to a known value
db = SessionLocal()
try:
    faculty = db.query(FACULTY).first()
    if faculty:
        print(f'Faculty found: {faculty.name} ({faculty.email})')
        # Reset password to 'faculty123'
        new_password = 'faculty123'
        hashed_password = get_password_hash(new_password)
        faculty.password = hashed_password
        db.commit()
        print(f'Password reset successfully for faculty {faculty.email}')
        print(f'New password is: {new_password}')
        
        # Test the new password
        from auth import verify_password
        if verify_password(new_password, hashed_password):
            print('Password verification test passed!')
        else:
            print('Password verification test failed!')
    else:
        print('No faculty found in database')
            
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
