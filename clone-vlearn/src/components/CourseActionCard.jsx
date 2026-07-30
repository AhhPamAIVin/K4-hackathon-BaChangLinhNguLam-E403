import React from 'react';
import { BookOpen, ArrowRight } from 'lucide-react';
import './CourseActionCard.css';

export default function CourseActionCard({ onClick, t }) {
  return (
    <div className="course-action-card v-card" onClick={onClick}>
      <div className="action-card-left">
        <div className="action-icon-wrapper">
          <BookOpen size={24} />
        </div>

        <div className="action-card-text">
          <h3 className="action-card-title">{t.actionCardTitle}</h3>
          <p className="action-card-subtitle">
            {t.actionCardSubtitle}
          </p>
        </div>
      </div>

      <div className="action-card-right">
        <ArrowRight size={20} className="arrow-icon" />
      </div>
    </div>
  );
}
