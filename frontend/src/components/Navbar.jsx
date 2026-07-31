import React from 'react';
import { BookOpen, ExternalLink, Moon, Sun, ChevronDown, Home, BookMarked } from 'lucide-react';
import './Navbar.css';

export default function Navbar({ activeTab, setActiveTab, darkMode, setDarkMode, lang, setLang, t, userEmail = "bachanglinhngulam" }) {
  return (
    <header className="navbar">
      <div className="app-container navbar-inner">
        {/* Left Side: Logo & Tabs */}
        <div className="navbar-left">
          <div className="navbar-logo" onClick={() => setActiveTab('home')}>
            <svg width="32" height="32" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 8L16 28L21 17L13 8H6Z" fill="#C81E1E" />
              <path d="M22 8L16 28L30 8H22Z" fill="#0F2B48" />
            </svg>
            <span className="logo-text">VLearn</span>
          </div>

          <nav className="navbar-nav">
            <button
              className={`nav-tab ${activeTab === 'home' ? 'active' : ''}`}
              onClick={() => setActiveTab('home')}
            >
              <Home size={18} className="tab-icon" />
              <span>{t.homeTab}</span>
            </button>

            <button
              className={`nav-tab ${activeTab === 'my-courses' || activeTab === 'course-detail' ? 'active' : ''}`}
              onClick={() => setActiveTab('my-courses')}
            >
              <BookOpen size={18} className="tab-icon" />
              <span>{t.myCoursesTab}</span>
            </button>

            <button
              className={`nav-tab ${activeTab === 'notebook' ? 'active' : ''}`}
              onClick={() => setActiveTab('my-courses')}
            >
              <BookMarked size={18} className="tab-icon" />
              <span>{t.notebookTab}</span>
            </button>
          </nav>
        </div>

        {/* Right Side: Tools & Profile */}
        <div className="navbar-right">
          <button className="btn-codelabs" title={t.openCodelabs}>
            <ExternalLink size={15} />
            <span>{t.openCodelabs}</span>
          </button>

          <button 
            className="btn-pill btn-lang"
            onClick={() => setLang(lang === 'VI' ? 'EN' : 'VI')}
            title="Switch Language / Đổi ngôn ngữ"
          >
            {lang}
          </button>

          <button 
            className="btn-circle btn-theme" 
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          <div className="user-profile-dropdown">
            <div className="user-badge-num">2</div>
            <span className="user-email-text">{userEmail}</span>
            <ChevronDown size={14} className="dropdown-arrow" />
          </div>
        </div>
      </div>
    </header>
  );
}
