from sqlalchemy.orm import Session
from models import SUBJECTS, FACULTY, SCHEDULE
from typing import List, Dict, Tuple, Optional
import uuid
from datetime import datetime
import random

class AutomatedTimetableGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.sections = ['A', 'B', 'C']  # 3 sections
        self.working_days = [1, 2, 3, 4, 5]  # Monday to Friday
        self.periods_per_day = 8  # 8 periods per day
        self.break_period = 4  # 4th period is break
        
    def generate_automated_timetable(self, subject_faculty_assignments: Dict[str, Dict]) -> Dict:
        """
        Generate automated timetable for all sections
        
        Args:
            subject_faculty_assignments: Dict with section as key and subject-faculty mapping as value
            Example: {
                'A': {'CS101': 'ABC', 'CS102': 'XYZ'},
                'B': {'CS101': 'PQR', 'CS102': 'XYZ'},
                'C': {'CS101': 'ABC', 'CS102': 'LMN'}
            }
        """
        
        # Generate timetable for each section
        results = {}
        for section in self.sections:
            if section in subject_faculty_assignments:
                section_schedule = self._generate_section_timetable(
                    section, 
                    subject_faculty_assignments[section]
                )
                results[section] = section_schedule
            else:
                # For sections not being generated, check if they already have schedules
                existing_schedule = self._get_section_schedule(section)
                if existing_schedule:
                    results[section] = {
                        "status": "existing", 
                        "message": f"Existing timetable found for section {section}",
                        "schedule": existing_schedule
                    }
                else:
                    results[section] = {"status": "skipped", "reason": "No assignments provided"}
        
        return results
    
    def _clear_all_schedules(self):
        """Clear all existing schedule entries"""
        self.db.query(SCHEDULE).delete()
        self.db.commit()
    
    def _clear_section_schedule(self, section: str):
        """Clear existing schedule entries for a specific section"""
        self.db.query(SCHEDULE).filter(SCHEDULE.section == section).delete()
        self.db.commit()
    
    def _generate_section_timetable(self, section: str, subject_faculty_map: Dict[str, str]) -> Dict:
        """Generate timetable for a single section"""
        
        # Clear existing schedule for this section only
        self._clear_section_schedule(section)
        
        # Validate subject-faculty assignments
        validation_result = self._validate_assignments(subject_faculty_map)
        if not validation_result["valid"]:
            return {"status": "error", "message": validation_result["message"]}
        
        # Get subject requirements
        subject_requirements = self._get_subject_requirements(subject_faculty_map.keys())
        
        # Create schedule matrix
        schedule_matrix = self._initialize_schedule_matrix()
        
        # Schedule subjects
        scheduling_result = self._schedule_subjects(
            section, 
            subject_faculty_map, 
            subject_requirements, 
            schedule_matrix
        )
        
        if scheduling_result["success"]:
            return {
                "status": "success", 
                "message": f"Timetable generated for section {section}",
                "schedule": self._get_section_schedule(section)
            }
        else:
            return {
                "status": "error", 
                "message": scheduling_result["message"]
            }
    
    def _validate_assignments(self, subject_faculty_map: Dict[str, str]) -> Dict:
        """Validate subject-faculty assignments"""
        
        for subcode, fini in subject_faculty_map.items():
            # Check if subject exists
            subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == subcode).first()
            if not subject:
                return {"valid": False, "message": f"Subject {subcode} not found"}
            
            # Check if faculty exists
            faculty = self.db.query(FACULTY).filter(FACULTY.initials == fini).first()
            if not faculty:
                return {"valid": False, "message": f"Faculty {fini} not found"}
        
        return {"valid": True, "message": "All assignments valid"}
    
    def _get_subject_requirements(self, subject_codes: List[str]) -> Dict[str, Dict]:
        """Get requirements for each subject"""
        requirements = {}
        
        for subcode in subject_codes:
            subject = self.db.query(SUBJECTS).filter(SUBJECTS.code == subcode).first()
            if subject:
                periods_needed = self._calculate_periods_needed(subject)
                is_lab = subject.subtype.upper() in ['L', 'P']
                
                requirements[subcode] = {
                    'name': subject.name,
                    'credits': subject.credits,
                    'subtype': subject.subtype,
                    'periods_needed': periods_needed,
                    'is_lab': is_lab,
                    'consecutive_periods': self._get_consecutive_periods_needed(subject)
                }
        
        return requirements
    
    def _calculate_periods_needed(self, subject) -> int:
        """Calculate periods needed based on credits and type"""
        if subject.subtype.upper() == 'T':
            return int(subject.credits)
        elif subject.subtype.upper() in ['L', 'P']:
            return int(2 * subject.credits)
        else:
            return int(subject.credits)
    
    def _get_consecutive_periods_needed(self, subject) -> int:
        """Get number of consecutive periods needed for lab subjects"""
        if subject.subtype.upper() in ['L', 'P']:
            if subject.credits == 1.5:
                return 3  # 1.5 credits = 3 consecutive periods
            elif subject.credits == 1.0:
                return 2  # 1 credit = 2 consecutive periods
            else:
                return int(subject.credits)  # Default behavior
        return 1  # Theory subjects don't need consecutive periods
    
    def _initialize_schedule_matrix(self) -> Dict:
        """Initialize empty schedule matrix"""
        schedule = {}
        for day in self.working_days:
            schedule[day] = {}
            for period in range(1, self.periods_per_day + 1):
                schedule[day][period] = None
        return schedule
    
    def _schedule_subjects(self, section: str, subject_faculty_map: Dict[str, str], 
                          subject_requirements: Dict, schedule_matrix: Dict) -> Dict:
        """Schedule all subjects for a section"""
        
        # Sort subjects by priority (labs first, then by periods needed)
        sorted_subjects = sorted(
            subject_requirements.items(),
            key=lambda x: (not x[1]['is_lab'], -x[1]['periods_needed'])
        )
        
        for subcode, req in sorted_subjects:
            success = self._schedule_single_subject(
                section, subcode, subject_faculty_map[subcode], req, schedule_matrix
            )
            
            if not success:
                return {
                    "success": False,
                    "message": f"Failed to schedule {subcode} for section {section}"
                }
        
        # Save schedule to database
        self._save_schedule_to_db(section, schedule_matrix)
        
        return {"success": True, "message": "All subjects scheduled successfully"}
    
    def _schedule_single_subject(self, section: str, subcode: str, fini: str, 
                               req: Dict, schedule_matrix: Dict) -> bool:
        """Schedule a single subject"""
        
        periods_scheduled = 0
        periods_needed = req['periods_needed']
        
        if req['is_lab']:
            # Schedule lab periods consecutively
            consecutive_needed = req['consecutive_periods']
            blocks_needed = periods_needed // consecutive_needed
            
            for block in range(blocks_needed):
                if periods_scheduled >= periods_needed:
                    break
                    
                # Find consecutive slots
                start_day, start_period = self._find_consecutive_slots(
                    section, fini, consecutive_needed, schedule_matrix
                )
                
                if start_day is None:
                    return False  # Cannot find consecutive slots
                
                # Schedule the consecutive periods
                for i in range(consecutive_needed):
                    schedule_matrix[start_day][start_period + i] = {
                        'subcode': subcode,
                        'fini': fini,
                        'name': req['name']
                    }
                    periods_scheduled += 1
        else:
            # Schedule theory periods individually
            for _ in range(periods_needed):
                day, period = self._find_available_slot(section, fini, schedule_matrix)
                
                if day is None:
                    return False  # Cannot find available slot
                
                schedule_matrix[day][period] = {
                    'subcode': subcode,
                    'fini': fini,
                    'name': req['name']
                }
                periods_scheduled += 1
        
        return periods_scheduled == periods_needed
    
    def _find_consecutive_slots(self, section: str, fini: str, consecutive_needed: int, 
                               schedule_matrix: Dict) -> Tuple[Optional[int], Optional[int]]:
        """Find consecutive available slots for lab periods"""
        
        # Try different days in random order for better distribution
        days_shuffled = self.working_days.copy()
        random.shuffle(days_shuffled)
        
        for day in days_shuffled:
            # Try different starting periods
            for start_period in range(1, self.periods_per_day - consecutive_needed + 2):
                # Skip if this would include the break period
                if self.break_period >= start_period and self.break_period < start_period + consecutive_needed:
                    continue
                
                # Check if all consecutive slots are available
                all_available = True
                for i in range(consecutive_needed):
                    period = start_period + i
                    if not self._is_slot_available(day, period, section, fini, schedule_matrix):
                        all_available = False
                        break
                
                if all_available:
                    return day, start_period
        
        return None, None
    
    def _find_available_slot(self, section: str, fini: str, schedule_matrix: Dict) -> Tuple[Optional[int], Optional[int]]:
        """Find a single available slot"""
        
        # Try different days in random order for better distribution
        days_shuffled = self.working_days.copy()
        random.shuffle(days_shuffled)
        
        for day in days_shuffled:
            for period in range(1, self.periods_per_day + 1):
                # Skip break period
                if period == self.break_period:
                    continue
                
                if self._is_slot_available(day, period, section, fini, schedule_matrix):
                    return day, period
        
        return None, None
    
    def _is_slot_available(self, day: int, period: int, section: str, fini: str, schedule_matrix: Dict) -> bool:
        """Check if a slot is available"""
        
        # Check if slot is already occupied in this section
        if schedule_matrix[day][period] is not None:
            return False
        
        # Check for teacher conflict across all sections
        for other_section in self.sections:
            if other_section != section:
                other_schedule = self._get_section_schedule_from_db(other_section)
                for entry in other_schedule:
                    if entry['day_id'] == day and entry['period_id'] == period and entry['fini'] == fini:
                        return False
        
        return True
    
    def _get_section_schedule_from_db(self, section: str) -> List[Dict]:
        """Get existing schedule for a section from database"""
        schedule = self.db.query(SCHEDULE).filter(SCHEDULE.section == section).all()
        return [
            {
                'day_id': entry.day_id,
                'period_id': entry.period_id,
                'subcode': entry.subcode,
                'fini': entry.fini
            }
            for entry in schedule
        ]
    
    def _save_schedule_to_db(self, section: str, schedule_matrix: Dict):
        """Save schedule matrix to database"""
        
        for day in self.working_days:
            for period in range(1, self.periods_per_day + 1):
                entry = schedule_matrix[day][period]
                if entry is not None:
                    schedule_entry = SCHEDULE(
                        id=str(uuid.uuid4())[:8],
                        day_id=day,
                        period_id=period,
                        subcode=entry['subcode'],
                        section=section,
                        fini=entry['fini']
                    )
                    self.db.add(schedule_entry)
        
        self.db.commit()
    
    def _get_section_schedule(self, section: str) -> List[Dict]:
        """Get formatted schedule for a section"""
        schedule = self.db.query(SCHEDULE).filter(SCHEDULE.section == section).all()
        
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
    
    def get_available_subjects(self) -> List[Dict]:
        """Get all available subjects"""
        subjects = self.db.query(SUBJECTS).all()
        return [
            {
                "code": subject.code,
                "name": subject.name,
                "credits": subject.credits,
                "subtype": subject.subtype
            }
            for subject in subjects
        ]
    
    def get_available_faculty(self) -> List[Dict]:
        """Get all available faculty"""
        faculty_list = self.db.query(FACULTY).all()
        return [
            {
                "id": faculty.id,
                "name": faculty.name,
                "initials": faculty.initials,
                "email": faculty.email,
                "subcode1": faculty.subcode1,
                "subcode2": faculty.subcode2
            }
            for faculty in faculty_list
        ]
