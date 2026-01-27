from agno.tools import Toolkit


class MemorySkills(Toolkit):
    """Helpers to summarize and compress session context."""

    def __init__(self):
        super().__init__(name="memory_skills")
        self.register(self.summarize_thread)
        self.register(self.extract_decisions)

    def summarize_thread(self, messages: list, max_bullets: int = 5) -> str:
        """
        Summarize a list of messages into a short bullet list.
        Expects messages as list of strings or dicts with 'content'.
        """
        bullets = []
        for msg in messages or []:
            if isinstance(msg, dict):
                content = msg.get("content") or ""
            else:
                content = str(msg)
            content = content.strip()
            if content:
                bullets.append(content)
            if len(bullets) >= max_bullets:
                break
        if not bullets:
            return "- (sin contexto)"
        return "\n".join([f"- {b[:180]}" for b in bullets])

    def extract_decisions(self, notes: list) -> list:
        """
        Extract key decisions from notes.
        """
        decisions = []
        for note in notes or []:
            text = str(note).strip()
            if not text:
                continue
            if text.lower().startswith(("decisión", "decision", "acuerdo")):
                decisions.append(text)
        return decisions
