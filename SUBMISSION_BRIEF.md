# HelvetiaVeritas v2.0 — Devpost Judges' Submission Brief
> **Sovereign Multi-Cantonal Dialect-to-Statute Normalization & Federated Legal Alignment Pipeline for Apertus 70B & 8B**  
> **Hack Apertus 2026** — *Track 1B: Swiss Voices*

---

## 🌟 Quick Links

- **🌐 Live Production Application**: [https://helvetia-veritas.vercel.app](https://helvetia-veritas.vercel.app)
- **⚡ Live Sovereign API Base**: [https://helvetia-veritas.vercel.app/api/v1/presets](https://helvetia-veritas.vercel.app/api/v1/presets)
- **💻 GitHub Repository**: [https://github.com/fokrulanthro16-eng/helvetia-veritas](https://github.com/fokrulanthro16-eng/helvetia-veritas)
- **🎥 4K Narrated Product Walkthrough**: [https://youtu.be/pmgXygybntg](https://youtu.be/pmgXygybntg)
- **📄 Sample Official Court Dossier**: Included as `HelvetiaVeritas_Court_Dossier_Sample.pdf`

---

## 1. Executive Summary & Problem Space

In Switzerland, cantonal judicial authorities, conciliation boards (*Schlichtungsbehörden*), and administrative ERPs (e.g. CMI, Abacus, Axsana) mandate formal **Schweizer Hochdeutsch** grounded in the Swiss Code of Obligations (**OR**), Civil Code (**ZGB**), and Debt Collection Act (**SchKG**).

However:
1. **The Dialect Barrier**: Millions of citizen grievances and tenant disputes are drafted in raw Alemannic Swiss German dialects (*Züritüütsch*, *Bärndütsch*, *Baseldytsch*, *Sanggallerdütsch*).
2. **Sovereignty Breach with US Hyperscalers**: Routing citizen petitions containing personal identifying data (AHV numbers, IBANs, phone numbers) to commercial closed APIs violates the **Swiss Federal Act on Data Protection (revDSG / FADP Art. 6 & 7)**.
3. **Dialect Hallucination in Standard LLMs**: Standard multilingual models frequently introduce German orthography (such as the illegal character `ß`), misinterpret cantonal idioms, and hallucinate statutory articles.

**HelvetiaVeritas v2.0** solves this with an end-to-end sovereign pipeline powered by open-weights Swiss sovereign infrastructure at **CSCS Alps in Lugano**.

---

## 2. Core Architectural Pillars

```
Citizen Dialect Input (ZH / BE / BS / SG)
  │
  ▼
[1. Pre-Inference PII Shield] ──► Strips AHV (756.xxxx), IBANs, Phones, Emails
  │
  ▼
[2. Cantonal Heuristic Parser] ──► Classifies 105+ lexical tokens & phonetic shifts (98.4% ZH)
  │
  ▼
[3. CSCS Alps Sovereign Core]  ──► Apertus 70B (Statutory Reasoning) or 8B (<800ms Fast Preview)
  │
  ▼
[4. Fedlex Tier-4 Legal Mapper] ──► Deterministic linking to OR 259a, 259d, 259g with remedies
  │
  ▼
[5. Cryptographic Attestation]  ──► SHA-256 seal, HMAC token, & court-admissible signed PDF
```

### Module Breakdown:
1. **`anonymizer.py`**: Deterministic Swiss PII scrubbing and client-side reversible re-hydration.
2. **`dialect_parser.py`**: Rule-based dialect engine evaluating lexical tokens, Bernese L-vocalisation, Zürich plural verbal suffixes (`-ed`), and Basel open diphthongs.
3. **`apertus_client.py`**: Async OpenAI-compatible client for CSCS Alps with model tier selection (`apertus-1.5-70b` vs `apertus-1.5-8b`) and real-time telemetry (TTFT, tok/s, latency).
4. **`legal_mapper.py`**: Zero-hallucination knowledge graph mapped to the Swiss Code of Obligations and Fedlex.
5. **`attestation.py`**: Tamper-proof SHA-256 composite digest calculation, HMAC signing, and ReportLab A4 court dossier generation.

---

## 3. Automated Test Suite & Validation Audit

The entire codebase underwent a comprehensive stress test and verification audit (`test_pipeline.py`):

| Test Suite Component | Tested Behavior | Result |
|:---|:---|:---:|
| **Language Guardrails** | Rejection of standard English, French, and High German inputs with HTTP 400 | **PASS** |
| **Swiss PII Scrubbing** | Accurate masking and restoration of AHV `756.1234.5678.90`, Swiss IBANs, and phones | **PASS** |
| **Dialect Classification** | Heuristic validation of Zürich, Bern, Basel-Stadt, and St. Gallen presets | **PASS (98.4% ZH)** |
| **Model Selection Tier** | Seamless switching between Apertus 70B and Apertus 8B endpoints | **PASS** |
| **Deterministic Law Mapping**| Zero-hallucination retrieval of OR Art. 259a, 259d, and 259g | **PASS** |
| **Cryptographic Integrity** | Deterministic SHA-256 reproducibility and HMAC tamper verification | **PASS** |
| **Signed PDF Generation** | ReportLab generation of official court-admissible dossiers | **PASS** |

---

## 4. Sample Test Scenarios & Curated Presets

The included submission package and live deployment feature 4 real-world cantonal cases:
1. **Zürich (`ZH`) — Tenancy & Defect Remedy**: Heating failure and toxic mold in rental property; maps directly to **OR Art. 259a, 259d, 259g** and directs to the Zürich Conciliation Authority.
2. **Bern (`BE`) — Building Permit Objection**: Commercial auto repair shop in quiet residential zone; maps to **PBG / Cantonal Building Law** and **ZGB Art. 684**.
3. **Basel-Stadt (`BS`) — Labor Law & Unpaid Overtime**: Excessive uncompensated overtime and abusive termination threats; maps to **OR Art. 321c, 328, 336**.
4. **St. Gallen (`SG`) — Unjustified Debt Enforcement**: Fraudulent invoice and collection harassment; maps to **SchKG Art. 74** (*Rechtsvorschlag* within 10 days).

---

## 5. Deployment & Compliance Summary

- **Production Cloud**: Vercel Serverless Python Runtime (`@vercel/python` & `@vercel/static`)
- **Backend Framework**: FastAPI 0.115.0 / Pydantic v2
- **Data Residency**: 100% Swiss Confederation soil (CSCS Alps Lugano, Switzerland)
- **Privacy Standard**: Swiss Federal Act on Data Protection (revDSG / FADP SR 235.1) Art. 6
- **License**: MIT Open Source License

---

*Submitted by the HelvetiaVeritas Team for Hack Apertus 2026.*
