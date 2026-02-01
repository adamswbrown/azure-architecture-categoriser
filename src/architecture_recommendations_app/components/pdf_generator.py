"""PDF report generator using reportlab with professional styling."""

from io import BytesIO
from datetime import datetime
from typing import Callable

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, Flowable, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.widgets.markers import makeMarker

from architecture_scorer.schema import ScoringResult, ArchitectureRecommendation, ClarificationQuestion
from architecture_recommendations_app.utils.sanitize import validate_url


# Azure brand colors
AZURE_BLUE = HexColor('#0078D4')
AZURE_BLUE_DARK = HexColor('#005A9E')
AZURE_BLUE_LIGHT = HexColor('#DEECF9')
AZURE_GREEN = HexColor('#107C10')
AZURE_GREEN_LIGHT = HexColor('#DFF6DD')
AZURE_YELLOW = HexColor('#FFB900')
AZURE_YELLOW_LIGHT = HexColor('#FFF4CE')
AZURE_RED = HexColor('#D13438')
AZURE_RED_LIGHT = HexColor('#FDE7E9')
LIGHT_GRAY = HexColor('#F5F5F5')
MEDIUM_GRAY = HexColor('#E1E1E1')
DARK_GRAY = HexColor('#333333')
TEXT_GRAY = HexColor('#605E5C')


class ScoreBar(Flowable):
    """A visual progress bar showing match percentage."""

    def __init__(self, score: float, width: float = 3*inch, height: float = 0.25*inch):
        super().__init__()
        self.score = min(max(score, 0), 100)  # Clamp to 0-100
        self.bar_width = width
        self.bar_height = height
        self.width = width
        self.height = height

    def draw(self):
        # Background bar
        self.canv.setFillColor(MEDIUM_GRAY)
        self.canv.roundRect(0, 0, self.bar_width, self.bar_height, 3, fill=1, stroke=0)

        # Score bar with gradient color based on score
        if self.score >= 80:
            fill_color = AZURE_GREEN
        elif self.score >= 60:
            fill_color = AZURE_BLUE
        elif self.score >= 40:
            fill_color = AZURE_YELLOW
        else:
            fill_color = AZURE_RED

        fill_width = (self.score / 100) * self.bar_width
        if fill_width > 0:
            self.canv.setFillColor(fill_color)
            self.canv.roundRect(0, 0, fill_width, self.bar_height, 3, fill=1, stroke=0)

        # Score text
        self.canv.setFillColor(white if self.score > 50 else DARK_GRAY)
        self.canv.setFont('Helvetica-Bold', 10)
        text_x = self.bar_width / 2
        text_y = self.bar_height / 2 - 3
        self.canv.drawCentredString(text_x, text_y, f"{self.score:.0f}%")


class ConfidenceBadge(Flowable):
    """A color-coded confidence level badge."""

    COLORS = {
        'high': (AZURE_GREEN, AZURE_GREEN_LIGHT, 'High'),
        'medium': (AZURE_YELLOW, AZURE_YELLOW_LIGHT, 'Medium'),
        'low': (AZURE_RED, AZURE_RED_LIGHT, 'Low'),
    }

    def __init__(self, level: str, width: float = 1.2*inch, height: float = 0.3*inch):
        super().__init__()
        self.level = level.lower()
        self.badge_width = width
        self.badge_height = height
        self.width = width
        self.height = height

    def draw(self):
        colors = self.COLORS.get(self.level, self.COLORS['medium'])
        border_color, fill_color, label = colors

        # Badge background
        self.canv.setFillColor(fill_color)
        self.canv.setStrokeColor(border_color)
        self.canv.setLineWidth(1.5)
        self.canv.roundRect(0, 0, self.badge_width, self.badge_height, 4, fill=1, stroke=1)

        # Badge text
        self.canv.setFillColor(border_color)
        self.canv.setFont('Helvetica-Bold', 9)
        text_x = self.badge_width / 2
        text_y = self.badge_height / 2 - 3
        self.canv.drawCentredString(text_x, text_y, label.upper())


