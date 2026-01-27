import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="header">
        <div className="header-container">
          <div className="logo">
            <h1>Timetable Creator</h1>
            <p>Smart Scheduling Solution</p>
          </div>
          <nav className="nav-menu">
            <a href="#home" className="nav-link" onClick={(e) => { e.preventDefault(); document.getElementById('home')?.scrollIntoView({ behavior: 'smooth' }); }}>Home</a>
            <a href="#features" className="nav-link" onClick={(e) => { e.preventDefault(); document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' }); }}>Features</a>
            <a href="#about" className="nav-link" onClick={(e) => { e.preventDefault(); document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' }); }}>About</a>
            <a href="#contact" className="nav-link" onClick={(e) => { e.preventDefault(); document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' }); }}>Contact</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero" id="home">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">Welcome to Timetable Creator</h1>
            <p className="hero-subtitle">
              Streamline your academic scheduling with our intelligent timetable management system. 
              Designed for students, faculty, and administrators.
            </p>
            <div className="login-options">
              <h2>Choose Your Login</h2>
              <div className="login-cards">
                <div className="login-card student-card" onClick={() => navigate('/login?userType=student')}>
                  <div className="card-icon">👨‍🎓</div>
                  <h3>Student</h3>
                  <p>View your class schedule and manage your academic timetable</p>
                  <button className="card-btn">Student Login</button>
                </div>
                <div className="login-card faculty-card" onClick={() => navigate('/login?userType=faculty')}>
                  <div className="card-icon">👨‍🏫</div>
                  <h3>Faculty</h3>
                  <p>Manage your teaching schedule and view class assignments</p>
                  <button className="card-btn">Faculty Login</button>
                </div>
                <div className="login-card admin-card" onClick={() => navigate('/login?userType=admin')}>
                  <div className="card-icon">⚙️</div>
                  <h3>Administrator</h3>
                  <p>Full system control and timetable management</p>
                  <button className="card-btn">Admin Login</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="features-container">
          <h2 className="section-title">Key Features</h2>
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">📅</div>
              <h3>Smart Scheduling</h3>
              <p>Intelligent timetable generation with conflict detection and resolution</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">🔄</div>
              <h3>Real-time Updates</h3>
              <p>Instant schedule changes and notifications for all stakeholders</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">📱</div>
              <h3>Mobile Friendly</h3>
              <p>Access your timetable from any device, anywhere, anytime</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">📊</div>
              <h3>Analytics Dashboard</h3>
              <p>Comprehensive insights and reporting for administrators</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">🔒</div>
              <h3>Secure Access</h3>
              <p>Role-based permissions and secure authentication</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">🎯</div>
              <h3>Easy Management</h3>
              <p>Intuitive interface for effortless timetable management</p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about" id="about">
        <div className="about-container">
          <h2 className="section-title">About Timetable Creator</h2>
          <div className="about-content">
            <div className="about-text">
              <p>
                Timetable Creator is a comprehensive scheduling solution designed to simplify 
                academic timetable management for educational institutions. Our platform brings 
                together students, faculty, and administrators in a unified system that makes 
                scheduling efficient, transparent, and conflict-free.
              </p>
              <p>
                With advanced algorithms and user-friendly interfaces, we ensure that creating 
                and managing timetables becomes a seamless experience for everyone involved.
              </p>
            </div>
            <div className="about-stats">
              <div className="stat-item">
                <h3>1000+</h3>
                <p>Active Users</p>
              </div>
              <div className="stat-item">
                <h3>50+</h3>
                <p>Institutions</p>
              </div>
              <div className="stat-item">
                <h3>99.9%</h3>
                <p>Uptime</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer" id="contact">
        <div className="footer-container">
          <div className="footer-content">
            <div className="footer-section">
              <h3>Timetable Creator</h3>
              <p>Smart Scheduling Solution for Modern Education</p>
              <div className="social-links">
                <a href="#" className="social-link">📧</a>
                <a href="#" className="social-link">💼</a>
                <a href="#" className="social-link">🐦</a>
                <a href="#" className="social-link">📱</a>
              </div>
            </div>
            <div className="footer-section">
              <h4>Quick Links</h4>
              <ul>
                <li><a href="#home" onClick={(e) => { e.preventDefault(); document.getElementById('home')?.scrollIntoView({ behavior: 'smooth' }); }}>Home</a></li>
                <li><a href="#features" onClick={(e) => { e.preventDefault(); document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' }); }}>Features</a></li>
                <li><a href="#about" onClick={(e) => { e.preventDefault(); document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' }); }}>About</a></li>
                <li><a href="#contact" onClick={(e) => { e.preventDefault(); document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' }); }}>Contact</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Support</h4>
              <ul>
                <li><a href="#">Help Center</a></li>
                <li><a href="#">Documentation</a></li>
                <li><a href="#">Privacy Policy</a></li>
                <li><a href="#">Terms of Service</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Contact Us</h4>
              <div className="contact-info">
                <p>📧 support@timetablecreator.com</p>
                <p>📞 +1 (555) 123-4567</p>
                <p>📍 123 Education Street, Learning City, LC 12345</p>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 Timetable Creator. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
