from sqlalchemy.orm import Session
from models import SUBJECTS, FACULTY, SCHEDULE
from typing import List, Dict, Optional
import uuid

class ScheduleGenerator:
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
        
    def create_schedule_entry(self, day_id: int, period_id: int, subcode: str, section: str, fini: str) -> SCHEDULE:
        """Create a single schedule entry"""
        
        # Verify subject exists
        subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == subcode).first()
        if not subject:
            raise ValueError(f"Subject with code {subcode} not found")
        
        # Verify teacher exists
        teacher = self.db.query(FACULTY).filter(FACULTY.initials == fini).first()
        if not teacher:
            raise ValueError(f"Teacher with initials {fini} not found")
        
        # Check for conflicts
        existing = self.db.query(SCHEDULE).filter(
            SCHEDULE.day_id == day_id,
            SCHEDULE.period_id == period_id,
            SCHEDULE.section == section
        ).first()
        
        if existing:
            raise ValueError(f"Schedule conflict: Section {section} already has a class at day {day_id}, period {period_id}")
        
        # Check teacher availability (any class at same time)
        teacher_conflict = self.db.query(SCHEDULE).filter(
            SCHEDULE.day_id == day_id,
            SCHEDULE.period_id == period_id,
            SCHEDULE.fini == fini
        ).first()
        
        if teacher_conflict:
            raise ValueError(f"Teacher {fini} already has a class at day {day_id}, period {period_id}")
        
        # Check if teacher is teaching the same subject at same time in another section
        same_subject_conflict = self.db.query(SCHEDULE).filter(
            SCHEDULE.day_id == day_id,
            SCHEDULE.period_id == period_id,
            SCHEDULE.fini == fini,
            SCHEDULE.subcode == subcode,
            SCHEDULE.section != section
        ).first()
        
        if same_subject_conflict:
            raise ValueError(f"Teacher {fini} is already teaching {subcode} at day {day_id}, period {period_id} in section {same_subject_conflict.section}. Cannot teach the same subject in multiple sections at the same time.")
        
        # Create schedule entry
        schedule_id = str(uuid.uuid4())[:8]  # Generate short unique ID
        timetable_entry = SCHEDULE(
            id=schedule_id,
            day_id=day_id,
            period_id=period_id,
            subcode=subcode,
            section=section,
            fini=fini
        )
        
        self.db.add(timetable_entry)
        self.db.commit()
        self.db.refresh(timetable_entry)
        
        return timetable_entry
    
    def get_schedule_by_section(self, section: str) -> List[Dict]:
        """Get schedule for a specific section"""
        schedule = self.db.query(SCHEDULE).filter(
            SCHEDULE.section == section
        ).all()
        
        result = []
        for entry in schedule:
            # Handle None values for subcode and fini
            subcode = entry.subcode if entry.subcode else None
            fini = entry.fini if entry.fini else None
            
            subject = None
            if subcode:
                subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == subcode).first()
            
            teacher = None
            if fini:
                teacher = self.db.query(FACULTY).filter(FACULTY.initials == fini).first()
            
            result.append({
                "id": entry.id,
                "day_id": entry.day_id,
                "period_id": entry.period_id,
                "subcode": subcode,
                "subject_name": subject.name if subject else "Unknown",
                "section": entry.section,
                "fini": fini,
                "teacher_name": teacher.name if teacher else "Unknown"
            })
        
        return result
    
    def get_schedule_by_teacher(self, fini: str) -> List[Dict]:
        """Get schedule for a specific teacher"""
        schedule = self.db.query(SCHEDULE).filter(
            SCHEDULE.fini == fini
        ).all()
        
        result = []
        for entry in schedule:
            subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == entry.subcode).first()
            
            result.append({
                "id": entry.id,
                "day_id": entry.day_id,
                "period_id": entry.period_id,
                "subcode": entry.subcode,
                "subject_name": subject.name if subject else "Unknown",
                "section": entry.section,
                "fini": entry.fini
            })
        
        return result
    
    def get_full_schedule(self) -> List[Dict]:
        """Get complete schedule"""
        schedule = self.db.query(SCHEDULE).all()
        
        result = []
        for entry in schedule:
            subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == entry.subcode).first()
            teacher = self.db.query(FACULTY).filter(FACULTY.initials == entry.fini).first()
            
            result.append({
                "id": entry.id,
                "day_id": entry.day_id,
                "period_id": entry.period_id,
                "subcode": entry.subcode,
                "subject_name": subject.name if subject else "Unknown",
                "section": entry.section,
                "fini": entry.fini,
                "teacher_name": teacher.name if teacher else "Unknown"
            })
        
        return result
    
    def update_schedule_entry(self, entry_id: str, day_id: int = None, period_id: int = None, 
                           subcode: str = None, section: str = None, fini: str = None) -> SCHEDULE:
        """Update an existing schedule entry"""
        
        entry = self.db.query(SCHEDULE).filter(SCHEDULE.id == entry_id).first()
        if not entry:
            raise ValueError(f"Schedule entry with id {entry_id} not found")
        
        # Get final values (use existing if not provided)
        final_day_id = day_id if day_id is not None else entry.day_id
        final_period_id = period_id if period_id is not None else entry.period_id
        final_subcode = subcode if subcode is not None else entry.subcode
        final_section = section if section is not None else entry.section
        final_fini = fini if fini is not None else entry.fini
        
        # Check for conflicts with other entries (excluding current entry)
        # Check section conflict
        section_conflict = self.db.query(SCHEDULE).filter(
            SCHEDULE.day_id == final_day_id,
            SCHEDULE.period_id == final_period_id,
            SCHEDULE.section == final_section,
            SCHEDULE.id != entry_id
        ).first()
        
        if section_conflict:
            raise ValueError(f"Schedule conflict: Section {final_section} already has a class at day {final_day_id}, period {final_period_id}")
        
        # Check teacher availability (any class at same time)
        teacher_conflict = self.db.query(SCHEDULE).filter(
            SCHEDULE.day_id == final_day_id,
            SCHEDULE.period_id == final_period_id,
            SCHEDULE.fini == final_fini,
            SCHEDULE.id != entry_id
        ).first()
        
        if teacher_conflict:
            raise ValueError(f"Teacher {final_fini} already has a class at day {final_day_id}, period {final_period_id}")
        
        # Check if teacher is teaching the same subject at same time in another section
        same_subject_conflict = self.db.query(SCHEDULE).filter(
            SCHEDULE.day_id == final_day_id,
            SCHEDULE.period_id == final_period_id,
            SCHEDULE.fini == final_fini,
            SCHEDULE.subcode == final_subcode,
            SCHEDULE.section != final_section,
            SCHEDULE.id != entry_id
        ).first()
        
        if same_subject_conflict:
            raise ValueError(f"Teacher {final_fini} is already teaching {final_subcode} at day {final_day_id}, period {final_period_id} in section {same_subject_conflict.section}. Cannot teach the same subject in multiple sections at the same time.")
        
        # Update fields if provided
        if day_id is not None:
            entry.day_id = day_id
        if period_id is not None:
            entry.period_id = period_id
        if subcode is not None:
            # Verify subject exists
            subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == subcode).first()
            if not subject:
                raise ValueError(f"Subject with code {subcode} not found")
            entry.subcode = subcode
        if section is not None:
            entry.section = section
        if fini is not None:
            # Verify teacher exists
            teacher = self.db.query(FACULTY).filter(FACULTY.initials == fini).first()
            if not teacher:
                raise ValueError(f"Teacher with initials {fini} not found")
            entry.fini = fini
        
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    def delete_schedule_entry(self, entry_id: str) -> bool:
        """Delete a schedule entry"""
        
        entry = self.db.query(SCHEDULE).filter(SCHEDULE.id == entry_id).first()
        if not entry:
            return False
        
        self.db.delete(entry)
        self.db.commit()
        
        return True
    
    def detect_conflicts(self) -> List[Dict]:
        """Detect conflicts in the schedule"""
        conflicts = []
        
        # Check section conflicts
        schedule = self.db.query(SCHEDULE).all()
        schedule_dict = {}
        
        for entry in schedule:
            key = f"{entry.day_id}_{entry.period_id}_{entry.section}"
            if key in schedule_dict:
                conflicts.append({
                    "type": "section_conflict",
                    "day_id": entry.day_id,
                    "period_id": entry.period_id,
                    "section": entry.section,
                    "entries": [schedule_dict[key]["id"], entry.id]
                })
            else:
                schedule_dict[key] = {"id": entry.id}
        
        # Check teacher conflicts
        teacher_dict = {}
        
        for entry in schedule:
            key = f"{entry.day_id}_{entry.period_id}_{entry.fini}"
            if key in teacher_dict:
                conflicts.append({
                    "type": "teacher_conflict",
                    "day_id": entry.day_id,
                    "period_id": entry.period_id,
                    "fini": entry.fini,
                    "entries": [teacher_dict[key]["id"], entry.id]
                })
            else:
                teacher_dict[key] = {"id": entry.id}
        
        return conflicts
