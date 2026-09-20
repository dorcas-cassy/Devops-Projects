class FixRecommendationEngine:
    """Normalizes command suggestions. It never executes them."""
    def normalize_commands(self, commands: object) -> list[str]:
        if isinstance(commands, str): commands = [commands]
        if not isinstance(commands, list): return []
        return [value.strip() for value in commands if isinstance(value, str) and value.strip().startswith("kubectl ")][:5]
