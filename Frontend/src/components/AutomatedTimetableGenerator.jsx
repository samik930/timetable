import { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';

const AutomatedTimetableGenerator = () => {
  const [subjects, setSubjects] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [generationResults, setGenerationResults] = useState(null);

  useEffect(() => {
    fetchSubjectsAndFaculty();
  }, []);

  const fetchSubjectsAndFaculty = async () => {
    try {
      setLoading(true);
      const [subjectsData, facultyData] = await Promise.all([
        adminAPI.getAutomatedSubjects(),
        adminAPI.getAutomatedFaculty()
      ]);
      setSubjects(subjectsData.subjects || []);
      setFaculty(facultyData.faculty || []);
    } catch (err) {
      setError('Failed to load subjects and faculty data');
    } finally {
      setLoading(false);
    }
  };

  const addAssignment = () => {
    setAssignments([...assignments, {
      section: 'A',
      subject_code: '',
      faculty_initials: ''
    }]);
  };

  const removeAssignment = (index) => {
    setAssignments(assignments.filter((_, i) => i !== index));
  };

  const updateAssignment = (index, field, value) => {
    const updatedAssignments = [...assignments];
    updatedAssignments[index][field] = value;
    
    // If subject is changed, reset faculty selection
    if (field === 'subject_code') {
      updatedAssignments[index].faculty_initials = '';
    }
    
    setAssignments(updatedAssignments);
  };

  const generateTimetable = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      setGenerationResults(null);

      // Validate assignments
      if (assignments.length === 0) {
        setError('Please add at least one subject-faculty assignment');
        return;
      }

      for (let assignment of assignments) {
        if (!assignment.subject_code || !assignment.faculty_initials) {
          setError('Please fill in all subject and faculty fields');
          return;
        }
      }

      const response = await adminAPI.generateAutomatedTimetable({ assignments });
      setGenerationResults(response.results);
      setSuccess('Timetable generated successfully!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate timetable');
    } finally {
      setLoading(false);
    }
  };

  const refreshResults = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Get current schedules for all sections
      const results = {};
      for (const section of ['A', 'B', 'C']) {
        try {
          const scheduleResponse = await adminAPI.previewSectionTimetable(section);
          if (scheduleResponse && scheduleResponse.schedule && scheduleResponse.schedule.length > 0) {
            results[section] = {
              "status": "existing", 
              "message": `Existing timetable found for section ${section}`,
              "schedule": scheduleResponse.schedule
            };
          } else {
            results[section] = {"status": "empty", "message": `No timetable found for section ${section}`};
          }
        } catch (err) {
          results[section] = {"status": "error", "message": `Error loading section ${section}`};
        }
      }
      
      setGenerationResults(results);
    } catch (err) {
      setError('Failed to refresh timetables');
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setAssignments([]);
    setGenerationResults(null);
    setSuccess('');
    setError('');
  };

  const getSubjectName = (code) => {
    const subject = subjects.find(s => s.code === code);
    return subject ? subject.name : code;
  };

  const getFacultyName = (initials) => {
    const facultyMember = faculty.find(f => f.initials === initials);
    return facultyMember ? facultyMember.name : initials;
  };

  const getFilteredFaculty = (subjectCode) => {
    if (!subjectCode) return faculty;
    
    return faculty.filter(facultyMember => 
      facultyMember.subcode1 === subjectCode || facultyMember.subcode2 === subjectCode
    );
  };

  return (
    <div className="automated-timetable-generator">
      <h2>Automated Timetable Generator</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="assignments-section">
        <h3>Subject-Faculty Assignments</h3>
        <p>Assign subjects and faculty for each section. The system will automatically generate timetables ensuring:</p>
        <ul>
          <li>One teacher per class per slot</li>
          <li>No teacher/class overlap</li>
          <li>Lab periods are scheduled back-to-back</li>
          <li>4th period is break time for all sections</li>
          <li>Credit validation is maintained</li>
        </ul>

        <button 
          className="btn btn-primary" 
          onClick={addAssignment}
          disabled={loading}
        >
          Add Subject
        </button>

        {assignments.length > 0 && (
          <button 
            className="btn btn-secondary" 
            onClick={clearAll}
            disabled={loading}
            style={{ marginLeft: '10px' }}
          >
            Clear All
          </button>
        )}

        <button 
          className="btn btn-info"
          onClick={refreshResults}
          disabled={loading}
          style={{ marginLeft: '10px' }}
        >
          {loading ? 'Loading...' : 'Refresh Existing Timetables'}
        </button>

        <div className="assignments-list">
          {assignments.map((assignment, index) => {
            const filteredFaculty = getFilteredFaculty(assignment.subject_code);
            return (
              <div key={index} className="assignment-row">
                <select
                  value={assignment.section}
                  onChange={(e) => updateAssignment(index, 'section', e.target.value)}
                  disabled={loading}
                >
                  <option value="A">Section A</option>
                  <option value="B">Section B</option>
                  <option value="C">Section C</option>
                </select>

                <select
                  value={assignment.subject_code}
                  onChange={(e) => updateAssignment(index, 'subject_code', e.target.value)}
                  disabled={loading}
                >
                  <option value="">Select Subject</option>
                  {subjects.map(subject => (
                    <option key={subject.code} value={subject.code}>
                      {subject.code} - {subject.name} ({subject.credits} credits, {subject.subtype})
                    </option>
                  ))}
                </select>

                <select
                  value={assignment.faculty_initials}
                  onChange={(e) => updateAssignment(index, 'faculty_initials', e.target.value)}
                  disabled={loading || !assignment.subject_code}
                >
                  <option value="">
                    {assignment.subject_code ? 'Select Faculty' : 'Select Subject First'}
                  </option>
                  {filteredFaculty.map(facultyMember => (
                    <option key={facultyMember.initials} value={facultyMember.initials}>
                      {facultyMember.initials} - {facultyMember.name}
                    </option>
                  ))}
                </select>

                <button 
                  className="btn btn-danger"
                  onClick={() => removeAssignment(index)}
                  disabled={loading}
                >
                  Remove
                </button>
              </div>
            );
          })}
        </div>

        <button 
          className="btn btn-success"
          onClick={generateTimetable}
          disabled={loading || assignments.length === 0}
          style={{ marginTop: '20px' }}
        >
          {loading ? 'Generating...' : 'Generate Timetable'}
        </button>
      </div>

      {generationResults && (
        <div className="results-section">
          <h3>Generation Results</h3>
          {Object.entries(generationResults).map(([section, result]) => (
            <div key={section} className={`result-item ${result.status}`}>
              <h4>Section {section}</h4>
              <p><strong>Status:</strong> {result.status}</p>
              <p><strong>Message:</strong> {result.message}</p>
              
              {(result.status === 'success' || result.status === 'existing') && result.schedule && (
                <div className="schedule-preview">
                  <h5>Schedule Preview:</h5>
                  <div className="schedule-grid">
                    <table>
                      <thead>
                        <tr>
                          <th>Day</th>
                          <th>Period 1</th>
                          <th>Period 2</th>
                          <th>Period 3</th>
                          <th>Period 4</th>
                          <th>Period 5</th>
                          <th>Period 6</th>
                          <th>Period 7</th>
                          <th>Period 8</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[1, 2, 3, 4, 5].map(day => (
                          <tr key={day}>
                            <td>Day {day}</td>
                            {[1, 2, 3, 4, 5, 6, 7, 8].map(period => {
                              const scheduleItem = result.schedule.find(
                                item => item.day_id === day && item.period_id === period
                              );
                              return (
                                <td key={period} className={period === 4 ? 'break-period' : ''}>
                                  {period === 4 ? 'BREAK' : (
                                    scheduleItem ? 
                                      `${scheduleItem.subcode}\n${scheduleItem.fini}` : 
                                      '-'
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
          ))}
        </div>
      )}

      <style jsx>{`
        .automated-timetable-generator {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .assignments-section {
          margin-bottom: 30px;
        }

        .assignments-list {
          margin: 20px 0;
        }

        .assignment-row {
          display: flex;
          gap: 10px;
          margin-bottom: 10px;
          align-items: center;
        }

        .assignment-row select {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          min-width: 150px;
        }

        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .btn-primary { background-color: #007bff; color: white; }
        .btn-secondary { background-color: #6c757d; color: white; }
        .btn-success { background-color: #28a745; color: white; }
        .btn-danger { background-color: #dc3545; color: white; }
        .btn-info { background-color: #17a2b8; color: white; }

        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .success-message {
          background-color: #d4edda;
          color: #155724;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .results-section {
          margin-top: 30px;
        }

        .result-item {
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 15px;
          margin-bottom: 15px;
        }

        .result-item.success {
          border-color: #28a745;
          background-color: #f8fff9;
        }

        .result-item.existing {
          border-color: #17a2b8;
          background-color: #f0f8f9;
        }

        .result-item.error {
          border-color: #dc3545;
          background-color: #fff8f8;
        }

        .schedule-preview {
          margin-top: 15px;
        }

        .schedule-grid table {
          width: 100%;
          border-collapse: collapse;
          font-size: 12px;
        }

        .schedule-grid th,
        .schedule-grid td {
          border: 1px solid #ddd;
          padding: 4px;
          text-align: center;
          vertical-align: top;
        }

        .schedule-grid th {
          background-color: #f8f9fa;
          font-weight: bold;
        }

        .break-period {
          background-color: #fff3cd;
          font-weight: bold;
        }

        ul {
          margin: 10px 0;
          padding-left: 20px;
        }

        li {
          margin-bottom: 5px;
        }
      `}</style>
    </div>
  );
};

export default AutomatedTimetableGenerator;
