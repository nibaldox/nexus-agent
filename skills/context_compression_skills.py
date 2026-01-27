from agno.tools import Toolkit


class ContextCompressionSkills(Toolkit):
    """Helpers to compress long context into compact bullets."""

    def __init__(self):
        super().__init__(name="context_compression_skills")
        self.register(self.compress_bullets)
        self.register(self.merge_summaries)

    def compress_bullets(self, bullets: list, max_items: int = 5, max_len: int = 180) -> list:
        """
        Truncate and cap bullets for compact context.
        """
        compact = []
        for bullet in bullets or []:
            text = str(bullet).strip()
            if not text:
                continue
            if len(text) > max_len:
                text = text[: max_len - 3] + "..."
            compact.append(text)
            if len(compact) >= max_items:
                break
        return compact

    def merge_summaries(self, summaries: list) -> str:
        """
        Merge multiple summary strings into one block.
        """
        return "\n".join([s for s in summaries or [] if s]).strip()
