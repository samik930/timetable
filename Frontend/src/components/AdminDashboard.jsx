import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { adminAPI } from '../services/api';
import AutomatedTimetableGenerator from './AutomatedTimetableGenerator';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('subjects');
  const [subjects, setSubjects] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [students, setStudents] = useState([]);
  const [schedule, setSchedule] = useState([]);
  const [selectedSection, setSelectedSection] = useState('A');
  const [editingCell, setEditingCell] = useState(null);
  const [cellFormData, setCellFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [attendanceModal, setAttendanceModal] = useState({ open: false, schedule: null, attendance: [] });
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (activeTab !== 'schedule') {
      fetchData();
    }
  }, [activeTab]);

  useEffect(() => {
    // Load subjects and faculty when schedule tab is active (needed for dropdowns)
    if (activeTab === 'schedule') {
      const loadDropdownData = async () => {
        try {
          const [subjectsData, facultyData] = await Promise.all([
            adminAPI.getSubjects(),
            adminAPI.getFaculty()
          ]);
          setSubjects(subjectsData);
          setFaculty(facultyData);
        } catch (err) {
          console.error('Failed to load dropdown data:', err);
        }
      };
      loadDropdownData();
    }
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      if (activeTab === 'subjects') {
        const data = await adminAPI.getSubjects();
        setSubjects(data);
      } else if (activeTab === 'faculty') {
        const data = await adminAPI.getFaculty();
        setFaculty(data);
      } else if (activeTab === 'students') {
        const data = await adminAPI.getStudents();
        setStudents(data);
      } else if (activeTab === 'schedule') {
        await fetchSchedule();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const fetchSchedule = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await adminAPI.getScheduleBySection(selectedSection);
      console.log('Schedule data fetched:', data); // Debug log
      // Handle both possible response formats
      if (data && data.schedule) {
        setSchedule(data.schedule);
      } else if (Array.isArray(data)) {
        setSchedule(data);
      } else {
        setSchedule([]);
      }
    } catch (err) {
      console.error('Error fetching schedule:', err); // Debug log
      console.error('Error response:', err.response); // Debug log
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load schedule';
      setError(errorMessage);
      setSchedule([]); // Reset schedule on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'schedule') {
      fetchSchedule();
    }
  }, [selectedSection, activeTab]);

  const handleAdd = () => {
    setEditingItem(null);
    if (activeTab === 'subjects') {
      setFormData({ code: '', name: '', subtype: 'T' });
    } else if (activeTab === 'faculty') {
      setFormData({ password: '', name: '', initials: '', email: '', subcode1: '', subcode2: '', max_periods_per_day: 6 });
    } else if (activeTab === 'students') {
      setFormData({ id: '', password: '', name: '', roll_number: '', section: '' });
    }
    setShowForm(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setFormData({ ...item });
    setShowForm(true);
  };

  const handleDelete = async (item) => {
    if (!window.confirm(`Are you sure you want to delete this ${activeTab.slice(0, -1)}?`)) {
      return;
    }

    try {
      if (activeTab === 'subjects') {
        await adminAPI.deleteSubject(item.code);
      } else if (activeTab === 'faculty') {
        await adminAPI.deleteFaculty(item.id);
      } else if (activeTab === 'students') {
        await adminAPI.deleteStudent(item.id);
      }
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (activeTab === 'subjects') {
        if (editingItem) {
          await adminAPI.updateSubject(editingItem.code, formData);
        } else {
          await adminAPI.createSubject(formData);
        }
      } else if (activeTab === 'faculty') {
        if (editingItem) {
          await adminAPI.updateFaculty(editingItem.id, formData);
        } else {
          await adminAPI.createFaculty(formData);
        }
      } else if (activeTab === 'students') {
        if (editingItem) {
          await adminAPI.updateStudent(editingItem.id, formData);
        } else {
          await adminAPI.createStudent(formData);
        }
      }
      setShowForm(false);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save');
    }
  };

  const renderSubjectsTable = () => (
    <div className="admin-table-container">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Subtype</th>
            <th>Credits</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {subjects.map((subject) => (
            <tr key={subject.code}>
              <td>{subject.code}</td>
              <td>{subject.name}</td>
              <td>{subject.subtype}</td>
              <td>{subject.credits}</td>
              <td>
                <button onClick={() => handleEdit(subject)} className="btn-edit">Edit</button>
                <button onClick={() => handleDelete(subject)} className="btn-delete">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderFacultyTable = () => (
    <div className="admin-table-container">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Initials</th>
            <th>Email</th>
            <th>Subject 1</th>
            <th>Subject 2</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {faculty.map((fac) => (
            <tr key={fac.id}>
              <td>{fac.name}</td>
              <td>{fac.initials}</td>
              <td>{fac.email}</td>
              <td>{fac.subcode1}</td>
              <td>{fac.subcode2}</td>
              <td>
                <button onClick={() => handleEdit(fac)} className="btn-edit">Edit</button>
                <button onClick={() => handleDelete(fac)} className="btn-delete">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderStudentsTable = () => (
    <div className="admin-table-container">
      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Roll Number</th>
            <th>Section</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {students.map((student) => (
            <tr key={student.id}>
              <td>{student.id}</td>
              <td>{student.name}</td>
              <td>{student.roll_number}</td>
              <td>{student.section}</td>
              <td>
                <button onClick={() => handleEdit(student)} className="btn-edit">Edit</button>
                <button onClick={() => handleDelete(student)} className="btn-delete">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderForm = () => {
    if (activeTab === 'subjects') {
      return (
        <form onSubmit={handleSubmit} className="admin-form">
          <h3>{editingItem ? 'Edit Subject' : 'Add Subject'}</h3>
          <div className="form-group">
            <label>Code *</label>
            <input
              type="text"
              value={formData.code || ''}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              required
              disabled={!!editingItem}
            />
          </div>
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Subtype *</label>
            <select
              value={formData.subtype || 'T'}
              onChange={(e) => setFormData({ ...formData, subtype: e.target.value })}
              required
            >
              <option value="T">Theory (T)</option>
              <option value="P">Practical (P)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Credits *</label>
            <input
              type="number"
              step="0.5"
              min="0.5"
              value={formData.credits || ''}
              onChange={(e) => setFormData({ ...formData, credits: parseFloat(e.target.value) })}
              required
              placeholder="e.g., 4.0 for theory, 1.5 for lab"
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-save">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-cancel">Cancel</button>
          </div>
        </form>
      );
    } else if (activeTab === 'faculty') {
      return (
        <form onSubmit={handleSubmit} className="admin-form">
          <h3>{editingItem ? 'Edit Faculty' : 'Add Faculty'}</h3>
          <div className="form-group">
            <label>Password *</label>
            <input
              type="text"
              value={formData.password || ''}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Initials *</label>
            <input
              type="text"
              value={formData.initials || ''}
              onChange={(e) => setFormData({ ...formData, initials: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              value={formData.email || ''}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Subject Code 1 *</label>
            <input
              type="text"
              value={formData.subcode1 || ''}
              onChange={(e) => setFormData({ ...formData, subcode1: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Subject Code 2 *</label>
            <input
              type="text"
              value={formData.subcode2 || ''}
              onChange={(e) => setFormData({ ...formData, subcode2: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Max Periods Per Day</label>
            <input
              type="number"
              value={formData.max_periods_per_day || 6}
              onChange={(e) => setFormData({ ...formData, max_periods_per_day: parseInt(e.target.value) })}
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-save">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-cancel">Cancel</button>
          </div>
        </form>
      );
    } else if (activeTab === 'students') {
      return (
        <form onSubmit={handleSubmit} className="admin-form">
          <h3>{editingItem ? 'Edit Student' : 'Add Student'}</h3>
          <div className="form-group">
            <label>Student ID *</label>
            <input
              type="text"
              value={formData.id || ''}
              onChange={(e) => setFormData({ ...formData, id: e.target.value })}
              required
              disabled={!!editingItem}
            />
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input
              type="text"
              value={formData.password || ''}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Roll Number *</label>
            <input
              type="number"
              value={formData.roll_number || ''}
              onChange={(e) => setFormData({ ...formData, roll_number: parseInt(e.target.value) })}
              required
            />
          </div>
          <div className="form-group">
            <label>Section *</label>
            <input
              type="text"
              value={formData.section || ''}
              onChange={(e) => setFormData({ ...formData, section: e.target.value })}
              required
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-save">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-cancel">Cancel</button>
          </div>
        </form>
      );
    }
  };

  const handleCellClick = (dayId, periodId) => {
    const existingEntry = schedule.find(
      (entry) => entry.day_id === dayId && entry.period_id === periodId
    );
    
    if (existingEntry) {
      setEditingCell({ dayId, periodId, entry: existingEntry });
      setCellFormData({
        subcode: existingEntry.subcode,
        fini: existingEntry.fini,
        subject_name: existingEntry.subject_name,
        teacher_name: existingEntry.teacher_name || ''
      });
    } else {
      setEditingCell({ dayId, periodId, entry: null });
      setCellFormData({
        subcode: '',
        fini: '',
        subject_name: '',
        teacher_name: ''
      });
    }
  };

  const handleCellSave = async () => {
    if (!editingCell) return;
    
    setError('');
    try {
      const { dayId, periodId, entry } = editingCell;
      
      if (entry) {
        // Update existing entry
        await adminAPI.updateScheduleEntry(entry.id, {
          id: entry.id,
          day_id: dayId,
          period_id: periodId,
          subcode: cellFormData.subcode,
          section: selectedSection,
          fini: cellFormData.fini
        });
      } else {
        // Create new entry
        await adminAPI.createScheduleEntry({
          id: `SCH${Date.now()}`,
          day_id: dayId,
          period_id: periodId,
          subcode: cellFormData.subcode,
          section: selectedSection,
          fini: cellFormData.fini
        });
      }
      
      setEditingCell(null);
      setCellFormData({});
      fetchSchedule();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save schedule entry');
    }
  };

  const handleCellDelete = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this schedule entry?')) {
      return;
    }

    try {
      await adminAPI.deleteScheduleEntry(entryId);
      fetchSchedule();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete schedule entry');
    }
  };

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

  const renderScheduleTimetable = () => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const maxPeriods = 8;
    
    // Create a 2D grid
    const timetableGrid = Array(days.length)
      .fill(null)
      .map(() => Array(maxPeriods).fill(null));

    // Populate grid with schedule data from database
    if (schedule && schedule.length > 0) {
      schedule.forEach((entry) => {
        const dayIndex = entry.day_id - 1;
        const periodIndex = entry.period_id - 1;
        if (dayIndex >= 0 && dayIndex < days.length && periodIndex >= 0 && periodIndex < maxPeriods) {
          timetableGrid[dayIndex][periodIndex] = entry;
        }
      });
    }

    return (
      <div className="schedule-container">
        <div className="schedule-header">
          <div className="section-selector">
            <label>Select Section:</label>
            <select
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              className="section-select"
            >
              <option value="A">Section A</option>
              <option value="B">Section B</option>
              <option value="C">Section C</option>
            </select>
          </div>
        </div>

        {loading && (
          <div className="loading">Loading schedule for Section {selectedSection}...</div>
        )}
        
        {!loading && schedule.length === 0 && !error && (
          <div className="empty-state" style={{ marginBottom: '20px' }}>
            No schedule entries found for Section {selectedSection}. Click on cells to add entries.
          </div>
        )}
        
        {editingCell && (
          <div className="cell-edit-form">
            <h3>{editingCell.entry ? 'Edit Schedule Entry' : 'Add Schedule Entry'}</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Subject Code *</label>
                <select
                  value={cellFormData.subcode || ''}
                  onChange={(e) => {
                    const selectedSubject = subjects.find(s => s.code === e.target.value);
                    setCellFormData({
                      ...cellFormData,
                      subcode: e.target.value,
                      subject_name: selectedSubject ? selectedSubject.name : '',
                      fini: '', // Reset faculty when subject changes
                      teacher_name: ''
                    });
                  }}
                  required
                >
                  <option value="">Select Subject</option>
                  {subjects.map((subject) => (
                    <option key={subject.code} value={subject.code}>
                      {subject.code} - {subject.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Faculty Initials *</label>
                <select
                  value={cellFormData.fini || ''}
                  onChange={(e) => {
                    const selectedFac = faculty.find(f => f.initials === e.target.value);
                    setCellFormData({
                      ...cellFormData,
                      fini: e.target.value,
                      teacher_name: selectedFac ? selectedFac.name : ''
                    });
                  }}
                  required
                  disabled={!cellFormData.subcode}
                >
                  <option value="">
                    {cellFormData.subcode ? 'Select Faculty' : 'Select Subject First'}
                  </option>
                  {cellFormData.subcode && faculty
                    .filter((fac) => fac.subcode1 === cellFormData.subcode || fac.subcode2 === cellFormData.subcode)
                    .map((fac) => (
                      <option key={fac.id} value={fac.initials}>
                        {fac.initials} - {fac.name}
                      </option>
                    ))}
                </select>
                {cellFormData.subcode && faculty.filter((fac) => fac.subcode1 === cellFormData.subcode || fac.subcode2 === cellFormData.subcode).length === 0 && (
                  <small style={{ color: '#dc3545', display: 'block', marginTop: '5px' }}>
                    No faculty available for this subject code
                  </small>
                )}
              </div>
            </div>
            <div className="form-actions">
              <button type="button" onClick={handleCellSave} className="btn-save">Save</button>
              <button type="button" onClick={() => { setEditingCell(null); setCellFormData({}); }} className="btn-cancel">Cancel</button>
              {editingCell.entry && (
                <button
                  type="button"
                  onClick={() => handleCellDelete(editingCell.entry.id)}
                  className="btn-delete"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        )}

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
                    const isEditing = editingCell && editingCell.dayId === dayIndex + 1 && editingCell.periodId === periodIndex + 1;
                    
                    return (
                      <td
                        key={periodIndex}
                        className={`period-cell ${isEditing ? 'editing' : ''}`}
                        onClick={() => handleCellClick(dayIndex + 1, periodIndex + 1)}
                      >
                        {entry ? (
                          <div className="schedule-entry">
                            <div className="subject-name">{entry.subject_name}</div>
                            <div className="subject-code">{entry.subcode}</div>
                            <div className="teacher-name">{entry.teacher_name}</div>
                            <div className="entry-actions">
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCellClick(dayIndex + 1, periodIndex + 1);
                                }} 
                                className="btn-edit-small"
                                title="Edit"
                              >
                                ✏️
                              </button>
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleViewAttendance(entry);
                                }} 
                                className="btn-attendance-small"
                                title="View Attendance"
                              >
                                👥
                              </button>
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCellDelete(entry.id);
                                }} 
                                className="btn-delete-small"
                                title="Delete"
                              >
                                🗑️
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="empty-cell">Click to add</div>
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
    );
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p className="welcome-text">
            Welcome, {user?.userInfo?.username || 'Admin'}
          </p>
        </div>
        <button onClick={logout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="admin-panel">
        <div className="admin-tabs">
          <button
            className={`tab-button ${activeTab === 'subjects' ? 'active' : ''}`}
            onClick={() => { setActiveTab('subjects'); setShowForm(false); }}
          >
            Subjects
          </button>
          <button
            className={`tab-button ${activeTab === 'faculty' ? 'active' : ''}`}
            onClick={() => { setActiveTab('faculty'); setShowForm(false); }}
          >
            Faculty
          </button>
          <button
            className={`tab-button ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => { setActiveTab('students'); setShowForm(false); }}
          >
            Students
          </button>
          <button
            className={`tab-button ${activeTab === 'schedule' ? 'active' : ''}`}
            onClick={() => { setActiveTab('schedule'); setShowForm(false); }}
          >
            Schedule Timetable
          </button>
          <button
            className={`tab-button ${activeTab === 'automated' ? 'active' : ''}`}
            onClick={() => { setActiveTab('automated'); setShowForm(false); }}
          >
            Automated Timetable
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="admin-content">
          {showForm ? (
            <div className="admin-form-container">
              {renderForm()}
            </div>
          ) : (
            <div className="admin-list-container">
              {activeTab !== 'schedule' && activeTab !== 'automated' && (
                <div className="admin-list-header">
                  <h2>
                    {activeTab === 'subjects' ? 'Subjects' : activeTab === 'faculty' ? 'Faculty' : 'Students'}
                  </h2>
                  <button onClick={handleAdd} className="btn-add">+ Add New</button>
                </div>
              )}

              {activeTab === 'schedule' ? (
                renderScheduleTimetable()
              ) : (
                <>
                  {loading ? (
                    <div className="loading">Loading...</div>
                  ) : (
                    <>
                      {activeTab === 'subjects' && (
                        subjects.length === 0 ? (
                          <div className="empty-state">No subjects found. Click "Add New" to create one.</div>
                        ) : (
                          renderSubjectsTable()
                        )
                      )}
                      {activeTab === 'faculty' && (
                        faculty.length === 0 ? (
                          <div className="empty-state">No faculty found. Click "Add New" to create one.</div>
                        ) : (
                          renderFacultyTable()
                        )
                      )}
                      {activeTab === 'students' && (
                        students.length === 0 ? (
                          <div className="empty-state">No students found. Click "Add New" to create one.</div>
                        ) : (
                          renderStudentsTable()
                        )
                      )}
                      {activeTab === 'automated' && (
                        <AutomatedTimetableGenerator />
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>

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
                  <p><strong>Teacher:</strong> {attendanceModal.schedule.teacher_name}</p>
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

export default AdminDashboard;
