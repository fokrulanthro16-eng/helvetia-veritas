"""
HelvetiaVeritas - Pydantic v2 Strict Request/Response Schemas
=============================================================
Strict validation schemas for multi-cantonal dialect normalization,
statutory cross-referencing, and cryptographic FADP audit receipts.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class NormalizationRequest(BaseModel):
    """Citizen administrative grievance or dialect petition submission."""
    raw_dialect_text: str = Field(
        ...,
        min_length=0,
        max_length=100000,
        description="Raw Swiss German dialect input text (e.g. Züritüütsch, Bärndütsch, Baseldytsch)"
    )
    canton_hint: Optional[str] = Field(
        default=None,
        description="Optional cantonal hint code (e.g., 'ZH', 'BE', 'BS', 'SG') if citizen specified"
    )
    domain_hint: Optional[str] = Field(
        default=None,
        description="Optional domain focus hint (e.g., 'Mietrecht', 'Arbeitsrecht', 'Nachbarrecht')"
    )
    model_selection: Optional[str] = Field(
        default="apertus-1.5-70b",
        description="Model tier: 'apertus-1.5-70b' (Full Legal Reasoning) or 'apertus-1.5-8b' (Rapid Dialect Preview)"
    )
    include_attestation: bool = Field(
        default=True,
        description="Whether to generate the sovereign SHA-256 cryptographic audit receipt"
    )


class LexicalMarkerMatch(BaseModel):
    """Matched dialect lexical token."""
    token: str
    gloss_de: str
    weight: float
    canton: str


class PhonologyRuleMatch(BaseModel):
    """Matched cantonal phonology / morphological rule."""
    rule_name: str
    description: str
    matched_sample: str
    weight: float


class CantonalDialectResult(BaseModel):
    """Heuristic dialect classification analysis."""
    canton_code: str = Field(..., description="Canton ISO code (ZH, BE, BS, SG, or CH-DE)")
    canton_name: str = Field(..., description="Official Canton name")
    dialect_name: str = Field(..., description="Traditional Alemannic dialect designation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Normalized classification confidence score")
    coat_of_arms: str
    cantonal_color: str
    detected_markers: List[LexicalMarkerMatch]
    phonology_matches: List[PhonologyRuleMatch]
    distribution: Dict[str, float] = Field(..., description="Score distribution across cantons")
    dialect_density: float = Field(..., description="Ratio of dialect markers to total tokens")
    word_count: int


class MatchedLegalArticle(BaseModel):
    """Statutory article matched from Swiss Codes Index."""
    article_id: str
    law: str = Field(..., description="ZGB, OR, SchKG, PBG")
    article_number: str
    title_de: str
    domain: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    summary_de: str
    remedy_action_de: str
    competent_authority: str
    fedlex_url: str
    matched_keywords: List[str]


class LegalAnalysisResult(BaseModel):
    """Statutory cross-referencing and judicial remedy mapping."""
    primary_domain: str
    matched_articles: List[MatchedLegalArticle]
    recommended_procedural_steps: List[str]
    competent_authorities: List[str]


class AttestationCertificate(BaseModel):
    """Cryptographic tamper-evident SHA-256 audit receipt for judicial/ERP submission."""
    audit_id: str = Field(..., description="Unique UUIDv4 audit identification")
    timestamp_iso: str = Field(..., description="ISO 8601 UTC timestamp of transformation")
    input_sha256: str = Field(..., description="SHA-256 hash of the citizen raw dialect text")
    normalized_sha256: str = Field(..., description="SHA-256 hash of normalized Schweizer Hochdeutsch text")
    articles_digest_sha256: str = Field(..., description="SHA-256 digest of aligned statutory articles")
    pipeline_composite_hash: str = Field(..., description="Composite SHA-256 pipeline fingerprint")
    signature_token: str = Field(..., description="HMAC cryptographic seal")
    infrastructure: str
    supercomputer: str
    model_id: str
    fadp_revdsg_compliance: str
    fedlex_tier: str
    verification_status: str = Field(default="VERIFIED_TAMPER_EVIDENT")


class InferencePerformanceMetrics(BaseModel):
    """Real-time CSCS Apertus inference latency and throughput telemetry."""
    model_id: str
    model_tier: str
    total_duration_ms: float
    estimated_tokens: int
    tokens_per_second: float
    ttft_ms: float


class NormalizationResponse(BaseModel):
    """Unified pipeline response returned to the frontend and cantonal ERPs."""
    success: bool
    raw_input: str
    canton_analysis: CantonalDialectResult
    normalized_hochdeutsch: str
    legal_analysis: LegalAnalysisResult
    attestation: AttestationCertificate
    performance: InferencePerformanceMetrics
    processing_time_ms: float
    upstream_provider: str
    model_used: str


class PresetScenario(BaseModel):
    """Pre-curated real-world Swiss citizen grievance scenario."""
    id: str
    title: str
    canton: str
    category: str
    description: str
    dialect_sample: str
    expected_statutes: List[str]


class HealthStatus(BaseModel):
    """Service health and CSCS upstream connectivity status."""
    status: str
    version: str
    cscs_endpoint: str
    cscs_model: str
    uptime_seconds: float
    dialect_rules_loaded: int
    legal_articles_loaded: int
