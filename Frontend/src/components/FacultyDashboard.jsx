import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { facultyAPI, adminAPI } from '../services/api';
import './Dashboard.css';

const FacultyDashboard = () => {
  const { user, logout } = useAuth();
  const [timetable, setTimetable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [attendanceModal, setAttendanceModal] = useState({ open: false, schedule: null, attendance: [] });

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const maxPeriods = 8; // Adjust based on your needs

  useEffect(() => {
    const fetchTimetable = async () => {
      if (!user?.userInfo?.initials) {
        setError('Faculty initials not available');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await facultyAPI.getTimetable(user.userInfo.initials);
        setTimetable(data.schedule || []);
        setError('');
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load schedule');
      } finally {
        setLoading(false);
      }
    };

    fetchTimetable();
  }, [user]);

  const handleViewAttendance = async (scheduleEntry) => {
    try {
      setLoading(true);
      const response = await adminAPI.getAttendanceBySchedule(scheduleEntry.id);
      
      // Get student details for attendance records
      const attendanceWithStudents = await Promise.all(
        response.map(async (record) => {
          try {
            const studentResponse = await adminAPI.getStudents();
            const student = studentResponse.find(s => s.id === record.student_id);
            return {
              ...record,
              student_name: student ? student.name : 'Unknown',
              roll_number: student ? student.roll_number : 'N/A'
            };
          } catch (err) {
            return {
              ...record,
              student_name: 'Unknown',
              roll_number: 'N/A'
            };
          }
        })
      );
      
      setAttendanceModal({
        open: true,
        schedule: scheduleEntry,
        attendance: attendanceWithStudents
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch attendance');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Present': return '#4CAF50';
      case 'Late': return '#FF9800';
      case 'Absent': return '#F44336';
      default: return '#666';
    }
  };

  // Create a 2D array for the timetable grid
  const timetableGrid = Array(days.length)
    .fill(null)
    .map(() => Array(maxPeriods).fill(null));

  timetable.forEach((entry) => {
    const dayIndex = entry.day_id - 1; // Assuming day_id starts from 1
    const periodIndex = entry.period_id - 1; // Assuming period_id starts from 1
    
    if (dayIndex >= 0 && dayIndex < days.length && periodIndex >= 0 && periodIndex < maxPeriods) {
      timetableGrid[dayIndex][periodIndex] = entry;
    }
  });

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Faculty Dashboard</h1>
          <p className="welcome-text">
            Welcome, {user?.userInfo?.name || 'Faculty'} | 
            Initials: {user?.userInfo?.initials || 'N/A'} | 
            Email: {user?.userInfo?.email || 'N/A'}
          </p>
        </div>
        <button onClick={logout} className="logout-button">
          Logout
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading schedule...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="timetable-container">
          <h2>Teaching Schedule</h2>
          <div className="timetable-table-wrapper">
            <table className="timetable-table">
              <thead>
                <tr>
                  <th>Day/Period</th>
                  {Array.from({ length: maxPeriods }, (_, i) => (
                    <th key={i + 1}>Period {i + 1}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {days.map((day, dayIndex) => (
                  <tr key={day}>
                    <td className="day-cell">{day}</td>
                    {Array.from({ length: maxPeriods }, (_, periodIndex) => {
                      const entry = timetableGrid[dayIndex][periodIndex];
                      return (
                        <td key={periodIndex} className="period-cell">
                          {entry ? (
                            <div className="schedule-entry">
                              <div className="subject-name">{entry.subject_name}</div>
                              <div className="subject-code">{entry.subcode}</div>
                              <div className="section-name">Section: {entry.section}</div>
                              <div className="entry-actions">
                                <button 
                                  onClick={() => handleViewAttendance(entry)}
                                  className="btn-attendance-small"
                                  title="View Attendance"
                                >
                                  👥 View Attendance
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="empty-cell">-</div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Attendance Modal */}
      {attendanceModal.open && (
        <div className="modal-overlay">
          <div className="attendance-modal">
            <div className="attendance-modal-header">
              <h3>👥 Class Attendance</h3>
              <button onClick={() => setAttendanceModal({ open: false, schedule: null, attendance: [] })} className="btn-close">
                ✕
              </button>
            </div>
            <div className="attendance-modal-content">
              {attendanceModal.schedule && (
                <div className="class-info">
                  <p><strong>Subject:</strong> {attendanceModal.schedule.subject_name}</p>
                  <p><strong>Code:</strong> {attendanceModal.schedule.subcode}</p>
                  <p><strong>Section:</strong> {attendanceModal.schedule.section}</p>
                  <p><strong>Day:</strong> {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][attendanceModal.schedule.day_id - 1]}</p>
                  <p><strong>Period:</strong> {attendanceModal.schedule.period_id}</p>
                  <p><strong>Total Attended:</strong> {attendanceModal.attendance.length} students</p>
                </div>
              )}
              
              <div className="attendance-list">
                {attendanceModal.attendance.length === 0 ? (
                  <div className="no-attendance">
                    <p>📝 No students have marked attendance for this class yet</p>
                  </div>
                ) : (
                  <table className="attendance-table">
                    <thead>
                      <tr>
                        <th>Student Name</th>
                        <th>Roll Number</th>
                        <th>Status</th>
                        <th>Time</th>
                        <th>Method</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendanceModal.attendance.map((record) => (
                        <tr key={record.id}>
                          <td>{record.student_name}</td>
                          <td>{record.roll_number}</td>
                          <td>
                            <span 
                              className="status-badge"
                              style={{ backgroundColor: getStatusColor(record.status) }}
                            >
                              {record.status}
                            </span>
                          </td>
                          <td>{new Date(record.marked_at).toLocaleTimeString('en-US', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}</td>
                          <td>{record.verification_method}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FacultyDashboard;


