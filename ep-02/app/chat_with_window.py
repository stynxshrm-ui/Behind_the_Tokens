"""
app/chat_with_window.py

Interactive chat loop that trims history to a fixed window before every
call. Run with: python -m app.chat_with_window
"""

from llm.client import chat_completion, cost_usd
from memory.window import trim_to_window

SYSTEM_PROMPT = "You are a marathon training assistant. Answer briefly and practically."
MAX_MESSAGES = 8


def main():
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Chat with a fixed sliding window. Type 'quit' to exit.\n")

    while True:
        user_text = input("you> ").strip()
        if user_text.lower() in {"quit", "exit"}:
            break

        history.append({"role": "user", "content": user_text})
        sent = trim_to_window(history, max_messages=MAX_MESSAGES)

        response = chat_completion(messages=sent, model="gpt-4o-mini")
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        cost = cost_usd(response.usage, model="gpt-4o-mini")
        print(f"bot> {reply}")
        print(f"     [prompt_tokens={response.usage.prompt_tokens} cost=${cost:.6f}]\n")


if __name__ == "__main__":
    main()
