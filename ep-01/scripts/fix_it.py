"""
The same four-turn conversation, but the running history is resent every
call. Watch what that does to correctness — and to the input token count.

Run:  python -m scripts.fix_it
"""

from __future__ import annotations

from llm.client import LIVE_MODEL, chat_completion, cost_usd

GREEN = "\033[92m"
DIM = "\033[2m"
OFF = "\033[0m"

SCRIPT = [
    "hey, I'm Priya. I'm building a support bot for my bike shop, Nordic Cycles.",
    "what should the bot be able to do on day one?",
    "can you remind me what my name is?",
    "and what's the shop called again?",
]

RECALL_TURNS = {3, 4}
RECALL_TOKENS = {3: "priya", 4: "nordic cycles"}


def main() -> None:
    print(f"fix_it | model={LIVE_MODEL}\n")

    total_in = total_out = 0
    total_cost = 0.0
    inputs_per_turn = []
    recall_answers = {}
    history: list[dict[str, str]] = []

    for turn, user_text in enumerate(SCRIPT, start=1):
        # The only change from scripts/break_it.py: we append to a running
        # list instead of building a fresh one-item list each time.
        history.append({"role": "user", "content": user_text})

        response = chat_completion(history)
        answer = response["choices"][0]["message"]["content"]
        usage = response["usage"]

        history.append({"role": "assistant", "content": answer})

        total_in += usage["prompt_tokens"]
        total_out += usage["completion_tokens"]
        total_cost += cost_usd(usage)
        inputs_per_turn.append(usage["prompt_tokens"])

        if turn in RECALL_TURNS:
            recall_answers[turn] = answer

        print(f"{DIM}--- turn {turn} ---{OFF}")
        print(f"> {user_text}\n")
        print(answer + "\n")
        print(
            f"{DIM}[turn {turn}] in={usage['prompt_tokens']} "
            f"out={usage['completion_tokens']} "
            f"| running ${total_cost:.6f}{OFF}\n"
        )

    trend = " -> ".join(str(n) for n in inputs_per_turn)

    print("=" * 54)
    print("RECALL CHECK")
    for turn in sorted(RECALL_TURNS):
        recalled = RECALL_TOKENS[turn] in recall_answers.get(turn, "").lower()
        print(
            f"  turn {turn} recalled '{RECALL_TOKENS[turn]}' : "
            f"{GREEN + 'PASS' + OFF if recalled else 'FAIL'}"
        )
    print("-" * 54)
    print(f"  input tokens by turn : {trend}   <- grows every turn. that's the cost.")
    print(f"  session tokens       : in={total_in} out={total_out}")
    print(f"  session cost         : ${total_cost:.6f}")
    print("=" * 54)


if __name__ == "__main__":
    main()
