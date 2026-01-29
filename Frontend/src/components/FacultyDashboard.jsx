import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { facultyAPI, adminAPI } from '../services/api';
import './Dashboard.css';

const FacultyDashboard = () => {
  const { user, logout } = useAuth();
  const [timetable, setTimetable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [demoModal, setDemoModal] = useState({ open: false, message: '' });

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

  const handleViewAttendanceDemo = (scheduleEntry) => {
    setDemoModal({
      open: true,
      message: `🎯 Demo: Attendance tracking for ${scheduleEntry.subject_name} (${scheduleEntry.subcode}) - Section ${scheduleEntry.section}\n\nThis feature would show:\n• Total students: 45\n• Present: 42 (93%)\n• Absent: 3 (7%)\n• Late: 0\n\nAttendance tracking has been disabled in this version.`
    });
  };

  const downloadPDF = () => {
    // TO DO: implement download PDF functionality
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
                                  onClick={() => handleViewAttendanceDemo(entry)}
                                  className="btn-attendance-demo"
                                  title="View Attendance Demo"
                                >
                                  � View Attendance (Demo)
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

      {/* Demo Modal */}
      {demoModal.open && (
        <div className="modal-overlay">
          <div className="demo-modal">
            <div className="demo-modal-header">
              <h3>Attendance Demo</h3>
              <button onClick={() => setDemoModal({ open: false, message: '' })} className="btn-close">
                ✕
              </button>
            </div>
            <div className="demo-modal-content">
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', lineHeight: '1.6' }}>
                {demoModal.message}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FacultyDashboard;


