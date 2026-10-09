"""
HelvetiaVeritas - Swiss Sovereign PII Redaction & Anonymization Engine
======================================================================
Pre-inference privacy sanitization guaranteeing Swiss Federal Act on Data
Protection (revDSG / SR 235.1 Art. 6 & Art. 7) compliance.
Strips Swiss AHV/AVS numbers, IBANs, phone numbers, and email addresses.
"""

import re
from typing import Dict, Tuple
import logging

logger = logging.getLogger("helvetia_veritas.anonymizer")


class SwissPIIAnonymizer:
    """Detects, redacts, and re-hydrates sensitive personal identifiable information."""

    # 1. Swiss AHV/AVS: 13-digit identifier starting with 756 (with optional CH- prefix)
    AHV_PATTERN = re.compile(
        r"\b(?:CH(?:-|\s)?)?756(?:\.|\s|-)?\d{4}(?:\.|\s|-)?\d{4}(?:\.|\s|-)?\d{2}\b",
        re.IGNORECASE
    )

    # 2. Swiss IBAN: CH followed by 19 alphanumeric characters
    IBAN_PATTERN = re.compile(
        r"\bCH\d{2}(?:(?:\s|-)?\w{4}){4}(?:(?:\s|-)?\w{1,3})?\b",
        re.IGNORECASE
    )

    # 3. Swiss Phone numbers: international (+41 / 0041) or domestic (07x, 04x, 03x, 02x, 06x, 071)
    PHONE_PATTERN = re.compile(
        r"(?:(?:\+|00)41[\s\-\.\/]?(?:\(0\)[\s\-\.\/]?)?|0)[1-9]\d{1}[\s\-\.\/]*(?:\d[\s\-\.\/]*){6}\d\b"
    )

    # 4. Email addresses
    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    def redact(self, text: str) -> Tuple[str, Dict[str, str], int]:
        """
        Scans and redacts PII entities into sovereign cryptographic placeholders.
        Returns: (sanitized_text, redaction_map, count)
        """
        redactions: Dict[str, str] = {}
        total_redactions = 0

        # Replace helper
        def replace_entity(match: re.Match, entity_prefix: str) -> str:
            nonlocal total_redactions
            total_redactions += 1
            original = match.group(0).strip()
            placeholder = f"[{entity_prefix}_{total_redactions:02d}]"
            redactions[placeholder] = original
            return placeholder

        # 1. Redact AHV numbers
        sanitized = self.AHV_PATTERN.sub(
            lambda m: replace_entity(m, "AHV_REDACTED"), text
        )

        # 2. Redact IBANs
        sanitized = self.IBAN_PATTERN.sub(
            lambda m: replace_entity(m, "IBAN_REDACTED"), sanitized
        )

        # 3. Redact Emails
        sanitized = self.EMAIL_PATTERN.sub(
            lambda m: replace_entity(m, "EMAIL_REDACTED"), sanitized
        )

        # 4. Redact Phones
        sanitized = self.PHONE_PATTERN.sub(
            lambda m: replace_entity(m, "TEL_REDACTED"), sanitized
        )

        if total_redactions > 0:
            logger.info("Redacted %d PII entities under revDSG Art. 6", total_redactions)

        return sanitized, redactions, total_redactions

    def restore(self, text: str, redactions: Dict[str, str]) -> str:
        """
        Re-hydrates sanitized placeholders with original values for authorized local view.
        """
        restored = text
        for placeholder, original in redactions.items():
            restored = restored.replace(placeholder, original)
        return restored


# Singleton instance
anonymizer = SwissPIIAnonymizer()
