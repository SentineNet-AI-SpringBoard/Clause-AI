"""
Q&A Report Component - Simplified, non-technical view for end users
Replaces complex JSON output with clean question-answer format
"""
from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional, Union

import streamlit as st
import streamlit.components.v1 as components


def QuestionAnswerReport(result: Dict[str, Any], pdf_bytes: Optional[bytes] = None) -> None:
    """
    Display analysis results as clean Q&A format with optional PDF highlighting.
    Non-technical users never see JSON - just questions and answers.
    
    Args:
        result: Analysis result dictionary
        pdf_bytes: Optional PDF bytes for interactive highlighting
    """
    analysis = result.get("analysis") or {}
    overall_risk = (analysis.get("overall_risk") or "unknown").upper()
    question = result.get("question") or ""
    
    # Risk banner
    risk_color = "#dc2626" if overall_risk == "HIGH" else "#f59e0b" if overall_risk == "MEDIUM" else "#16a34a"
    risk_bg = "#fee2e2" if overall_risk == "HIGH" else "#fef3c7" if overall_risk == "MEDIUM" else "#dcfce7"
    
    st.markdown(f"""
    <div style='background: {risk_bg}; border-left: 4px solid {risk_color}; padding: 16px; margin-bottom: 20px; border-radius: 6px;'>
        <h3 style='margin: 0; color: {risk_color};'>⚠️ Overall Risk Level: {overall_risk}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate Q&A pairs from result
    qa_pairs = _extract_qa_pairs(result, question)
    
    if not qa_pairs:
        st.info("No analysis questions were generated for this document.")
        return
    
    # Display Q&A
    for idx, qa in enumerate(qa_pairs):
        q_text = qa.get("question", "")
        a_text = qa.get("answer", "")
        evidence = qa.get("evidence", [])
        page_refs = qa.get("page_refs", [])
        
        with st.container():
            st.markdown(f"""
            <div style='background: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 16px; border: 1px solid #e2e8f0;'>
                <div style='font-weight: 600; color: #0f172a; font-size: 15px; margin-bottom: 8px;'>
                    ❓ {q_text}
                </div>
                <div style='color: #475569; line-height: 1.6; font-size: 14px;'>
                    {a_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Optional: Show evidence in collapsible section
            if evidence and pdf_bytes:
                with st.expander("📄 View source text from document", expanded=False):
                    st.caption("These are the actual clauses extracted from your document:")
                    for ev_idx, ev_text in enumerate(evidence[:3]):  # Limit to 3 evidence items
                        st.markdown(f"**Source {ev_idx + 1}:**")
                        st.code(ev_text, language="text")
    
    # Advanced mode toggle
    st.markdown("---")
    with st.expander("🔧 Advanced / Developer View (JSON)", expanded=False):
        st.json(result, expanded=False)


def QuestionAnswerWithPDF(result: Union[Dict[str, Any], List[Dict[str, Any]]], pdf_bytes: Optional[bytes]) -> None:
    """
    Split view: Q&A on left, PDF with highlights on right.
    Clicking a question scrolls to and highlights the relevant text in PDF.
    Supports single result dict or list of results (for chat history).
    """
    if not pdf_bytes:
        # Fallback to simple Q&A view (only handles single result for now)
        if isinstance(result, list):
             # Just show the last one if it's a list fallback
            QuestionAnswerReport(result[-1] if result else {}, pdf_bytes)
        else:
            QuestionAnswerReport(result, pdf_bytes)
        return
    
    qa_pairs = []
    all_analyses = []
    
    results_list = result if isinstance(result, list) else [result]
    
    # Process all results to build Q&A pairs
    for item in results_list:
        user_question = item.get("question", "")
        answer_text = item.get("report", "")
        if user_question and answer_text:
            qa_pairs.append({
                "question": user_question,
                "answer": answer_text,
                "category": "user_query"
            })
            all_analyses.append(item.get("analysis") or {})
    
    # If no Q&A data, show a message
    if not qa_pairs:
        st.info("📋 Analysis completed. Generate comprehensive report below to see detailed findings.")
        return
    
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    
    # Build combined evidence mapping
    evidence_map = []
    for idx, analysis in enumerate(all_analyses):
        items = _build_evidence_map_for_qa(analysis, qa_index=idx)
        evidence_map.extend(items)

    # For backward compatibility, if logic expects overall_risk from single result
    last_risk = (results_list[-1].get("analysis") or {}).get("overall_risk", "unknown")

    html = _render_qa_pdf_split_view(qa_pairs, pdf_b64, evidence_map, {"analysis": {"overall_risk": last_risk}})
    components.html(html, height=800, scrolling=False)


def _build_evidence_map_for_qa(analysis: Dict[str, Any], qa_index: int = 0) -> List[Dict[str, Any]]:
    """Build evidence items tagged for a specific Q&A pair"""
    evidence_items = []
    key_evidence = analysis.get("key_evidence", [])
    
    if isinstance(key_evidence, list):
        for idx, ev in enumerate(key_evidence):
            item_id = f"q{qa_index}-key-{idx}"
            if isinstance(ev, dict):
                evidence_items.append({
                    "id": item_id,
                    "text": ev.get("text", ""),
                    "page": ev.get("page"),
                    "bbox": ev.get("bbox"),
                    "qa_index": qa_index 
                })
            elif isinstance(ev, str):
                evidence_items.append({
                    "id": item_id,
                    "text": ev,
                    "page": None,
                    "bbox": None,
                    "qa_index": qa_index
                })
    return evidence_items


def _extract_qa_pairs(result: Dict[str, Any], user_question: str) -> List[Dict[str, Any]]:
    """Extract Q&A pairs from analysis results"""
    qa_pairs = []
    
    # If there's a user question, make it the primary Q&A
    if user_question:
        # The answer is in the top-level 'report' field
        answer_text = result.get("report", "No analysis report available.")
        qa_pairs.append({
            "question": user_question,
            "answer": answer_text,
            "evidence": [],
            "category": "user_query"
        })
    
    return qa_pairs


def _build_evidence_map(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build evidence items with page numbers and text for highlighting"""
    evidence_items = []
    
    key_evidence = analysis.get("key_evidence", [])
    if isinstance(key_evidence, list):
        for idx, ev in enumerate(key_evidence):
            if isinstance(ev, dict):
                evidence_items.append({
                    "id": f"key-{idx}",
                    "text": ev.get("text", ""),
                    "page": ev.get("page"),
                    "bbox": ev.get("bbox")
                })
            elif isinstance(ev, str):
                evidence_items.append({
                    "id": f"key-{idx}",
                    "text": ev,
                    "page": None,
                    "bbox": None
                })
    
    return evidence_items


def _render_qa_pdf_split_view(qa_pairs: List[Dict], pdf_b64: str, evidence_map: List[Dict], result: Dict) -> str:
    """Generate HTML for split-pane Q&A + PDF view"""
    import json
    
    payload = {
        "qa_pairs": qa_pairs,
        "evidence": evidence_map,
        "pdf_b64": pdf_b64,
        "overall_risk": (result.get("analysis") or {}).get("overall_risk", "unknown")
    }
    
    # Dump JSON and sanitize for HTML script injection
    payload_json = json.dumps(payload, ensure_ascii=False)
    payload_json = (
        payload_json
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
  <style>
    body {{ margin: 0; font-family: "Segoe UI", Arial, sans-serif; background: #f8fafc; }}
    .container {{ display: grid; grid-template-columns: 45% 55%; gap: 16px; height: 780px; padding: 16px; }}
    .qa-pane {{ overflow-y: auto; padding: 16px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    .pdf-pane {{ overflow-y: auto; padding: 16px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    .qa-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px; cursor: pointer; transition: all 0.2s; }}
    .qa-card:hover {{ border-color: #3b82f6; box-shadow: 0 2px 8px rgba(59,130,246,0.15); }}
    .qa-card.active {{ border-color: #2563eb; background: #eff6ff; }}
    .question {{ font-weight: 600; color: #0f172a; margin-bottom: 8px; font-size: 15px; }}
    .answer {{ color: #475569; line-height: 1.6; font-size: 14px; white-space: pre-line; }}
    .pdf-page {{ position: relative; margin: 12px auto; box-shadow: 0 2px 8px rgba(0,0,0,0.08); background: white; }}
    .textLayer {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; }}
    .textLayer span {{ color: transparent; position: absolute; white-space: pre; }}
    .highlight {{ background: rgba(250, 204, 21, 0.5) !important; border-bottom: 2px solid #eab308; }}
    .title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; color: #0f172a; }}
    @media (max-width: 980px) {{ .container {{ grid-template-columns: 1fr; height: auto; }} }}
  </style>
</head>
<body>
  <div class="container">
    <div class="qa-pane">
      <div class="title">📋 Analysis Questions & Answers</div>
      <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        Click any question below to see the evidence highlighted in the document →
      </p>
      <div id="qa-list"></div>
    </div>
    <div class="pdf-pane">
      <div class="title">📄 Original Document</div>
      <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
        ✨ Highlights show the actual clauses used to generate each answer
      </p>
      <div id="pdf-container"></div>
    </div>
  </div>

  <script>
    try {{
        const payload = {payload_json};
        let pdfDoc = null;
        let pageViews = new Map();

        // Check if payload loaded correctly
        if (!payload) throw new Error("Payload is empty");

        function renderQA() {{
          const qaList = document.getElementById('qa-list');
          if (!qaList) return;
          
          const pairs = payload.qa_pairs || [];
          
          if (pairs.length === 0) {{
            qaList.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;">No questions available</div>';
            return;
          }}
          
          qaList.innerHTML = pairs.map((qa, idx) => {{
            const questionEscaped = (qa.question || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            const answerEscaped = (qa.answer || '').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
            return `
              <div class="qa-card" data-qa-id="${{idx}}" onclick="selectQA(${{idx}})">
                <div class="question">❓ ${{questionEscaped}}</div>
                <div class="answer">${{answerEscaped}}</div>
              </div>
            `;
          }}).join('');
        }}

        async function loadPDF() {{
          const container = document.getElementById('pdf-container');
          
          if (!payload.pdf_b64) {{
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: #64748b;">PDF preview unavailable (No Data)</div>';
            return;
          }}

          try {{
            const raw = atob(payload.pdf_b64);
            const bytes = new Uint8Array(raw.length);
            for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);

            // Configure worker
            pdfjsLib.GlobalWorkerOptions.workerSrc = 
              'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            
            pdfDoc = await pdfjsLib.getDocument({{ data: bytes }}).promise;
            container.innerHTML = '';

            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {{
              await renderPage(pageNum);
            }}
          }} catch (err) {{
            console.error(err);
            container.innerHTML = `<div style="color: red; padding: 20px;">Error loading PDF: ${{err.message}}</div>`;
          }}
        }}

        async function renderPage(pageNum) {{
          const page = await pdfDoc.getPage(pageNum);
          const viewport = page.getViewport({{ scale: 1.2 }});

          const pageDiv = document.createElement('div');
          pageDiv.className = 'pdf-page';
          pageDiv.style.width = `${{viewport.width}}px`;
          pageDiv.style.height = `${{viewport.height}}px`;

          const canvas = document.createElement('canvas');
          canvas.height = viewport.height;
          canvas.width = viewport.width;
          pageDiv.appendChild(canvas);

          const textLayer = document.createElement('div');
          textLayer.className = 'textLayer';
          textLayer.style.width = `${{viewport.width}}px`;
          textLayer.style.height = `${{viewport.height}}px`;
          pageDiv.appendChild(textLayer);

          document.getElementById('pdf-container').appendChild(pageDiv);

          await page.render({{ canvasContext: canvas.getContext('2d'), viewport }}).promise;
          const textContent = await page.getTextContent();
          pdfjsLib.renderTextLayer({{ textContent, container: textLayer, viewport, textDivs: [] }});

          pageViews.set(pageNum, {{ container: pageDiv, textLayer }});
        }}

        window.selectQA = function(idx) {{
          document.querySelectorAll('.qa-card').forEach(c => c.classList.remove('active'));
          const activeCard = document.querySelector(`[data-qa-id="${{idx}}"]`);
          if (activeCard) activeCard.classList.add('active');
          
          clearHighlights();
          const qa = payload.qa_pairs[idx];
          const evidence = payload.evidence || [];
          
          // Highlight evidence text in PDF matching this QA index
          evidence.forEach(ev => {{
            if (ev.qa_index === idx && ev.text) highlightText(ev.text);
          }});
          
          // Legacy support (fallback)
          evidence.forEach(ev => {{
            if (ev.qa_index === undefined && ev.text) highlightText(ev.text);
          }});
        }}

        function clearHighlights() {{
          document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
        }}

        function highlightText(text) {{
          if (!text || text.length < 5) return;
          const needle = text.toLowerCase().trim();
          
          pageViews.forEach(view => {{
            view.textLayer.querySelectorAll('span').forEach(span => {{
              const spanText = (span.textContent || '').toLowerCase().trim();
              if (spanText && needle.includes(spanText) && spanText.length > 4) {{
                span.classList.add('highlight');
              }}
            }});
          }});
        }}

        // Initialize
        renderQA();
        loadPDF();

    }} catch (e) {{
        document.body.innerHTML = `<div style="color:red; padding:20px;"><h3>Display Error</h3><pre>${{e.message}}</pre></div>`;
        console.error("Critical component error:", e);
    }}
  </script>
</body>
</html>
"""
