from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch

def build_agent_recommendations_pdf(
    output_path: str,
    contract_name: str,
    recommendations_text: str, 
):
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>Contract:</b> {contract_name}", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    for line in recommendations_text.split('\n'):
        if not line.strip():
            story.append(Spacer(1, 0.1 * inch))
            continue
        
        style = styles["BodyText"]
        if line.isupper():
            style = styles["Heading3"]
            
        story.append(Paragraph(line, style))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    doc.build(story)