"""
scripts/_conversation.py

The same seven-turn conversation is fed through three different history
strategies (naive append, fixed window, rolling summary) so the token
counts and the final answer are directly comparable across scripts/measure
_growth.py, scripts/break_window.py, and scripts/fix_with_summary.py.
"""

SYSTEM_PROMPT = (
    "You are a marathon training assistant. Answer briefly and practically."
)

USER_TURNS = [
    "Hi, I'm Priya. I'm training for a marathon in 10 weeks and I'm strictly vegetarian.",
    "Can you put together a one-week meal plan for marathon training?",
    "What should my long run schedule look like this month?",
    "How much water should I drink on long run days?",
    "I've been getting a dull pain in my left knee after runs, any advice?",
    "What should I eat the morning of the race?",
    "I just landed near the start line, can you suggest a restaurant for tonight?",
]
