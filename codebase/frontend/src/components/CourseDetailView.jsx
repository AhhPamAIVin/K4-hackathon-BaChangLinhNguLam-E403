import React, { useState } from 'react';
import { CheckCircle2, ChevronUp, ChevronDown, FileText } from 'lucide-react';
import './CourseDetailView.css';

export default function CourseDetailView({ onSelectDocument, t }) {
  const [openDays, setOpenDays] = useState({
    day01: true,
    day02: false,
  });

  const toggleDay = (dayKey) => {
    setOpenDays((prev) => ({
      ...prev,
      [dayKey]: !prev[dayKey],
    }));
  };

  const daysData = [
    {
      id: 'day01',
      dayNum: '01',
      title: 'Day01',
      subtitle: t.day01Sub,
      files: ['d1-slide-hackathon.pdf'],
    },
    {
      id: 'day02',
      dayNum: '02',
      title: 'Day02',
      subtitle: t.day02Sub,
      files: ['d2-slide-hackathon.pdf'],
    },
  ];

  return (
    <div className="course-detail-page animate-fade-in">
      {/* Sub-Header Banner */}
      <div className="detail-header">
        <div className="detail-header-left">
          <span className="detail-tag">{t.bannerTag}</span>
          <h1 className="detail-title">{t.detailTitle}</h1>
          <p className="detail-subtitle">{t.classmatesCount}</p>
        </div>

        {/* Header Right Progress Controls */}
        <div className="detail-header-right">
          <div className="reading-progress-info">
            <CheckCircle2 size={16} className="check-icon" />
            <span>{t.readDaysCount}</span>
            <div className="mini-progress-bar">
              <div className="mini-progress-fill" style={{ width: '0%' }}></div>
            </div>
            <span className="percent-text">0%</span>
          </div>

          <button className="btn-start-read">
            {t.btnStartRead}
          </button>
        </div>
      </div>

      {/* Accordion List */}
      <div className="days-accordion-list">
        {daysData.map((day) => {
          const isOpen = !!openDays[day.id];
          return (
            <div 
              key={day.id} 
              className={`day-accordion-card v-card ${isOpen ? 'expanded' : ''}`}
            >
              <div 
                className="day-accordion-header"
                onClick={() => toggleDay(day.id)}
              >
                <div className="day-header-left">
                  {/* Round Badge: DAY / 01 or 02 */}
                  <div className="day-badge-circle">
                    <span className="day-badge-top">DAY</span>
                    <span className="day-badge-num">{day.dayNum}</span>
                  </div>

                  <div className="day-title-group">
                    <h3 className="day-title-text">{day.title}</h3>
                    <p className="day-subtitle-text">{day.subtitle}</p>
                  </div>
                </div>

                <div className="day-header-right">
                  {isOpen ? (
                    <ChevronUp size={20} className="accordion-chevron" />
                  ) : (
                    <ChevronDown size={20} className="accordion-chevron" />
                  )}
                </div>
              </div>

              {/* Accordion Content (Slides / PDFs) */}
              {isOpen && (
                <div className="day-accordion-content">
                  {day.files.map((file, idx) => (
                    <div 
                      key={idx} 
                      className="pdf-item-row"
                      onClick={() => onSelectDocument && onSelectDocument(file)}
                    >
                      <FileText size={18} className="pdf-icon" />
                      <span className="pdf-filename">{file}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
