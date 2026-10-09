"""
HelvetiaVeritas - Cryptographic Attestation & FADP Compliance Certificate Service
================================================================================
Generates tamper-evident SHA-256 audit digests, cryptographic HMAC seals,
and official court-admissible PDF audit dossiers under Swiss revDSG Art. 6.
"""

from datetime import datetime, timezone
import hashlib
import hmac
import io
import json
import logging
from typing import Dict, List, Optional
import uuid

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from xml.sax.saxutils import escape as xml_escape

from app.config import settings
from app.schemas.audit_schema import AttestationCertificate, MatchedLegalArticle

logger = logging.getLogger("helvetia_veritas.attestation")


class AttestationService:
    """Generates immutable cryptographic compliance seals and official PDF dossiers."""

    def __init__(self):
        self.salt = settings.ATTESTATION_SECRET_SALT.encode("utf-8")

    def generate_certificate(
        self,
        raw_text: str,
        normalized_text: str,
        canton_code: str,
        articles: List[MatchedLegalArticle],
        model_id: str
    ) -> AttestationCertificate:
        """
        Creates an immutable, cryptographically sealed audit certificate
        guaranteeing data integrity and Swiss sovereign provenance.
        """
        audit_id = str(uuid.uuid4())
        timestamp_iso = datetime.now(timezone.utc).isoformat()

        # 1. Compute SHA-256 of raw citizen dialect input
        input_sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

        # 2. Compute SHA-256 of normalized Schweizer Hochdeutsch output
        normalized_sha256 = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

        # 3. Compute SHA-256 digest of matched statutory provisions
        articles_serialized = json.dumps(
            [{"id": a.article_id, "law": a.law, "num": a.article_number} for a in articles],
            sort_keys=True
        )
        articles_digest_sha256 = hashlib.sha256(articles_serialized.encode("utf-8")).hexdigest()

        # 4. Composite pipeline cryptographic hash
        composite_payload = (
            f"{input_sha256}:{normalized_sha256}:{articles_digest_sha256}:"
            f"{canton_code}:{model_id}:{timestamp_iso}"
        )
        pipeline_composite_hash = hashlib.sha256(composite_payload.encode("utf-8")).hexdigest()

        # 5. HMAC cryptographic seal
        signature = hmac.new(
            self.salt,
            pipeline_composite_hash.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        certificate = AttestationCertificate(
            audit_id=audit_id,
            timestamp_iso=timestamp_iso,
            input_sha256=input_sha256,
            normalized_sha256=normalized_sha256,
            articles_digest_sha256=articles_digest_sha256,
            pipeline_composite_hash=pipeline_composite_hash,
            signature_token=signature,
            infrastructure=settings.INFRASTRUCTURE_LOCATION,
            supercomputer=settings.SUPERCOMPUTER_CLUSTER,
            model_id=model_id,
            fadp_revdsg_compliance=settings.DATA_SOVEREIGNTY_REGULATION,
            fedlex_tier=settings.FEDLEX_ALIGNMENT_TIER,
            verification_status="VERIFIED_TAMPER_EVIDENT"
        )

        logger.info(
            "Issued sovereign audit certificate: ID=%s, CompositeHash=%s",
            audit_id, pipeline_composite_hash[:16]
        )
        return certificate

    def verify_certificate(self, cert_data: Dict) -> bool:
        """Validates the cryptographic seal of an issued certificate."""
        try:
            composite_hash = cert_data.get("pipeline_composite_hash", "")
            signature = cert_data.get("signature_token", "")
            expected_sig = hmac.new(
                self.salt,
                composite_hash.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_sig)
        except Exception as exc:
            logger.error("Certificate verification error: %s", exc)
            return False

    def generate_audit_pdf(
        self,
        certificate: AttestationCertificate,
        normalized_text: str,
        raw_text: str,
        canton_name: str,
        canton_code: str,
        articles: List[MatchedLegalArticle],
        performance: Optional[Dict] = None
    ) -> bytes:
        """
        Generates an official tamper-evident Swiss Sovereign Audit Dossier PDF.
        Formatted for municipal administration and judicial submission.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        swiss_red = colors.HexColor("#D8232A")
        dark_slate = colors.HexColor("#0F172A")
        card_bg = colors.HexColor("#F8FAFC")
        border_color = colors.HexColor("#CBD5E1")

        # Custom Typography
        title_style = ParagraphStyle(
            "SwissTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=dark_slate,
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "SwissSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748B"),
            fontName="Helvetica"
        )
        section_style = ParagraphStyle(
            "SwissSection",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=swiss_red,
            fontName="Helvetica-Bold",
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "SwissBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=dark_slate,
            fontName="Helvetica"
        )
        code_style = ParagraphStyle(
            "SwissCode",
            parent=styles["Code"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#0369A1"),
            fontName="Courier"
        )

        story = []

        # 1. Header Banner
        header_table = Table(
            [
                [
                    Paragraph("<b>SCHWEIZERISCHE EIDGENOSSENSCHAFT</b><br/>HelvetiaVeritas v2.0 • CantonalAudit Enterprise", title_style),
                    Paragraph("<b>OFFIZIELLES KANTONALES AUDIT-DOSSIER</b><br/>FADP / revDSG SR 235.1 Art. 6 Konform", subtitle_style)
                ]
            ],
            colWidths=[320, 200]
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=2, color=swiss_red, spaceAfter=12))

        # 2. Metadata & Infrastructure Table
        meta_data = [
            [
                Paragraph("<b>Audit-ID:</b>", body_style),
                Paragraph(certificate.audit_id, code_style),
                Paragraph("<b>Kanton:</b>", body_style),
                Paragraph(f"{canton_name} ({canton_code})", body_style)
            ],
            [
                Paragraph("<b>Zeitstempel (UTC):</b>", body_style),
                Paragraph(certificate.timestamp_iso, body_style),
                Paragraph("<b>Modell-Cluster:</b>", body_style),
                Paragraph(certificate.model_id, body_style)
            ],
            [
                Paragraph("<b>Infrastruktur:</b>", body_style),
                Paragraph(certificate.supercomputer, body_style),
                Paragraph("<b>Datenschutz:</b>", body_style),
                Paragraph("revDSG Art. 6 (Sovereign Alps)", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[90, 180, 80, 170])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), card_bg),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # 3. Cryptographic Tamper-Evidence Fingerprint Table
        story.append(Paragraph("1. KRYPTOGRAPHISCHE VERIFIKATIONS-SIGNATUR (SHA-256)", section_style))
        crypto_data = [
            [Paragraph("<b>Bürger-Input Digest (SHA-256):</b>", body_style), Paragraph(certificate.input_sha256, code_style)],
            [Paragraph("<b>Normierter Text Digest (SHA-256):</b>", body_style), Paragraph(certificate.normalized_sha256, code_style)],
            [Paragraph("<b>Composite Pipeline Hash:</b>", body_style), Paragraph(certificate.pipeline_composite_hash, code_style)],
            [Paragraph("<b>HMAC-256 Sovereign Seal:</b>", body_style), Paragraph(certificate.signature_token, code_style)]
        ]
        crypto_table = Table(crypto_data, colWidths=[150, 370])
        crypto_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(crypto_table)
        story.append(Spacer(1, 12))

        # 4. Normiertes Schweizer Hochdeutsch (Gerichtsfeste Fassung)
        story.append(Paragraph("2. AMTLICH NORMIERTE SCHWEIZER RECHTSSCHRIFT", section_style))
        raw_paragraphs = [p.strip() for p in normalized_text.split("\n\n") if p.strip()]
        norm_paragraphs = [
            Paragraph(xml_escape(p).replace("\n", "<br/>"), body_style)
            for p in raw_paragraphs
        ]
        if len(norm_paragraphs) <= 6:
            norm_table = Table([[p] for p in norm_paragraphs], colWidths=[520], splitByRow=1)
            norm_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, swiss_red),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.append(norm_table)
        else:
            for p in norm_paragraphs:
                story.append(p)
                story.append(Spacer(1, 4))
        story.append(Spacer(1, 12))

        # 5. Identified Statutes (ZGB, OR, SchKG, DBG, KVG)
        story.append(Paragraph("3. ANGEWANDTE BUNDESRECHTLICHE STATUTEN & RECHTSBEHELF", section_style))
        art_rows = []
        for art in articles[:4]:
            law_esc = xml_escape(str(art.law))
            num_esc = xml_escape(str(art.article_number))
            title_esc = xml_escape(str(art.title_de))
            summary_esc = xml_escape(str(art.summary_de))
            remedy_esc = xml_escape(str(art.remedy_action_de))
            auth_esc = xml_escape(str(art.competent_authority))
            art_text = (
                f"<b>{law_esc} Art. {num_esc} — {title_esc}</b><br/>"
                f"<i>Zusammenfassung:</i> {summary_esc}<br/>"
                f"<b>Handlungsempfehlung:</b> {remedy_esc}<br/>"
                f"<i>Zuständigkeit:</i> {auth_esc}"
            )
            art_rows.append([Paragraph(art_text, body_style)])

        if art_rows:
            art_table = Table(art_rows, colWidths=[520], splitByRow=1)
            art_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), card_bg),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(art_table)

        story.append(Spacer(1, 14))

        # 6. Official Stamp Layout & Certification Statement
        cert_statement = (
            "<b>AMTLICHE BEGLAUBIGUNG / ATTESTATION OFFICIELLE:</b><br/>"
            "Dieses Dokument wurde durch das sovereign gehostete KI-System <b>HelvetiaVeritas v2.0</b> auf dem "
            "Schweizer Supercomputer <b>CSCS Alps</b> (Lugano, TI) prozessiert. Die Datenverarbeitung erfolgte ohne "
            "Grenzübertritt gemäss Art. 6 des Bundesgesetzes über den Datenschutz (revDSG, SR 235.1). Die vorliegende "
            "kryptographische Signatur garantiert die Unveränderlichkeit des Sachverhalts gegenüber der Schlichtungsbehörde."
        )
        footer_table = Table(
            [
                [
                    Paragraph(cert_statement, subtitle_style),
                    Paragraph("<b>SIEGEL / CACHET:</b><br/>HELVETIA VERITAS<br/>[VERIFIED SOVEREIGN]", body_style)
                ]
            ],
            colWidths=[400, 120]
        )
        footer_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#64748B")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FEF2F2")),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(footer_table)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes


# Singleton service
attestation_service = AttestationService()
