
"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Gemini models
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "models/gemini-embedding-001",
)

# RAG configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "4"))

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
            "GOOGLE_API_KEY is missing. Add it to your .env file."
        )

    if CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")

    if not 0 <= CHUNK_OVERLAP < CHUNK_SIZE:
        raise ValueError(
            "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE."
        )

    if TOP_K <= 0:
        raise ValueError("TOP_K must be greater than zero.")
