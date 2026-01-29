import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { studentAPI, adminAPI } from '../services/api';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import './Dashboard.css';

const StudentDashboard = () => {
  const { user, logout } = useAuth();
  const [timetable, setTimetable] = useState([]);
  const [activeTab, setActiveTab] = useState('timetable');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
                                    <div className="subject-code">{entry.subcode}</div>
                                    <div className="teacher-name">{entry.teacher_name}</div>
                                  </div>
                                ) : (
                                  <span className="empty-cell">-</span>
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
      </div>
    </div>
  );
};

export default StudentDashboard;
