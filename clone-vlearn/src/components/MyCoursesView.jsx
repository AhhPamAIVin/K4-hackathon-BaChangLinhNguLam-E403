import React from 'react';
import { BookOpen, Activity, BookMarked, ArrowRight } from 'lucide-react';
import './MyCoursesView.css';

export default function MyCoursesView({ onSelectCourse, t }) {
  return (
    <div className="my-courses-page animate-fade-in">
      {/* Sub-Header Banner for My Courses */}
      <div className="my-courses-header">
        <div className="header-text-group">
          <span className="header-tag">{t.bannerTag}</span>
          <h1 className="header-title">{t.myCoursesTitle}</h1>
          <p className="header-subtitle">
            {t.myCoursesSubtitle}
          </p>
        </div>

        <div className="header-badge">
          <span>{t.enrolledBadge}</span>
        </div>
      </div>

      {/* Courses Cards Grid */}
      <div className="courses-grid">
        <div className="course-card v-card" onClick={onSelectCourse}>
          {/* Card Top Row: Book Icon & Progress Badge */}
          <div className="card-top-row">
            <div className="course-icon-box">
              <BookOpen size={20} />
            </div>
            <div className="badge-read-percent">
              <span>{t.readPercent}</span>
            </div>
          </div>

          {/* Card Main Info */}
          <div className="course-main-info">
            <span className="course-code">{t.courseCode}</span>
            <h2 className="course-name">{t.courseName}</h2>
            <p className="course-sub-description">{t.courseSubDesc}</p>
          </div>

          <div className="card-divider"></div>

          {/* Card Bottom Row: Ready Status & Actions */}
          <div className="card-bottom-row">
            <div className="status-ready">
              <Activity size={15} className="status-icon" />
              <span>{t.statusReady}</span>
            </div>

            <div className="card-actions-group">
              <button 
                className="btn-notebook-pill"
                onClick={(e) => { e.stopPropagation(); onSelectCourse(); }}
              >
                <BookMarked size={14} />
                <span>{t.btnNotebook}</span>
              </button>

              <button 
                className="btn-open-course"
                onClick={(e) => { e.stopPropagation(); onSelectCourse(); }}
              >
                <span>{t.btnOpenCourse}</span>
                <ArrowRight size={14} className="arrow-icon" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Notebook Full-Width Action Card */}
      <div className="notebook-banner-card v-card">
        <div className="notebook-card-left">
          <div className="notebook-icon-box">
            <BookMarked size={22} />
          </div>

          <div className="notebook-text-group">
            <h3 className="notebook-title">{t.notebookCardTitle}</h3>
            <p className="notebook-subtitle">
              {t.notebookCardSubtitle}
            </p>
          </div>
        </div>

        <div className="notebook-card-right">
          <ArrowRight size={20} className="arrow-icon" />
        </div>
      </div>
    </div>
  );
}
