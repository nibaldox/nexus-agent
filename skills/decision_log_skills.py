from agno.tools import Toolkit


class DecisionLogSkills(Toolkit):
    """Helpers to track and format key decisions."""

    def __init__(self):
        super().__init__(name="decision_log_skills")
        self.register(self.add_decision)
        self.register(self.format_decisions)

    def add_decision(self, decisions: list, decision: str) -> list:
        """
        Append a decision to the list.
        """
        items = list(decisions or [])
        if decision:
            items.append(str(decision))
        return items

    def format_decisions(self, decisions: list) -> str:
        """
        Format decisions as a markdown list.
        """
        if not decisions:
            return "- (sin decisiones)"
        return "\n".join([f"- {d}" for d in decisions])
