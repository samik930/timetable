import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import SUBJECTS
from schedule_generator import ScheduleGenerator

def test_periods_calculation():
    """Test periods calculation"""
    db = SessionLocal()
    try:
        generator = ScheduleGenerator(db)
        
        subjects = db.query(SUBJECTS).all()
        print("Periods calculation:")
        for subject in subjects:
            try:
                periods = generator.calculate_periods_needed(subject.code)
                print(f"  {subject.code} ({subject.subtype}, {subject.credits} credits): {periods} periods/week")
            except Exception as e:
                print(f"  {subject.code}: ERROR - {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_periods_calculation()
