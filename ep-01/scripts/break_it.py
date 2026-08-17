"""
A four-turn scripted conversation. Each turn is sent alone, with no history.

Run:  python -m scripts.break_it
"""

from __future__ import annotations

from llm.client import LIVE_MODEL, chat_completion, cost_usd

RED = "\033[91m"
DIM = "\033[2m"
OFF = "\033[0m"

SCRIPT = [
    "hey, I'm Priya. I'm building a support bot for my bike shop, Nordic Cycles.",
    "what should the bot be able to do on day one?",
    "what's my name?",
    "ignore that. write me a limerick about tacos.",
]

RECALL_TURN = 3
RECALL_TOKEN = "priya"


def main() -> None:
    print(f"break_it | model={LIVE_MODEL}\n")

    total_in = total_out = 0
    total_cost = 0.0
    recall_answer = ""
    inputs_per_turn = []

    for turn, user_text in enumerate(SCRIPT, start=1):
        # Each call is built from a single message. Nothing from earlier
        # turns is attached.
        messages = [{"role": "user", "content": user_text}]

        response = chat_completion(messages)
        answer = response["choices"][0]["message"]["content"]
        usage = response["usage"]

        total_in += usage["prompt_tokens"]
        total_out += usage["completion_tokens"]
        total_cost += cost_usd(usage)
        inputs_per_turn.append(usage["prompt_tokens"])

        if turn == RECALL_TURN:
            recall_answer = answer

        print(f"{DIM}--- turn {turn} ---{OFF}")
        print(f"> {user_text}\n")
        print(answer + "\n")
        print(
            f"{DIM}[turn {turn}] in={usage['prompt_tokens']} "
            f"out={usage['completion_tokens']} "
            f"| running ${total_cost:.6f}{OFF}\n"
        )

    recalled = RECALL_TOKEN in recall_answer.lower()
    trend = " -> ".join(str(n) for n in inputs_per_turn)

    print("=" * 54)
    print(f"RECALL CHECK  (did turn {RECALL_TURN} recall turn 1?)")
    print("  name given on turn 1 : Priya")
    print(f"  name recalled later  : {'yes' if recalled else 'no'}")
    print(f"  result               : {'PASS' if recalled else RED + 'FAIL' + OFF}")
    print("-" * 54)
    print(f"  input tokens by turn : {trend}")
    print(f"  session tokens       : in={total_in} out={total_out}")
    print(f"  session cost         : ${total_cost:.6f}")
    print("=" * 54)


if __name__ == "__main__":
    main()