class SectionDivider(Flowable):
    """A styled section divider line."""

    def __init__(self, width: float = 6.5*inch, color: Color = AZURE_BLUE):
        super().__init__()
        self.line_width = width
        self.line_color = color
        self.width = width
        self.height = 0.15*inch

    def draw(self):
        # Main line
        self.canv.setStrokeColor(self.line_color)
        self.canv.setLineWidth(2)
        self.canv.line(0, 0.075*inch, self.line_width * 0.3, 0.075*inch)

        # Faded extension
        self.canv.setStrokeColor(MEDIUM_GRAY)
        self.canv.setLineWidth(1)
        self.canv.line(self.line_width * 0.3, 0.075*inch, self.line_width, 0.075*inch)


class RecommendationCard(Flowable):
    """A framed card for displaying a recommendation."""

    def __init__(self, content_flowables: list, score: float, rank: int,
                 width: float = 6.5*inch, padding: float = 0.15*inch):
        super().__init__()
        self.content = content_flowables
        self.score = score
        self.rank = rank
        self.card_width = width
        self.padding = padding

        # Calculate height based on content
        self.card_height = self._calculate_height()
        self.width = width
        self.height = self.card_height

    def _calculate_height(self) -> float:
        # Estimate height based on content
        total = self.padding * 2 + 0.4*inch  # Top bar + padding
        for item in self.content:
            if hasattr(item, 'wrap'):
                w, h = item.wrap(self.card_width - self.padding * 2 - 0.3*inch, 1000)
                total += h
            elif hasattr(item, 'height'):
                total += item.height
            else:
                total += 0.2*inch
        return total

    def draw(self):
        # Rank indicator color
        if self.rank == 1:
            accent_color = AZURE_GREEN
        elif self.rank <= 3:
            accent_color = AZURE_BLUE
        else:
            accent_color = TEXT_GRAY

        # Card background
        self.canv.setFillColor(white)
        self.canv.setStrokeColor(MEDIUM_GRAY)
        self.canv.setLineWidth(1)
        self.canv.roundRect(0, 0, self.card_width, self.card_height, 6, fill=1, stroke=1)

        # Left accent bar
        self.canv.setFillColor(accent_color)
        self.canv.roundRect(0, 0, 0.15*inch, self.card_height, 6, fill=1, stroke=0)
        # Cover the right rounded corners of accent
        self.canv.rect(0.1*inch, 0, 0.05*inch, self.card_height, fill=1, stroke=0)

        # Rank badge in top-left
        self.canv.setFillColor(accent_color)
        badge_size = 0.35*inch
        self.canv.circle(0.3*inch, self.card_height - 0.3*inch, badge_size/2, fill=1, stroke=0)
        self.canv.setFillColor(white)
        self.canv.setFont('Helvetica-Bold', 12)
        self.canv.drawCentredString(0.3*inch, self.card_height - 0.34*inch, f"#{self.rank}")


def _header_footer(canvas, doc):
    """Add header and footer to each page."""
    canvas.saveState()

    # Header
    canvas.setFillColor(AZURE_BLUE)
    canvas.rect(0, doc.pagesize[1] - 0.5*inch, doc.pagesize[0], 0.5*inch, fill=1, stroke=0)

    canvas.setFillColor(white)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(0.75*inch, doc.pagesize[1] - 0.32*inch, "Azure Architecture Recommendations")

    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(
        doc.pagesize[0] - 0.75*inch,
        doc.pagesize[1] - 0.32*inch,
        datetime.now().strftime('%Y-%m-%d')
    )

    # Footer
    canvas.setFillColor(LIGHT_GRAY)
    canvas.rect(0, 0, doc.pagesize[0], 0.4*inch, fill=1, stroke=0)

    canvas.setFillColor(TEXT_GRAY)
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(
        doc.pagesize[0] / 2,
        0.15*inch,
        f"Page {doc.page}"
    )

    canvas.drawString(
        0.75*inch,
        0.15*inch,
        "Generated by Azure Architecture Recommender"
    )

    canvas.restoreState()


def _first_page_header_footer(canvas, doc):
    """Add minimal header/footer for cover page."""
    canvas.saveState()

    # Footer only for cover page
    canvas.setFillColor(TEXT_GRAY)
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(
        doc.pagesize[0] / 2,
        0.5*inch,
        "Generated by Azure Architecture Recommender"
    )

    canvas.restoreState()


