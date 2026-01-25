from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from sqlalchemy.orm import Session
from models import Class, Teacher, Timetable, TimeSlot
from timetable_generator import TimetableGenerator
from typing import List
import io

class PDFExporter:
    def __init__(self, db: Session):
        self.db = db
        self.styles = getSampleStyleSheet()
        self.generator = TimetableGenerator(db)
        
    def export_class_timetable(self, class_id: int) -> bytes:
        """Export class timetable as PDF"""
        
        # Get class information
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise ValueError(f"Class with id {class_id} not found")
        
        # Get schedule
        schedule = self.generator.get_class_schedule(class_id)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(f"Class Timetable - {class_obj.name}", title_style))
        story.append(Spacer(1, 12))
        
        # Create timetable grid
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        periods = sorted(list(set(entry['period'] for entry in schedule)))
        
        # Get time slots for period headers
        time_slots = {}
        for entry in schedule:
            period = entry['period']
            if period not in time_slots:
                time_slot = self.db.query(TimeSlot).filter(
                    TimeSlot.period_number == period
                ).first()
                if time_slot:
                    time_slots[period] = f"{time_slot.start_time} - {time_slot.end_time}"
        
        # Create table data
        table_data = [["Period/Day"] + [day for day in days if any(entry['day'] == days.index(day) for entry in schedule)]]
        
        for period in sorted(periods):
            row = [f"{period}<br/>{time_slots.get(period, '')}"]
            
            for day_idx, day in enumerate(days):
                if not any(entry['day'] == day_idx for entry in schedule):
                    continue
                    
                # Find entry for this day and period
                entry = next((e for e in schedule if e['day'] == day_idx and e['period'] == period), None)
                
                if entry:
                    cell_content = f"{entry['subject']}<br/>{entry['teacher']}<br/>{entry['room']}"
                else:
                    cell_content = ""
                
                row.append(cell_content)
            
            table_data.append(row)
        
        # Create table
        if len(table_data) > 1:
            table = Table(table_data, repeatRows=1)
            
            # Style the table
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                
                # Cell styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("No timetable data available.", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def export_teacher_timetable(self, teacher_id: int) -> bytes:
        """Export teacher timetable as PDF"""
        
        # Get teacher information
        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise ValueError(f"Teacher with id {teacher_id} not found")
        
        # Get schedule
        schedule = self.generator.get_teacher_schedule(teacher_id)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(f"Teacher Timetable - {teacher.name}", title_style))
        story.append(Spacer(1, 12))
        
        # Create timetable grid
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        periods = sorted(list(set(entry['period'] for entry in schedule)))
        
        # Get time slots for period headers
        time_slots = {}
        for entry in schedule:
            period = entry['period']
            if period not in time_slots:
                time_slot = self.db.query(TimeSlot).filter(
                    TimeSlot.period_number == period
                ).first()
                if time_slot:
                    time_slots[period] = f"{time_slot.start_time} - {time_slot.end_time}"
        
        # Create table data
        table_data = [["Period/Day"] + [day for day in days if any(entry['day'] == days.index(day) for entry in schedule)]]
        
        for period in sorted(periods):
            row = [f"{period}<br/>{time_slots.get(period, '')}"]
            
            for day_idx, day in enumerate(days):
                if not any(entry['day'] == day_idx for entry in schedule):
                    continue
                    
                # Find entry for this day and period
                entry = next((e for e in schedule if e['day'] == day_idx and e['period'] == period), None)
                
                if entry:
                    cell_content = f"{entry['class']}<br/>{entry['subject']}<br/>{entry['room']}"
                else:
                    cell_content = ""
                
                row.append(cell_content)
            
            table_data.append(row)
        
        # Create table
        if len(table_data) > 1:
            table = Table(table_data, repeatRows=1)
            
            # Style the table
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                
                # Cell styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("No timetable data available.", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def export_summary(self) -> bytes:
        """Export summary of all timetables as PDF"""
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Timetable Summary", title_style))
        story.append(Spacer(1, 12))
        
        # Get all classes
        classes = self.db.query(Class).all()
        
        for class_obj in classes:
            # Class title
            class_title = ParagraphStyle(
                'ClassTitle',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            story.append(Paragraph(f"Class: {class_obj.name}", class_title))
            
            # Get class schedule
            schedule = self.generator.get_class_schedule(class_obj.id)
            
            if schedule:
                # Create simple table for this class
                table_data = [["Day", "Period", "Subject", "Teacher", "Room"]]
                
                for entry in schedule:
                    day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][entry['day']]
                    table_data.append([
                        day_name,
                        f"{entry['period']} ({entry['start_time']}-{entry['end_time']})",
                        entry['subject'],
                        entry['teacher'],
                        entry['room']
                    ])
                
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                story.append(table)
            else:
                story.append(Paragraph("No timetable data available.", self.styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
