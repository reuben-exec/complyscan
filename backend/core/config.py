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
    cf_llm_model: str = os.getenv("CF_LLM_MODEL", "@cf/meta/llama-3.1-8b-instruct")
    
    # LLM semantic analysis settings
    llm_enabled: bool = True
    llm_confidence_threshold: float = 0.7
    llm_timeout: int = 30

    # Tiered confidence thresholds for LLM overrides
    # Different thresholds depending on Pass 1 status (how much evidence already found)
    llm_threshold_notfound_to_compliant: float = 0.85   # High bar: NOT_FOUND -> COMPLIANT
    llm_threshold_partial_to_compliant: float = 0.75    # Moderate: PARTIAL -> COMPLIANT
    llm_threshold_noncomp_to_compliant: float = 0.80    # High: NON_COMPLIANT -> COMPLIANT
    llm_threshold_refine: float = 0.70                  # Lower: refine within non-compliant range
    
    # Knowledge base paths
    hic_data_path: str = "data/knowledge_base/HIC"
    pre_data_path: str = "data/knowledge_base/PRE"
    
    # Report settings
    reports_output_path: str = "output/reports"


settings = Settings()