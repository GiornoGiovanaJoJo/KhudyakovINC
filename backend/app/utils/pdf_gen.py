import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

# Try to find a Unicode font for Cyrillic support
# In a real environment, we'd bundle a font file. 
# For now, we'll try to find a common system font or just use standard ones (which might fail for Cyrillic)
# Let's assume we can use a DejaVu or similar if available, or just stick to basics and warn.
# Since we are on Windows, we might find Arial or similar.
font_path = "C:\\Windows\\Fonts\\arial.ttf"
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('Arial', font_path))
    FONT_NAME = 'Arial'
else:
    FONT_NAME = 'Helvetica'


def generate_proposal_pdf(lead_name: str, ai_summary: str) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=24,
        textColor=colors.HexColor("#6366f1"),
        spaceAfter=30
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=12,
        leading=16,
        spaceAfter=12
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=20,
        spaceAfter=10
    )

    elements = []

    # Header
    elements.append(Paragraph("KHUDYAKOV INC.", title_style))
    elements.append(Paragraph(f"Предварительное коммерческое предложение", header_style))
    elements.append(Spacer(1, 12))
    
    # Client Info
    elements.append(Paragraph(f"Для клиента: <b>{lead_name}</b>", body_style))
    elements.append(Paragraph(f"Дата: {os.popen('date /t').read().strip()}", body_style))
    elements.append(Spacer(1, 24))

    # Project Understanding
    elements.append(Paragraph("Ваш запрос и наше понимание задачи:", header_style))
    
    # Process AI summary to look better (split by lines/points)
    summary_lines = ai_summary.split('\n')
    for line in summary_lines:
        if line.strip():
            elements.append(Paragraph(line.strip(), body_style))

    elements.append(Spacer(1, 12))

    # Standard "Why Us" Section
    elements.append(Paragraph("Почему выбирают нас?", header_style))
    elements.append(Paragraph("• Комплексный подход: от аналитики до запуска.", body_style))
    elements.append(Paragraph("• Современный стек технологий (Vue 3, Python, FastAPI).", body_style))
    elements.append(Paragraph("• Прозрачные сроки и фиксированные этапы оплаты.", body_style))
    
    elements.append(Spacer(1, 24))

    # Call to Action
    elements.append(Paragraph("Следующие шаги:", header_style))
    elements.append(Paragraph("1. Детальный созвон для уточнения ТЗ.", body_style))
    elements.append(Paragraph("2. Оценка точной стоимости и сроков.", body_style))
    elements.append(Paragraph("3. Подписание договора и старт работ.", body_style))

    elements.append(Spacer(1, 40))
    elements.append(Paragraph("С уважением,<br/>Команда Khudyakov Inc.<br/>https://khudyakov.inc", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
