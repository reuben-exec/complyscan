"""Core application configuration and settings."""
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env BEFORE anything else (class-level os.getenv runs at class definition time)
load_dotenv()

DISCLAIMER = "Advisory tool only \u2014 not a substitute for an official NABH assessment."


class Settings(BaseModel):
    """Application settings."""

    # App metadata
    app_name: str = "ComplyScan"
    app_version: str = "0.1.0"

    # Cloudflare Workers AI
    cf_api_token: str = os.getenv("CF_API_TOKEN", "")
    cf_account_id: str = os.getenv("CF_ACCOUNT_ID", "")
    cf_ocr_model: str = "@cf/ocr"
    cf_llm_model: str = os.getenv("CF_LLM_MODEL", "@cf/meta/llama-3.3-70b-instruct-fp8-fast")

    # ── Score thresholds (0-1 scale, single source of truth) ──────────
    # Used by: engine.py (Pass 1), logic.py, analyzer.py (Pass 2), generator.py
    score_compliant: float = 0.80       # >= this = COMPLIANT
    score_partial: float = 0.50         # >= this = PARTIAL
    score_noncompliant_floor: float = 0.10  # >= this = NON_COMPLIANT; below = NOT_FOUND

    # ── Frontend UI display thresholds (0-1 scale, display-only) ──────
    # Deliberately lower than backend to avoid harsh visual appearance.
    # Used by: utils.ts, ComplianceGauge.tsx
    ui_compliant: float = 0.70          # >= this = green
    ui_partial: float = 0.40            # >= this = amber

    # ── Fuzzy matching (Pass 1) ──────────────────────────────────────
    fuzzy_enabled: bool = True
    fuzzy_threshold: float = 0.85       # minimum SequenceMatcher ratio
    fuzzy_discount: float = 0.5         # fuzzy hits count as this fraction of exact hits

    # ── Cross-validation ─────────────────────────────────────────────
    cross_validation_boost: float = 0.03   # max boost when >= 50% related are COMPLIANT
    cross_validation_penalty: float = 0.02  # penalty when >= 70% related are NOT_FOUND

    # ── LLM semantic analysis ────────────────────────────────────────
    llm_enabled: bool = True
    llm_confidence_threshold: float = 0.7
    llm_timeout: int = 60

    # Tiered confidence thresholds for LLM overrides
    llm_threshold_notfound_to_compliant: float = 0.85
    llm_threshold_partial_to_compliant: float = 0.75
    llm_threshold_noncomp_to_compliant: float = 0.80

    # Knowledge base paths
    hic_data_path: str = "data/knowledge_base/HIC"
    pre_data_path: str = "data/knowledge_base/PRE"

    # Report settings
    reports_output_path: str = "output/reports"


settings = Settings()
