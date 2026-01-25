import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import LandingPage from './LandingPage';
import './Login.css';

const Login = () => {
  const [userType, setUserType] = useState('student');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // Check if userType is specified in URL params
    const userTypeParam = searchParams.get('userType');
    if (userTypeParam && ['student', 'faculty', 'admin'].includes(userTypeParam)) {
      setUserType(userTypeParam);
      setShowLogin(true);
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(username, password, userType);
      
      // Store auth data
      login(response.access_token, response.user_info, response.user_type);
      
      // Navigate based on user type
      if (response.user_type === 'student') {
        navigate('/student/dashboard');
      } else if (response.user_type === 'faculty') {
        navigate('/faculty/dashboard');
      } else if (response.user_type === 'admin') {
        navigate('/admin/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLanding = () => {
    setShowLogin(false);
    navigate('/');
  };

  if (!showLogin) {
    return <LandingPage />;
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <button onClick={handleBackToLanding} className="back-button">
          ← Back to Home
        </button>
        <h1>Timetable Creator</h1>
        <h2>{userType.charAt(0).toUpperCase() + userType.slice(1)} Login</h2>
        
        <div className="user-type-selector">
          <button
            type="button"
            className={`user-type-btn ${userType === 'student' ? 'active' : ''}`}
            onClick={() => setUserType('student')}
          >
            Student
          </button>
          <button
            type="button"
            className={`user-type-btn ${userType === 'faculty' ? 'active' : ''}`}
            onClick={() => setUserType('faculty')}
          >
            Faculty
          </button>
          <button
            type="button"
            className={`user-type-btn ${userType === 'admin' ? 'active' : ''}`}
            onClick={() => setUserType('admin')}
          >
            Admin
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">
              {userType === 'student' ? 'Student ID' : userType === 'faculty' ? 'Email' : 'Username'}
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder={
                userType === 'student' 
                  ? 'Enter your Student ID' 
                  : userType === 'faculty' 
                  ? 'Enter your Email' 
                  : 'Enter your Username'
              }
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your Password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;


