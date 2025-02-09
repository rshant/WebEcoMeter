from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io
import datetime

def create_pdf_report(metrics: dict, url: str, monthly_visits: int) -> bytes:
    """Generate a detailed PDF report of the carbon footprint analysis."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        spaceAfter=30,
        fontSize=24,
        textColor=colors.HexColor('#2ECC71')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        spaceAfter=12,
        fontSize=14,
        textColor=colors.HexColor('#2C3E50')
    )

    # Title
    story.append(Paragraph("Website Carbon Footprint Report", title_style))
    story.append(Spacer(1, 20))

    # Basic Information
    story.append(Paragraph("Analysis Details", heading_style))
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    info_data = [
        ["Website URL:", url],
        ["Analysis Date:", current_date],
        ["Monthly Visits:", f"{monthly_visits:,}"]
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F4F8')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # Metrics
    story.append(Paragraph("Carbon Footprint Metrics", heading_style))
    metrics_data = [
        ["Metric", "Value", "Impact Level"],
        ["Page Size", f"{metrics['page_size_kb']:.2f} KB", "Information"],
        ["Annual Energy Consumption", f"{metrics['annual_energy_kwh']:.2f} kWh", "Medium"],
        ["Annual Carbon Emissions", f"{metrics['annual_carbon_kg']:.2f} kg CO2", "High"],
        ["Trees Needed for Offset", f"{metrics['trees_needed']} trees", "Action Required"]
    ]
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    metrics_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 20))

    # Calculation Methodology
    story.append(Paragraph("Calculation Methodology", heading_style))
    methodology_text = """
    Our carbon footprint calculations are based on industry-standard methodologies and empirical research. Here's how we calculate each metric:

    1. Data Transfer Calculation:
    • We measure the total page size including all resources (HTML, CSS, JavaScript, images, etc.)
    • Monthly data transfer = Page Size × Monthly Visits
    • Annual data transfer = Monthly data transfer × 12 months

    2. Energy Consumption:
    • Energy intensity of web data = 1.805 kWh/GB (kilowatt-hours per gigabyte)
    • Annual energy consumption = Annual data transfer × Energy intensity

    3. Carbon Emissions:
    • Carbon intensity of electricity = 442 g CO2/kWh (global average)
    • Annual carbon emissions = Annual energy consumption × Carbon intensity

    4. Tree Offset Calculation:
    • Average CO2 absorption per tree = 21 kg CO2 per year
    • Trees needed = Annual carbon emissions ÷ CO2 absorption per tree

    Note: These calculations represent estimates based on global averages. Actual values may vary depending on:
    • Data center energy sources
    • Server locations
    • Network infrastructure
    • User device energy efficiency
    """
    story.append(Paragraph(methodology_text, styles['Normal']))
    story.append(Spacer(1, 20))

    # Recommendations
    story.append(Paragraph("Recommendations for Improvement", heading_style))
    recommendations = [
        "1. Optimize images and use modern formats (WebP)",
        "2. Implement efficient caching strategies",
        "3. Minimize JavaScript and CSS files",
        "4. Use a green hosting provider",
        "5. Enable compression (GZIP/Brotli)"
    ]
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
        story.append(Spacer(1, 6))

    # Disclaimer
    story.append(Spacer(1, 30))
    disclaimer = """Note: This report provides estimates based on industry standard calculations. 
    Actual environmental impact may vary depending on specific circumstances and data center configurations."""
    story.append(Paragraph(disclaimer, styles['Italic']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()