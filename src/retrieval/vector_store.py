
"""Load and cache the persisted FAISS vector store."""

import streamlit as st

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import (
    GOOGLE_API_KEY,
    EMBEDDING_MODEL,
    VECTOR_STORE_DIR,
)


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Initialize the embedding model."""

    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )


@st.cache_resource
def load_vector_store() -> FAISS:
    """Load and cache the persisted FAISS index."""

    index_path = VECTOR_STORE_DIR / "index.faiss"

    if not index_path.exists():
        raise FileNotFoundError(
            "FAISS index not found. Run the ingestion pipeline first."
        )

    embeddings = get_embeddings()

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store

