import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (username, password, userType) => {
    const response = await api.post('/auth/login', {
      username,
      password,
      user_type: userType,
    });
    return response.data;
  },
};

export const studentAPI = {
  getTimetable: async (section) => {
    const response = await api.get(`/student/timetable/${section}`);
    return response.data;
  },
};

export const facultyAPI = {
  getTimetable: async (fini) => {
    const response = await api.get(`/faculty/timetable/${fini}`);
    return response.data;
  },
};

export const adminAPI = {
  // Subjects
  getSubjects: async () => {
    const response = await api.get('/subjects/');
    return response.data;
  },
  createSubject: async (subject) => {
    const response = await api.post('/subjects/', subject);
    return response.data;
  },
  updateSubject: async (code, subject) => {
    const response = await api.put(`/subjects/${code}`, subject);
    return response.data;
  },
  deleteSubject: async (code) => {
    const response = await api.delete(`/subjects/${code}`);
    return response.data;
  },
  
  // Faculty
  getFaculty: async () => {
    const response = await api.get('/faculty/');
    return response.data;
  },
  createFaculty: async (faculty) => {
    const response = await api.post('/faculty/', faculty);
    return response.data;
  },
  updateFaculty: async (id, faculty) => {
    const response = await api.put(`/faculty/${id}`, faculty);
    return response.data;
  },
  deleteFaculty: async (id) => {
    const response = await api.delete(`/faculty/${id}`);
    return response.data;
  },
  
  // Students
  getStudents: async () => {
    const response = await api.get('/students/');
    return response.data;
  },
  createStudent: async (student) => {
    const response = await api.post('/students/', student);
    return response.data;
  },
  updateStudent: async (id, student) => {
    const response = await api.put(`/students/${id}`, student);
    return response.data;
  },
  deleteStudent: async (id) => {
    const response = await api.delete(`/students/${id}`);
    return response.data;
  },
  
  // Schedule
  getScheduleBySection: async (section) => {
    const response = await api.get(`/schedule/section/${section}`);
    return response.data;
  },
  createScheduleEntry: async (schedule) => {
    const response = await api.post('/schedule/', schedule);
    return response.data;
  },
  updateScheduleEntry: async (id, schedule) => {
    const response = await api.put(`/schedule/${id}`, schedule);
    return response.data;
  },
  deleteScheduleEntry: async (id) => {
    const response = await api.delete(`/schedule/${id}`);
    return response.data;
  },
  getSubjects: async () => {
    const response = await api.get('/subjects/');
    return response.data;
  },
  getFaculty: async () => {
    const response = await api.get('/faculty/');
    return response.data;
  },
  
  // Automated Timetable Generation
  getAutomatedSubjects: async () => {
    const response = await api.get('/automated/subjects');
    return response.data;
  },
  getAutomatedFaculty: async () => {
    const response = await api.get('/automated/faculty');
    return response.data;
  },
  generateAutomatedTimetable: async (assignments) => {
    const response = await api.post('/automated/generate', assignments);
    return response.data;
  },
  previewSectionTimetable: async (section) => {
    const response = await api.get(`/automated/preview/${section}`);
    return response.data;
  },
  
  // Clear entire timetable for a section
  clearSectionSchedule: async (section) => {
    const response = await api.delete(`/schedule/section/${section}`);
    return response.data;
  },
  
  // Attendance Management
  generateQRCode: async (scheduleId) => {
    const response = await api.post('/attendance/generate-qr', { schedule_id: scheduleId });
    return response.data;
  },
  markAttendance: async (qrHash, studentId, scheduleId) => {
    const response = await api.post('/attendance/mark', { 
      qr_hash: qrHash, 
      student_id: studentId,
      schedule_id: scheduleId 
    });
    return response.data;
  },
  getAttendanceBySchedule: async (scheduleId) => {
    const response = await api.get(`/attendance/schedule/${scheduleId}`);
    return response.data;
  },
  getAttendanceByStudent: async (studentId) => {
    const response = await api.get(`/attendance/student/${studentId}`);
    return response.data;
  },
  getAttendanceStats: async (scheduleId) => {
    const response = await api.get(`/attendance/stats/${scheduleId}`);
    return response.data;
  },
  markManualAttendance: async (studentId, scheduleId, status = 'Present') => {
    const response = await api.post('/attendance/manual', null, {
      params: { student_id: studentId, schedule_id: scheduleId, status }
    });
    return response.data;
  },
};

export default api;
