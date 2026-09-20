from app.ai.confidence_engine import ConfidenceEngine
from app.ai.fix_recommendation_engine import FixRecommendationEngine
from app.ai.llm_client import LLMClient
from app.ai.prompt_builder import PromptBuilder
from app.models.diagnosis import Diagnosis

class RootCauseAnalyzer:
    def __init__(self, client: LLMClient | None = None):
        self.client = client or LLMClient(); self.prompts = PromptBuilder(); self.confidence = ConfidenceEngine(); self.fixes = FixRecommendationEngine()
    def analyze(self, investigation: dict) -> Diagnosis:
        raw = self.client.complete(self.prompts.build(investigation))
        raw["confidence"] = self.confidence.normalize(raw.get("confidence"))
        raw["kubectl_commands"] = self.fixes.normalize_commands(raw.get("kubectl_commands"))
        return Diagnosis.model_validate(raw)
