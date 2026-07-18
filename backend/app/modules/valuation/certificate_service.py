"""
Certificate Service

Generates Proclamation 1365/2025-compliant PDF valuation certificates
using ReportLab.  Each certificate contains:
  • Property & valuation details
  • Market value / taxable value breakdown
  • QR code linking to the public verification URL
  • Official header / footer matching Ethiopian government formatting guidelines
"""

import io
import uuid
import qrcode
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Brand colours (Ethiopian flag palette + professional accents)
# ---------------------------------------------------------------------------
_GREEN  = colors.HexColor("#078160")   # Primary green
_GOLD   = colors.HexColor("#FFCB00")   # Ethiopian flag gold
_NAVY   = colors.HexColor("#1E3A8A")   # Deep navy
_LIGHT  = colors.HexColor("#F3F4F6")   # Table row background
_BORDER = colors.HexColor("#D1D5DB")   # Subtle border


class CertificateService:
    """Generates PDF valuation certificates compliant with Proclamation 1365/2025."""

    # Verification base URL (override per deployment)
    VERIFY_BASE_URL: str = "https://valuadis.et/verify"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_certificate(
        self,
        valuation: Dict[str, Any],
        property_data: Dict[str, Any],
        owner_name: str,
        certificate_number: Optional[str] = None,
    ) -> bytes:
        """
        Generate a PDF certificate.

        Args:
            valuation:          Valuation record dict (id, market_value, taxable_value, …).
            property_data:      Property record dict (address, municipality, area_sqm, …).
            owner_name:         Full name of the registered property owner.
            certificate_number: Human-readable cert ID; auto-generated if None.

        Returns:
            Raw PDF bytes ready to stream as a response or save to disk.
        """
        if certificate_number is None:
            certificate_number = self._generate_certificate_number(valuation.get("id"))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2 * cm,
            title=f"Property Valuation Certificate – {certificate_number}",
            author="ValuAdis – Ethiopian Property Valuation Platform",
            subject="Proclamation 1365/2025 Valuation Certificate",
        )

        styles  = self._build_styles()
        story   = self._build_story(
            styles, valuation, property_data, owner_name, certificate_number
        )

        doc.build(story, onFirstPage=self._add_page_border, onLaterPages=self._add_page_border)
        return buffer.getvalue()

    def generate_rent_certificate(
        self,
        valuation: Dict[str, Any],
        property_data: Dict[str, Any],
        owner_name: str,
        rent_result: Dict[str, Any],
        certificate_number: Optional[str] = None,
    ) -> bytes:
        """
        Generate a rent-valuation certificate PDF: property summary,
        suggested monthly rent, the published ±10% band, confidence, and a
        validity note. Same approved-only gate (enforced by the caller,
        matching the sale certificate route convention) and PDF pipeline
        as generate_certificate().

        Args:
            valuation:    Valuation record dict (id, status, purpose, …).
            property_data: Property record dict (address, municipality, …).
            owner_name:   Full name of the registered property owner.
            rent_result:  Output of ValuationService.get_rent_valuation()
                          (suggested_rent, band_min, band_max, confidence,
                          requires_officer_review).
            certificate_number: Human-readable cert ID; auto-generated if None.
        """
        if certificate_number is None:
            certificate_number = self._generate_rent_certificate_number(valuation.get("id"))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2 * cm,
            title=f"Rent Valuation Certificate – {certificate_number}",
            author="ValuAdis – Ethiopian Property Valuation Platform",
            subject="Rent Valuation Certificate",
        )

        styles = self._build_styles()
        story = self._build_rent_story(
            styles, valuation, property_data, owner_name, certificate_number, rent_result
        )

        doc.build(story, onFirstPage=self._add_page_border, onLaterPages=self._add_page_border)
        return buffer.getvalue()

    # ------------------------------------------------------------------
    # Story construction helpers
    # ------------------------------------------------------------------

    def _build_story(
        self,
        styles: dict,
        valuation: Dict[str, Any],
        property_data: Dict[str, Any],
        owner_name: str,
        cert_number: str,
    ) -> list:
        story: list = []

        # --- Header ---
        story += self._build_header(styles, cert_number)
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", thickness=2, color=_GREEN))
        story.append(Spacer(1, 0.4 * cm))

        # --- Certificate title ---
        story.append(Paragraph("PROPERTY VALUATION CERTIFICATE", styles["cert_title"]))
        story.append(Paragraph(
            "Issued under Proclamation No. 1365/2025 – Federal Democratic Republic of Ethiopia",
            styles["subtitle"],
        ))
        story.append(Spacer(1, 0.5 * cm))

        # --- Certificate meta (number / date) ---
        story += self._build_meta_table(styles, cert_number, valuation)
        story.append(Spacer(1, 0.4 * cm))

        # --- Owner & property details ---
        story.append(Paragraph("PROPERTY OWNER", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        story += self._build_owner_table(styles, owner_name, property_data)
        story.append(Spacer(1, 0.4 * cm))

        # --- Valuation details ---
        story.append(Paragraph("VALUATION DETAILS", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        story += self._build_valuation_table(styles, valuation, property_data)
        story.append(Spacer(1, 0.4 * cm))

        # --- Financial summary box ---
        story.append(Paragraph("FINANCIAL SUMMARY", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        story += self._build_financial_table(styles, valuation)
        story.append(Spacer(1, 0.5 * cm))

        # --- Legal notice ---
        story.append(HRFlowable(width="100%", thickness=1, color=_BORDER))
        story.append(Spacer(1, 0.3 * cm))
        story += self._build_legal_notice(styles)
        story.append(Spacer(1, 0.4 * cm))

        # --- QR code + signature side by side ---
        story += self._build_bottom_row(styles, cert_number)

        return story

    def _build_rent_story(
        self,
        styles: dict,
        valuation: Dict[str, Any],
        property_data: Dict[str, Any],
        owner_name: str,
        cert_number: str,
        rent_result: Dict[str, Any],
    ) -> list:
        story: list = []

        story += self._build_header(styles, cert_number)
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", thickness=2, color=_GREEN))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("RENT VALUATION CERTIFICATE", styles["cert_title"]))
        story.append(Paragraph(
            "Suggested monthly rent and published band — Ethiopian Rent Control and "
            "Administration Proclamation No. 1320/2024",
            styles["subtitle"],
        ))
        story.append(Spacer(1, 0.5 * cm))

        story += self._build_meta_table(styles, cert_number, valuation)
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("PROPERTY OWNER", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        story += self._build_owner_table(styles, owner_name, property_data)
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("RENT VALUATION SUMMARY", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        story += self._build_rent_financial_table(styles, rent_result)
        story.append(Spacer(1, 0.5 * cm))

        story.append(HRFlowable(width="100%", thickness=1, color=_BORDER))
        story.append(Spacer(1, 0.3 * cm))
        story += self._build_rent_validity_notice(styles, rent_result)
        story.append(Spacer(1, 0.4 * cm))

        story += self._build_bottom_row(styles, cert_number)

        return story

    # --- Header ----------------------------------------------------------

    def _build_header(self, styles: dict, cert_number: str) -> list:
        header_data = [[
            Paragraph("Federal Democratic Republic of Ethiopia<br/>"
                      "<b>Ministry of Finance – Property Tax Administration</b>",
                      styles["header_left"]),
            Paragraph("<b>ValuAdis</b><br/>Ethiopian Property Valuation Platform",
                      styles["header_right"]),
        ]]
        t = Table(header_data, colWidths=["60%", "40%"])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return [t]

    # --- Meta table (cert number / issue date) ---------------------------

    def _build_meta_table(self, styles: dict, cert_number: str, valuation: Dict) -> list:
        issue_date = date.today().strftime("%d %B %Y")
        valuation_date = valuation.get("valuation_date") or issue_date
        if hasattr(valuation_date, "strftime"):
            valuation_date = valuation_date.strftime("%d %B %Y")
        elif isinstance(valuation_date, str) and valuation_date != issue_date:
            # Parse ISO datetime strings (e.g. "2025-03-04T12:34:56" or "2025-03-04")
            # that originate from Valuation.to_dict() so the certificate always
            # displays a human-readable date rather than a raw timestamp.
            try:
                valuation_date = datetime.fromisoformat(valuation_date).strftime("%d %B %Y")
            except ValueError:
                pass  # keep the raw string if it cannot be parsed

        data = [
            ["Certificate No.", cert_number, "Issue Date", issue_date],
            ["Valuation Date", str(valuation_date), "Status",
             str(valuation.get("status", "approved")).upper()],
        ]
        t = Table(data, colWidths=["22%", "28%", "22%", "28%"])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), _GREEN),
            ("BACKGROUND", (2, 0), (2, -1), _GREEN),
            ("TEXTCOLOR",  (0, 0), (0, -1), colors.white),
            ("TEXTCOLOR",  (2, 0), (2, -1), colors.white),
            ("FONTNAME",   (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",   (0, 0), (-1, -1), 9),
            ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",   (2, 0), (2, -1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (1, 0), (1, -1), [_LIGHT]),
            ("ROWBACKGROUNDS", (3, 0), (3, -1), [_LIGHT]),
            ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
            ("GRID",       (0, 0), (-1, -1), 0.5, _BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        return [t]

    # --- Owner / property table ------------------------------------------

    def _build_owner_table(self, styles: dict, owner_name: str, prop: Dict) -> list:
        rows = [
            ["Owner Name", owner_name],
            ["Property Address", prop.get("address", "—")],
            ["Municipality", prop.get("municipality", "—")],
            ["Property Type", str(prop.get("property_type", "—")).replace("_", " ").title()],
            ["Area (sqm)", f"{float(prop.get('area_sqm', 0)):,.2f} m²"],
        ]
        t = Table(rows, colWidths=["30%", "70%"])
        t.setStyle(self._detail_table_style())
        return [t]

    # --- Valuation details table -----------------------------------------

    def _build_valuation_table(self, styles: dict, val: Dict, prop: Dict) -> list:
        condition         = str(val.get("condition") or prop.get("condition", "good")).title()
        neighborhood      = str(val.get("neighborhood_quality") or prop.get("neighborhood_quality", "average")).replace("_", " ").title()
        base_rate         = val.get("base_rate_per_sqm") or prop.get("base_rate_per_sqm", "—")
        depreciation_rate = val.get("depreciation_rate", 0)

        rows = [
            ["Base Rate (ETB/m²)", f"{float(base_rate):,.2f}" if base_rate != "—" else "—"],
            ["Condition Grade",    condition],
            ["Neighborhood Quality", neighborhood],
            ["Depreciation Applied",
             f"{float(depreciation_rate) * 100:.1f}%" if depreciation_rate else "0%"],
            ["Proclamation Reference", "Proclamation 1365/2025, Art. 12"],
        ]
        t = Table(rows, colWidths=["30%", "70%"])
        t.setStyle(self._detail_table_style())
        return [t]

    # --- Financial summary -----------------------------------------------

    def _build_financial_table(self, styles: dict, val: Dict) -> list:
        market_value  = float(val.get("market_value", 0))
        taxable_value = float(val.get("taxable_value", 0))

        rows = [
            ["Market Value (ETB)", f"{market_value:,.2f}"],
            ["Taxable Value (ETB) [25% of Market Value]", f"{taxable_value:,.2f}"],
        ]
        t = Table(rows, colWidths=["60%", "40%"])
        t.setStyle(TableStyle([
            ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 10),
            ("FONTNAME",      (0, 0), (0, 0),   "Helvetica-Bold"),
            ("FONTNAME",      (0, 1), (0, 1),   "Helvetica-Bold"),
            ("FONTNAME",      (1, 0), (1, 0),   "Helvetica-Bold"),
            ("FONTNAME",      (1, 1), (1, 1),   "Helvetica-Bold"),
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#E8F5F1")),
            ("BACKGROUND",    (0, 1), (-1, 1),  _GOLD),
            ("TEXTCOLOR",     (0, 1), (-1, 1),  colors.black),
            ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
            ("GRID",          (0, 0), (-1, -1), 0.5, _BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (1, 0), (1, -1),  8),
        ]))
        return [t]

    # --- Rent valuation summary ------------------------------------------

    def _build_rent_financial_table(self, styles: dict, rent_result: Dict[str, Any]) -> list:
        suggested_rent = float(rent_result.get("suggested_rent", 0))
        band_min       = float(rent_result.get("band_min", 0))
        band_max       = float(rent_result.get("band_max", 0))
        confidence     = float(rent_result.get("confidence", 0))

        rows = [
            ["Suggested Monthly Rent (ETB)", f"{suggested_rent:,.2f}"],
            ["Published Band (ETB/month)", f"{band_min:,.2f} – {band_max:,.2f}"],
            ["Confidence Score", f"{confidence * 100:.0f}%"],
        ]
        t = Table(rows, colWidths=["60%", "40%"])
        t.setStyle(TableStyle([
            ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 10),
            ("FONTNAME",      (0, 0), (0, 0),   "Helvetica-Bold"),
            ("FONTNAME",      (1, 0), (1, 0),   "Helvetica-Bold"),
            ("BACKGROUND",    (0, 0), (-1, 0),  _GOLD),
            ("BACKGROUND",    (0, 1), (-1, -1), colors.HexColor("#E8F5F1")),
            ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
            ("GRID",          (0, 0), (-1, -1), 0.5, _BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (1, 0), (1, -1),  8),
        ]))
        return [t]

    def _build_rent_validity_notice(self, styles: dict, rent_result: Dict[str, Any]) -> list:
        review_note = (
            " This estimate carries a below-floor confidence score and "
            "requires rental officer review before publication."
            if rent_result.get("requires_officer_review")
            else ""
        )
        text = (
            "This certificate presents a system-generated rent valuation issued in support "
            "of the tenancy registration process under <b>Proclamation No. 1320/2024</b> of "
            "the Federal Democratic Republic of Ethiopia. The suggested rent and published "
            "band are valid for <b>90 days</b> from the issue date and are not a substitute "
            "for a registered tenancy contract." + review_note +
            " For verification, scan the QR code below or visit <b>valuadis.et/verify</b>."
        )
        return [Paragraph(text, styles["legal"])]

    # --- Legal notice ---------------------------------------------------

    def _build_legal_notice(self, styles: dict) -> list:
        text = (
            "This certificate is issued pursuant to <b>Proclamation No. 1365/2025</b> of the "
            "Federal Democratic Republic of Ethiopia and constitutes official evidence of the "
            "assessed property value for taxation and legal purposes. The taxable value is "
            "calculated at <b>25% of the market value</b> in accordance with Article 12 of the "
            "Proclamation. Any alteration of this document renders it void. For verification, "
            "scan the QR code below or visit <b>valuadis.et/verify</b>."
        )
        return [Paragraph(text, styles["legal"])]

    # --- Bottom row: QR + signature -------------------------------------

    def _build_bottom_row(self, styles: dict, cert_number: str) -> list:
        verify_url = f"{self.VERIFY_BASE_URL}/{cert_number}"
        qr_img     = self._build_qr_image(verify_url, size=90)

        sig_block = Table(
            [
                [Paragraph("Authorized Signatory", styles["sig_label"])],
                [Spacer(1, 1.5 * cm)],
                [HRFlowable(width=5 * cm, thickness=1, color=colors.black)],
                [Paragraph("ValuAdis Platform / Municipal Valuer", styles["sig_label"])],
                [Paragraph(date.today().strftime("%d %B %Y"), styles["sig_label"])],
            ],
            colWidths=["100%"],
        )
        sig_block.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))

        row = Table(
            [[qr_img, sig_block]],
            colWidths=["40%", "60%"],
        )
        row.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
            ("ALIGN",         (0, 0), (0, 0),   "CENTER"),
            ("ALIGN",         (1, 0), (1, 0),   "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return [row]

    # ------------------------------------------------------------------
    # Reusable helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _detail_table_style() -> TableStyle:
        return TableStyle([
            ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("FONTNAME",      (0, 0), (0, -1),  "Helvetica-Bold"),
            ("TEXTCOLOR",     (0, 0), (0, -1),  _NAVY),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, _LIGHT]),
            ("GRID",          (0, 0), (-1, -1), 0.5, _BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ])

    @staticmethod
    def _build_qr_image(url: str, size: int = 80) -> Image:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        pil_img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        return Image(buf, width=size, height=size)

    @staticmethod
    def _build_styles() -> dict:
        base = getSampleStyleSheet()
        return {
            "cert_title": ParagraphStyle(
                "cert_title",
                parent=base["Heading1"],
                fontSize=16,
                textColor=_GREEN,
                alignment=TA_CENTER,
                spaceAfter=4,
                fontName="Helvetica-Bold",
            ),
            "subtitle": ParagraphStyle(
                "subtitle",
                parent=base["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#6B7280"),
                alignment=TA_CENTER,
                spaceAfter=2,
            ),
            "section_heading": ParagraphStyle(
                "section_heading",
                parent=base["Normal"],
                fontSize=10,
                textColor=colors.white,
                backColor=_GREEN,
                fontName="Helvetica-Bold",
                leftIndent=4,
                spaceBefore=4,
                spaceAfter=2,
                leading=16,
            ),
            "header_left": ParagraphStyle(
                "header_left",
                parent=base["Normal"],
                fontSize=9,
                textColor=_NAVY,
                alignment=TA_LEFT,
            ),
            "header_right": ParagraphStyle(
                "header_right",
                parent=base["Normal"],
                fontSize=10,
                textColor=_GREEN,
                alignment=TA_RIGHT,
            ),
            "legal": ParagraphStyle(
                "legal",
                parent=base["Normal"],
                fontSize=7.5,
                textColor=colors.HexColor("#374151"),
                leading=11,
            ),
            "sig_label": ParagraphStyle(
                "sig_label",
                parent=base["Normal"],
                fontSize=8,
                textColor=colors.HexColor("#374151"),
                alignment=TA_CENTER,
            ),
        }

    @staticmethod
    def _generate_certificate_number(valuation_id: Any) -> str:
        year    = date.today().year
        uid_seg = str(uuid.uuid4()).split("-")[0].upper()
        vid     = f"{valuation_id:05d}" if isinstance(valuation_id, int) else "00000"
        return f"ETH-VAL-{year}-{vid}-{uid_seg}"

    @staticmethod
    def _generate_rent_certificate_number(valuation_id: Any) -> str:
        year    = date.today().year
        uid_seg = str(uuid.uuid4()).split("-")[0].upper()
        vid     = f"{valuation_id:05d}" if isinstance(valuation_id, int) else "00000"
        return f"ETH-RENT-{year}-{vid}-{uid_seg}"

    @staticmethod
    def _add_page_border(canvas, doc):
        """Draw a coloured border on every page."""
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(_GREEN)
        canvas.setLineWidth(3)
        canvas.rect(8 * mm, 8 * mm, w - 16 * mm, h - 16 * mm)
        canvas.setStrokeColor(_GOLD)
        canvas.setLineWidth(1)
        canvas.rect(10 * mm, 10 * mm, w - 20 * mm, h - 20 * mm)

        # Footer
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#9CA3AF"))
        canvas.drawCentredString(
            w / 2,
            6 * mm,
            f"ValuAdis | Ethiopian Property Valuation Platform | valuadis.et | "
            f"Page {doc.page}",
        )
        canvas.restoreState()
