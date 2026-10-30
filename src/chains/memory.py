
"""Conversation memory utilities for SupportPearlz."""

from typing import Dict, List


def format_chat_history(
    messages: List[Dict[str, str]],
    max_messages: int = 10,
) -> str:
    """
    Format recent conversation messages into readable chat history.

    Args:
        messages: Previous conversation messages.
        max_messages: Maximum number of recent messages to include.

    Returns:
        Formatted conversation history.
    """

    if not messages:
        return "No previous conversation."

    recent_messages = messages[-max_messages:]

    formatted_history = []

    for message in recent_messages:
        role = message.get("role", "").lower()
        content = message.get("content", "").strip()

        if not content:
            continue

        if role == "user":
            speaker = "Customer"
        elif role == "assistant":
            speaker = "SupportPearlz Assistant"
        else:
            continue

        formatted_history.append(
            f"{speaker}: {content}"
        )

    if not formatted_history:
        return "No previous conversation."

    return "\n".join(formatted_history)


def get_conversation_context(
    messages: List[Dict[str, str]],
    max_messages: int = 10,
) -> str:
    """Get formatted context from previous conversation messages."""

    return format_chat_history(
        messages=messages,
        max_messages=max_messages,
    )


def clear_conversation_memory(messages: List[Dict[str, str]]) -> None:
    """Clear the existing conversation message list."""

    messages.clear()
