"""
memory/window.py

The simplest possible fix for unbounded history growth: keep only the most
recent N messages. Cheap and immediate, but it has no memory of anything
older than the window.
"""

from __future__ import annotations


def trim_to_window(messages: list[dict], max_messages: int = 10) -> list[dict]:
    """
    Return at most `max_messages` messages: the system message (if the first
    message has role "system"), plus the most recent messages from the rest
    of the list. Older messages are dropped entirely, not summarized.
    """
    if not messages:
        return []

    if messages[0]["role"] == "system":
        system_msg, rest = messages[0], messages[1:]
        budget = max_messages - 1
        return [system_msg] + rest[-budget:] if budget > 0 else [system_msg]

    return messages[-max_messages:]
