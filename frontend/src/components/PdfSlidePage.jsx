import React, { useEffect, useRef, useState } from 'react';

export default function PdfSlidePage({ pdfDoc, pageNum, totalPages, docName }) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const textLayerRef = useRef(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!pdfDoc || !canvasRef.current || !containerRef.current) return;
    let isCancelled = false;

    pdfDoc.getPage(pageNum).then((page) => {
      if (isCancelled) return;

      const containerWidth = containerRef.current.clientWidth || 760;
      const unscaledViewport = page.getViewport({ scale: 1.0 });
      const scale = containerWidth / unscaledViewport.width;
      const viewport = page.getViewport({ scale: scale });

      const outputScale = window.devicePixelRatio || 1;
      const canvas = canvasRef.current;
      if (!canvas) return;

      const context = canvas.getContext('2d');
      canvas.width = Math.floor(viewport.width * outputScale);
      canvas.height = Math.floor(viewport.height * outputScale);
      canvas.style.width = `${viewport.width}px`;
      canvas.style.height = `${viewport.height}px`;

      const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : null;

      // Track matrix transformation state to detect diagonal watermark rotation
      let isDiagonalRotated = false;

      const origTransform = context.transform;
      context.transform = function(a, b, c, d, e, f) {
        if (Math.abs(b) > 0.08 && Math.abs(c) > 0.08) {
          isDiagonalRotated = true;
        }
        return origTransform.apply(this, arguments);
      };

      const origSetTransform = context.setTransform;
      context.setTransform = function(a, b, c, d, e, f) {
        if (typeof a === 'object' && a !== null) {
          if (Math.abs(a.b) > 0.08 && Math.abs(a.c) > 0.08) {
            isDiagonalRotated = true;
          } else {
            isDiagonalRotated = false;
          }
        } else if (b !== undefined && c !== undefined) {
          if (Math.abs(b) > 0.08 && Math.abs(c) > 0.08) {
            isDiagonalRotated = true;
          } else {
            isDiagonalRotated = false;
          }
        } else {
          isDiagonalRotated = false;
        }
        return origSetTransform.apply(this, arguments);
      };

      // Intercept fill & stroke calls: suppress drawing if rotated diagonally or semi-transparent
      const origFill = context.fill;
      context.fill = function() {
        if (isDiagonalRotated || context.globalAlpha < 0.35) return;
        return origFill.apply(this, arguments);
      };

      const origStroke = context.stroke;
      context.stroke = function() {
        if (isDiagonalRotated || context.globalAlpha < 0.35) return;
        return origStroke.apply(this, arguments);
      };

      const origFillText = context.fillText;
      context.fillText = function(text, x, y, maxWidth) {
        if (isDiagonalRotated || context.globalAlpha < 0.35 || (typeof text === 'string' && /HACKATHON|26AI|BAONT2|VINUNI/i.test(text))) {
          return;
        }
        return origFillText.apply(this, arguments);
      };

      const origStrokeText = context.strokeText;
      context.strokeText = function(text, x, y, maxWidth) {
        if (isDiagonalRotated || context.globalAlpha < 0.35 || (typeof text === 'string' && /HACKATHON|26AI|BAONT2|VINUNI/i.test(text))) {
          return;
        }
        return origStrokeText.apply(this, arguments);
      };

      // Get PDF Operator List and filter out watermark text & form operations
      page.getOperatorList().then((opList) => {
        if (isCancelled) return;

        const OPS = window.pdfjsLib ? window.pdfjsLib.OPS : null;
        if (OPS) {
          for (let i = 0; i < opList.fnArray.length; i++) {
            const fn = opList.fnArray[i];
            if (fn === OPS.showText || fn === OPS.showSpacedText) {
              const args = opList.argsArray[i];
              if (args && args[0]) {
                let textStr = '';
                if (Array.isArray(args[0])) {
                  textStr = args[0].map(item => {
                    if (typeof item === 'string') return item;
                    if (item && typeof item.str === 'string') return item.str;
                    return '';
                  }).join('');
                } else if (typeof args[0] === 'string') {
                  textStr = args[0];
                }

                if (/HACKATHON|26AI|BAONT2|VINUNI|ACTION/i.test(textStr)) {
                  opList.fnArray[i] = OPS.nop;
                }
              }
            }
          }
        }

        const renderContext = {
          canvasContext: context,
          transform: transform,
          viewport: viewport,
          operatorList: opList,
        };

        page.render(renderContext).promise.then(() => {
          if (isCancelled) return;
          setLoading(false);

          // Render Text Layer for text selection & AI Agent
          if (textLayerRef.current && window.pdfjsLib) {
            const textLayerDiv = textLayerRef.current;
            textLayerDiv.innerHTML = '';
            textLayerDiv.style.width = `${viewport.width}px`;
            textLayerDiv.style.height = `${viewport.height}px`;

            page.getTextContent().then((textContent) => {
              if (isCancelled) return;

              const filteredItems = textContent.items.filter(item => {
                return !/HACKATHON|26AI|BAONT2|VINUNI|ACTION/i.test(item.str);
              });

              // Create precise selectable DOM text spans for each PDF text item
              filteredItems.forEach((item) => {
                if (!item.str || !item.str.trim()) return;
                const tx = window.pdfjsLib.Util.transform(viewport.transform, item.transform);
                const span = document.createElement('span');
                span.textContent = item.str;
                span.style.left = `${tx[4]}px`;
                span.style.top = `${tx[5] - (item.height * scale)}px`;
                span.style.fontSize = `${item.height * scale}px`;
                span.style.fontFamily = item.fontName || 'sans-serif';
                span.style.position = 'absolute';
                span.className = 'selectable-pdf-text';
                textLayerDiv.appendChild(span);
              });
            });
          }
        }).catch(err => {
          console.error(`Error rendering page ${pageNum}:`, err);
          setLoading(false);
        });
      });
    }).catch(err => {
      console.error(`Error loading page ${pageNum}:`, err);
      setLoading(false);
    });

    return () => {
      isCancelled = true;
    };
  }, [pdfDoc, pageNum]);

  return (
    <div className="slide-page-card" id={`page-${pageNum}`}>
      <div className="slide-card-header-row">
        <span className="page-number-label">Page {pageNum} / {totalPages}</span>
        <span className="doc-name-label">{docName}</span>
      </div>

      <div className="pdf-canvas-container" ref={containerRef}>
        {loading && (
          <div className="pdf-page-skeleton">
            <div className="spinner"></div>
            <span>Đang tải trang {pageNum}...</span>
          </div>
        )}
        <canvas ref={canvasRef} className="pdf-page-canvas" />
        <div ref={textLayerRef} className="pdf-text-layer" />
      </div>
    </div>
  );
}
