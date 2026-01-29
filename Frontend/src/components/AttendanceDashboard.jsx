import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import './AttendanceDashboard.css';

const AttendanceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [schedules, setSchedules] = useState([]);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [attendanceStats, setAttendanceStats] = useState(null);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSchedules();
    fetchStudents();
  }, []);

  const fetchSchedules = async () => {
    try {
      const response = await adminAPI.getScheduleBySection('A'); // You can make this dynamic
      setSchedules(response.schedule || []);
    } catch (error) {
      console.error('Error fetching schedules:', error);
      setMessage('Failed to fetch schedules');
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await adminAPI.getStudents();
      setStudents(response);
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  const generateQRCode = async (scheduleId) => {
    setLoading(true);
    try {
      const response = await adminAPI.generateQRCode(scheduleId);
      setQrCode(response);
      setMessage('QR Code generated successfully!');
      setSelectedSchedule(scheduleId);
      
      // Auto-refresh stats after QR generation
      setTimeout(() => fetchAttendanceStats(scheduleId), 2000);
    } catch (error) {
      console.error('Error generating QR code:', error);
      setMessage('Failed to generate QR code');
    } finally {
      setLoading(false);
    }
  };

  const fetchAttendanceStats = async (scheduleId) => {
    try {
      const response = await adminAPI.getAttendanceStats(scheduleId);
      setAttendanceStats(response);
    } catch (error) {
      console.error('Error fetching attendance stats:', error);
    }
  };

  const fetchAttendanceRecords = async (scheduleId) => {
    try {
      const response = await adminAPI.getAttendanceBySchedule(scheduleId);
      setAttendanceRecords(response);
    } catch (error) {
      console.error('Error fetching attendance records:', error);
    }
  };

  const markManualAttendance = async (studentId, scheduleId, status) => {
    try {
      await adminAPI.markManualAttendance(studentId, scheduleId, status);
      setMessage(`Attendance marked as ${status} for student ${studentId}`);
      fetchAttendanceRecords(scheduleId);
      fetchAttendanceStats(scheduleId);
    } catch (error) {
      console.error('Error marking manual attendance:', error);
      setMessage('Failed to mark attendance');
    }
  };

  const handleScheduleSelect = (schedule) => {
    setSelectedSchedule(schedule.id);
    fetchAttendanceStats(schedule.id);
    fetchAttendanceRecords(schedule.id);
    setQrCode(null);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Present': return '#4CAF50';
      case 'Late': return '#FF9800';
      case 'Absent': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  return (
    <div className="attendance-dashboard">
      <div className="dashboard-header">
        <h2>Automated Attendance System</h2>
        <div className="header-stats">
          <div className="stat-card">
            <h3>{schedules.length}</h3>
            <p>Total Classes</p>
          </div>
          <div className="stat-card">
            <h3>{students.length}</h3>
            <p>Total Students</p>
          </div>
          <div className="stat-card">
            <h3>{attendanceStats?.attendance_percentage || 0}%</h3>
            <p>Avg Attendance</p>
          </div>
        </div>
      </div>

      {message && (
        <div className={`message ${message.includes('Failed') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'qr-generator' ? 'active' : ''}`}
          onClick={() => setActiveTab('qr-generator')}
        >
          QR Generator
        </button>
        <button
          className={`tab-button ${activeTab === 'attendance' ? 'active' : ''}`}
          onClick={() => setActiveTab('attendance')}
        >
          Attendance Records
        </button>
        <button
          className={`tab-button ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => setActiveTab('manual')}
        >
          Manual Marking
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <h3>Today's Classes</h3>
            <div className="schedule-grid">
              {schedules.map((schedule) => (
                <div
                  key={schedule.id}
                  className="schedule-card"
                  onClick={() => handleScheduleSelect(schedule)}
                >
                  <h4>{schedule.subject_name || 'Subject'}</h4>
                  <p>Day {schedule.day_id}, Period {schedule.period_id}</p>
                  <p>Section: {schedule.section}</p>
                  <p>Faculty: {schedule.teacher_name || 'N/A'}</p>
                  {attendanceStats && selectedSchedule === schedule.id && (
                    <div className="mini-stats">
                      <span>Present: {attendanceStats.present_count}</span>
                      <span>Absent: {attendanceStats.absent_count}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'qr-generator' && (
          <div className="qr-generator-tab">
            <h3>Generate QR Code for Attendance</h3>
            <div className="qr-controls">
              <select
                value={selectedSchedule || ''}
                onChange={(e) => setSelectedSchedule(e.target.value)}
                className="schedule-select"
              >
                <option value="">Select a class</option>
                {schedules.map((schedule) => (
                  <option key={schedule.id} value={schedule.id}>
                    Day {schedule.day_id}, Period {schedule.period_id} - {schedule.subject_name || 'Subject'} ({schedule.section})
                  </option>
                ))}
              </select>
              <button
                onClick={() => selectedSchedule && generateQRCode(selectedSchedule)}
                disabled={!selectedSchedule || loading}
                className="generate-btn"
              >
                {loading ? 'Generating...' : 'Generate QR Code'}
              </button>
            </div>

            {qrCode && (
              <div className="qr-display">
                <h4>QR Code Generated</h4>
                <div className="qr-code-container">
                  <img src={`data:image/png;base64,${qrCode.qr_code}`} alt="Attendance QR Code" />
                  <div className="qr-info">
                    <p><strong>Expires at:</strong> {formatTime(qrCode.expires_at)}</p>
                    <p><strong>Schedule ID:</strong> {qrCode.schedule_id}</p>
                    <p><strong>QR Hash:</strong> {qrCode.qr_hash.substring(0, 20)}...</p>
                  </div>
                </div>
                <div className="qr-instructions">
                  <h5>Instructions:</h5>
                  <ul>
                    <li>Display this QR code to students during class</li>
                    <li>Students can scan using their mobile devices</li>
                    <li>QR code expires in 15 minutes</li>
                    <li>Students can mark attendance within 30 minutes of class start</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'attendance' && (
          <div className="attendance-tab">
            <h3>Attendance Records</h3>
            <div className="attendance-controls">
              <select
                value={selectedSchedule || ''}
                onChange={(e) => handleScheduleSelect(schedules.find(s => s.id === e.target.value))}
                className="schedule-select"
              >
                <option value="">Select a class</option>
                {schedules.map((schedule) => (
                  <option key={schedule.id} value={schedule.id}>
                    Day {schedule.day_id}, Period {schedule.period_id} - {schedule.subject_name || 'Subject'} ({schedule.section})
                  </option>
                ))}
              </select>
            </div>

            {attendanceStats && (
              <div className="attendance-stats">
                <h4>Statistics</h4>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-value">{attendanceStats.total_students}</span>
                    <span className="stat-label">Total Students</span>
                  </div>
                  <div className="stat-item present">
                    <span className="stat-value">{attendanceStats.present_count}</span>
                    <span className="stat-label">Present</span>
                  </div>
                  <div className="stat-item absent">
                    <span className="stat-value">{attendanceStats.absent_count}</span>
                    <span className="stat-label">Absent</span>
                  </div>
                  <div className="stat-item percentage">
                    <span className="stat-value">{attendanceStats.attendance_percentage}%</span>
                    <span className="stat-label">Attendance Rate</span>
                  </div>
                </div>
              </div>
            )}

            {attendanceRecords.length > 0 && (
              <div className="attendance-table">
                <h4>Attendance Details</h4>
                <table>
                  <thead>
                    <tr>
                      <th>Student ID</th>
                      <th>Timestamp</th>
                      <th>Status</th>
                      <th>Verification Method</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendanceRecords.map((record) => (
                      <tr key={record.id}>
                        <td>{record.student_id}</td>
                        <td>{formatTime(record.timestamp)}</td>
                        <td>
                          <span
                            className="status-badge"
                            style={{ backgroundColor: getStatusColor(record.status) }}
                          >
                            {record.status}
                          </span>
                        </td>
                        <td>{record.verification_method}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'manual' && (
          <div className="manual-tab">
            <h3>Manual Attendance Marking</h3>
            <div className="manual-controls">
              <select
                value={selectedSchedule || ''}
                onChange={(e) => setSelectedSchedule(e.target.value)}
                className="schedule-select"
              >
                <option value="">Select a class</option>
                {schedules.map((schedule) => (
                  <option key={schedule.id} value={schedule.id}>
                    Day {schedule.day_id}, Period {schedule.period_id} - {schedule.subject_name || 'Subject'} ({schedule.section})
                  </option>
                ))}
              </select>
            </div>

            {selectedSchedule && (
              <div className="student-list">
                <h4>Mark Attendance for Students</h4>
                <div className="students-grid">
                  {students.map((student) => {
                    const attendance = attendanceRecords.find(r => r.student_id === student.id);
                    const currentStatus = attendance?.status || 'Absent';
                    
                    return (
                      <div key={student.id} className="student-card">
                        <div className="student-info">
                          <h5>{student.name}</h5>
                          <p>ID: {student.id}</p>
                          <p>Roll: {student.roll_number}</p>
                          <p>Section: {student.section}</p>
                        </div>
                        <div className="attendance-status">
                          <span
                            className="current-status"
                            style={{ backgroundColor: getStatusColor(currentStatus) }}
                          >
                            {currentStatus}
                          </span>
                          <div className="status-buttons">
                            <button
                              onClick={() => markManualAttendance(student.id, selectedSchedule, 'Present')}
                              className="status-btn present"
                            >
                              Present
                            </button>
                            <button
                              onClick={() => markManualAttendance(student.id, selectedSchedule, 'Late')}
                              className="status-btn late"
                            >
                              Late
                            </button>
                            <button
                              onClick={() => markManualAttendance(student.id, selectedSchedule, 'Absent')}
                              className="status-btn absent"
                            >
                              Absent
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AttendanceDashboard;
