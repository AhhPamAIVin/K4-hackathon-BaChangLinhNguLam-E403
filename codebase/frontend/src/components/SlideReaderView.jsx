import React, { useState, useEffect, useRef } from 'react';
import { 
  ArrowLeft, BookOpen, Check, ChevronLeft, ChevronRight, ChevronDown, ChevronUp,
  Moon, Sun, Eye, Edit3, Highlighter, Plus, Minus, Download, Bookmark, Undo, Trash2, BookMarked, MoreHorizontal, Sparkles
} from 'lucide-react';
import PdfSlidePage from './PdfSlidePage';
import AiTutorPanel from './AiTutorPanel';
import './SlideReaderView.css';

export default function SlideReaderView({ 
  selectedDocName = "d1-slide-hackathon.pdf", 
  onBack, 
  darkMode, 
  setDarkMode, 
  lang, 
  setLang, 
  t 
}) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeDoc, setActiveDoc] = useState(selectedDocName);
  const [openDay, setOpenDay] = useState('day01');
  const [activeTool, setActiveTool] = useState('read');
  const [zoomLevel, setZoomLevel] = useState(100);
  const [activePage, setActivePage] = useState(1);
  const [selectionTooltip, setSelectionTooltip] = useState(null);
  const [selectedContext, setSelectedContext] = useState(null);
  const [tutorOpen, setTutorOpen] = useState(false);
  const [tutorMode, setTutorMode] = useState('qa');

  // PDF.js Loaded State
  const [pdfDoc, setPdfDoc] = useState(null);
  const [numPages, setNumPages] = useState(0);
  const [pdfLoading, setPdfLoading] = useState(true);

  const mainCanvasRef = useRef(null);

  useEffect(() => {
    if (selectedDocName) {
      setActiveDoc(selectedDocName);
      if (selectedDocName.includes('d2')) {
        setOpenDay('day02');
      } else {
        setOpenDay('day01');
      }
    }
  }, [selectedDocName]);

  // Load PDF Document via PDF.js
  useEffect(() => {
    let isCancelled = false;
    setPdfLoading(true);
      setPdfDoc(null);
      setActivePage(1);
      setSelectionTooltip(null);
      setSelectedContext(null);

    const pdfUrl = `/slide/${activeDoc}`;

    const loadPdf = () => {
      if (window.pdfjsLib) {
        window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        
        const loadingTask = window.pdfjsLib.getDocument(pdfUrl);
        loadingTask.promise.then((pdf) => {
          if (isCancelled) return;
          setPdfDoc(pdf);
          setNumPages(pdf.numPages);
          setPdfLoading(false);
        }).catch((err) => {
          console.error("Error loading PDF via PDF.js:", err);
          if (!isCancelled) setPdfLoading(false);
        });
      } else {
        setTimeout(loadPdf, 300);
      }
    };

    loadPdf();

    return () => {
      isCancelled = true;
    };
  }, [activeDoc]);

  // Dynamic Scroll Spy: Detect visible slide page and update activePage state
  useEffect(() => {
    const container = mainCanvasRef.current;
    if (!container || numPages === 0) return;

    const handleScroll = () => {
      const pageElements = container.querySelectorAll('.slide-page-card');
      if (!pageElements.length) return;

      const containerRect = container.getBoundingClientRect();
      const triggerY = containerRect.top + containerRect.height / 3;

      let currentVisible = 1;

      pageElements.forEach((el, index) => {
        const rect = el.getBoundingClientRect();
        if (rect.top <= triggerY && rect.bottom >= containerRect.top) {
          currentVisible = index + 1;
        }
      });

      setActivePage(currentVisible);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, [numPages, activeDoc]);

  // Scroll smoothly to a specific page
  const scrollToPage = (pageNum) => {
    const targetPage = document.getElementById(`page-${pageNum}`);
    if (targetPage) {
      targetPage.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActivePage(pageNum);
    }
  };

  // Text selection handler for AI Agent
  const handleMouseUp = (event) => {
    if (event.target.closest('.ai-tutor-panel, .ai-selection-tooltip')) return;
    const selection = window.getSelection();
    if (selection && selection.toString().trim().length > 0) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      const tooltipLeft = Math.min(
        Math.max(rect.left + rect.width / 2, 130),
        window.innerWidth - 130,
      );
      setSelectionTooltip({
        text: selection.toString().trim().slice(0, 12000),
        top: Math.max(rect.top - 46, 62),
        left: tooltipLeft,
      });
    } else {
      setSelectionTooltip(null);
    }
  };

  const openTutor = (mode = 'qa') => {
    setTutorMode(mode);
    setTutorOpen(true);
  };

  const askAboutSelection = () => {
    if (!selectionTooltip?.text) return;
    setSelectedContext({
      text: selectionTooltip.text,
      source: activeDoc,
      page: activePage,
    });
    setSelectionTooltip(null);
    openTutor('qa');
    window.getSelection()?.removeAllRanges();
  };

  const daysSidebarData = [
    {
      id: 'day01',
      title: 'Day01',
      materialsText: `1 ${t.materialsPublished}`,
      inProgress: true,
      files: [
        { name: 'd1-slide-hackathon.pdf', pages: `PDF Slide` },
      ]
    },
    {
      id: 'day02',
      title: 'Day02',
      materialsText: `1 ${t.materialsPublished}`,
      inProgress: false,
      files: [
        { name: 'd2-slide-hackathon.pdf', pages: `PDF Slide` }
      ]
    }
  ];

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = `/slide/${activeDoc}`;
    link.download = activeDoc;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="slide-reader-root animate-fade-in" onMouseUp={handleMouseUp}>
      {/* 1. Top Navbar */}
      <header className="reader-navbar">
        <div className="reader-navbar-left">
          <button className="btn-icon-back" onClick={onBack} title="Quay lại danh sách bài học">
            <ArrowLeft size={18} />
          </button>

          <div className="reader-logo">
            <svg width="26" height="26" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 8L16 28L21 17L13 8H6Z" fill="#C81E1E" />
              <path d="M22 8L16 28L30 8H22Z" fill="#0F2B48" />
            </svg>
            <span className="logo-text">VLearn</span>
          </div>

          <div className="active-doc-badge">
            <div className="doc-icon-box">
              <BookOpen size={16} />
            </div>
            <div className="doc-meta-text">
              <span className="doc-filename">{activeDoc}</span>
              <span className="doc-subtitle">COMP2010 · Lecture_material_ms2039d0_hnxpxy</span>
            </div>
          </div>
        </div>

        <div className="reader-navbar-right">
          <button 
            className="btn-pill btn-lang"
            onClick={() => setLang(lang === 'VI' ? 'EN' : 'VI')}
          >
            {lang}
          </button>

          <button 
            className="btn-circle btn-theme" 
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      {/* 2. Main Body */}
      <div className={`reader-body-container ${tutorOpen ? 'tutor-open' : ''}`}>
        {/* Left Sidebar */}
        <aside className={`reader-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <div className="sidebar-header">
            <div className="sidebar-title-row">
              <BookOpen size={18} className="sidebar-icon" />
              <div className="sidebar-header-text">
                <h3 className="sidebar-title">{t.courseMaterials}</h3>
                <p className="sidebar-subtitle">{t.materialsSubtitle}</p>
              </div>
            </div>
          </div>

          <div className="sidebar-accordion">
            {daysSidebarData.map((day) => {
              const isOpen = openDay === day.id;
              return (
                <div key={day.id} className="sidebar-day-group">
                  <div 
                    className="day-group-header"
                    onClick={() => setOpenDay(isOpen ? null : day.id)}
                  >
                    <div className="day-header-meta">
                      <div className="day-bullet-circle"></div>
                      <span className="day-name">{day.title}</span>
                    </div>

                    <div className="day-header-right-meta">
                      {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </div>
                  </div>

                  <div className="day-sub-label">{day.materialsText}</div>

                  {isOpen && day.files.length > 0 && (
                    <div className="day-files-list">
                      {day.files.map((file, idx) => {
                        const isSelected = activeDoc === file.name;
                        return (
                          <div
                            key={idx}
                            className={`sidebar-file-item ${isSelected ? 'active' : ''}`}
                            onClick={() => setActiveDoc(file.name)}
                          >
                            <div className="file-item-left">
                              <div className="file-dot-icon"></div>
                              <div className="file-info-group">
                                <span className="file-item-name">{file.name}</span>
                                <span className="file-item-pages">
                                  {numPages > 0 && isSelected ? `${numPages} ${t.pagesCount}` : file.pages}
                                </span>
                              </div>
                            </div>

                            {isSelected && (
                              <div className="active-checkmark-badge">
                                <Check size={12} />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <button 
            className="btn-toggle-sidebar" 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            title={sidebarOpen ? "Thu gọn thanh bên" : "Mở rộng thanh bên"}
          >
            {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
          </button>
        </aside>

        {/* Center Workspace: Dynamic PDF Pages Stack */}
        <main className="reader-main-canvas custom-pages-workspace" ref={mainCanvasRef}>
          {/* FLOATING TOP READER TOOLBAR (Nhảy theo activePage) */}
          <div className="floating-top-reader-bar">
            <div className="toolbar-pill-group">
              <button 
                className={`tool-pill-btn ${activeTool === 'read' ? 'active' : ''}`}
                onClick={() => setActiveTool('read')}
              >
                <Eye size={15} />
                <span>{t.toolRead}</span>
              </button>

              <button 
                className={`tool-pill-btn ${activeTool === 'pen' ? 'active' : ''}`}
                onClick={() => setActiveTool('pen')}
              >
                <Edit3 size={15} />
                <span>{t.toolPen}</span>
              </button>

              <button 
                className={`tool-pill-btn ${activeTool === 'highlight' ? 'active' : ''}`}
                onClick={() => setActiveTool('highlight')}
              >
                <Highlighter size={15} />
                <span>& {t.toolHighlight}</span>
              </button>

              <button className="tool-pill-btn btn-more" title="Thêm công cụ">
                <MoreHorizontal size={15} />
              </button>
            </div>

            <div className="toolbar-v-divider"></div>

            <div className="toolbar-center-section">
              <span className="notes-count-label">
                {typeof t.pageNotes === 'function' ? t.pageNotes(activePage) : t.pageNotes}
              </span>

              <div className="zoom-adjust-box">
                <button 
                  className="btn-zoom-step"
                  onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}
                  title="Thu nhỏ"
                >
                  <Minus size={13} />
                </button>
                <span className="zoom-text">{zoomLevel}%</span>
                <button 
                  className="btn-zoom-step"
                  onClick={() => setZoomLevel(Math.min(200, zoomLevel + 10))}
                  title="Phóng to"
                >
                  <Plus size={13} />
                </button>
              </div>
            </div>

            <div className="toolbar-v-divider"></div>

            <div className="toolbar-action-icons">
              <button className="btn-tool-icon" onClick={() => setZoomLevel(Math.min(200, zoomLevel + 10))}><Plus size={15} /></button>
              <button className="btn-tool-icon" onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}><Minus size={15} /></button>
              <button className="btn-tool-icon" onClick={handleDownload} title="Tải xuống"><Download size={15} /></button>
              <button className="btn-tool-icon" title="Đánh dấu trang"><Bookmark size={15} /></button>
              <button className="btn-tool-icon" title="Hoàn tác"><Undo size={15} /></button>
              <button className="btn-tool-icon" title="Xóa ghi chú"><Trash2 size={15} /></button>
            </div>
          </div>

          {/* Text Selection Floating AI Agent Popup Tooltip */}
          {selectionTooltip && (
            <div 
              className="ai-selection-tooltip animate-fade-in"
              style={{ top: `${selectionTooltip.top}px`, left: `${selectionTooltip.left}px` }}
            >
              <button
                className="btn-ai-ask"
                onMouseDown={(event) => event.preventDefault()}
                onClick={askAboutSelection}
              >
                <Sparkles size={14} />
                <span>Hỏi VLearn AI Agent</span>
              </button>
              <button className="btn-ai-highlight">
                <Highlighter size={14} />
                <span>Highlight</span>
              </button>
            </div>
          )}

          {/* ALL PDF SLIDE PAGES STACK */}
          <div className="slides-pages-stack" style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}>
            {pdfLoading && (
              <div className="pdf-global-loading">
                <div className="spinner-large"></div>
                <h3>Đang xử lý và tách {activeDoc}...</h3>
              </div>
            )}

            {!pdfLoading && pdfDoc && Array.from({ length: numPages }, (_, i) => i + 1).map((pageNum) => (
              <PdfSlidePage
                key={`${activeDoc}-page-${pageNum}`}
                pdfDoc={pdfDoc}
                pageNum={pageNum}
                totalPages={numPages}
                docName={activeDoc}
              />
            ))}
          </div>

          {/* Floating Bottom Pager (Nhảy theo activePage) */}
          <div className="floating-bottom-pager">
            <button 
              className="btn-pager" 
              onClick={() => scrollToPage(Math.max(1, activePage - 1))}
            >
              <ChevronLeft size={16} />
            </button>
            <span className="pager-text">Page {activePage} / {numPages || 1}</span>
            <button 
              className="btn-pager" 
              onClick={() => scrollToPage(Math.min(numPages || 1, activePage + 1))}
            >
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Far Right Floating Button (AI Tutor) */}
          <button
            className="floating-right-tutor-btn"
            title="Mở VLearn AI Tutor"
            onClick={() => openTutor('qa')}
          >
            <Sparkles size={20} />
          </button>
        </main>

        {tutorOpen && (
          <AiTutorPanel
            mode={tutorMode}
            onModeChange={setTutorMode}
            selection={selectedContext}
            onClearSelection={() => setSelectedContext(null)}
            currentDay={activeDoc.includes('d2') ? 'day-2' : 'day-1'}
            onClose={() => setTutorOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
