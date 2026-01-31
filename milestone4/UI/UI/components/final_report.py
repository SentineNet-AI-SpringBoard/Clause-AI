from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components


def ReportSummary(result: Dict[str, Any]) -> None:
    analysis = result.get("analysis") or {}
    overall = (analysis.get("overall_risk") or "unknown").upper()
    summary_points = analysis.get("executive_summary_points") or []
    question = (result.get("question") or "").strip()

    st.markdown("#### Executive Summary")
    st.markdown(f"**Overall risk:** {overall}")
    if question:
        st.caption(f"Question: {question}")

    if summary_points:
        st.markdown("**Highlights**")
        for p in summary_points:
            if (p or "").strip():
                st.markdown(f"- {p}")
    else:
        st.info("No executive summary points were generated for this document.")

    st.markdown("#### Full Report")
    st.code(result.get("report", ""), language="markdown")


def evidenceToPdfMapper(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    analysis = result.get("analysis") or {}
    items: List[Dict[str, Any]] = []

    def _bbox_from(item: Dict[str, Any]) -> Optional[List[float]]:
        for key in ("bbox", "bounding_box", "box"):
            val = item.get(key)
            if isinstance(val, (list, tuple)) and len(val) == 4:
                return [float(v) for v in val]
        return None

    def _page_from(item: Dict[str, Any]) -> Optional[int]:
        for key in ("page", "page_number", "page_index"):
            val = item.get(key)
            if isinstance(val, (int, float)):
                return int(val)
        return None

    key_evidence = analysis.get("key_evidence") or []
    for idx, ev in enumerate(key_evidence):
        if not isinstance(ev, dict):
            continue
        text = (ev.get("text") or "").strip()
        if not text:
            continue
        items.append(
            {
                "id": f"key-{idx}",
                "heading": (ev.get("label") or "Evidence").strip(),
                "text": text,
                "risk": analysis.get("overall_risk"),
                "page": _page_from(ev),
                "bbox": _bbox_from(ev),
            }
        )

    for section in ("legal", "compliance", "finance", "operations"):
        sec = analysis.get(section) or {}
        ev_list = sec.get("evidence") or []
        for j, text in enumerate(ev_list):
            if not (text or "").strip():
                continue
            items.append(
                {
                    "id": f"{section}-{j}",
                    "heading": f"{section.title()} Evidence",
                    "text": (text or "").strip(),
                    "risk": sec.get("risk_level"),
                    "page": None,
                    "bbox": None,
                }
            )

    return items


def JsonEvidencePanel(result: Dict[str, Any], pdf_bytes: Optional[bytes]) -> None:
    """Render split-pane view: left=evidence cards, right=PDF with highlights"""
    
    evidence_items = evidenceToPdfMapper(result)
    raw_json = json.dumps(result, ensure_ascii=False, indent=2)
    
    # Handle missing PDF
    if not pdf_bytes:
        st.warning("⚠️ PDF preview unavailable. Only showing extracted data below.")
        pdf_b64 = ""
    else:
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

    payload = {
        "metadata": {
            "contract_id": result.get("contract_id") or result.get("filename") or "N/A",
            "intent": result.get("intent") or "risk_analysis",
            "generated_at": result.get("generated_at") or "N/A",
            "overall_risk": (result.get("analysis") or {}).get("overall_risk") or "unknown",
        },
        "evidence": evidence_items,
        "raw_json": raw_json,
        "pdf_b64": pdf_b64,
    }

    html = _render_data_view_html(payload)
    
    # Render with larger height for better UX
    components.html(html, height=850, scrolling=False)


def PdfViewer() -> str:
    return "<div id=\"pdf-pane\" class=\"pdf-pane\"></div>"


def HighlightOverlay() -> str:
    return "<div id=\"highlight-overlay\" class=\"highlight-overlay\"></div>"


def _render_data_view_html(payload: Dict[str, Any]) -> str:
  """Generate HTML for split-pane data view with PDF viewer and evidence highlighting"""
  # Properly escape JSON for embedding in JavaScript
  import html as html_module
  data_json = json.dumps(payload, ensure_ascii=False)
  # Prevent script injection but keep JSON valid for JS parsing
  data_json_escaped = data_json.replace("<", "\\u003c").replace(">", "\\u003e")
  
  template = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
  <style>
    :root {{
      --bg: #ffffff;
      --panel-bg: #f7f7fb;
      --border: #e2e6ef;
      --text: #1a1a1a;
      --muted: #6b7280;
      --highlight: rgba(255, 215, 64, 0.55);
      --highlight-border: rgba(255, 170, 0, 0.9);
      --card-bg: #ffffff;
    }}
    body {{ margin: 0; font-family: "Segoe UI", Arial, sans-serif; color: var(--text); background: var(--bg); }}
    .container {{ display: grid; grid-template-columns: 40% 60%; gap: 16px; height: 800px; }}
    .left-pane {{ border: 1px solid var(--border); background: var(--panel-bg); padding: 16px; overflow-y: auto; border-radius: 8px; }}
    .right-pane {{ border: 1px solid var(--border); background: var(--card-bg); padding: 8px; overflow-y: auto; position: relative; border-radius: 8px; }}
    .meta {{ font-size: 12px; color: var(--muted); margin-bottom: 16px; padding: 12px; background: var(--card-bg); border-radius: 6px; }}
    .meta div {{ margin-bottom: 4px; }}
    .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 14px; margin-bottom: 12px; cursor: pointer; transition: all 0.2s; }}
    .card:hover {{ border-color: #93c5fd; box-shadow: 0 2px 8px rgba(37,99,235,0.1); }}
    .card.active {{ border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.15); background: #eff6ff; }}
    .card h4 {{ margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #0f172a; }}
    .card p {{ margin: 0; font-size: 13px; color: var(--muted); line-height: 1.5; }}
    .risk-pill {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 10px; font-weight: 600; margin-left: 8px; }}
    .risk-pill.high {{ background: #fef2f2; color: #991b1b; }}
    .risk-pill.medium {{ background: #fefce8; color: #a16207; }}
    .risk-pill.low {{ background: #f0fdf4; color: #166534; }}
    .pdf-page {{ position: relative; margin: 12px auto; box-shadow: 0 2px 10px rgba(0,0,0,0.08); background: white; }}
    .textLayer {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; }}
    .textLayer span {{ color: transparent; position: absolute; white-space: pre; cursor: text; }}
    .highlight {{ background: var(--highlight) !important; border-bottom: 2px solid var(--highlight-border); }}
    .highlight-box {{ position: absolute; pointer-events: none; }}
    .raw-json {{ white-space: pre-wrap; font-size: 11px; font-family: 'Consolas', monospace; background: #0f172a; color: #cbd5e1; padding: 12px; border-radius: 8px; overflow-x: auto; max-height: 400px; }}
    .empty {{ color: var(--muted); font-size: 13px; padding: 20px; text-align: center; }}
    .section-title {{ font-size: 15px; font-weight: 600; margin: 20px 0 12px 0; color: #0f172a; }}
    @media (max-width: 980px) {{
      .container {{ grid-template-columns: 1fr; height: auto; }}
      .right-pane {{ height: 560px; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="left-pane" id="left-pane"></div>
    <div class="right-pane" id="right-pane">
      <div id="pdf-pane"></div>
    </div>
  </div>

  <script>
    const payload = {data_json_escaped};  // Directly injected JSON object
    const leftPane = document.getElementById('left-pane');
    const pdfPane = document.getElementById('pdf-pane');

    function renderLeftPane() {{
      const meta = payload.metadata || {{}};
      const evidence = payload.evidence || [];
      
      leftPane.innerHTML = `
        <div class="meta">
          <div><strong>📄 Contract:</strong> ${{meta.contract_id || 'N/A'}}</div>
          <div><strong>🎯 Intent:</strong> ${{meta.intent || 'N/A'}}</div>
          <div><strong>🕐 Generated:</strong> ${{meta.generated_at || 'N/A'}}</div>
          <div><strong>⚠️ Overall Risk:</strong> <span style="text-transform: uppercase; font-weight: 600;">${{meta.overall_risk || 'N/A'}}</span></div>
        </div>
        <h3 class="section-title">📋 Extracted Clauses & Evidence</h3>
        ${{evidence.length ? '' : '<div class="empty">No evidence clauses found in the analysis.</div>'}}
        <div id="evidence-list"></div>
        <h3 class="section-title">🔧 Raw JSON (Technical View)</h3>
        <details>
          <summary style="cursor: pointer; padding: 8px; background: #f1f5f9; border-radius: 6px; margin-bottom: 8px;">Click to show/hide raw JSON</summary>
          <div class="raw-json">${{(payload.raw_json || '{{}}').replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</div>
        </details>
      `;

      const list = document.getElementById('evidence-list');
      evidence.forEach((item, idx) => {{
        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.evidenceId = item.id;
        
        const riskClass = (item.risk || '').toLowerCase();
        const riskPill = item.risk ? `<span class="risk-pill ${{riskClass}}">${{String(item.risk).toUpperCase()}}</span>` : '';
        
        card.innerHTML = `
          <h4>${{item.heading || 'Evidence'}} ${{riskPill}}</h4>
          <p>${{item.text || 'No text available'}}</p>
        `;
        card.addEventListener('click', () => selectEvidence(item.id));
        list.appendChild(card);
      }});
    }}

    let pdfDoc = null;
    let pageViews = new Map();

    async function loadPdf() {{
      if (!payload.pdf_b64 || payload.pdf_b64 === '') {{
        pdfPane.innerHTML = '<div class="empty" style="padding: 40px;">📄 PDF preview unavailable.<br/><small>Upload a PDF file to enable side-by-side viewing.</small></div>';
        return;
      }}
      
      try {{
        const raw = atob(payload.pdf_b64);
        const bytes = new Uint8Array(raw.length);
        for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);

        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        pdfDoc = await pdfjsLib.getDocument({{ data: bytes }}).promise;
        pdfPane.innerHTML = '';
        
        for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {{
          await renderPage(pageNum);
        }}
      }} catch (err) {{
        pdfPane.innerHTML = `<div class="empty">Failed to load PDF: ${{err.message}}</div>`;
        console.error('PDF load error:', err);
      }}
    }}

    async function renderPage(pageNum) {{
      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({{ scale: 1.2 }});

      const pageContainer = document.createElement('div');
      pageContainer.className = 'pdf-page';
      pageContainer.style.width = `${{viewport.width}}px`;
      pageContainer.style.height = `${{viewport.height}}px`;
      pageContainer.dataset.pageNumber = pageNum;

      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      pageContainer.appendChild(canvas);

      const textLayer = document.createElement('div');
      textLayer.className = 'textLayer';
      textLayer.style.width = `${{viewport.width}}px`;
      textLayer.style.height = `${{viewport.height}}px`;
      pageContainer.appendChild(textLayer);

      pdfPane.appendChild(pageContainer);

      await page.render({{ canvasContext: context, viewport }}).promise;
      const textContent = await page.getTextContent();
      pdfjsLib.renderTextLayer({{
        textContent,
        container: textLayer,
        viewport,
        textDivs: []
      }});

      pageViews.set(pageNum, {{ page, viewport, container: pageContainer, textLayer }});
    }}

    function clearHighlights() {{
      document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
      document.querySelectorAll('.highlight-box').forEach(el => el.remove());
    }}

    function applyBoxHighlight(pageNum, bbox) {{
      const view = pageViews.get(pageNum);
      if (!view || !bbox || bbox.length !== 4) return;
      
      const [x, y, w, h] = bbox;
      const box = document.createElement('div');
      box.className = 'highlight-box';
      box.style.position = 'absolute';
      box.style.border = '2px solid rgba(255,165,0,0.9)';
      box.style.background = 'rgba(255,215,64,0.35)';
      box.style.left = `${{x}}px`;
      box.style.top = `${{y}}px`;
      box.style.width = `${{w}}px`;
      box.style.height = `${{h}}px`;
      box.style.pointerEvents = 'none';
      view.container.appendChild(box);
    }}

    function applyTextHighlight(pageNum, anchorText) {{
      const view = pageViews.get(pageNum);
      if (!view || !anchorText) return;
      
      const needle = anchorText.toLowerCase().trim();
      if (needle.length < 4) return;
      
      const spans = view.textLayer.querySelectorAll('span');
      spans.forEach(span => {{
        const text = (span.textContent || '').toLowerCase().trim();
        if (text && needle.includes(text) && text.length > 3) {{
          span.classList.add('highlight');
        }}
      }});
    }}

    function scrollToPage(pageNum) {{
      const view = pageViews.get(pageNum);
      if (view) {{
        view.container.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    function selectEvidence(id) {{
      const evidence = payload.evidence || [];
      const item = evidence.find(e => e.id === id);
      if (!item) return;
      
      // Update card selection
      document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
      const card = document.querySelector(`.card[data-evidence-id='${{id}}']`);
      if (card) card.classList.add('active');

      // Clear previous highlights
      clearHighlights();
      
      // Apply new highlights
      const pageNum = item.page ? Number(item.page) : null;
      if (pageNum && pageViews.has(pageNum)) {{
        scrollToPage(pageNum);
        if (item.bbox) applyBoxHighlight(pageNum, item.bbox);
        applyTextHighlight(pageNum, item.text);
      }} else {{
        // Fallback: search all pages for text anchor
        pageViews.forEach((_, p) => applyTextHighlight(p, item.text));
      }}
    }}

    // Initialize
    renderLeftPane();
    loadPdf();
  </script>
</body>
</html>
"""
  return template
