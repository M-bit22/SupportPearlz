"""Load supported documents from the knowledge-base directory."""

from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_core.documents import Document

from src.config import KNOWLEDGE_BASE_DIR


def load_documents() -> list[Document]:
    """Load PDF, DOCX, and TXT files from the knowledge base."""

    documents = []

    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt",
    }

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()

        if extension not in supported_extensions:
            continue

        try:
            if extension == ".pdf":
                loader = PyPDFLoader(str(file_path))

            elif extension == ".docx":
                loader = Docx2txtLoader(str(file_path))

            else:
                loader = TextLoader(
                    str(file_path),
                    encoding="utf-8",
                    autodetect_encoding=True,
                )

            loaded_documents = loader.load()

            for document in loaded_documents:
                document.metadata["source"] = file_path.name
                document.metadata["file_path"] = str(file_path)

            documents.extend(loaded_documents)

            print(f"Loaded: {file_path.name}")

        except Exception as error:
            print(f"Could not load {file_path.name}: {error}")

    if not documents:
        raise ValueError(
            f"No supported documents found in {KNOWLEDGE_BASE_DIR}. "
            "Add PDF, DOCX, or TXT files first."
        )

    return documents