def generate_pdf_report(
    result: ScoringResult,
    questions: list[ClarificationQuestion] | None = None,
    user_answers: dict[str, str] | None = None
) -> bytes:
    """Generate a professionally styled PDF report from scoring results.

    Args:
        result: The ScoringResult to format as PDF
        questions: Optional list of clarification questions
        user_answers: Optional dictionary of user's answers (question_id -> value)

    Returns:
        PDF file as bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.6 * inch
    )

    # Build story (list of flowables)
    story = []
    styles = _get_custom_styles()

    # === COVER PAGE ===
    story.extend(_build_cover_page(result, styles))
    story.append(PageBreak())

    # === EXECUTIVE SUMMARY ===
    story.extend(_build_executive_summary(result, styles))

    # === USER ANSWERS SECTION ===
    if questions and user_answers:
        story.extend(_build_answers_section(questions, user_answers, styles))

    # === RECOMMENDATIONS ===
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Detailed Recommendations", styles['SectionTitle']))
    story.append(SectionDivider())
    story.append(Spacer(1, 0.2 * inch))

    for i, rec in enumerate(result.recommendations, 1):
        story.extend(_build_recommendation_section(rec, i, styles))

    # Build PDF with header/footer
    doc.build(
        story,
        onFirstPage=_first_page_header_footer,
        onLaterPages=_header_footer
    )
    buffer.seek(0)
    return buffer.getvalue()


def _build_cover_page(result: ScoringResult, styles) -> list:
    """Build the cover page content."""
    elements = []

    elements.append(Spacer(1, 1.5 * inch))

    # Azure logo placeholder (blue rectangle with text)
    logo_table = Table(
        [[Paragraph("AZURE", styles['LogoText'])]],
        colWidths=[2*inch],
        rowHeights=[0.5*inch]
    )
    logo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), AZURE_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(logo_table)

    elements.append(Spacer(1, 0.5 * inch))

    # Main title
    elements.append(Paragraph("Architecture", styles['CoverTitle']))
    elements.append(Paragraph("Recommendations", styles['CoverTitle']))

    elements.append(Spacer(1, 0.3 * inch))

    # Divider line
    elements.append(HRFlowable(
        width="40%",
        thickness=3,
        color=AZURE_BLUE,
        spaceBefore=10,
        spaceAfter=10
    ))

    elements.append(Spacer(1, 0.3 * inch))

    # Application name
    elements.append(Paragraph(
        f"<b>Application:</b> {result.application_name}",
        styles['CoverSubtitle']
    ))

    elements.append(Spacer(1, 0.8 * inch))

    # Summary stats in a styled box
    summary = result.summary
    stats_data = [
        ["PRIMARY RECOMMENDATION", summary.primary_recommendation or "Evaluation Required"],
        ["CONFIDENCE LEVEL", summary.confidence_level.upper()],
        ["OPTIONS EVALUATED", f"{result.catalog_architecture_count} architectures"],
        ["TOP MATCHES", f"{len(result.recommendations)} recommendations"],
    ]

    stats_table = Table(stats_data, colWidths=[2.5*inch, 3.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), AZURE_BLUE_LIGHT),
        ('BACKGROUND', (1, 0), (1, -1), white),
        ('TEXTCOLOR', (0, 0), (0, -1), AZURE_BLUE_DARK),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK_GRAY),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, AZURE_BLUE),
        ('LINEAFTER', (0, 0), (0, -1), 1, AZURE_BLUE),
    ]))
    elements.append(stats_table)

    elements.append(Spacer(1, 1 * inch))

    # Date
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles['CoverDate']
    ))

    return elements


def _build_executive_summary(result: ScoringResult, styles) -> list:
    """Build the executive summary section."""
    elements = []

    elements.append(Paragraph("Executive Summary", styles['SectionTitle']))
    elements.append(SectionDivider())
    elements.append(Spacer(1, 0.15 * inch))

    summary = result.summary

    # Confidence badge and primary recommendation
    conf_table_data = [[
        Paragraph("Confidence Level:", styles['LabelText']),
        ConfidenceBadge(summary.confidence_level),
        Spacer(0.5*inch, 0),
        Paragraph("Primary Match:", styles['LabelText']),
        Paragraph(f"<b>{summary.primary_recommendation or 'N/A'}</b>", styles['ValueText'])
    ]]

    conf_table = Table(conf_table_data, colWidths=[1.2*inch, 1.3*inch, 0.3*inch, 1.1*inch, 2.5*inch])
    conf_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(conf_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Two-column layout for drivers and risks
    left_content = []
    right_content = []

    # Key drivers
    if summary.key_drivers:
        left_content.append(Paragraph("Key Drivers", styles['SubsectionTitle']))
        for driver in summary.key_drivers[:5]:
            left_content.append(Paragraph(f"✓ {driver}", styles['CheckItem']))

    # Key risks/considerations
    if summary.key_risks:
        right_content.append(Paragraph("Key Considerations", styles['SubsectionTitle']))
        for risk in summary.key_risks[:5]:
            right_content.append(Paragraph(f"⚠ {risk}", styles['WarningItem']))

    if left_content or right_content:
        # Pad to equal length
        while len(left_content) < len(right_content):
            left_content.append(Spacer(1, 0.15*inch))
        while len(right_content) < len(left_content):
            right_content.append(Spacer(1, 0.15*inch))

        two_col_data = [[left_content, right_content]]
        two_col_table = Table(two_col_data, colWidths=[3.25*inch, 3.25*inch])
        two_col_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(two_col_table)

    return elements


def _build_answers_section(
    questions: list[ClarificationQuestion],
    user_answers: dict[str, str],
    styles
) -> list:
    """Build the user answers section."""
    elements = []

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Assessment Inputs", styles['SectionTitle']))
    elements.append(SectionDivider())
    elements.append(Spacer(1, 0.15 * inch))

    # Build answer pairs
    answer_data = []
    for q in questions:
        if q.question_id in user_answers:
            answer_value = user_answers[q.question_id]
            answer_label = answer_value
            for opt in q.options:
                if opt.value == answer_value:
                    answer_label = opt.label
                    break
            answer_data.append([q.question_text, answer_label])

    if answer_data:
        answer_table = Table(answer_data, colWidths=[3.5*inch, 3*inch])
        answer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), DARK_GRAY),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, LIGHT_GRAY]),
        ]))
        elements.append(answer_table)

    return elements


def _build_recommendation_section(rec: ArchitectureRecommendation, index: int, styles) -> list:
    """Build a recommendation section with card styling."""
    elements = []

    # Card header with rank and score
    header_data = [[
        Paragraph(f"#{index}", styles['RankBadge']),
        Paragraph(rec.name, styles['CardTitle']),
        ScoreBar(rec.likelihood_score, width=2*inch, height=0.22*inch)
    ]]

    header_table = Table(header_data, colWidths=[0.5*inch, 4*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, 0), AZURE_BLUE if index == 1 else (AZURE_GREEN if index <= 3 else TEXT_GRAY)),
        ('TEXTCOLOR', (0, 0), (0, 0), white),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
    ]))
    elements.append(header_table)

    # Pattern and quality badges
    quality_label = rec.catalog_quality.value.replace('_', ' ').title()
    quality_color = AZURE_GREEN if 'curated' in quality_label.lower() else (
        AZURE_BLUE if 'enriched' in quality_label.lower() else TEXT_GRAY
    )

    elements.append(Spacer(1, 0.08 * inch))
    elements.append(Paragraph(
        f"<font color='#605E5C'>Pattern: {rec.pattern_name} | Quality: </font>"
        f"<font color='{quality_color.hexval()}'><b>{quality_label}</b></font>",
        styles['MetaText']
    ))

    # Description
    if rec.description:
        elements.append(Spacer(1, 0.1 * inch))
        desc = rec.description[:400] + "..." if len(rec.description) > 400 else rec.description
        elements.append(Paragraph(desc, styles['Normal']))

    # Try to include diagram image (with SSRF protection)
    if rec.diagram_url:
        url_valid, url_error = validate_url(rec.diagram_url, allow_http=True)
        if url_valid:
            try:
                import requests
                response = requests.get(rec.diagram_url, timeout=10)
                if response.ok:
                    img_buffer = BytesIO(response.content)
                    if rec.diagram_url.lower().endswith('.svg'):
                        from svglib.svglib import svg2rlg
                        drawing = svg2rlg(img_buffer)
                        if drawing:
                            target_width = 5 * inch
                            scale = target_width / drawing.width if drawing.width > 0 else 1
                            drawing.width = target_width
                            drawing.height = drawing.height * scale
                            drawing.scale(scale, scale)
                            elements.append(Spacer(1, 0.1 * inch))
                            elements.append(drawing)
                    else:
                        img = Image(img_buffer, width=5 * inch, height=2.5 * inch)
                        img.hAlign = 'CENTER'
                        elements.append(Spacer(1, 0.1 * inch))
                        elements.append(img)
            except Exception:
                pass

    elements.append(Spacer(1, 0.1 * inch))

    # Two-column layout for fit and challenges
    left_col = []
    right_col = []

    if rec.fit_summary:
        left_col.append(Paragraph("Why It Fits", styles['SubsectionTitle']))
        for fit in rec.fit_summary[:4]:
            left_col.append(Paragraph(f"✓ {fit}", styles['CheckItem']))

    if rec.struggle_summary:
        right_col.append(Paragraph("Potential Challenges", styles['SubsectionTitle']))
        for struggle in rec.struggle_summary[:4]:
            right_col.append(Paragraph(f"⚠ {struggle}", styles['WarningItem']))

    if left_col or right_col:
        while len(left_col) < len(right_col):
            left_col.append(Spacer(1, 0.12*inch))
        while len(right_col) < len(left_col):
            right_col.append(Spacer(1, 0.12*inch))

        fit_table = Table([[left_col, right_col]], colWidths=[3.25*inch, 3.25*inch])
        fit_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(fit_table)

    # Core services
    if rec.core_services:
        elements.append(Spacer(1, 0.1 * inch))
        services = ", ".join(rec.core_services[:8])
        elements.append(Paragraph(
            f"<b>Core Azure Services:</b> {services}",
            styles['MetaText']
        ))

    # Learn URL
    if rec.learn_url:
        elements.append(Spacer(1, 0.05 * inch))
        elements.append(Paragraph(
            f"<link href='{rec.learn_url}'><font color='#0078D4'>Learn more →</font></link>",
            styles['MetaText']
        ))

    # Card bottom border/spacer
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=MEDIUM_GRAY, spaceBefore=5, spaceAfter=15))

    return elements


def _get_custom_styles():
    """Create custom paragraph styles for the report."""
    styles = getSampleStyleSheet()

    # Cover page styles
    styles.add(ParagraphStyle(
        'CoverTitle',
        parent=styles['Title'],
        textColor=AZURE_BLUE_DARK,
        fontSize=36,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=0,
        leading=42
    ))

    styles.add(ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        textColor=DARK_GRAY,
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        'CoverDate',
        parent=styles['Normal'],
        textColor=TEXT_GRAY,
        fontSize=11,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        'LogoText',
        parent=styles['Normal'],
        textColor=white,
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    ))

    # Section styles
    styles.add(ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading1'],
        textColor=AZURE_BLUE_DARK,
        fontSize=18,
        fontName='Helvetica-Bold',
        spaceBefore=20,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        'SubsectionTitle',
        parent=styles['Heading2'],
        textColor=DARK_GRAY,
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4
    ))

    # Card styles
    styles.add(ParagraphStyle(
        'CardTitle',
        parent=styles['Heading2'],
        textColor=DARK_GRAY,
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceBefore=0,
        spaceAfter=0
    ))

    styles.add(ParagraphStyle(
        'RankBadge',
        parent=styles['Normal'],
        textColor=white,
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    ))

    # Content styles
    styles.add(ParagraphStyle(
        'LabelText',
        parent=styles['Normal'],
        textColor=TEXT_GRAY,
        fontSize=10
    ))

    styles.add(ParagraphStyle(
        'ValueText',
        parent=styles['Normal'],
        textColor=DARK_GRAY,
        fontSize=10
    ))

    styles.add(ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        textColor=TEXT_GRAY,
        fontSize=9
    ))

    styles.add(ParagraphStyle(
        'CheckItem',
        parent=styles['Normal'],
        textColor=AZURE_GREEN,
        fontSize=10,
        leftIndent=10,
        spaceBefore=2,
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        'WarningItem',
        parent=styles['Normal'],
        textColor=HexColor('#B7791F'),  # Darker yellow/orange for readability
        fontSize=10,
        leftIndent=10,
        spaceBefore=2,
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        leftIndent=20,
        spaceBefore=2,
        spaceAfter=2
    ))

    return styles
