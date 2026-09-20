class ConfidenceEngine:
    def normalize(self, value: int | float | str) -> int:
        try: return max(0, min(100, int(float(value))))
        except (TypeError, ValueError): return 0
