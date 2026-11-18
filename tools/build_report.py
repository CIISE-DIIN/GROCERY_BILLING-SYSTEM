"""Generate the assignment PDF from editable Markdown with ReportLab."""
import re
from pathlib import Path
from html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/Grocery_Billing_System_Report.pdf'
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyText2', fontName='Helvetica', fontSize=10, leading=13.5,
                          spaceAfter=7, textColor=colors.HexColor('#20252b')))
styles.add(ParagraphStyle(name='ReportTitle', fontName='Helvetica-Bold', fontSize=27, leading=33,
                          spaceAfter=23, textColor=colors.black))
styles.add(ParagraphStyle(name='ReportH1', fontName='Helvetica-Bold', fontSize=17, leading=22,
                          spaceBefore=10, spaceAfter=13, textColor=colors.black, keepWithNext=True))
styles.add(ParagraphStyle(name='ReportH2', fontName='Helvetica-Bold', fontSize=11.5, leading=16,
                          spaceBefore=8, spaceAfter=7, textColor=colors.black, keepWithNext=True))
styles.add(ParagraphStyle(name='Cell2', fontName='Helvetica', fontSize=8.6, leading=11.5))
styles.add(ParagraphStyle(name='Caption2', fontName='Helvetica-Oblique', fontSize=8.5, leading=12,
                          spaceBefore=6, spaceAfter=13, textColor=colors.HexColor('#475569')))


def para(text, style='BodyText2'):
    return Paragraph(escape(text), styles[style])


def table(rows):
    count = len(rows[0])
    widths = {3: [142, 100, 241], 4: [65, 175, 150, 93], 2: [174, 309]}[count]
    # Requirements need a compact first column and ample explanatory space.
    if count == 3 and rows[0][0] == 'Item or calculation':
        widths = [270, 80, 133]
    if count == 3 and rows[0][0] == 'Module':
        widths = [80, 198, 205]
    if count == 3 and rows[0][0] == 'Test group':
        widths = [93, 45, 345]
    data = [[para(value, 'Cell2') for value in row] for row in rows]
    result = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    commands = [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dce6ef')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d9d9d9')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]
    for n in range(1, len(rows)):
        if n % 2 == 0:
            commands.append(('BACKGROUND', (0, n), (-1, n), colors.HexColor('#f6f8fa')))
    result.setStyle(TableStyle(commands))
    return result


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#64748b'))
    canvas.drawString(56, 28, 'Grocery Billing System | Assignment 2')
    canvas.drawRightString(A4[0] - 56, 28, str(doc.page))
    canvas.restoreState()


def main():
    lines = (ROOT / 'docs/report.md').read_text().splitlines()
    story = []
    index = 0
    first_heading = True
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == '[[PAGE]]':
            story.append(PageBreak())
        elif line.startswith('[[IMAGE:'):
            filename, caption = line[len('[[IMAGE:'):-2].split('|')
            image = Image(str(ROOT / 'docs/screenshots' / filename))
            limit_width = 360 if filename == '05_tests.png' else 483
            scale = min(limit_width / image.imageWidth, 385 / image.imageHeight)
            image.drawWidth = image.imageWidth * scale
            image.drawHeight = image.imageHeight * scale
            image.hAlign = 'LEFT'
            story.append(KeepTogether([Spacer(1, 5), image, para(caption, 'Caption2')]))
        elif line.startswith('|'):
            rows = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                cells = [cell.strip() for cell in lines[index].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', cell) for cell in cells):
                    rows.append(cells)
                index += 1
            story.extend([table(rows), Spacer(1, 12)])
            continue
        elif line.startswith('# '):
            if first_heading:
                story.extend([Spacer(1, 24), para(line[2:], 'ReportTitle')])
                first_heading = False
            else:
                story.append(para(line[2:], 'ReportH1'))
        elif line.startswith('## '):
            story.append(para(line[3:], 'ReportH2'))
        else:
            story.append(para(line))
        index += 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=56, leftMargin=56,
                            topMargin=43, bottomMargin=48,
                            title='Grocery Billing System Technical Report', author='',
                            subject='Python Assignment 2 implementation and computational thinking')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)

if __name__ == '__main__':
    main()
