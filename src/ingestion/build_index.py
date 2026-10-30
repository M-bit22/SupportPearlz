"""Build and persist the FAISS vector index."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import (
    GOOGLE_API_KEY,
    EMBEDDING_MODEL,
    VECTOR_STORE_DIR,
    validate_config,
)
from src.ingestion.loaders import load_documents
from src.ingestion.chunking import split_documents


def build_vector_index() -> FAISS:
    """Load documents, split them, embed them, and save the FAISS index."""

    validate_config()

    print("Loading documents...")
    documents = load_documents()

    print("Splitting documents...")
    chunks = split_documents(documents)

    print("Initializing embedding model...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )

    print("Creating FAISS vector index...")
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    print("Saving vector index...")
    vector_store.save_local(str(VECTOR_STORE_DIR))

    print(f"Index successfully saved to: {VECTOR_STORE_DIR}")

    return vector_store


if __name__ == "__main__":
    build_vector_index()