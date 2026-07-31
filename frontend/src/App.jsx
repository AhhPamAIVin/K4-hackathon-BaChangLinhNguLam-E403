import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HeaderBanner from './components/HeaderBanner';
import WelcomeCard from './components/WelcomeCard';
import StatsGrid from './components/StatsGrid';
import CourseActionCard from './components/CourseActionCard';
import MyCoursesView from './components/MyCoursesView';
import CourseDetailView from './components/CourseDetailView';
import SlideReaderView from './components/SlideReaderView';
import { translations } from './translations';

export default function App() {
  const [activeTab, setActiveTab] = useState(() => {
    const path = window.location.pathname;
    if (path === '/reader') return 'reader';
    if (path === '/course-detail') return 'course-detail';
    if (path === '/my-courses') return 'my-courses';
    return 'home';
  });
  const [selectedDoc, setSelectedDoc] = useState('day01_302.pdf');
  const [darkMode, setDarkMode] = useState(false); // Default mode
  const [lang, setLang] = useState('EN'); // Default match to user's latest screenshot!

  const t = translations[lang] || translations.EN;

  // Handle browser back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/reader') {
        setActiveTab('reader');
      } else if (path === '/course-detail') {
        setActiveTab('course-detail');
      } else if (path === '/my-courses') {
        setActiveTab('my-courses');
      } else {
        setActiveTab('home');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Update tab state and browser history
  const navigateTo = (tab, docName = 'day01_302.pdf') => {
    if (docName) setSelectedDoc(docName);
    setActiveTab(tab);

    let path = '/';
    if (tab === 'my-courses') path = '/my-courses';
    if (tab === 'course-detail') path = '/course-detail';
    if (tab === 'reader') path = '/reader';

    if (window.location.pathname !== path) {
      window.history.pushState({ tab }, '', path);
    }
  };

  // Toggle Dark/Light Theme on root html element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }, [darkMode]);

  return (
    <div className="app-root">
      {/* Show main navbar only when not in full-screen reader workspace */}
      {activeTab !== 'reader' && (
        <Navbar
          activeTab={activeTab}
          setActiveTab={navigateTo}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          lang={lang}
          setLang={setLang}
          t={t}
          userEmail="bachanglinhngulam"
        />
      )}

      <main className={activeTab === 'reader' ? 'reader-wrapper' : 'app-container'}>
        {activeTab === 'home' && (
          <div className="home-view animate-fade-in">
            <HeaderBanner t={t} />
            <WelcomeCard 
              userName="BA CHANG LINH NGU LAM" 
              onGoToCourses={() => navigateTo('my-courses')} 
              t={t}
            />
            <StatsGrid 
              courseCount={1} 
              tutorQuestionsCount={3} 
              onCardClick={(tab) => navigateTo(tab)} 
              t={t}
            />
            <CourseActionCard 
              onClick={() => navigateTo('my-courses')} 
              t={t}
            />
          </div>
        )}

        {activeTab === 'my-courses' && (
          <MyCoursesView 
            onSelectCourse={() => navigateTo('course-detail')} 
            t={t}
          />
        )}

        {activeTab === 'course-detail' && (
          <CourseDetailView 
            onSelectDocument={(docName) => navigateTo('reader', docName)} 
            t={t}
          />
        )}

        {activeTab === 'reader' && (
          <SlideReaderView 
            selectedDocName={selectedDoc}
            onBack={() => navigateTo('course-detail')}
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            lang={lang}
            setLang={setLang}
            t={t}
          />
        )}
      </main>
    </div>
  );
}
