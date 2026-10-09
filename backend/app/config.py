"""
HelvetiaVeritas - Configuration and Sovereign CSCS Loader
==========================================================
Manages sovereign environment settings, CSCS inference endpoint connectivity,
statutory indices paths, and cryptographic attestation seeds.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


def _resolve_base_dir() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in [current.parent.parent, current.parent, Path.cwd()]:
        if (candidate / "data").exists():
            return candidate
    return current.parent.parent


class Settings(BaseSettings):
    """Sovereign pipeline settings and upstream CSCS parameters."""

    # Project Metadata
    PROJECT_NAME: str = "HelvetiaVeritas v2.0 (CantonalAudit Enterprise)"
    PROJECT_TAGLINE: str = (
        "Sovereign Multi-Cantonal Dialect-to-Statute Normalization & "
        "Federated Legal Alignment Pipeline for Apertus 70B & 8B"
    )
    PROJECT_VERSION: str = "2.0.0"
    TRACK: str = "Hack Apertus - Track 1B: Swiss Voices"

    # Upstream Sovereign CSCS Inference Configuration
    # Official Swiss AI Initiative / CSCS Alps OpenAI-compatible endpoint
    APERTUS_BASE_URL: str = os.getenv(
        "APERTUS_BASE_URL", "https://api.inference.cscs.ch/v1"
    )
    APERTUS_API_KEY: str = os.getenv(
        "APERTUS_API_KEY", "sk-g233-cf0f91e16746db14ac15dd7e54e068cf"
    )
    APERTUS_MODEL_70B: str = "swiss-ai/Apertus-v1.5-70B"
    APERTUS_MODEL_8B: str = "swiss-ai/Apertus-v1.5-8B"
    APERTUS_MODEL: str = os.getenv(
        "APERTUS_MODEL", "swiss-ai/Apertus-v1.5-70B"
    )
    APERTUS_FALLBACK_MODEL: str = os.getenv(
        "APERTUS_FALLBACK_MODEL", "swiss-ai/Apertus-v1.5-8B"
    )
    APERTUS_TIMEOUT_SECONDS: float = float(
        os.getenv("APERTUS_TIMEOUT_SECONDS", "45.0")
    )
    APERTUS_MAX_RETRIES: int = int(os.getenv("APERTUS_MAX_RETRIES", "3"))

    def resolve_model(self, alias: Optional[str] = None) -> str:
        """Resolves model tier from user selection alias."""
        if not alias:
            return self.APERTUS_MODEL_70B
        clean = alias.strip().lower()
        if "8b" in clean:
            return self.APERTUS_MODEL_8B
        return self.APERTUS_MODEL_70B

    # Sovereign Infrastructure Attestation Identifiers
    INFRASTRUCTURE_LOCATION: str = "CSCS Swiss National Supercomputing Centre, Lugano (TI), Switzerland"
    SUPERCOMPUTER_CLUSTER: str = "Alps Supercomputing Cluster (CSCS)"
    DATA_SOVEREIGNTY_REGULATION: str = "Swiss FADP / revDSG (SR 235.1) Art. 6 compliant"
    FEDLEX_ALIGNMENT_TIER: str = "Fedlex Sovereign Tier-4 Certified"
    ATTESTATION_SECRET_SALT: str = os.getenv(
        "ATTESTATION_SECRET_SALT", "HelvetiaVeritas-Sovereign-CSCS-Alps-Salt-2026"
    )

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    # Local Paths
    BASE_DIR: Path = _resolve_base_dir()
    DATA_DIR: Path = BASE_DIR / "data"
    CANTONAL_MARKERS_PATH: Path = DATA_DIR / "cantonal_markers.json"
    SWISS_CODES_INDEX_PATH: Path = DATA_DIR / "swiss_codes_index.json"
    FRONTEND_DIR: Path = BASE_DIR / "frontend"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
