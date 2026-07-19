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


def _fmt_date(value: Any) -> str:
    """Format dates/ISO strings for PDF display; falls back to a dash."""
    if not value:
        return "—"
    if hasattr(value, "strftime"):
        return value.strftime("%d %B %Y")
    try:
        return datetime.fromisoformat(str(value)).strftime("%d %B %Y")
    except ValueError:
        return str(value)


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
    # Rentals (Phase C): tenancy contract + owner listing agreement
    # ------------------------------------------------------------------

    # Addis Ababa 2026/27 rent-increase cap (Proclamation 1320/2024 directive).
    RENEWAL_CAP_PERCENT: float = 11.5

    # Footer marker required on rentals legal PDFs until counsel signs off.
    PILOT_LEGAL_FOOTER = "PILOT DRAFT — PENDING LEGAL REVIEW"

    def generate_tenancy_contract(
        self,
        contract: Dict[str, Any],
        owner: Dict[str, Any],
        renter: Dict[str, Any],
        property_data: Dict[str, Any],
        rent_context: Dict[str, Any],
    ) -> bytes:
        """Generate the registered tenancy contract PDF from the Proclamation
        1320/2024 model-contract structure.

        Args:
            contract:     Contract dict (contract_no, monthly_rent, start_date,
                          end_date, deposit_amount, deposit_receipt_ref, status).
            owner:        {"full_name", "fayda_id_number", "phone"} of the lessor.
            renter:       {"full_name", "fayda_id_number", "phone"} of the lessee.
            property_data: Property record dict (address, municipality, area_sqm, …).
            rent_context: {"band_min", "band_max", "valuation_reference"} for the
                          published band and its backing valuation.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2 * cm,
            title=f"Tenancy Contract – {contract.get('contract_no', '')}",
            author="ValuAdis / Addis Ababa Housing Administration",
            subject="Registered Tenancy Contract – Proclamation 1320/2024",
        )
        styles = self._build_styles()
        story = self._build_contract_story(styles, contract, owner, renter, property_data, rent_context)
        doc.build(story, onFirstPage=self._add_rentals_page_frame, onLaterPages=self._add_rentals_page_frame)
        return buffer.getvalue()

    def generate_listing_agreement(
        self,
        listing: Dict[str, Any],
        owner: Dict[str, Any],
        property_data: Dict[str, Any],
    ) -> bytes:
        """Generate the owner ↔ administration listing agreement PDF produced
        at publish time.

        Args:
            listing:      {"public_id", "suggested_rent", "band_min", "band_max"}.
            owner:        {"full_name", "fayda_id_number", "phone"}.
            property_data: Property record dict (address, municipality, area_sqm, …).
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2 * cm,
            title=f"Listing Agreement – {listing.get('public_id', '')}",
            author="ValuAdis / Addis Ababa Housing Administration",
            subject="Rental Listing Agreement – Proclamation 1320/2024",
        )
        styles = self._build_styles()
        story = self._build_listing_agreement_story(styles, listing, owner, property_data)
        doc.build(story, onFirstPage=self._add_rentals_page_frame, onLaterPages=self._add_rentals_page_frame)
        return buffer.getvalue()

    def _build_contract_story(
        self,
        styles: dict,
        contract: Dict[str, Any],
        owner: Dict[str, Any],
        renter: Dict[str, Any],
        prop: Dict[str, Any],
        rent_context: Dict[str, Any],
    ) -> list:
        story: list = []
        story += self._build_header(styles, contract.get("contract_no", "—"))
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", thickness=2, color=_GREEN))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("REGISTERED TENANCY CONTRACT", styles["cert_title"]))
        story.append(Paragraph(
            "Model contract under the Rent Control and Administration Proclamation "
            "No. 1320/2024 — Addis Ababa Housing Administration",
            styles["subtitle"],
        ))
        story.append(Spacer(1, 0.5 * cm))

        meta = [
            ["Contract No.", contract.get("contract_no", "—"), "Status", str(contract.get("status", "draft")).upper()],
            ["Start Date", _fmt_date(contract.get("start_date")), "End Date", _fmt_date(contract.get("end_date"))],
        ]
        story += [self._meta_grid(meta)]
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("PARTIES", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        party_rows = [
            ["", "Lessor (Owner)", "Lessee (Renter)"],
            ["Full Name", owner.get("full_name", "—"), renter.get("full_name", "—")],
            ["Fayda ID", owner.get("fayda_id_number") or "—", renter.get("fayda_id_number") or "—"],
            ["Phone", owner.get("phone") or "—", renter.get("phone") or "—"],
        ]
        t = Table(party_rows, colWidths=["22%", "39%", "39%"])
        t.setStyle(self._detail_table_style())
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("PROPERTY", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        prop_rows = [
            ["Address", prop.get("address", "—")],
            ["Municipality / Sub-city", f"{prop.get('municipality', '—')} / {prop.get('subcity', '—')}"],
            ["Type", str(prop.get("property_type", "—")).replace("_", " ").title()],
            ["Area (sqm)", f"{float(prop.get('area_sqm', 0)):,.2f} m²"],
        ]
        pt = Table(prop_rows, colWidths=["30%", "70%"])
        pt.setStyle(self._detail_table_style())
        story.append(pt)
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("RENT, BAND & DEPOSIT", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        monthly = float(contract.get("monthly_rent", 0))
        deposit = float(contract.get("deposit_amount", 0))
        rent_rows = [
            ["Monthly Rent (ETB)", f"{monthly:,.2f}"],
            ["Published Band (ETB/month)",
             f"{float(rent_context.get('band_min', 0)):,.2f} – {float(rent_context.get('band_max', 0)):,.2f}"],
            ["Valuation Reference", str(rent_context.get("valuation_reference", "—"))],
            ["Deposit (ETB)", f"{deposit:,.2f}"],
            ["Deposit Receipt Ref", contract.get("deposit_receipt_ref") or "Pending — contract inactive until recorded"],
        ]
        rt = Table(rent_rows, colWidths=["40%", "60%"])
        rt.setStyle(self._detail_table_style())
        story.append(rt)
        story.append(Spacer(1, 0.5 * cm))

        story.append(HRFlowable(width="100%", thickness=1, color=_BORDER))
        story.append(Spacer(1, 0.3 * cm))
        clause = (
            "<b>Rent increase cap.</b> Any renewal of this tenancy is subject to the maximum "
            f"annual rent increase in force for Addis Ababa, currently <b>{self.RENEWAL_CAP_PERCENT:.1f}%</b>, "
            "under the Rent Control and Administration Proclamation No. 1320/2024 and the Addis "
            "Ababa directive for 2026/27. <b>Deposit.</b> The deposit is recorded against this "
            "registered contract as evidence; it is not held in custody by the administration in "
            "this phase. The contract is legally active only once the deposit receipt is recorded. "
            "This document reproduces the parties' identity and the registered price; alteration "
            "renders it void."
        )
        story.append(Paragraph(clause, styles["legal"]))
        story.append(Spacer(1, 0.5 * cm))

        story += self._build_signature_row(styles, ["Lessor (Owner)", "Lessee (Renter)", "Rental Officer"])
        return story

    def _build_listing_agreement_story(
        self,
        styles: dict,
        listing: Dict[str, Any],
        owner: Dict[str, Any],
        prop: Dict[str, Any],
    ) -> list:
        story: list = []
        story += self._build_header(styles, listing.get("public_id", "—"))
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", thickness=2, color=_GREEN))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("RENTAL LISTING AGREEMENT", styles["cert_title"]))
        story.append(Paragraph(
            "Owner and Addis Ababa Housing Administration — listing terms under "
            "Proclamation No. 1320/2024",
            styles["subtitle"],
        ))
        story.append(Spacer(1, 0.5 * cm))

        meta = [
            ["Listing No.", listing.get("public_id", "—"), "Published", _fmt_date(listing.get("published_at"))],
        ]
        story += [self._meta_grid(meta)]
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("OWNER", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        owner_rows = [
            ["Full Name", owner.get("full_name", "—")],
            ["Fayda ID", owner.get("fayda_id_number") or "—"],
            ["Phone", owner.get("phone") or "—"],
        ]
        ot = Table(owner_rows, colWidths=["30%", "70%"])
        ot.setStyle(self._detail_table_style())
        story.append(ot)
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("PROPERTY & PUBLISHED BAND", styles["section_heading"]))
        story.append(Spacer(1, 0.2 * cm))
        band_rows = [
            ["Address", prop.get("address", "—")],
            ["Municipality / Sub-city", f"{prop.get('municipality', '—')} / {prop.get('subcity', '—')}"],
            ["Area (sqm)", f"{float(prop.get('area_sqm', 0)):,.2f} m²"],
            ["Suggested Rent (ETB/month)", f"{float(listing.get('suggested_rent', 0)):,.2f}"],
            ["Published Band (ETB/month)",
             f"{float(listing.get('band_min', 0)):,.2f} – {float(listing.get('band_max', 0)):,.2f}"],
        ]
        bt = Table(band_rows, colWidths=["40%", "60%"])
        bt.setStyle(self._detail_table_style())
        story.append(bt)
        story.append(Spacer(1, 0.5 * cm))

        story.append(HRFlowable(width="100%", thickness=1, color=_BORDER))
        story.append(Spacer(1, 0.3 * cm))
        terms = (
            "The owner authorises the Addis Ababa Housing Administration to publish this property "
            "on the public rental registry at the band shown above, which is frozen at publication "
            "and backed by an approved rent valuation. Applications are accepted only within this "
            "band. The owner confirms the property is residential and eligible under Proclamation "
            "No. 1320/2024, and that the ownership details provided are accurate."
        )
        story.append(Paragraph(terms, styles["legal"]))
        story.append(Spacer(1, 0.5 * cm))

        story += self._build_signature_row(styles, ["Owner", "Rental Officer"])
        return story

    def _meta_grid(self, data: list) -> Table:
        # Normalise to 4 columns per row for a consistent green label grid.
        col_widths = ["22%", "28%", "22%", "28%"]
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), _GREEN),
            ("BACKGROUND", (2, 0), (2, -1), _GREEN),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
            ("TEXTCOLOR", (2, 0), (2, -1), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, _BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    def _build_signature_row(self, styles: dict, labels: list) -> list:
        cells = []
        for label in labels:
            cells.append(Table(
                [
                    [Spacer(1, 1.2 * cm)],
                    [HRFlowable(width=4.5 * cm, thickness=1, color=colors.black)],
                    [Paragraph(label, styles["sig_label"])],
                    [Paragraph("Signature / Date", styles["sig_label"])],
                ],
                colWidths=["100%"],
            ))
        width = f"{100 // len(labels)}%"
        row = Table([cells], colWidths=[width] * len(labels))
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        return [row]

    def _add_rentals_page_frame(self, canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(_GREEN)
        canvas.setLineWidth(3)
        canvas.rect(8 * mm, 8 * mm, w - 16 * mm, h - 16 * mm)
        canvas.setStrokeColor(_GOLD)
        canvas.setLineWidth(1)
        canvas.rect(10 * mm, 10 * mm, w - 20 * mm, h - 20 * mm)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(colors.HexColor("#9D3A28"))
        canvas.drawCentredString(w / 2, 11 * mm, self.PILOT_LEGAL_FOOTER)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#9CA3AF"))
        canvas.drawCentredString(
            w / 2, 6 * mm,
            f"ValuAdis / Addis Ababa Housing Administration | Proclamation 1320/2024 | Page {doc.page}",
        )
        canvas.restoreState()

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
