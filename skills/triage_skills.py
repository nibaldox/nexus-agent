from agno.tools import Toolkit


class TriageSkills(Toolkit):
    """Lightweight task classification helpers."""

    def __init__(self):
        super().__init__(name="triage_skills")
        self.register(self.classify_task)

    def classify_task(self, text: str) -> str:
        """
        Classify a request into a squad category.
        """
        lowered = (text or "").lower()
        if any(k in lowered for k in ["api", "backend", "database", "fastapi", "endpoint"]):
            return "Development"
        if any(k in lowered for k in ["frontend", "ui", "ux", "css", "html", "javascript"]):
            return "Development"
        if any(k in lowered for k in ["grafico", "chart", "visual", "plot", "tabla"]):
            return "Data Intelligence"
        if any(k in lowered for k in ["investigar", "research", "fuentes", "citas"]):
            return "Data Intelligence"
        if any(k in lowered for k in ["documento", "pdf", "knowledge", "kb"]):
            return "Knowledge"
        return "General"
