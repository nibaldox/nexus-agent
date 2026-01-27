from agno.tools import Toolkit


class RiskSkills(Toolkit):
    """Helpers to flag risks and gaps."""

    def __init__(self):
        super().__init__(name="risk_skills")
        self.register(self.flag_risks)

    def flag_risks(self, findings: list) -> list:
        """
        Return a list of detected risk flags based on simple heuristics.
        """
        flags = []
        text = " ".join([str(f) for f in findings or []]).lower()
        if "sin fuente" in text or "sin fuentes" in text:
            flags.append("Faltan fuentes")
        if "estimado" in text or "aprox" in text:
            flags.append("Datos estimados")
        if "contradic" in text:
            flags.append("Datos contradictorios")
        return flags
