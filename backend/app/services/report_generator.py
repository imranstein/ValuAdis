"""Report generation service for compliance reports"""

from sqlalchemy.orm import Session
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
import logging

from app.data.models.vehicle_valuation import VehicleValuation
from app.data.models.vehicle import Vehicle
from app.data.models.property import Property

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate compliance reports for valuations"""

    def generate_compliance_report(self, valuation_id: int, db: Session) -> bytes:
        """
        Generate a compliance report PDF for a valuation

        Args:
            valuation_id: ID of the valuation to report on
            db: Database session

        Returns:
            PDF file as bytes
        """
        # Fetch valuation data
        valuation = db.query(VehicleValuation).filter(
            VehicleValuation.id == valuation_id
        ).first()

        if not valuation:
            raise ValueError(f"Valuation {valuation_id} not found")

        # Fetch related vehicle and property
        vehicle = db.query(Vehicle).filter(Vehicle.id == valuation.vehicle_id).first()
        property_record = db.query(Property).filter(Property.id == vehicle.property_id).first() if vehicle else None

        # Create PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#059669'),
            spaceAfter=30,
            alignment=1  # Center
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#047857'),
            spaceAfter=12
        )

        # Build document content
        content = []

        # Title
        content.append(Paragraph("COMPLIANCE REPORT", title_style))
        content.append(Spacer(1, 0.2*inch))

        # Report info
        content.append(Paragraph(f"Report Date: {datetime.utcnow().strftime('%Y-%m-%d')}", styles['Normal']))
        content.append(Paragraph(f"Valuation ID: {valuation_id}", styles['Normal']))
        content.append(Spacer(1, 0.3*inch))

        # Vehicle Information
        content.append(Paragraph("VEHICLE INFORMATION", heading_style))
        vehicle_data = [
            ["Field", "Value"],
            ["VIN", vehicle.vin if vehicle else "N/A"],
            ["Make", vehicle.make if vehicle else "N/A"],
            ["Model", vehicle.model if vehicle else "N/A"],
            ["Year", str(vehicle.year) if vehicle else "N/A"],
            ["Plate Number", vehicle.plate_number if vehicle else "N/A"],
        ]
        vehicle_table = Table(vehicle_data, colWidths=[2*inch, 3*inch])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        content.append(vehicle_table)
        content.append(Spacer(1, 0.3*inch))

        # Valuation Information
        content.append(Paragraph("VALUATION DETAILS", heading_style))
        valuation_data = [
            ["Metric", "Value (ETB)"],
            ["Base Value", f"{valuation.base_value:,.2f}"],
            ["Market Value", f"{valuation.market_value:,.2f}"],
            ["Taxable Value", f"{valuation.taxable_value:,.2f}"],
            ["Confidence Score", f"{valuation.confidence_score:.1%}"],
        ]
        valuation_table = Table(valuation_data, colWidths=[2*inch, 3*inch])
        valuation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        content.append(valuation_table)
        content.append(Spacer(1, 0.3*inch))

        # Ethiopian Compliance Factors
        content.append(Paragraph("ETHIOPIAN COMPLIANCE FACTORS", heading_style))
        ethiopian_data = [
            ["Factor", "Value"],
            ["Regional Multiplier", f"{valuation.regional_multiplier:.2f}"],
            ["Import Year Adjustment", f"{valuation.import_year_adjustment:.2f}"],
            ["Customs Duty Factor", f"{valuation.customs_duty_factor:.2f}"],
            ["Make Reliability", f"{valuation.make_reliability:.2f}"],
            ["Fuel Type Adjustment", f"{valuation.fuel_type_adjustment:.2f}"],
        ]
        ethiopian_table = Table(ethiopian_data, colWidths=[2*inch, 3*inch])
        ethiopian_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        content.append(ethiopian_table)

        # Build PDF
        doc.build(content)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()


# Singleton instance
report_generator = ReportGenerator()
