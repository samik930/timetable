# Timetable Creator System

A comprehensive timetabling system for educational institutions that automatically generates class and exam timetables while avoiding conflicts.

## Features

- **Automatic Timetable Generation**: Uses greedy algorithm with constraint satisfaction
- **Conflict Detection**: Identifies teacher and room conflicts
- **Manual Editing**: Full CRUD operations for timetable entries
- **PDF Export**: Export timetables as formatted PDF documents
- **Admin Authentication**: Secure admin access for management operations
- **RESTful API**: Complete FastAPI backend with Swagger documentation

## Tech Stack

- **Backend**: Python FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt
- **PDF Generation**: ReportLab
- **API Documentation**: Swagger/OpenAPI

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database and update `.env` file:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/timetable_db
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Authentication

Default admin credentials:
- Username: `admin`
- Password: `admin123`

## Core Endpoints

### Authentication
- `POST /auth/login` - Login to get JWT token
- `GET /auth/me` - Get current user info

### Subjects
- `POST /subjects/` - Create subject (admin)
- `GET /subjects/` - Get all subjects
- `PUT /subjects/{id}` - Update subject (admin)
- `DELETE /subjects/{id}` - Delete subject (admin)

### Teachers
- `POST /teachers/` - Create teacher (admin)
- `GET /teachers/` - Get all teachers
- `PUT /teachers/{id}` - Update teacher (admin)
- `DELETE /teachers/{id}` - Delete teacher (admin)

### Classes
- `POST /classes/` - Create class (admin)
- `GET /classes/` - Get all classes
- `PUT /classes/{id}` - Update class (admin)
- `DELETE /classes/{id}` - Delete class (admin)

### Time Slots
- `POST /time_slots/` - Create time slot (admin)
- `GET /time_slots/` - Get all time slots
- `DELETE /time_slots/{id}` - Delete time slot (admin)

### Class-Subject Assignments
- `POST /class_subjects/` - Assign subject to class (admin)
- `GET /class_subjects/class/{class_id}` - Get subjects for class
- `DELETE /class_subjects/{id}` - Remove assignment (admin)

### Teacher Availability
- `POST /teacher_availability/` - Set availability (admin)
- `GET /teacher_availability/teacher/{teacher_id}` - Get availability
- `DELETE /teacher_availability/{id}` - Remove availability (admin)

### Timetable Management
- `POST /timetable/generate/{class_id}` - Generate timetable (admin)
- `GET /timetable/class/{class_id}` - Get class timetable
- `GET /timetable/teacher/{teacher_id}` - Get teacher timetable
- `GET /timetable/` - Get all timetable entries
- `POST /timetable/` - Create manual entry (admin)
- `PUT /timetable/{id}` - Update entry (admin)
- `DELETE /timetable/{id}` - Delete entry (admin)
- `GET /timetable/conflicts` - Get conflicts
- `DELETE /timetable/class/{class_id}` - Clear class timetable (admin)

### PDF Export
- `GET /export/class/{class_id}/pdf` - Export class timetable
- `GET /export/teacher/{teacher_id}/pdf` - Export teacher timetable
- `GET /export/summary/pdf` - Export summary

## Algorithm

The system uses a greedy algorithm with constraint satisfaction:

1. **Input Validation**: Checks if class has assigned subjects and teachers
2. **Slot Assignment**: Iterates through time slots and subjects
3. **Conflict Checking**: Validates teacher availability and slot availability
4. **Backtracking**: Attempts alternative slots if conflicts detected
5. **Generation**: Creates timetable entries in database

## Database Schema

- **Subjects**: Subject information and weekly period requirements
- **Teachers**: Teacher details and availability constraints
- **Classes**: Class/section information
- **TimeSlots**: Period definitions with days and times
- **ClassSubjects**: Many-to-many relationship between classes and subjects
- **TeacherAvailability**: Teacher availability by day and period
- **Timetables**: Generated timetable entries

## Usage Example

1. **Setup Data**:
   - Create subjects, teachers, and classes
   - Define time slots (periods and times)
   - Assign subjects to classes with teachers
   - Set teacher availability

2. **Generate Timetable**:
   ```bash
   curl -X POST "http://localhost:8000/timetable/generate/1" \
        -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **View Results**:
   ```bash
   curl "http://localhost:8000/timetable/class/1"
   ```

4. **Export PDF**:
   ```bash
   curl "http://localhost:8000/export/class/1/pdf" --output timetable.pdf
   ```

## Future Enhancements

- Genetic Algorithm optimization
- Room allocation system
- Advanced constraint handling
- Web frontend interface
- Real-time conflict detection
- Bulk operations
- Import/Export functionality
