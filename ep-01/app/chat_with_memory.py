"""
A chatbot that carries the whole conversation forward. Every call sends the
full running history, not just the newest message.

Run:  python -m app.chat_with_memory
"""

from __future__ import annotations

import sys

from llm.client import LIVE_MODEL, cost_usd, render_stream, stream_chat_completion


def _write(piece: str) -> None:
    sys.stdout.write(piece)
    sys.stdout.flush()


def main() -> None:
    print(f"chat-with-memory | model={LIVE_MODEL}")
    print("ctrl-c to quit\n")

    turn = 0
    total_in = total_out = 0
    total_cost = 0.0
    history: list[dict[str, str]] = []

    while True:
        try:
            user_text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return
        if not user_text:
            continue

        turn += 1

        # The only change from app/chat.py: we append to a running list
        # instead of building a fresh one-item list each time.
        history.append({"role": "user", "content": user_text})

        _write("\n")
        reply, usage = render_stream(stream_chat_completion(history), _write)
        _write("\n")

        history.append({"role": "assistant", "content": reply})

        total_in += usage.get("prompt_tokens", 0)
        total_out += usage.get("completion_tokens", 0)
        total_cost += cost_usd(usage)

        print(
            f"\n[turn {turn}] in={usage.get('prompt_tokens', 0)} "
            f"out={usage.get('completion_tokens', 0)} "
            f"| session in={total_in} out={total_out} "
            f"| running ${total_cost:.6f}\n"
        )


if __name__ == "__main__":
    main()
