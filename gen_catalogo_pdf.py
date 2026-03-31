#!/usr/bin/env python3
"""
Genera PDF del Catálogo de Efectos CDP desde el markdown.
Usa reportlab para formato profesional con tablas.
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Colors ──
ACCENT = HexColor("#7c6ff0")
ACCENT_LIGHT = HexColor("#e8e5fc")
DARK_BG = HexColor("#2d2d3d")
HEADER_BG = HexColor("#3d3d5c")
TABLE_HEADER = HexColor("#4a4a6a")
TABLE_ROW_ALT = HexColor("#f5f4ff")
TABLE_ROW = HexColor("#ffffff")
BORDER_COLOR = HexColor("#c8c5e8")
TEXT_DARK = HexColor("#1a1a2e")
TEXT_GRAY = HexColor("#555577")
CHECKBOX_BG = HexColor("#f0eeff")
WAV_COLOR = HexColor("#2e7d32")
SPECTRAL_COLOR = HexColor("#c62828")
SYNTH_COLOR = HexColor("#1565c0")
SECTION_BG = HexColor("#eae7ff")

MD_PATH = Path(__file__).parent / "docs" / "04_CATALOGO_EFECTOS_CDP.md"
OUT_PATH = Path(__file__).parent / "Catalogo_Efectos_CDP_v02.pdf"


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'DocTitle', parent=styles['Title'],
        fontSize=22, leading=28, textColor=ACCENT,
        spaceAfter=4*mm, alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=TEXT_GRAY,
        spaceAfter=6*mm, alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    ))
    styles.add(ParagraphStyle(
        'SectionH', parent=styles['Heading1'],
        fontSize=16, leading=20, textColor=white,
        spaceBefore=8*mm, spaceAfter=4*mm,
        fontName='Helvetica-Bold', backColor=ACCENT,
        borderPadding=(3*mm, 4*mm, 3*mm, 4*mm),
        borderRadius=2,
    ))
    styles.add(ParagraphStyle(
        'EffectTitle', parent=styles['Heading2'],
        fontSize=12, leading=16, textColor=ACCENT,
        spaceBefore=5*mm, spaceAfter=2*mm,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'EffectType', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=TEXT_GRAY,
        spaceAfter=2*mm, fontName='Helvetica-Oblique'
    ))
    styles.add(ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=TEXT_DARK,
        spaceAfter=2*mm, fontName='Helvetica',
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        'SubMode', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=TEXT_DARK,
        spaceBefore=2*mm, spaceAfter=1*mm,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontSize=8, leading=10, textColor=TEXT_DARK,
        fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontSize=8, leading=10, textColor=white,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'Legend', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=TEXT_DARK,
        fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        'Blockquote', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=TEXT_GRAY,
        fontName='Helvetica-Oblique',
        leftIndent=8*mm, spaceAfter=2*mm,
    ))
    return styles


def parse_markdown(md_text):
    """Parse the markdown into structured sections."""
    sections = []
    current_section = None
    current_effect = None
    current_sub = None
    lines = md_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Section header (## N. TITLE)
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            if title == 'Leyenda':
                current_section = {'title': 'Leyenda', 'type': 'legend', 'content': []}
                sections.append(current_section)
            elif re.match(r'\d+\.', title):
                current_section = {'title': title, 'type': 'section', 'effects': []}
                sections.append(current_section)
                current_effect = None
            i += 1
            continue

        # Effect header (### N.N name)
        if stripped.startswith('### ') and current_section and current_section['type'] == 'section':
            effect_title = stripped[4:].strip()
            current_effect = {
                'title': effect_title,
                'tipo': '',
                'integrar': True,
                'content': [],
                'tables': [],
                'submodes': [],
            }
            current_section['effects'].append(current_effect)
            current_sub = None
            i += 1
            continue

        # Effect type line
        if current_effect and stripped.startswith('- **Tipo:**'):
            current_effect['tipo'] = stripped.replace('- **Tipo:**', '').strip()
            i += 1
            continue

        # Integrar line (skip, we show checkbox)
        if current_effect and stripped.startswith('- **Integrar:**'):
            i += 1
            continue

        # Sub-mode header (#### or **Modo)
        if current_effect and (stripped.startswith('####') or stripped.startswith('**Modo')):
            sub_title = stripped.lstrip('#').strip()
            sub_title = sub_title.replace('**', '')
            current_sub = sub_title
            current_effect['content'].append(('subtitle', sub_title))
            i += 1
            continue

        # Table detection
        if current_effect and stripped.startswith('|') and '|' in stripped[1:]:
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                # Skip separator rows
                if re.match(r'\|[\s\-:|]+\|', row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.split('|')[1:-1]]
                table_rows.append(cells)
                i += 1
            if table_rows:
                current_effect['tables'].append(table_rows)
            continue

        # Blockquote
        if current_effect and stripped.startswith('>'):
            text = stripped[1:].strip()
            current_effect['content'].append(('quote', text))
            i += 1
            continue

        # Legend content
        if current_section and current_section['type'] == 'legend' and stripped.startswith('|'):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                if re.match(r'\|[\s\-:|]+\|', row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.split('|')[1:-1]]
                table_rows.append(cells)
                i += 1
            if table_rows:
                current_section['content'] = table_rows
            continue

        # Regular text for section-level (resumen table)
        if current_section and current_section.get('type') == 'section' and stripped.startswith('|') and not current_effect:
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                if re.match(r'\|[\s\-:|]+\|', row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.split('|')[1:-1]]
                table_rows.append(cells)
                i += 1
            # Treat as a pseudo-effect with just a table
            pseudo = {
                'title': '',
                'tipo': '',
                'integrar': False,
                'content': [],
                'tables': [table_rows],
                'submodes': [],
            }
            current_section['effects'].append(pseudo)
            continue

        i += 1

    return sections


def type_color(tipo):
    t = tipo.upper()
    if 'SPECTRAL' in t:
        return SPECTRAL_COLOR
    elif 'SYNTH' in t:
        return SYNTH_COLOR
    else:
        return WAV_COLOR


def escape_xml(text):
    """Escape text for reportlab XML paragraphs."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('**', '')
    return text


