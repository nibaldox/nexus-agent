from agno.tools import Toolkit


class VisualizationSkills(Toolkit):
    """Reusable visualization heuristics and helpers."""

    def __init__(self):
        super().__init__(name="visualization_skills")
        self.register(self.recommend_chart_type)
        self.register(self.validate_series_lengths)
        self.register(self.build_chart_brief)
        self.register(self.normalize_labels)
        self.register(self.cap_categories)

    def recommend_chart_type(
        self,
        time_series: bool = False,
        comparison: bool = False,
        distribution: bool = False,
        correlation: bool = False,
        categories: int = 0,
    ) -> str:
        """
        Recommend a chart type based on basic signals.
        """
        if correlation:
            return "scatter"
        if distribution:
            return "histogram"
        if time_series:
            return "line"
        if comparison:
            return "bar"
        if categories and categories <= 6:
            return "pie"
        return "bar"

    def validate_series_lengths(self, x_values: list, y_values: list) -> dict:
        """
        Validate that x/y series lengths match.
        """
        if x_values is None or y_values is None:
            return {"valid": False, "reason": "x_values or y_values missing"}
        if len(x_values) != len(y_values):
            return {
                "valid": False,
                "reason": "length_mismatch",
                "x_len": len(x_values),
                "y_len": len(y_values),
            }
        return {"valid": True, "length": len(x_values)}

    def build_chart_brief(
        self,
        title: str,
        chart_type: str,
        x_label: str,
        y_label: str,
        notes: str = "",
    ) -> str:
        """
        Build a short visualization brief.
        """
        brief_lines = [
            f"Titulo: {title}",
            f"Tipo: {chart_type}",
            f"Eje X: {x_label}",
            f"Eje Y: {y_label}",
        ]
        if notes:
            brief_lines.append(f"Notas: {notes}")
        return "\n".join(brief_lines)

    def normalize_labels(self, labels: list, max_len: int = 24) -> list:
        """
        Normalize labels to a max length.
        """
        normalized = []
        for label in labels or []:
            text = str(label)
            if len(text) > max_len:
                text = text[: max_len - 3] + "..."
            normalized.append(text)
        return normalized

    def cap_categories(self, labels: list, values: list, max_items: int = 8) -> dict:
        """
        Cap categories to max_items; aggregate remainder into 'Otros'.
        """
        if not labels or not values or len(labels) != len(values):
            return {"labels": labels or [], "values": values or []}
        if len(labels) <= max_items:
            return {"labels": labels, "values": values}
        head_labels = labels[: max_items - 1]
        head_values = values[: max_items - 1]
        tail_sum = sum(values[max_items - 1 :])
        return {
            "labels": head_labels + ["Otros"],
            "values": head_values + [tail_sum],
        }
