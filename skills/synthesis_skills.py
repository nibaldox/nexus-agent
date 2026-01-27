from agno.tools import Toolkit


class SynthesisSkills(Toolkit):
    """Helpers to synthesize outputs into structured summaries."""

    def __init__(self):
        super().__init__(name="synthesis_skills")
        self.register(self.build_summary)
        self.register(self.combine_sections)

    def build_summary(self, title: str, bullets: list) -> str:
        """
        Build a markdown summary section.
        """
        lines = [f"## {title}"]
        for bullet in bullets or []:
            lines.append(f"- {bullet}")
        return "\n".join(lines)

    def combine_sections(self, sections: list) -> str:
        """
        Combine multiple markdown sections.
        """
        return "\n\n".join([s for s in sections or [] if s])
