"""
A thin chat client wrapping the OpenAI Chat Completions API.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Iterator, List

LIVE_MODEL = "gpt-4o-mini"

# Published per-million-token pricing for LIVE_MODEL.
PRICE_IN_PER_1M = 0.15
PRICE_OUT_PER_1M = 0.60


def _client():
    from openai import OpenAI          # pip install openai
    from dotenv import load_dotenv     # pip install python-dotenv

    load_dotenv()
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def chat_completion(
    messages: List[Dict[str, str]], model: str = LIVE_MODEL
) -> Dict[str, Any]:
    """Non-streaming completion. Returns the raw OpenAI response dict."""
    resp = _client().chat.completions.create(model=model, messages=messages)
    return resp.model_dump()


def stream_chat_completion(
    messages: List[Dict[str, str]], model: str = LIVE_MODEL
) -> Iterator[Dict[str, Any]]:
    """Streaming completion. Yields OpenAI `chat.completion.chunk` dicts."""
    stream = _client().chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
    )
    for chunk in stream:
        yield chunk.model_dump()


def cost_usd(usage: Dict[str, int]) -> float:
    """Dollar cost of one call at LIVE_MODEL pricing."""
    return (
        usage.get("prompt_tokens", 0) * PRICE_IN_PER_1M
        + usage.get("completion_tokens", 0) * PRICE_OUT_PER_1M
    ) / 1_000_000


def render_stream(chunks: Iterator[Dict[str, Any]], write) -> tuple[str, Dict[str, int]]:
    """Print deltas as they arrive; return the assembled text and the usage block."""
    text_parts: List[str] = []
    usage: Dict[str, int] = {}
    for chunk in chunks:
        if chunk.get("usage"):
            usage = chunk["usage"]
        for choice in chunk.get("choices", []):
            piece = choice.get("delta", {}).get("content")
            if piece:
                text_parts.append(piece)
                write(piece)
    return "".join(text_parts), usage
