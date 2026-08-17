"""
A single-turn chatbot. Every message is sent alone, with nothing before it.

Run:  python -m app.chat
"""

from __future__ import annotations

import sys

from llm.client import LIVE_MODEL, cost_usd, render_stream, stream_chat_completion


def _write(piece: str) -> None:
    sys.stdout.write(piece)
    sys.stdout.flush()


def main() -> None:
    print(f"chat | model={LIVE_MODEL}")
    print("ctrl-c to quit\n")

    turn = 0
    total_in = total_out = 0
    total_cost = 0.0

    while True:
        try:
            user_text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return
        if not user_text:
            continue

        turn += 1

        # Each call is built from a single message. Nothing from earlier
        # turns is attached — this is the whole story of this episode.
        messages = [{"role": "user", "content": user_text}]

        _write("\n")
        _, usage = render_stream(stream_chat_completion(messages), _write)
        _write("\n")

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
