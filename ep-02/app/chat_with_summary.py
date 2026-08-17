"""
app/chat_with_summary.py

Interactive chat loop backed by memory.summarizer.RollingMemory. Old turns
fold into a short state-summary block instead of being dropped. Run with:
python -m app.chat_with_summary
"""

from llm.client import chat_completion, cost_usd
from memory.summarizer import RollingMemory

SYSTEM_PROMPT = "You are a marathon training assistant. Answer briefly and practically."
KEEP_RECENT = 4
COMPACT_AFTER = 6


def main():
    memory = RollingMemory(keep_recent=KEEP_RECENT, compact_after=COMPACT_AFTER)
    print("Chat with rolling summarization. Type 'quit' to exit.\n")

    while True:
        user_text = input("you> ").strip()
        if user_text.lower() in {"quit", "exit"}:
            break

        memory.add_turn("user", user_text)
        extra_cost = 0.0
        if memory.last_extraction_usage is not None:
            extra_cost += cost_usd(memory.last_extraction_usage, model="gpt-4o-mini")

        sent = memory.get_context(SYSTEM_PROMPT)
        response = chat_completion(messages=sent, model="gpt-4o-mini")
        reply = response.choices[0].message.content
        memory.add_turn("assistant", reply)
        if memory.last_extraction_usage is not None:
            extra_cost += cost_usd(memory.last_extraction_usage, model="gpt-4o-mini")

        cost = cost_usd(response.usage, model="gpt-4o-mini") + extra_cost
        print(f"bot> {reply}")
        print(f"     [prompt_tokens={response.usage.prompt_tokens} cost=${cost:.6f}]\n")


if __name__ == "__main__":
    main()


