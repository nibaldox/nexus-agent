from agno.tools import Toolkit
from urllib.parse import urlparse
from datetime import datetime


class ResearchSkills(Toolkit):
    """Reusable research helpers for source handling."""

    def __init__(self):
        super().__init__(name="research_skills")
        self.register(self.score_source)
        self.register(self.format_citation)
        self.register(self.summarize_findings)
        self.register(self.is_recent)
        self.register(self.extract_domain)

    def score_source(self, url: str) -> dict:
        """
        Score a source based on domain heuristics.
        """
        domain = urlparse(url).netloc.lower()
        if domain.endswith(".gov") or domain.endswith(".edu"):
            level = "HIGH"
        elif domain.endswith(".org"):
            level = "HIGH"
        elif any(d in domain for d in ["reuters.com", "bbc.", "who.int", "un.org"]):
            level = "HIGH"
        elif any(d in domain for d in ["medium.com", "blog", "substack"]):
            level = "LOW"
        else:
            level = "MEDIUM"
        return {"domain": domain, "confidence": level}

    def extract_domain(self, url: str) -> str:
        """
        Return the domain from a URL.
        """
        return urlparse(url).netloc.lower()

    def format_citation(self, title: str, url: str, published_date: str = "") -> str:
        """
        Format a short citation string.
        """
        date_part = f" ({published_date})" if published_date else ""
        return f"{title}{date_part} - {url}"

    def summarize_findings(self, findings: list) -> str:
        """
        Create a compact summary list from findings.
        """
        if not findings:
            return "- (sin hallazgos)"
        return "\n".join([f"- {item}" for item in findings])

    def is_recent(self, published_date: str, days: int = 30) -> dict:
        """
        Check if a YYYY-MM-DD date is within the last N days.
        """
        try:
            date_obj = datetime.strptime(published_date, "%Y-%m-%d")
        except Exception:
            return {"valid": False, "recent": False}
        delta = datetime.utcnow() - date_obj
        return {"valid": True, "recent": delta.days <= days, "age_days": delta.days}
