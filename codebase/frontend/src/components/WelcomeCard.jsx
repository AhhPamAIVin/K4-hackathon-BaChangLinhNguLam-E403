import React from 'react';
import './WelcomeCard.css';

export default function WelcomeCard({ userName = "BA CHANG LINH NGU LAM", onGoToCourses, t }) {
  return (
    <div className="welcome-card v-card">
      <div className="welcome-card-top-bar"></div>
      
      <div className="welcome-card-inner">
        <div className="welcome-card-content">
          <span className="welcome-tag">{t.welcomeTag}</span>
          <h2 className="welcome-heading">{t.welcomeHeading}, {userName}!</h2>
          <p className="welcome-text">
            {t.welcomeTextBeforeLink}
            <span className="link-inline" onClick={onGoToCourses}>
              {t.welcomeLinkText}
            </span>
            {t.welcomeTextAfterLink}
          </p>

          <div className="welcome-badges">
            <div className="badge-pill badge-active-signal">
              <span className="status-dot-green"></span>
              <span>{t.activeSignal}</span>
            </div>

            <div className="badge-pill badge-reading-progress">
              <span>{t.readingProgress}</span>
            </div>
          </div>
        </div>

        {/* Right Slanted Red Decorative Banner Block */}
        <div className="welcome-card-red-accent" aria-hidden="true"></div>
      </div>
    </div>
  );
}
