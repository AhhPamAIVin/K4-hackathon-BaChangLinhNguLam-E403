import React from 'react';
import { BookOpen, Activity } from 'lucide-react';
import './StatsGrid.css';

export default function StatsGrid({ courseCount = 1, tutorQuestionsCount = 3, onCardClick, t }) {
  return (
    <div className="stats-grid">
      {/* Stat 1: Khóa học */}
      <div className="stat-card v-card" onClick={() => onCardClick('my-courses')}>
        <div className="stat-icon-wrapper">
          <BookOpen size={24} className="stat-icon" />
        </div>
        <div className="stat-info">
          <span className="stat-label">{t.statCourses}</span>
          <span className="stat-value">{courseCount}</span>
        </div>
      </div>

      {/* Stat 2: Câu hỏi với Tutor */}
      <div className="stat-card v-card">
        <div className="stat-icon-wrapper">
          <Activity size={24} className="stat-icon" />
        </div>
        <div className="stat-info">
          <span className="stat-label">{t.statTutorQuestions}</span>
          <span className="stat-value">{tutorQuestionsCount}</span>
        </div>
      </div>
    </div>
  );
}
