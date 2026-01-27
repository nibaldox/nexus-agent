from agno.tools import Toolkit


class DataNormalizationSkills(Toolkit):
    """Helpers to normalize metrics and units."""

    def __init__(self):
        super().__init__(name="data_normalization_skills")
        self.register(self.format_number)
        self.register(self.format_percent)
        self.register(self.normalize_unit)

    def format_number(self, value: float, decimals: int = 2) -> str:
        """
        Format a number with thousands separators.
        """
        try:
            return f"{float(value):,.{decimals}f}"
        except Exception:
            return str(value)

    def format_percent(self, value: float, decimals: int = 1) -> str:
        """
        Format a percentage value.
        """
        try:
            return f"{float(value):.{decimals}f}%"
        except Exception:
            return str(value)

    def normalize_unit(self, value: float, unit: str = "") -> str:
        """
        Normalize large values into K/M/B notation.
        """
        try:
            num = float(value)
        except Exception:
            return f"{value}{unit}"
        suffix = ""
        if abs(num) >= 1_000_000_000:
            num /= 1_000_000_000
            suffix = "B"
        elif abs(num) >= 1_000_000:
            num /= 1_000_000
            suffix = "M"
        elif abs(num) >= 1_000:
            num /= 1_000
            suffix = "K"
        return f"{num:,.2f}{suffix}{unit}"
