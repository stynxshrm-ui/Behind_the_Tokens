"""
memory/summarizer.py

Instead of dropping old turns (see memory/window.py), fold them into a short
state-summary block using the same model we already talk to. The summary
block plus a handful of recent raw turns replaces the full transcript on
every call.
"""

from __future__ import annotations

from llm.client import chat_completion

_EXTRACTION_SYSTEM_PROMPT = (
    "You maintain a running state summary for a customer conversation. "
    "You will be given the current summary (which may be empty) and a block "
    "of new conversation turns. Rewrite the summary so it still contains "
    "every fact that matters for answering future questions: stated name, "
    "stated constraints or preferences (dietary, medical, scheduling, "
    "budget), stated goals, and any commitment already made to the user. "
    "Write it as short labeled lines, for example:\n"
    "Name: Priya\n"
    "Dietary: vegetarian\n"
    "Goal: marathon in 10 weeks\n"
    "Drop small talk and anything not needed to answer later questions. "
    "Output only the updated summary lines, nothing else."
)


def extract_state_summary(
    previous_summary: str | None,
    new_turns: list[dict],
    model: str = "gpt-4o-mini",
):
    """
    Fold `new_turns` into `previous_summary`. Returns (summary_text, usage) —
    the usage object is exposed so callers can account for the cost of the
    extraction call itself, since it is a real API call and not free.
    """
    turns_text = "\n".join(f"{t['role']}: {t['content']}" for t in new_turns)
    user_block = (
        f"Current summary:\n{previous_summary or '(empty)'}\n\n"
        f"New turns:\n{turns_text}"
    )
    response = chat_completion(
        messages=[
            {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_block},
        ],
        model=model,
    )
    return response.choices[0].message.content.strip(), response.usage


class RollingMemory:
    """
    Keeps a short state-summary of everything older than `keep_recent`
    messages, and the last `keep_recent` raw messages verbatim. Once more
    than `compact_after` raw messages have piled up since the last
    compaction, it automatically folds the oldest of them into the summary.
    """

    def __init__(self, keep_recent: int = 4, compact_after: int = 8, model: str = "gpt-4o-mini"):
        self.keep_recent = keep_recent
        self.compact_after = compact_after
        self.model = model
        self._raw: list[dict] = []
        self._summarized_upto = 0
        self.summary: str | None = None
        self.last_extraction_usage = None  # usage of the most recent compaction call, if any

    def add_turn(self, role: str, content: str) -> None:
        self._raw.append({"role": role, "content": content})
        pending = len(self._raw) - self._summarized_upto
        self.last_extraction_usage = None
        if pending > self.compact_after:
            self.compact()

    def compact(self) -> None:
        """Force a compaction now, folding everything but the most recent turns into the summary."""
        fold_end = max(self._summarized_upto, len(self._raw) - self.keep_recent)
        turns_to_fold = self._raw[self._summarized_upto:fold_end]
        if not turns_to_fold:
            return
        self.summary, self.last_extraction_usage = extract_state_summary(
            self.summary, turns_to_fold, model=self.model
        )
        self._summarized_upto = fold_end

    def get_context(self, system_prompt: str) -> list[dict]:
        """Build the message list to actually send: system prompt, summary block, recent raw turns."""
        context = [{"role": "system", "content": system_prompt}]
        if self.summary:
            context.append(
                {"role": "system", "content": f"Conversation summary so far:\n{self.summary}"}
            )
        context.extend(self._raw[self._summarized_upto:])
        return context
