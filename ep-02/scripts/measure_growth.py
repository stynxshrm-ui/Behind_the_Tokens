"""
scripts/measure_growth.py

Runs the seven-turn conversation with no trimming and no summarization: the
full raw transcript is resent on every call. Prints prompt tokens and cost
per turn so the growth curve is visible before we fix anything.
"""

from llm.client import chat_completion, cost_usd
from scripts._conversation import SYSTEM_PROMPT, USER_TURNS


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    total_cost = 0.0

    print(f"{'turn':>4}  {'prompt_tokens':>13}  {'cost_usd':>10}  {'cumulative_usd':>14}")
    for i, user_text in enumerate(USER_TURNS, start=1):
        messages.append({"role": "user", "content": user_text})
        response = chat_completion(messages=messages, model="gpt-4o-mini")
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        turn_cost = cost_usd(response.usage, model="gpt-4o-mini")
        total_cost += turn_cost
        print(
            f"{i:>4}  {response.usage.prompt_tokens:>13}  "
            f"{turn_cost:>10.6f}  {total_cost:>14.6f}"
        )

    print("\nFinal reply to the recall question:")
    print(messages[-1]["content"])


if __name__ == "__main__":
    main()
