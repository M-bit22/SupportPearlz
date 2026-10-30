
"""Application configuration loaded from environment variables and Streamlit secrets."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_setting(name: str, default: str = "") -> str:
    """Read Streamlit Cloud secrets first, then environment variables."""
    try:
        import streamlit as st

        value = st.secrets.get(name)
        if value is not None:
            return str(value)
    except Exception:
        pass

    return os.getenv(name, default)


# API configuration
GOOGLE_API_KEY = get_setting("GOOGLE_API_KEY")

# Gemini models
CHAT_MODEL = get_setting("CHAT_MODEL", "gemini-3.8-flash")
EMBEDDING_MODEL = get_setting(
    "EMBEDDING_MODEL",
    "models/gemini-embedding-001",
)

# RAG configuration
CHUNK_SIZE = int(get_setting("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(get_setting("CHUNK_OVERLAP", "120"))
TOP_K = int(get_setting("TOP_K", "4"))

# Project paths
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"

# Ensure required directories exist
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


def validate_config() -> None:
    """Check that required configuration is available."""
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Add it to .env or Streamlit Cloud Secrets."
        )

    if CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")

    if not 0 <= CHUNK_OVERLAP < CHUNK_SIZE:
        raise ValueError(
            "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE."
        )

    if TOP_K <= 0:
        raise ValueError("TOP_K must be greater than zero.")
