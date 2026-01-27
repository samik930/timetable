import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { studentAPI, adminAPI } from '../services/api';
import StudentAttendance from './StudentAttendance';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import './Dashboard.css';

const StudentDashboard = () => {
  const { user, logout } = useAuth();
  const [timetable, setTimetable] = useState([]);
  const [activeTab, setActiveTab] = useState('timetable');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [qrModal, setQrModal] = useState({ open: false, schedule: null, qrCode: null });

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const maxPeriods = 8; // Adjust based on your needs

  useEffect(() => {
    const fetchTimetable = async () => {
      if (!user?.userInfo?.section) {
        setError('Section information not available');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await studentAPI.getTimetable(user.userInfo.section);
        setTimetable(data.schedule || []);
        setError('');
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load timetable');
      } finally {
        setLoading(false);
      }
    };

    fetchTimetable();
  }, [user]);

  const handleShowQR = async (scheduleEntry) => {
    try {
      setLoading(true);
      const response = await adminAPI.generateQRCode(scheduleEntry.id);
      setQrModal({
        open: true,
        schedule: scheduleEntry,
        qrCode: response.qr_code
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate QR code');
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(18);
    doc.text('Timetable', 14, 22);
    
    // Add student info
    doc.setFontSize(12);
    doc.text(`Name: ${user?.userInfo?.name || 'Student'}`, 14, 35);
    doc.text(`Section: ${user?.userInfo?.section || 'N/A'}`, 14, 42);
    doc.text(`Roll No: ${user?.userInfo?.roll_number || 'N/A'}`, 14, 49);
    
    // Prepare table data
    const tableData = [];
    
    // Add header row
    const headerRow = ['Day/Period'];
    for (let i = 1; i <= maxPeriods; i++) {
      headerRow.push(`Period ${i}`);
    }
    tableData.push(headerRow);
    
    // Add data rows
    days.forEach((day, dayIndex) => {
      const row = [day];
      for (let periodIndex = 0; periodIndex < maxPeriods; periodIndex++) {
        const entry = timetableGrid[dayIndex][periodIndex];
        if (periodIndex === 3) { // 4th period (index 3) is break
          row.push('BREAK');
        } else if (entry) {
          row.push(`${entry.subcode}\n${entry.teacher_name}`);
        } else {
          row.push('-');
        }
      }
      tableData.push(row);
    });
    
    // Add the table to PDF using the imported autoTable function
    autoTable(doc, {
      head: [tableData[0]],
      body: tableData.slice(1),
      startY: 60,
      theme: 'grid',
      styles: {
        fontSize: 10,
        cellPadding: 3,
        valign: 'middle',
        halign: 'center'
      },
      headStyles: {
        fillColor: [66, 139, 202],
        textColor: 255,
        fontStyle: 'bold'
      },
      columnStyles: {
        0: { fontStyle: 'bold', halign: 'left' }, // Day column
        4: { fillColor: [255, 235, 156], fontStyle: 'bold' } // Break period column (Period 4)
      },
      didDrawCell: (data) => {
        // Handle multi-line content in cells
        if (data.section === 'body' && data.column.index > 0) {
          const cell = data.cell;
          const text = cell.text || [];
          if (text.length > 1) {
            const lineHeight = doc.internal.getLineHeight();
            const cellHeight = cell.height;
            const verticalPadding = (cellHeight - (text.length * lineHeight)) / 2;
            cell.y += verticalPadding;
          }
        }
      }
    });
    
    // Save the PDF
    doc.save(`Timetable_${user?.userInfo?.section}_${user?.userInfo?.roll_number}.pdf`);
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
          <h1>Student Dashboard</h1>
          <p>Welcome, {user?.userInfo?.name || 'Student'}, Section {user?.userInfo?.section}</p>
        </div>
        <button onClick={logout} className="logout-button">
          <span>Logout</span>
        </button>
      </div>

      <div className="dashboard-tabs">
        <button
          className={`tab-button ${activeTab === 'timetable' ? 'active' : ''}`}
          onClick={() => setActiveTab('timetable')}
        >
          📅 My Timetable
        </button>
        <button
          className={`tab-button ${activeTab === 'attendance' ? 'active' : ''}`}
          onClick={() => setActiveTab('attendance')}
        >
          📊 Attendance
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'timetable' && (
          <div>
            {loading ? (
              <div className="loading">Loading timetable...</div>
            ) : error ? (
              <div className="error-message">{error}</div>
            ) : (
              <div className="timetable-container">
                <div className="timetable-header">
                  <h2>Timetable - Section {user?.userInfo?.section}</h2>
                  <button 
                    onClick={downloadPDF}
                    className="download-pdf-btn"
                    disabled={loading || timetable.length === 0}
                  >
                    📄 Download PDF
                  </button>
                </div>
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
                                    <div className="teacher-name">{entry.teacher_name}</div>
                                    <div className="entry-actions">
                                      <button 
                                        onClick={() => handleShowQR(entry)}
                                        className="btn-qr-small"
                                        title="Scan QR Code for Attendance"
                                      >
                                        📱 Scan QR
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
          </div>
        )}

        {activeTab === 'attendance' && (
          <StudentAttendance studentInfo={user?.userInfo} />
        )}
      </div>

      {/* QR Code Modal */}
      {qrModal.open && (
        <div className="modal-overlay">
          <div className="qr-modal">
            <div className="qr-modal-header">
              <h3>📱 Scan QR Code for Attendance</h3>
              <button onClick={() => setQrModal({ open: false, schedule: null, qrCode: null })} className="btn-close">
                ✕
              </button>
            </div>
            <div className="qr-modal-content">
              {qrModal.schedule && (
                <div className="class-info">
                  <p><strong>Subject:</strong> {qrModal.schedule.subject_name}</p>
                  <p><strong>Code:</strong> {qrModal.schedule.subcode}</p>
                  <p><strong>Teacher:</strong> {qrModal.schedule.teacher_name}</p>
                  <p><strong>Section:</strong> {qrModal.schedule.section}</p>
                  <p><strong>Day:</strong> {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][qrModal.schedule.day_id - 1]}</p>
                  <p><strong>Period:</strong> {qrModal.schedule.period_id}</p>
                  <p><strong>Schedule ID:</strong> <span className="schedule-id">{qrModal.schedule.id}</span></p>
                </div>
              )}
              {qrModal.qrCode && (
                <div className="qr-code-container">
                  <img src={`data:image/png;base64,${qrModal.qrCode}`} alt="Attendance QR Code" />
                  <p className="qr-instruction">Scan this QR code with your phone to mark attendance</p>
                  <p className="qr-alternative">Or go to the Attendance tab and enter the Schedule ID manually</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
