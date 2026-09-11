# spine-project

A minimal chat service built on `gpt-4o-mini`. This episode adds two history
management strategies on top of the naive full-transcript append from the
previous episode:

- `memory/window.py` — fixed sliding window, keep only the last N messages.
- `memory/summarizer.py` — rolling state-summary memory, fold old turns into
  a short summary block instead of dropping them.

## Setup

```
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
```

## Run it

```
python -m app.chat_with_window     # fixed sliding window (ep-02)
python -m app.chat_with_summary    # rolling summary (ep-02)
python -m app.chat_optimized       # + caching + routed extraction (ep-03)
```

Both are interactive. Type a message, press enter, type `quit` to exit.

## Files

- `llm/client.py` — the OpenAI wrapper used by every script and app here. `cost_usd` now accounts for cached input tokens (`usage.prompt_tokens_details.cached_tokens`), billed at a discounted rate.
- `memory/window.py` — `trim_to_window(messages, max_messages=10)`.
- `memory/summarizer.py` — `RollingMemory` and `extract_state_summary`. `RollingMemory`'s `model` argument is the model used for compaction calls — pass a cheaper model here to route extraction separately from the main conversation.
- `app/system_prompt.py` — `POLICY_SYSTEM_PROMPT`, a long, fully static system prompt used to demonstrate prompt caching.
- `app/chat_with_window.py`, `app/chat_with_summary.py` — interactive REPLs from ep-02.
- `app/chat_optimized.py` — interactive REPL combining both of this episode's fixes: the static cacheable system prompt, and compaction routed to `gpt-4.1-nano`.
- `scripts/measure_growth.py`, `scripts/break_window.py`, `scripts/fix_with_summary.py` — demonstration scripts from ep-02.
- `scripts/measure_caching.py` — runs the seven-turn conversation with the long static system prompt, printing prompt/cached tokens and cost per turn.
- `scripts/break_caching.py` — the same conversation with a timestamp appended to the system prompt every call, showing caching drop to zero.
- `scripts/route_extraction.py` — runs the same conversation twice, extraction on `gpt-4o-mini` vs `gpt-4.1-nano`, comparing cost and summary quality.
