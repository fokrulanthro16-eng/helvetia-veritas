"""
Comprehensive Sovereign Pipeline Test Suite (Sprints 1 & 2 Verification)
"""
import sys
import os
from pathlib import Path
import asyncio

backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.core.dialect_parser import dialect_parser, NonAlemannicLanguageError
from app.core.legal_mapper import legal_mapper
from app.core.apertus_client import apertus_client
from app.core.anonymizer import anonymizer
from app.services.attestation import attestation_service

async def main():
    print(f"=== {settings.PROJECT_NAME} Verification Suite ===")
    print(f"CSCS Model: {settings.APERTUS_MODEL}")
    print(f"Markers count: {len(dialect_parser.lexical_lookup)}")
    print(f"Articles count: {len(legal_mapper.articles_corpus)}")

    # -------------------------------------------------------------
    # Test 1: PII Redaction & Re-hydration (revDSG Art. 6 & 7)
    # -------------------------------------------------------------
    print("\n--- Test 1: Swiss PII Anonymizer Engine ---")
    pii_sample = (
        "Sali zäme, mini AHV-Nummer isch 756.9284.1029.44 und mini IBAN isch CH93 0076 2011 6238 5295 7. "
        "Bitte lütet mir aa uf +41 79 123 45 67 oder schribed es Mail a beat.meier@bluewin.ch."
    )
    redacted_text, redactions, count = anonymizer.redact(pii_sample)
    print("Redacted text:", redacted_text)
    print("Redaction count:", count)
    assert count == 4, f"Expected 4 PII entities, found {count}"
    assert "756.9284.1029.44" not in redacted_text
    assert "CH93 0076 2011 6238 5295 7" not in redacted_text
    assert "+41 79 123 45 67" not in redacted_text
    assert "beat.meier@bluewin.ch" not in redacted_text
    assert "[AHV_REDACTED_01]" in redacted_text

    # Test restoration
    restored_text = anonymizer.restore(redacted_text, redactions)
    assert "756.9284.1029.44" in restored_text
    assert "CH93 0076 2011 6238 5295 7" in restored_text
    print("[OK] PII redaction and restoration verified successfully!")

    # -------------------------------------------------------------
    # Test 2: Language Guardrail (Reject Foreign / Non-Alemannic)
    # -------------------------------------------------------------
    print("\n--- Test 2: Foreign Language Guardrail ---")
    french_sample = "Bonjour monsieur le juge, mon propriétaire refuse de réparer le toit et je voudrais faire opposition."
    try:
        dialect_parser.parse(french_sample)
        assert False, "French input should have been rejected by language guardrail!"
    except NonAlemannicLanguageError as e:
        print(f"[OK] Correctly rejected foreign language: {e}")

    # -------------------------------------------------------------
    # Test 3: Four Cantonal Alemannic Dialects
    # -------------------------------------------------------------
    print("\n--- Test 3: Multi-Cantonal Normalization & Ingestion ---")
    test_samples = [
        ("ZH", "Sali zäme, mini Wöschchuchi isch sit zwoo Wuche voll Schimmel und d'Heizig im dritte Stock lauft nüüt meh ghörig. Ich han de Verwaltig scho drüü Mal aglüütet, aber die mached eifach nüüt."),
        ("BE", "Grüessech wohl, mir hei im Quartier vernoo, dass dr Nachber e grossi Autowerkstatt mit Spritzwärch ir Wohnzone boue wott. Äuä spint dä ganz! Dä Lärm u d'Abgas si für üsi Ching e Katastrophe."),
        ("BS", "Sälü zämme, ich bi geschter bim Schugger gsi, wäje mim Chef wo mir sit drei Mönet d'Überstunde nit zahlt und mir mit Kündigung droht. Er het gseit das sig vorig und mir händ kai Rächt druff."),
        ("SG", "Hoi mitenand, de Nachber lauft d'Chreissägi jede Sunntig am Morge ab de Sibni diräkt bim Bomm a de Grundstücksgränze. Mir hend scho mehrmols gredt, aber er seit er heg s'Rächt dezue.")
    ]

    for expected, sample in test_samples:
        res = dialect_parser.parse(sample)
        print(f"Detected: {res.canton_code} ({res.dialect_name}), Confidence: {res.confidence}")
        assert res.canton_code == expected

        # Normalization via pooled client (v2.0 returns 4-tuple with performance metrics)
        norm_text, provider, model_used, perf = await apertus_client.normalize_dialect(
            raw_text=sample,
            canton_code=res.canton_code,
            dialect_name=res.dialect_name
        )
        assert "ß" not in norm_text, "Found forbidden 'ß' in Swiss text!"
        assert perf["tokens_per_second"] > 0

    print("[OK] All 4 Alemannic varieties normalized without error.")

    # -------------------------------------------------------------
    # Test 4: New Statutory Domains (DBG-132, SchKG-82, KVG-64)
    # -------------------------------------------------------------
    print("\n--- Test 4: Expanded Statutory Index Alignment ---")
    
    # 4a: Tax / DBG-132
    tax_claim = "Ich han geschter d'Steuerveranlagung vom kantonalen Steueramt übercho und wott fristgerecht Einsprache erheben wägem Einkommen und de Abzüg."
    tax_res = legal_mapper.map_statutes(tax_claim)
    tax_ids = [a.article_id for a in tax_res.matched_articles]
    print("Tax claim matched:", tax_ids)
    assert "DBG-132" in tax_ids, "Failed to match DBG-132 for tax claim"

    # 4b: Debt / SchKG-82
    debt_claim = "De Gläubiger verlangt provisorische Rechtsöffnung gestützt uf e unterzeichneti Schuldanerkennung und en Darlehensvertrag."
    debt_res = legal_mapper.map_statutes(debt_claim)
    debt_ids = [a.article_id for a in debt_res.matched_articles]
    print("Debt claim matched:", debt_ids)
    assert "SchKG-82" in debt_ids, "Failed to match SchKG-82 for Rechtsöffnung"

    # 4c: Health / KVG-64
    health_claim = "Mini Krankenkasse verweigeret d'Kostenübernahme für d'Behandlung und ich han zuedem e Prämienverbilligung beantreit."
    health_res = legal_mapper.map_statutes(health_claim)
    health_ids = [a.article_id for a in health_res.matched_articles]
    print("Health claim matched:", health_ids)
    assert "KVG-64" in health_ids, "Failed to match KVG-64 for healthcare claim"

    print("[OK] DBG-132, SchKG-82, and KVG-64 statutory alignments verified!")

    # -------------------------------------------------------------
    # Test 5: Cryptographic Attestation
    # -------------------------------------------------------------
    print("\n--- Test 5: SHA-256 Cryptographic Attestation ---")
    cert = attestation_service.generate_certificate(
        raw_text=test_samples[0][1],
        normalized_text="Sehr geehrte Damen und Herren...",
        canton_code="ZH",
        articles=tax_res.matched_articles,
        model_id=settings.APERTUS_MODEL
    )
    assert attestation_service.verify_certificate(cert.model_dump()) is True
    print(f"[OK] Certificate {cert.audit_id} verified with valid HMAC seal.")

    # -------------------------------------------------------------
    # Test 6: HelvetiaVeritas v2.0 Multi-Model & Telemetry
    # -------------------------------------------------------------
    print("\n--- Test 6: Multi-Model Inference (70B vs 8B) & Telemetry ---")
    
    # 6a: Test 70B
    norm_70b, prov_70b, model_70b, perf_70b = await apertus_client.normalize_dialect(
        raw_text=test_samples[0][1],
        canton_code="ZH",
        dialect_name="Züritüütsch",
        model_selection="apertus-1.5-70b"
    )
    print(f"70B Model: {model_70b}, TTFT: {perf_70b['ttft_ms']}ms, Latency: {perf_70b['total_duration_ms']}ms, tok/s: {perf_70b['tokens_per_second']}")
    assert "70B" in model_70b
    assert perf_70b["tokens_per_second"] > 0

    # 6b: Test 8B
    norm_8b, prov_8b, model_8b, perf_8b = await apertus_client.normalize_dialect(
        raw_text=test_samples[0][1],
        canton_code="ZH",
        dialect_name="Züritüütsch",
        model_selection="apertus-1.5-8b"
    )
    print(f"8B Model: {model_8b}, TTFT: {perf_8b['ttft_ms']}ms, Latency: {perf_8b['total_duration_ms']}ms, tok/s: {perf_8b['tokens_per_second']}")
    assert "8B" in model_8b
    assert perf_8b["tokens_per_second"] > 0
    print("[OK] Multi-Model resolution and performance telemetry verified!")

    # -------------------------------------------------------------
    # Test 7: Official Swiss Audit PDF Dossier Generation
    # -------------------------------------------------------------
    print("\n--- Test 7: Sovereign Audit Dossier PDF Generation ---")
    pdf_bytes = attestation_service.generate_audit_pdf(
        certificate=cert,
        normalized_text=norm_70b,
        raw_text=test_samples[0][1],
        canton_name="Zürich",
        canton_code="ZH",
        articles=tax_res.matched_articles,
        performance=perf_70b
    )
    assert len(pdf_bytes) > 2000, f"Expected valid PDF binary > 2000 bytes, got {len(pdf_bytes)}"
    assert pdf_bytes.startswith(b"%PDF-"), "Invalid PDF binary header!"
    print(f"[OK] Audit Dossier PDF generated successfully ({len(pdf_bytes)} bytes) with valid %PDF- magic bytes.")

    print("\n=======================================================")
    print(">>> ALL HELVETIAVERITAS v2.0 ENTERPRISE TESTS PASSED! <<<")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(main())
