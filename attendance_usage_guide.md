# Automated Attendance System Usage Guide

## Overview
The automated attendance system uses QR codes to track student attendance for scheduled classes. Students scan QR codes during class to mark their attendance automatically.

## API Endpoints

### 1. Generate QR Code for Attendance
**POST** `/attendance/generate-qr`

**Request Body:**
```json
{
    "schedule_id": "string"
}
```

**Response:**
```json
{
    "qr_code": "base64_encoded_image",
    "qr_hash": "unique_hash",
    "schedule_id": "schedule_id",
    "expires_at": "2024-01-01T10:15:00"
}
```

### 2. Mark Attendance (Student)
**POST** `/attendance/mark`

**Request Body:**
```json
{
    "qr_hash": "string",
    "student_id": "string"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Attendance marked successfully",
    "attendance": {
        "id": 1,
        "student_id": "student123",
        "schedule_id": "schedule456",
        "timestamp": "2024-01-01T10:05:00",
        "status": "Present",
        "verification_method": "QR"
    }
}
```

### 3. Get Attendance by Schedule
**GET** `/attendance/schedule/{schedule_id}`

Returns all attendance records for a specific class.

### 4. Get Attendance by Student
**GET** `/attendance/student/{student_id}`

Returns all attendance records for a specific student.

### 5. Get Attendance Statistics
**GET** `/attendance/stats/{schedule_id}`

**Response:**
```json
{
    "total_students": 30,
    "present_count": 25,
    "absent_count": 5,
    "attendance_percentage": 83.33
}
```

### 6. Manual Attendance Marking
**POST** `/attendance/manual?student_id=xxx&schedule_id=xxx&status=Present`

For faculty/admin to manually mark attendance.

## How It Works

### For Faculty:
1. **Generate QR Code**: Use the `/attendance/generate-qr` endpoint with the schedule ID
2. **Display QR Code**: Show the QR code to students during class (projector or screen)
3. **Monitor Attendance**: Use `/attendance/stats/{schedule_id}` to see real-time attendance
4. **Manual Override**: Use `/attendance/manual` for students who couldn't scan

### For Students:
1. **Scan QR Code**: Use mobile app or web scanner to scan the displayed QR code
2. **Auto Mark**: System automatically marks attendance with timestamp
3. **Get Confirmation**: Receive confirmation of successful attendance marking

### Time Windows:
- **QR Code Validity**: 15 minutes from generation
- **Attendance Window**: 10 minutes before to 30 minutes after class start
- **Late Detection**: Students marked as "Late" if arriving 5-15 minutes after start

## Features

### Automatic Status Detection:
- **Present**: Within 5 minutes of class start
- **Late**: 5-15 minutes after class start
- **Absent**: No attendance marked within window

### Security Features:
- **Unique QR Codes**: Each QR code contains unique hash and expiry
- **Schedule Validation**: Only valid for specific class schedule
- **Duplicate Prevention**: Students can only mark attendance once per class
- **Time Validation**: Prevents early/late attendance marking

### Reporting:
- **Real-time Statistics**: Live attendance counts and percentages
- **Student History**: Complete attendance record for each student
- **Class Analytics**: Attendance trends and patterns

## Integration with Timetable System

The attendance system integrates seamlessly with your existing timetable:
- Uses existing `SCHEDULE` table for class information
- Links to `STUDENT` and `FACULTY` records
- Respects section-based scheduling
- Works with automated timetable generation

## Database Schema

New `ATTENDANCE` table:
- `id`: Primary key
- `student_id`: Foreign key to STUDENT table
- `schedule_id`: Foreign key to SCHEDULE table
- `timestamp`: When attendance was marked
- `status`: Present/Late/Absent/Excused
- `qr_code_hash`: Unique identifier for QR code
- `verification_method`: QR/Manual/Biometric
- `created_at`: Record creation timestamp

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Migration**:
   - The new ATTENDANCE table will be created automatically when the app starts

3. **Test the System**:
   - Generate a QR code for a test schedule
   - Test attendance marking with a student ID
   - Verify attendance records and statistics

## Security Considerations

- QR codes expire after 15 minutes
- Each QR code is unique and contains schedule validation
- Students can only mark attendance once per class
- Manual attendance requires proper authentication
- All attendance actions are logged with timestamps

## Future Enhancements

- **Geolocation Validation**: Add GPS-based location verification
- **Face Recognition**: Integrate biometric attendance options
- **Offline Support**: Allow offline QR scanning with sync
- **Push Notifications**: Send attendance alerts to students/faculty
- **Advanced Analytics**: Attendance pattern analysis and predictions
