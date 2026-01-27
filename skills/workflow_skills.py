from agno.tools import Toolkit


class WorkflowSkills(Toolkit):
    """Helpers for planning and ordering tasks."""

    def __init__(self):
        super().__init__(name="workflow_skills")
        self.register(self.estimate_complexity)
        self.register(self.order_tasks)

    def estimate_complexity(self, text: str) -> str:
        """
        Estimate request complexity: LOW, MEDIUM, HIGH.
        """
        lowered = (text or "").lower()
        if len(lowered.split()) > 20:
            return "HIGH"
        if any(k in lowered for k in ["comparar", "analisis", "grafico", "dataset", "pipeline"]):
            return "MEDIUM"
        return "LOW"

    def order_tasks(self, tasks: list) -> list:
        """
        Order tasks by common sequence: research -> analysis -> visualization -> review.
        """
        priority = {
            "research": 1,
            "analysis": 2,
            "visual": 3,
            "review": 4,
        }
        def score(task: dict) -> int:
            name = (task.get("description") or "").lower()
            if "investig" in name:
                return priority["research"]
            if "anal" in name:
                return priority["analysis"]
            if "visual" in name or "graf" in name:
                return priority["visual"]
            if "review" in name or "revisi" in name:
                return priority["review"]
            return 99
        return sorted(tasks or [], key=score)
