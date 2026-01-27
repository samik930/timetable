import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import './StudentAttendance.css';

const StudentAttendance = ({ studentInfo }) => {
  const [attendanceHistory, setAttendanceHistory] = useState([]);
  const [scheduleId, setScheduleId] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchAttendanceHistory();
  }, []);

  const fetchAttendanceHistory = async () => {
    try {
      const response = await adminAPI.getAttendanceByStudent(studentInfo.id);
      setAttendanceHistory(response);
    } catch (error) {
      console.error('Error fetching attendance history:', error);
    }
  };

  const markAttendance = async () => {
    if (!scheduleId.trim()) {
      setMessage('Please enter a schedule ID');
      return;
    }

    setLoading(true);
    try {
      // Create a simple QR hash for testing
      const qrHash = `manual_${scheduleId}_${Date.now()}`;
      const response = await adminAPI.markAttendance(qrHash, studentInfo.id, scheduleId);
      
      if (response.success) {
        setMessage('Attendance marked successfully!');
        setScheduleId('');
        fetchAttendanceHistory();
      } else {
        setMessage(response.message || 'Failed to mark attendance');
      }
    } catch (error) {
      console.error('Error marking attendance:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to mark attendance';
      setMessage(`Error: ${errorMessage}`);
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

  return (
    <div className="student-attendance">
      <div className="attendance-header">
        <h2>📊 Attendance Management</h2>
        <p>Mark your attendance by entering the Schedule ID from your class</p>
      </div>

      <div className="mark-attendance-section">
        <h3>Mark Attendance</h3>
        <div className="attendance-form">
          <div className="form-group">
            <label htmlFor="scheduleId">Schedule ID:</label>
            <input
              type="text"
              id="scheduleId"
              value={scheduleId}
              onChange={(e) => setScheduleId(e.target.value)}
              placeholder="Enter schedule ID (e.g., dcf9f976)"
              className="schedule-input"
            />
            <small className="form-hint">
              Get the Schedule ID from your teacher or from the QR code displayed in class
            </small>
          </div>
          <button 
            onClick={markAttendance} 
            disabled={loading || !scheduleId.trim()}
            className="mark-attendance-btn"
          >
            {loading ? 'Marking...' : '📝 Mark Attendance'}
          </button>
        </div>
        
        {message && (
          <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>

      <div className="attendance-history">
        <h3>📚 Your Attendance History</h3>
        {attendanceHistory.length === 0 ? (
          <div className="no-attendance">
            <p>📝 No attendance records found</p>
            <p>Mark your attendance using the form above</p>
          </div>
        ) : (
          <div className="attendance-list">
            {attendanceHistory.map((record) => (
              <div key={record.id} className="attendance-record">
                <div className="record-info">
                  <p><strong>Schedule ID:</strong> <span className="schedule-id">{record.schedule_id}</span></p>
                  <p><strong>Date:</strong> {new Date(record.marked_at).toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}</p>
                  <p><strong>Time:</strong> {new Date(record.marked_at).toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}</p>
                  <p><strong>Method:</strong> {record.verification_method}</p>
                </div>
                <div className="record-status">
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(record.status) }}
                  >
                    {record.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentAttendance;
