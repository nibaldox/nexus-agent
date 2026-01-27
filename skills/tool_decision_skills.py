from agno.tools import Toolkit


class ToolDecisionSkills(Toolkit):
    """Helpers to suggest which tools to use."""

    def __init__(self):
        super().__init__(name="tool_decision_skills")
        self.register(self.suggest_tools)

    def suggest_tools(self, text: str) -> list:
        """
        Suggest tools based on keywords in the request.
        """
        lowered = (text or "").lower()
        tools = []
        if any(k in lowered for k in ["buscar", "investigar", "fuente", "web", "news"]):
            tools.append("SerperTools / DuckDuckGoTools")
        if any(k in lowered for k in ["pdf", "documento", "kb", "knowledge"]):
            tools.append("Knowledge / FileTools")
        if any(k in lowered for k in ["grafico", "chart", "visual", "plot", "tabla"]):
            tools.append("ChartTools")
        if any(k in lowered for k in ["finanzas", "precio", "ticker", "market"]):
            tools.append("YFinanceTools")
        if any(k in lowered for k in ["archivo", "guardar", "leer", "write", "read"]):
            tools.append("FileTools")
        return tools
