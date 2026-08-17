# spine-project

One repo, built across the whole series. Each episode is a git tag.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
```

## Run it

```bash
python -m app.chat              # single-turn chatbot, no memory
python -m app.chat_with_memory  # carries the full conversation forward
python -m scripts.break_it      # scripted: shows the no-memory failure
python -m scripts.fix_it        # scripted: shows correct recall, and its token cost
```

## Tags

- `ep-01` — a chatbot with no memory, a fixed version that carries full
  history, and the token growth that comes with the fix.
