
"""Gemini-powered Retrieval-Augmented Generation chain."""

from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import GOOGLE_API_KEY, CHAT_MODEL
from src.chains.prompts import RAG_PROMPT
from src.chains.memory import get_conversation_context
from src.retrieval.retriever import get_retriever


def format_documents(documents) -> str:
    """Format retrieved documents with their source information."""

    formatted_documents = []

    for document in documents:
        source = document.metadata.get("source", "Unknown")

        formatted_documents.append(
            f"Source: {source}\n"
            f"Content: {document.page_content}"
        )

    return "\n\n".join(formatted_documents)


def get_rag_chain():
    """Create the RAG question-answering function."""

    retriever = get_retriever()

    llm = ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
    )

    def answer_question(
        question: str,
        chat_history=None,
    ) -> dict:
        """Retrieve context and generate an answer using chat history."""

        if chat_history is None:
            chat_history = []

        formatted_history = get_conversation_context(
            messages=chat_history,
            max_messages=10,
        )

        # Retrieve relevant knowledge-base documents.
        documents = retriever.invoke(question)

        context = format_documents(documents)

        prompt = RAG_PROMPT.invoke(
            {
                "chat_history": formatted_history,
                "context": context,
                "question": question,
            }
        )

        response = llm.invoke(prompt)

        sources = list(
            dict.fromkeys(
                document.metadata.get("source", "Unknown")
                for document in documents
                if document.metadata.get("source")
            )
        )

        return {
            "question": question,
            "answer": response.content,
            "sources": sources,
            "retrieved_documents": documents,
        }

    return answer_question