def make_table(rows, styles, col_widths=None):
    """Create a styled reportlab table from parsed rows."""
    if not rows:
        return None

    s = styles
    ncols = max(len(r) for r in rows)

    # Normalize row lengths
    norm_rows = []
    for r in rows:
        while len(r) < ncols:
            r.append('')
        norm_rows.append(r)

    # Build table data with Paragraphs
    header = norm_rows[0]
    data = [[Paragraph(escape_xml(c), s['TableHeader']) for c in header]]
    for row in norm_rows[1:]:
        data.append([Paragraph(escape_xml(c), s['TableCell']) for c in row])

    if col_widths is None:
        avail = 170 * mm
        col_widths = [avail / ncols] * ncols

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 2*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2*mm),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [TABLE_ROW, TABLE_ROW_ALT]),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def compute_col_widths(rows, avail=170*mm):
    """Simple heuristic for column widths based on content."""
    if not rows:
        return None
    ncols = max(len(r) for r in rows)
    if ncols <= 2:
        return [avail * 0.3, avail * 0.7]
    elif ncols == 3:
        return [avail * 0.25, avail * 0.35, avail * 0.4]
    elif ncols == 4:
        return [avail * 0.22, avail * 0.18, avail * 0.08, avail * 0.52]
    elif ncols == 5:
        return [avail * 0.18, avail * 0.17, avail * 0.07, avail * 0.07, avail * 0.51]
    else:
        return [avail / ncols] * ncols


