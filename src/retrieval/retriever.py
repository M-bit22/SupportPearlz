
"""Retrieve relevant document chunks from FAISS."""

from src.config import TOP_K
from src.retrieval.vector_store import load_vector_store


def get_retriever():
    """Create a retriever using the persisted FAISS index."""

    vector_store = load_vector_store()

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    return retriever
