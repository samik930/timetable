import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import SUBJECTS

def check_subjects_data():
    """Check subjects data"""
    db = SessionLocal()
    try:
        subjects = db.query(SUBJECTS).all()
        print(f"Found {len(subjects)} subjects:")
        for subject in subjects:
            print(f"  - {subject.code}: {subject.name} ({subject.subtype}) - Credits: {subject.credits}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_subjects_data()
