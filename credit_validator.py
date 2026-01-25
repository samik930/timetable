from sqlalchemy.orm import Session
from models import SUBJECTS, SCHEDULE

class CreditValidator:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_periods_needed(self, subcode: str) -> int:
        """Calculate number of periods needed per week based on subject credits and type"""
        subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == subcode).first()
        if not subject:
            raise ValueError(f"Subject with code {subcode} not found")
        
        if not subject.credits:
            raise ValueError(f"Subject {subcode} has no credits defined")
        
        # For theory subjects ('T'): credits = number of classes per week
        if subject.subtype.upper() == 'T':
            return int(subject.credits)
        
        # For lab subjects ('L'/'P'): classes per week = 2 × credits
        elif subject.subtype.upper() in ['L', 'P']:
            periods_needed = int(2 * subject.credits)
            return periods_needed
        
        else:
            # Default to credits if subject type is unknown
            return int(subject.credits)
    
    def get_current_periods_count(self, subcode: str, section: str) -> int:
        """Get current number of periods scheduled for a subject in a section"""
        count = self.db.query(SCHEDULE).filter(
            SCHEDULE.subcode == subcode,
            SCHEDULE.section == section
        ).count()
        return count
    
    def validate_schedule_entry(self, subcode: str, section: str, day_id: int, period_id: int) -> dict:
        """Validate if a schedule entry can be added without exceeding credit limits"""
        try:
            # Check if subject exists
            subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == subcode).first()
            if not subject:
                return {
                    "valid": False,
                    "message": f"Subject {subcode} not found"
                }
            
            # Calculate required periods
            max_periods = self.calculate_periods_needed(subcode)
            
            # Get current periods count
            current_periods = self.get_current_periods_count(subcode, section)
            
            # Check if adding this entry would exceed the limit
            if current_periods >= max_periods:
                return {
                    "valid": False,
                    "message": f"Cannot add more classes for {subject.name} ({subcode}). Maximum {max_periods} classes allowed, but {current_periods} already scheduled."
                }
            
            # Check for slot conflicts
            existing_slot = self.db.query(SCHEDULE).filter(
                SCHEDULE.day_id == day_id,
                SCHEDULE.period_id == period_id,
                SCHEDULE.section == section
            ).first()
            
            if existing_slot:
                return {
                    "valid": False,
                    "message": f"Slot already occupied: Day {day_id}, Period {period_id} in Section {section} has {existing_slot.subcode}"
                }
            
            return {
                "valid": True,
                "message": f"Can add {subject.name} ({subcode}) to Section {section}, Day {day_id}, Period {period_id}"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}"
            }
