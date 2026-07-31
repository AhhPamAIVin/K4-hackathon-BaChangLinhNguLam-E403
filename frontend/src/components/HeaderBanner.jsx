import React from 'react';
import './HeaderBanner.css';

export default function HeaderBanner({ t }) {
  return (
    <div className="header-banner">
      <div className="header-banner-content">
        <span className="banner-tag">{t.bannerTag}</span>
        <h1 className="banner-title">{t.bannerTitle}</h1>
        <p className="banner-subtitle">
          {t.bannerSubtitle}
        </p>
      </div>

      <div className="header-banner-badge">
        <span>{t.enrolledBadge}</span>
      </div>
    </div>
  );
}
