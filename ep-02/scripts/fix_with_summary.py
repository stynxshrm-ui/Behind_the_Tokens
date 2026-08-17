"""
scripts/fix_with_summary.py

Runs the same seven-turn conversation through memory.summarizer.RollingMemory.
Old turns get folded into a short state-summary block instead of being
dropped, so the vegetarian constraint from turn one is still available when
the recall question comes at turn seven.
"""

from llm.client import chat_completion, cost_usd
from memory.summarizer import RollingMemory
from scripts._conversation import SYSTEM_PROMPT, USER_TURNS

KEEP_RECENT = 4
COMPACT_AFTER = 6


def main():
    memory = RollingMemory(keep_recent=KEEP_RECENT, compact_after=COMPACT_AFTER)
    total_cost = 0.0
    final_reply = ""

    print(f"{'turn':>4}  {'prompt_tokens':>13}  {'cost_usd':>10}  {'cumulative_usd':>14}  {'summary?':>9}  {'compacted?':>10}")
    for i, user_text in enumerate(USER_TURNS, start=1):
        memory.add_turn("user", user_text)
        compacted_on_user_add = memory.last_extraction_usage is not None
        if compacted_on_user_add:
            total_cost += cost_usd(memory.last_extraction_usage, model="gpt-4o-mini")

        sent = memory.get_context(SYSTEM_PROMPT)
        response = chat_completion(messages=sent, model="gpt-4o-mini")
        reply = response.choices[0].message.content
        memory.add_turn("assistant", reply)
        compacted_on_assistant_add = memory.last_extraction_usage is not None
        if compacted_on_assistant_add:
            total_cost += cost_usd(memory.last_extraction_usage, model="gpt-4o-mini")
        final_reply = reply

        turn_cost = cost_usd(response.usage, model="gpt-4o-mini")
        total_cost += turn_cost
        compacted_this_turn = compacted_on_user_add or compacted_on_assistant_add
        print(
            f"{i:>4}  {response.usage.prompt_tokens:>13}  "
            f"{turn_cost:>10.6f}  {total_cost:>14.6f}  "
            f"{'yes' if memory.summary else 'no':>9}  "
            f"{'yes' if compacted_this_turn else 'no':>10}"
        )

    print("\nCurrent state summary:")
    print(memory.summary)
    print("\nFinal reply to the recall question:")
    print(final_reply)
    print(
        "\nMentions vegetarian:",
        "yes" if "vegetarian" in final_reply.lower() else "no",
    )


if __name__ == "__main__":
    main()
