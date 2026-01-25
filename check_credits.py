import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from sqlalchemy import text

def check_subjects_columns():
    """Check columns in SUBJECTS table"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'SUBJECTS'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print("Columns in SUBJECTS table:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_subjects_columns()
