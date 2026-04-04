"""
PDF Preview Component with Pre-Analysis Highlighting
Shows users the document they're uploading with automatic highlights of key sections
"""
from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components


def PDFPreviewWithHighlights(pdf_bytes: bytes, filename: str, auto_highlight_keywords: Optional[List[str]] = None) -> None:
    """
    Display PDF preview without highlighting.
    User can review the document before analysis begins.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        filename: Name of the uploaded file
        auto_highlight_keywords: Not used (kept for compatibility)
    """
    # No auto-highlighting - user just reviews the document
    
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
  <style>
    body {{ 
      margin: 0; 
      font-family: "Segoe UI", Arial, sans-serif; 
      background: #f8fafc;
    }}
    .header {{
      background: #0f172a;
      color: white;
      padding: 20px;
      text-align: center;
    }}
    .header h2 {{ margin: 0 0 8px 0; font-size: 20px; }}
    .header p {{ margin: 0; font-size: 14px; opacity: 0.9; }}
    .info-banner {{
      background: #dbeafe;
      border-left: 4px solid #2563eb;
      padding: 16px 20px;
      margin: 16px;
      border-radius: 6px;
    }}
    .info-banner strong {{ color: #1e40af; }}
    .pdf-container {{
      padding: 20px;
      overflow-y: auto;
      height: calc(100vh - 200px);
      min-height: 500px;
    }}
    .pdf-page {{
      position: relative;
      margin: 0 auto 20px auto;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      background: white;
    }}
    .textLayer {{
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }}
    .textLayer span {{
      color: transparent;
      position: absolute;
      white-space: pre;
      cursor: text;
    }}
    .page-number {{
      position: absolute;
      top: -25px;
      left: 0;
      font-size: 12px;
      color: #64748b;
      font-weight: 500;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h2>📄 Document Preview: {filename}</h2>
    <p>Review the document below before analysis begins.</p>
  </div>
  
  <div class="info-banner">
    <strong>✓ What you're seeing:</strong> This is the exact document that will be analyzed. 
    After analysis, you'll see which specific clauses were extracted and used in the final report.
  </div>
  
  <div class="pdf-container" id="pdf-container"></div>

  <script>
    const pdfData = "{pdf_b64}";
    
    async function loadAndDisplayPDF() {{
      try {{
        const raw = atob(pdfData);
        const bytes = new Uint8Array(raw.length);
        for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);

        pdfjsLib.GlobalWorkerOptions.workerSrc = 
          'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        
        const pdf = await pdfjsLib.getDocument({{ data: bytes }}).promise;
        const container = document.getElementById('pdf-container');
        container.innerHTML = '';

        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
          await renderPage(pdf, pageNum, container);
        }}
      }} catch (err) {{
        console.error('PDF load error:', err);
        document.getElementById('pdf-container').innerHTML = 
          `<div style="color: red; padding: 20px;">Failed to load PDF: ${{err.message}}</div>`;
      }}
    }}

    async function renderPage(pdf, pageNum, container) {{
      const page = await pdf.getPage(pageNum);
      const viewport = page.getViewport({{ scale: 1.3 }});

      const pageDiv = document.createElement('div');
      pageDiv.className = 'pdf-page';
      pageDiv.style.width = `${{viewport.width}}px`;
      pageDiv.style.height = `${{viewport.height}}px`;
      
      const pageLabel = document.createElement('div');
      pageLabel.className = 'page-number';
      pageLabel.textContent = `Page ${{pageNum}}`;
      pageDiv.appendChild(pageLabel);

      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      pageDiv.appendChild(canvas);

      const textLayer = document.createElement('div');
      textLayer.className = 'textLayer';
      textLayer.style.width = `${{viewport.width}}px`;
      textLayer.style.height = `${{viewport.height}}px`;
      pageDiv.appendChild(textLayer);

      container.appendChild(pageDiv);

      await page.render({{ canvasContext: context, viewport }}).promise;
      const textContent = await page.getTextContent();
      
      pdfjsLib.renderTextLayer({{
        textContent,
        container: textLayer,
        viewport,
        textDivs: []
      }});
    }}

    loadAndDisplayPDF();
  </script>
</body>
</html>
"""
    
    components.html(html, height=700, scrolling=False)


def ConfirmationPanel() -> bool:
    """Shows confirmation UI for user to proceed with analysis"""
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: #f0fdf4; border: 2px solid #16a34a; border-radius: 10px; padding: 20px; text-align: center;'>
            <h3 style='margin: 0 0 10px 0; color: #15803d;'>✓ Confirm Document</h3>
            <p style='margin: 0; color: #166534;'>
                This document will be analyzed. After analysis completes, 
                you'll see which specific clauses were extracted and used in the final report.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        return st.button(
            "✓ Confirm & Start Analysis", 
            type="primary", 
            use_container_width=True,
            key="confirm_analysis_btn"
        )
