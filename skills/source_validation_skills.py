from agno.tools import Toolkit
from urllib.parse import urlparse


class SourceValidationSkills(Toolkit):
    """Source validation helpers for research."""

    def __init__(self):
        super().__init__(name="source_validation_skills")
        self.register(self.is_trusted_domain)
        self.register(self.classify_domain)

    def is_trusted_domain(self, url: str) -> bool:
        """
        Check if a URL belongs to a trusted domain category.
        """
        domain = urlparse(url).netloc.lower()
        if domain.endswith(".gov") or domain.endswith(".edu"):
            return True
        if domain.endswith(".org"):
            return True
        if any(d in domain for d in ["reuters.com", "bbc.", "who.int", "un.org"]):
            return True
        return False

    def classify_domain(self, url: str) -> str:
        """
        Classify domain into HIGH/MEDIUM/LOW reliability.
        """
        domain = urlparse(url).netloc.lower()
        if domain.endswith(".gov") or domain.endswith(".edu"):
            return "HIGH"
        if domain.endswith(".org"):
            return "HIGH"
        if any(d in domain for d in ["reuters.com", "bbc.", "who.int", "un.org"]):
            return "HIGH"
        if any(d in domain for d in ["medium.com", "blog", "substack"]):
            return "LOW"
        return "MEDIUM"