def build_pdf(sections, styles):
    elements = []

    # Title page
    elements.append(Spacer(1, 30*mm))
    elements.append(Paragraph(
        "Catálogo de Efectos CDP",
        styles['DocTitle']
    ))
    elements.append(Paragraph(
        "para Integración en Aleatoric Composer v0.2",
        styles['DocSubtitle']
    ))
    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph(
        "CDP Release 8 — Trevor Wishart et al.",
        styles['DocSubtitle']
    ))
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="60%", thickness=1, color=ACCENT, spaceAfter=4*mm))
    elements.append(Spacer(1, 4*mm))

    # Instructions
    instructions = [
        "Marca con <b>[X]</b> los efectos que quieras integrar en v0.2.",
        "Los marcados como <b><font color='#2e7d32'>WAV</font></b> trabajan directamente sobre archivos de audio.",
        "Los marcados como <b><font color='#c62828'>SPECTRAL</font></b> requieren pipeline specanal → proceso → pvoc.",
        "Los marcados como <b><font color='#1565c0'>SYNTH</font></b> generan audio desde cero.",
    ]
    for instr in instructions:
        elements.append(Paragraph(f"• {instr}", styles['Body']))
    elements.append(Spacer(1, 6*mm))

    for section in sections:
        if section['type'] == 'legend':
            elements.append(Paragraph("Leyenda", styles['SectionH']))
            if section['content']:
                t = make_table(section['content'], styles,
                               col_widths=[35*mm, 135*mm])
                if t:
                    elements.append(t)
                    elements.append(Spacer(1, 4*mm))
            continue

        # Section header
        elements.append(PageBreak())
        elements.append(Paragraph(section['title'], styles['SectionH']))
        elements.append(Spacer(1, 3*mm))

        for effect in section.get('effects', []):
            if not effect['title']:
                # Pseudo-effect (section-level table like resumen)
                for tbl_rows in effect['tables']:
                    cw = compute_col_widths(tbl_rows)
                    t = make_table(tbl_rows, styles, col_widths=cw)
                    if t:
                        elements.append(t)
                        elements.append(Spacer(1, 3*mm))
                continue

            # Effect block
            block = []

            # Title with checkbox
            tipo = effect['tipo']
            tc = type_color(tipo)
            tipo_tag = f"<font color='{tc.hexval()}'><b>{tipo}</b></font>" if tipo else ""
            checkbox = "☐"

            title_text = f"{checkbox}  {effect['title']}"
            if tipo_tag:
                title_text += f"  —  {tipo_tag}"

            block.append(Paragraph(title_text, styles['EffectTitle']))

            # Content items
            for ctype, ctext in effect['content']:
                if ctype == 'subtitle':
                    block.append(Paragraph(escape_xml(ctext), styles['SubMode']))
                elif ctype == 'quote':
                    block.append(Paragraph(escape_xml(ctext), styles['Blockquote']))

            # Tables
            for tbl_rows in effect['tables']:
                cw = compute_col_widths(tbl_rows)
                t = make_table(tbl_rows, styles, col_widths=cw)
                if t:
                    block.append(t)

            block.append(Spacer(1, 2*mm))
            block.append(HRFlowable(width="100%", thickness=0.3, color=BORDER_COLOR, spaceAfter=1*mm))

            elements.append(KeepTogether(block))

    return elements


def header_footer(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFillColor(ACCENT)
    canvas.rect(0, A4[1] - 12*mm, A4[0], 12*mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(15*mm, A4[1] - 8*mm, "Catálogo CDP — Aleatoric Composer v0.2")
    canvas.drawRightString(A4[0] - 15*mm, A4[1] - 8*mm, f"Pág. {doc.page}")

    # Footer
    canvas.setFillColor(TEXT_GRAY)
    canvas.setFont('Helvetica', 7)
    canvas.drawCentredString(A4[0] / 2, 8*mm, "CDP Release 8 — Trevor Wishart et al. — Auditoría de efectos para integración")
    canvas.restoreState()


def main():
    md_text = MD_PATH.read_text(encoding='utf-8')
    sections = parse_markdown(md_text)
    styles = create_styles()

    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        topMargin=18*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm,
        title="Catálogo de Efectos CDP para Aleatoric Composer v0.2",
        author="Aleatoric Composer Team",
    )

    elements = build_pdf(sections, styles)
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"PDF generado: {OUT_PATH}")
    print(f"  Secciones: {len(sections)}")
    print(f"  Tamaño: {OUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == '__main__':
    main()
