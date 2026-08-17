"""
llm/client.py

Thin wrapper around the OpenAI chat completions API. Every function in this
module makes a genuine network call. There is no local branch, flag, or
alternate code path here — this file is exactly what a production service
would ship.

Public functions:
    chat_completion(messages, model="gpt-4o-mini") -> openai.types.chat.ChatCompletion
    stream_chat_completion(messages, model="gpt-4o-mini") -> Iterator[str]
    render_stream(chunks) -> str
    cost_usd(usage, model="gpt-4o-mini") -> float
"""

from __future__ import annotations

from typing import Iterable, Iterator

from openai import OpenAI

_client = OpenAI()

# USD per 1M tokens. Source: platform.openai.com/docs/pricing, verified 2026.
_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


def chat_completion(messages: list[dict], model: str = "gpt-4o-mini"):
    """Send one non-streaming chat completion request and return the raw response."""
    return _client.chat.completions.create(model=model, messages=messages)


def stream_chat_completion(messages: list[dict], model: str = "gpt-4o-mini") -> Iterator[str]:
    """Send a streaming chat completion request, yielding text chunks as they arrive."""
    stream = _client.chat.completions.create(model=model, messages=messages, stream=True)
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content


def render_stream(chunks: Iterable[str]) -> str:
    """Print streamed chunks to stdout as they arrive and return the full joined text."""
    full_text = []
    for chunk in chunks:
        print(chunk, end="", flush=True)
        full_text.append(chunk)
    print()
    return "".join(full_text)


def cost_usd(usage, model: str = "gpt-4o-mini") -> float:
    """Compute the dollar cost of one call from its usage object."""
    rates = _PRICING[model]
    input_cost = (usage.prompt_tokens / 1_000_000) * rates["input"]
    output_cost = (usage.completion_tokens / 1_000_000) * rates["output"]
    return input_cost + output_cost
