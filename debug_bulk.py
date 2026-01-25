import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import SUBJECTS
from schedule_generator import ScheduleGenerator

def debug_bulk_endpoint():
    """Debug the bulk endpoint logic"""
    db = SessionLocal()
    try:
        generator = ScheduleGenerator(db)
        
        # Get all subjects
        subjects = db.query(SUBJECTS).all()
        print(f"Found {len(subjects)} subjects")
        
        periods_info = []
        for i, subject in enumerate(subjects):
            print(f"Processing subject {i+1}: {subject.code}")
            try:
                periods_needed = generator.calculate_periods_needed(subject.code)
                print(f"  ✅ Success: {periods_needed} periods")
                periods_info.append({
                    "code": subject.code,
                    "name": subject.name,
                    "subtype": subject.subtype,
                    "credits": subject.credits,
                    "periods_needed": periods_needed
                })
            except Exception as e:
                print(f"  ❌ Error: {e}")
                periods_info.append({
                    "code": subject.code,
                    "name": subject.name,
                    "subtype": subject.subtype,
                    "credits": subject.credits,
                    "periods_needed": None,
                    "error": str(e)
                })
                # Don't break, continue with other subjects
        
        print(f"\nFinal result: {len(periods_info)} items")
        return periods_info
            
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        db.close()

if __name__ == "__main__":
    result = debug_bulk_endpoint()
    print(f"\nResult length: {len(result)}")
