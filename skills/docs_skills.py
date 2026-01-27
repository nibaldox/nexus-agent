from agno.tools import Toolkit


class DocsSkills(Toolkit):
    """Reusable documentation helpers."""

    def __init__(self):
        super().__init__(name="docs_skills")
        self.register(self.build_outline)
        self.register(self.format_references)
        self.register(self.exec_summary)
        self.register(self.build_section)
        self.register(self.table_from_rows)

    def build_outline(self, title: str, sections: list) -> str:
        """
        Build a markdown outline for a document.
        """
        lines = [f"# {title}", ""]
        for section in sections or []:
            lines.append(f"## {section}")
            lines.append("")
        return "\n".join(lines).strip()

    def format_references(self, sources: list) -> str:
        """
        Format references as a markdown list.
        """
        if not sources:
            return "## Referencias\n- (sin fuentes)"
        lines = ["## Referencias"]
        for source in sources:
            lines.append(f"- {source}")
        return "\n".join(lines)

    def exec_summary(self, points: list) -> str:
        """
        Build a short executive summary from bullet points.
        """
        lines = ["## Resumen ejecutivo"]
        for point in points or []:
            lines.append(f"- {point}")
        return "\n".join(lines)

    def build_section(self, title: str, body: str) -> str:
        """
        Build a markdown section.
        """
        return f"## {title}\n\n{body}".strip()

    def table_from_rows(self, headers: list, rows: list) -> str:
        """
        Build a compact markdown table from headers and rows.
        """
        if not headers:
            return ""
        header_line = "| " + " | ".join(headers) + " |"
        divider = "| " + " | ".join(["---"] * len(headers)) + " |"
        body = []
        for row in rows or []:
            body.append("| " + " | ".join([str(cell) for cell in row]) + " |")
        return "\n".join([header_line, divider] + body)
