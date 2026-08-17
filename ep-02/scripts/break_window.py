"""
scripts/break_window.py

Runs the same seven-turn conversation, but trims to the last 8 messages
before every call using memory.window.trim_to_window. Cheaper than the
naive baseline, but the first turn (the vegetarian constraint) falls out
of the window before the recall question is asked.
"""

from llm.client import chat_completion, cost_usd
from memory.window import trim_to_window
from scripts._conversation import SYSTEM_PROMPT, USER_TURNS

MAX_MESSAGES = 8


def main():
    full_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    total_cost = 0.0

    print(f"{'turn':>4}  {'prompt_tokens':>13}  {'cost_usd':>10}  {'cumulative_usd':>14}")
    for i, user_text in enumerate(USER_TURNS, start=1):
        full_history.append({"role": "user", "content": user_text})
        sent = trim_to_window(full_history, max_messages=MAX_MESSAGES)

        response = chat_completion(messages=sent, model="gpt-4o-mini")
        reply = response.choices[0].message.content
        full_history.append({"role": "assistant", "content": reply})

        turn_cost = cost_usd(response.usage, model="gpt-4o-mini")
        total_cost += turn_cost
        print(
            f"{i:>4}  {response.usage.prompt_tokens:>13}  "
            f"{turn_cost:>10.6f}  {total_cost:>14.6f}"
        )

    final_reply = full_history[-1]["content"]
    print("\nFinal reply to the recall question:")
    print(final_reply)
    print(
        "\nMentions vegetarian:",
        "yes" if "vegetarian" in final_reply.lower() else "no",
    )


if __name__ == "__main__":
    main()
