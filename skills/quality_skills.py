from agno.tools import Toolkit


class QualitySkills(Toolkit):
    """Reusable QA helpers for review and synthesis."""

    def __init__(self):
        super().__init__(name="quality_skills")
        self.register(self.build_checklist)
        self.register(self.evaluate_coverage)
        self.register(self.build_review_json)

    def build_checklist(self) -> list:
        """
        Return a standard QA checklist.
        """
        return [
            "Cobertura completa de la solicitud",
            "Fuentes citadas y verificables",
            "Datos con fecha/unidad",
            "Consistencia entre agentes",
            "Artifacts generados y referenciados",
        ]

    def evaluate_coverage(self, expected_items: list, delivered_items: list) -> dict:
        """
        Compare expected vs delivered items.
        """
        expected = set(expected_items or [])
        delivered = set(delivered_items or [])
        missing = sorted(expected - delivered)
        return {
            "missing": missing,
            "coverage_ratio": 0 if not expected else round((len(expected) - len(missing)) / len(expected), 2),
        }

    def build_review_json(
        self,
        status: str,
        issues: list,
        recommendations: list,
        summary: str,
    ) -> dict:
        """
        Build a minimal review JSON object.
        """
        return {
            "status": status,
            "issues": issues or [],
            "recommendations": recommendations or [],
            "summary": summary,
        }
