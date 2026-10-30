"""Split loaded documents into smaller text chunks."""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """Split documents while preserving their metadata."""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Document splitting produced no chunks.")

    print(f"Created {len(chunks)} chunks.")

    return chunks