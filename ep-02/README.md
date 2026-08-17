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
python -m app.chat_with_window     # fixed sliding window
python -m app.chat_with_summary    # rolling summary
```

Both are interactive. Type a message, press enter, type `quit` to exit.

## Files

- `llm/client.py` — the OpenAI wrapper used by every script and app here.
- `memory/window.py` — `trim_to_window(messages, max_messages=10)`.
- `memory/summarizer.py` — `RollingMemory` and `extract_state_summary`.
- `app/chat_with_window.py`, `app/chat_with_summary.py` — interactive REPLs.
- `scripts/measure_growth.py` — naive full-history baseline, prints per-turn
  token and cost growth.
- `scripts/break_window.py` — runs a seven-turn conversation through the
  fixed window and shows what happens when an early fact ages out.
- `scripts/fix_with_summary.py` — the same conversation through
  `RollingMemory`, showing the fact surviving in the summary block.
