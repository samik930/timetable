from sqlalchemy.orm import Session
from models import Class, Subject, Teacher, TimeSlot, Timetable, ClassSubject, TeacherAvailability
from typing import List, Dict, Tuple, Optional
import random

class TimetableGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.timetable_entries = []
        
    def generate_timetable(self, class_id: int) -> List[Timetable]:
        """Generate timetable for a specific class using greedy algorithm"""
        
        # Clear existing timetable for this class
        self.db.query(Timetable).filter(Timetable.class_id == class_id).delete()
        self.db.commit()
        
        # Get class information
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise ValueError(f"Class with id {class_id} not found")
        
        # Get class subjects with assigned teachers
        class_subjects = self.db.query(ClassSubject).filter(
            ClassSubject.class_id == class_id
        ).all()
        
        if not class_subjects:
            raise ValueError(f"No subjects assigned to class {class_obj.name}")
        
        # Get all time slots
        time_slots = self.db.query(TimeSlot).order_by(
            TimeSlot.day_of_week, TimeSlot.period_number
        ).all()
        
        # Generate timetable using greedy approach
        timetable_entries = []
        
        for class_subject in class_subjects:
            subject = class_subject.subject
            teacher = class_subject.teacher
            periods_needed = class_subject.periods_per_week
            
            # Find available slots for this subject
            assigned_periods = 0
            attempts = 0
            max_attempts = len(time_slots) * 2
            
            while assigned_periods < periods_needed and attempts < max_attempts:
                attempts += 1
                
                # Try each time slot
                for time_slot in time_slots:
                    if assigned_periods >= periods_needed:
                        break
                    
                    # Check if slot is available
                    if self._is_slot_available(
                        time_slot, teacher.id, class_id, timetable_entries
                    ):
                        # Create timetable entry
                        timetable_entry = Timetable(
                            class_id=class_id,
                            subject_id=subject.id,
                            teacher_id=teacher.id,
                            time_slot_id=time_slot.id,
                            room=f"Room-{random.randint(1, 20)}"
                        )
                        timetable_entries.append(timetable_entry)
                        assigned_periods += 1
            
            if assigned_periods < periods_needed:
                print(f"Warning: Could only assign {assigned_periods}/{periods_needed} periods for {subject.name} in {class_obj.name}")
        
        # Save to database
        for entry in timetable_entries:
            self.db.add(entry)
        self.db.commit()
        
        return timetable_entries
    
    def _is_slot_available(
        self, 
        time_slot: TimeSlot, 
        teacher_id: int, 
        class_id: int, 
        current_entries: List[Timetable]
    ) -> bool:
        """Check if a time slot is available for assignment"""
        
        # Check teacher availability
        teacher_availability = self.db.query(TeacherAvailability).filter(
            TeacherAvailability.teacher_id == teacher_id,
            TeacherAvailability.day_of_week == time_slot.day_of_week,
            TeacherAvailability.period_number == time_slot.period_number,
            TeacherAvailability.is_available == True
        ).first()
        
        if not teacher_availability:
            return False
        
        # Check if teacher already has a class at this time
        teacher_conflict = self.db.query(Timetable).filter(
            Timetable.teacher_id == teacher_id,
            Timetable.time_slot_id == time_slot.id
        ).first()
        
        if teacher_conflict:
            return False
        
        # Check if class already has a subject at this time
        class_conflict = self.db.query(Timetable).filter(
            Timetable.class_id == class_id,
            Timetable.time_slot_id == time_slot.id
        ).first()
        
        if class_conflict:
            return False
        
        # Check against current entries (not yet saved)
        for entry in current_entries:
            if (entry.teacher_id == teacher_id and entry.time_slot_id == time_slot.id) or \
               (entry.class_id == class_id and entry.time_slot_id == time_slot.id):
                return False
        
        return True
    
    def get_teacher_schedule(self, teacher_id: int) -> List[Dict]:
        """Get schedule for a specific teacher"""
        timetable = self.db.query(Timetable).filter(
            Timetable.teacher_id == teacher_id
        ).all()
        
        schedule = []
        for entry in timetable:
            schedule.append({
                "day": entry.time_slot.day_of_week,
                "period": entry.time_slot.period_number,
                "class": entry.class_.name,
                "subject": entry.subject.name,
                "room": entry.room
            })
        
        return schedule
    
    def get_class_schedule(self, class_id: int) -> List[Dict]:
        """Get schedule for a specific class"""
        timetable = self.db.query(Timetable).filter(
            Timetable.class_id == class_id
        ).all()
        
        schedule = []
        for entry in timetable:
            schedule.append({
                "day": entry.time_slot.day_of_week,
                "period": entry.time_slot.period_number,
                "subject": entry.subject.name,
                "teacher": entry.teacher.name,
                "room": entry.room,
                "start_time": entry.time_slot.start_time,
                "end_time": entry.time_slot.end_time
            })
        
        return schedule
    
    def detect_conflicts(self) -> List[Dict]:
        """Detect conflicts in the current timetable"""
        conflicts = []
        
        # Check teacher conflicts
        teacher_schedules = self.db.query(Timetable).all()
        schedule_dict = {}
        
        for entry in teacher_schedules:
            key = f"{entry.teacher_id}_{entry.time_slot_id}"
            if key in schedule_dict:
                conflicts.append({
                    "type": "teacher_conflict",
                    "teacher_id": entry.teacher_id,
                    "time_slot_id": entry.time_slot_id,
                    "classes": [schedule_dict[key]["class_id"], entry.class_id]
                })
            else:
                schedule_dict[key] = {"class_id": entry.class_id}
        
        # Check class conflicts
        class_schedules = self.db.query(Timetable).all()
        class_dict = {}
        
        for entry in class_schedules:
            key = f"{entry.class_id}_{entry.time_slot_id}"
            if key in class_dict:
                conflicts.append({
                    "type": "class_conflict",
                    "class_id": entry.class_id,
                    "time_slot_id": entry.time_slot_id,
                    "subjects": [class_dict[key]["subject_id"], entry.subject_id]
                })
            else:
                class_dict[key] = {"subject_id": entry.subject_id}
        
        return conflicts
