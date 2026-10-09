"""
HelvetiaVeritas (CantonalAudit AI) - Sovereign Legal Pipeline Entrypoint
=========================================================================
FastAPI application exposing multi-cantonal dialect normalization,
statutory Swiss legal alignment (ZGB, OR, SchKG), and cryptographic FADP audit receipts.
"""

import sys
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.core.dialect_parser import dialect_parser, NonAlemannicLanguageError
from app.core.apertus_client import apertus_client
from app.core.legal_mapper import legal_mapper
from app.core.anonymizer import anonymizer
from app.services.attestation import attestation_service
from app.schemas.audit_schema import (
    HealthStatus,
    NormalizationRequest,
    NormalizationResponse,
    InferencePerformanceMetrics,
    PresetScenario,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("helvetia_veritas.main")

start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager ensuring graceful startup and pooled client shutdown."""
    logger.info("HelvetiaVeritas sovereign legal kernel online (FastAPI lifespan started).")
    yield
    logger.info("Closing Apertus pooled connections and freeing resources...")
    await apertus_client.close()
    logger.info("All connection pools cleanly closed. Zero memory leaks.")


# FastAPI application initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_TAGLINE,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware (Enable for sovereign cantonal intranet & web clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-curated real-world Swiss citizen grievance scenarios
CURATED_PRESETS: List[PresetScenario] = [
    PresetScenario(
        id="zh-tenancy-mold",
        title="Zürich: Mietzinsstreitigkeit wegen Schimmel & Heizungsausfall",
        canton="ZH",
        category="Mietrecht (Tenancy)",
        description="Mieter meldet massiven Schimmelbefall und Ausfall der Heizung; Liegenschaftsverwaltung ignoriert Mängelrüge.",
        dialect_sample=(
            "Sali zäme, mini Wöschchuchi isch sit zwoo Wuche voll Schimmel und d'Heizig im dritte Stock "
            "lauft nüüt meh ghörig. Ich han de Verwaltig scho drüü Mal aglüütet, aber die mached eifach nüüt "
            "und händ geschter sogar abghänkt! Chinde huested scho wägem Gstank. Ich han am 1. Oktober CHF 2'400.- "
            "Mietzins zahlt und wott jetzt wüsse, wie ich de Mietzins chan hinterlege oder reduziere."
        ),
        expected_statutes=["Art. 259a OR", "Art. 259d OR", "Art. 259g OR"]
    ),
    PresetScenario(
        id="be-building-permit",
        title="Bern: Baurechtliche Einsprache gegen Gewerbebetrieb im Wohnquartier",
        canton="BE",
        category="Öffentliches Baurecht & Nachbarrecht",
        description="Nachbarn wehren sich gegen ein publiziertes Baugesuch für eine lärmige Autowerkstatt in der ruhigen Wohnzone.",
        dialect_sample=(
            "Grüessech wohl, mir hei im Quartier vernoo, dass dr Nachber e grossi Autowerkstatt mit Spritzwärch "
            "ir Wohnzone boue wott. Äuä spint dä ganz! Dä Lärm u d'Abgas si für üsi Ching e Katastrophe. "
            "Mir wöi geng e ruhigi Wohnstrass bhalte u wüsse nid, bis wenn mir d'Einsprache bi dr Gmeind muesch "
            "ireiche u was für Paragraphe mir bruuche."
        ),
        expected_statutes=["Art. 684 ZGB", "Kantonales PBG", "Art. 8 ZGB"]
    ),
    PresetScenario(
        id="bs-labor-overtime",
        title="Basel: Lohnausstand & Schikane wegen unbezahlter Überstunden",
        canton="BS",
        category="Arbeitsrecht (Labor Law)",
        description="Arbeitnehmer fordert Vergütung von 140 geleisteten Überstunden; Arbeitgeber droht mit fristloser Kündigung.",
        dialect_sample=(
            "Sälü zämme, ich bi geschter bim Schugger gsi, wäje mim Chef wo mir sit drei Mönet d'Überstunde "
            "(über 140 Stunde) nit zahlt und mir mit Kündigung droht, wenn ich nit ruehig bi. Er het gseit das sig vorig "
            "und mir händ kai Rächt druff. Daas cha doch nit verhebe vor Gricht! Ich bruuch e formelli Abmahnig "
            "für s'Arbeitsgricht."
        ),
        expected_statutes=["Art. 322 OR", "Art. 328 OR", "Art. 336 OR"]
    ),
    PresetScenario(
        id="sg-property-noise",
        title="St. Gallen: Nachbarrechtsklage wegen Sonntags-Lärmbelästigung",
        canton="SG",
        category="Nachbarrecht (Property Law)",
        description="Eigentümer betreibt regelmässig sonntags schwere Holzverarbeitungsmaschinen an der Grundstücksgrenze.",
        dialect_sample=(
            "Hoi mitenand, de Nachber lauft d'Chreissägi jede Sunntig am Morge ab de Sibni diräkt bim Bomm a de "
            "Grundstücksgränze. Mir hend scho mehrmols gredt, aber er seit er heg s'Rächt dezue uf sim Grund. "
            "Das isch e Ruumstörig wo mer nöd länger dulde chönd. Ich bruuche e Verzeigig und e Unterlassigsklag "
            "bim Friedensrichter."
        ),
        expected_statutes=["Art. 684 ZGB", "Art. 679 ZGB", "Art. 2 ZGB"]
    )
]


@app.get("/health", response_model=HealthStatus, tags=["System Health"])
async def health_check():
    """System health check and upstream sovereign cluster readiness."""
    return HealthStatus(
        status="OPERATIONAL",
        version=settings.PROJECT_VERSION,
        cscs_endpoint=settings.APERTUS_BASE_URL,
        cscs_model=settings.APERTUS_MODEL,
        uptime_seconds=round(time.time() - start_time, 2),
        dialect_rules_loaded=len(dialect_parser.lexical_lookup),
        legal_articles_loaded=len(legal_mapper.articles_corpus)
    )


@app.get("/api/v1/presets", response_model=List[PresetScenario], tags=["Curated Scenarios"])
async def get_presets():
    """Retrieve pre-curated multi-cantonal citizen grievance scenarios."""
    return CURATED_PRESETS


@app.post("/api/v1/normalize", response_model=NormalizationResponse, tags=["Sovereign Normalization Pipeline"])
async def normalize_citizen_petition(request: NormalizationRequest):
    """
    Executes the complete 4-stage sovereign legal normalization pipeline:
    1. Deterministic Cantonal Heuristic Dialect Parser (ZH, BE, BS, SG)
    2. Apertus 70B Sovereign Dialect-to-Statute Normalization via CSCS Alps
    3. Swiss Statutory Mapper for ZGB, OR, and SchKG articles
    4. SHA-256 Tamper-Evident Cryptographic Compliance Certificate
    """
    start_ts = time.time()
    try:
        raw_text = request.raw_dialect_text.strip()
        if len(raw_text) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Die Eingabe darf nicht leer sein. Bitte erfassen Sie Ihr Anliegen im Schweizer Dialekt."
            )
        if len(raw_text) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Die Eingabe ist zu kurz (mindestens 5 Zeichen für eine kantonale Heuristik-Analyse erforderlich)."
            )

        # Stage 1: Cantonal Dialect Classification (with Language Guardrail)
        try:
            canton_result = dialect_parser.parse(
                text=raw_text,
                canton_hint=request.canton_hint
            )
        except NonAlemannicLanguageError as lang_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(lang_err)
            )

        # Stage 1b: revDSG / FADP PII Sanitization (Redact AHV, IBAN, Phone, Email)
        sanitized_input, redaction_map, pii_count = anonymizer.redact(raw_text)

        # Stage 2: Upstream CSCS Apertus Normalization (Pooled, Multi-Model, XML-Isolated)
        normalized_sanitized, provider, model_used, telemetry = await apertus_client.normalize_dialect(
            raw_text=sanitized_input,
            canton_code=canton_result.canton_code,
            dialect_name=canton_result.dialect_name,
            domain_hint=request.domain_hint,
            model_alias=request.model_selection
        )

        # Performance Telemetry
        performance_metrics = InferencePerformanceMetrics(**telemetry)

        # Re-hydrate sanitized entities for local citizen view
        final_normalized_text = anonymizer.restore(normalized_sanitized, redaction_map)

        # Stage 3: Swiss Statutory Alignment (ZGB / OR / SchKG / DBG / KVG)
        legal_result = legal_mapper.map_statutes(
            normalized_text=final_normalized_text,
            raw_text=raw_text,
            canton_code=canton_result.canton_code,
            domain_hint=request.domain_hint
        )

        # Stage 4: Cryptographic FADP / revDSG Compliance Attestation
        certificate = attestation_service.generate_certificate(
            raw_text=raw_text,
            normalized_text=final_normalized_text,
            canton_code=canton_result.canton_code,
            articles=legal_result.matched_articles,
            model_id=model_used
        )

        processing_duration = round((time.time() - start_ts) * 1000.0, 2)

        return NormalizationResponse(
            success=True,
            raw_input=raw_text,
            canton_analysis=canton_result,
            normalized_hochdeutsch=final_normalized_text,
            legal_analysis=legal_result,
            attestation=certificate,
            performance=performance_metrics,
            processing_time_ms=processing_duration,
            upstream_provider=provider,
            model_used=model_used
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error during dialect normalization pipeline: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sovereign pipeline error: {str(exc)}"
        )


@app.post("/api/v1/attest/pdf", tags=["Attestation Verification"])
async def export_audit_dossier_pdf(response_data: NormalizationResponse):
    """Generates an official tamper-evident Swiss Sovereign Audit Dossier PDF."""
    try:
        pdf_bytes = attestation_service.generate_audit_pdf(
            certificate=response_data.attestation,
            normalized_text=response_data.normalized_hochdeutsch,
            raw_text=response_data.raw_input,
            canton_name=response_data.canton_analysis.canton_name,
            canton_code=response_data.canton_analysis.canton_code,
            articles=response_data.legal_analysis.matched_articles,
            performance=response_data.performance.model_dump()
        )
        filename = f"HelvetiaVeritas_Audit_{response_data.attestation.audit_id[:8]}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as exc:
        logger.exception("Error generating audit PDF: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF Generation failed: {str(exc)}"
        )


@app.post("/api/v1/verify", tags=["Attestation Verification"])
async def verify_certificate(certificate: Dict):
    """Verifies a downloadable SHA-256 cryptographic audit receipt for courts and ERPs."""
    is_valid = attestation_service.verify_certificate(certificate)
    return {
        "valid": is_valid,
        "status": "AUTHENTIC_CSCS_ISSUED" if is_valid else "INVALID_OR_TAMPERED",
        "verification_timestamp": time.time()
    }


# Mount Frontend UI static files
if settings.FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(settings.FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = settings.FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "HelvetiaVeritas API Online. UI index.html not yet built."}

    @app.get("/style.css", include_in_schema=False)
    async def serve_style():
        css_path = settings.FRONTEND_DIR / "style.css"
        if css_path.exists():
            return FileResponse(css_path, media_type="text/css")
        raise HTTPException(status_code=404, detail="style.css not found")

    @app.get("/app.js", include_in_schema=False)
    async def serve_script():
        js_path = settings.FRONTEND_DIR / "app.js"
        if js_path.exists():
            return FileResponse(js_path, media_type="application/javascript")
        raise HTTPException(status_code=404, detail="app.js not found")

    @app.get("/api/docs", include_in_schema=False)
    async def serve_api_docs():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
