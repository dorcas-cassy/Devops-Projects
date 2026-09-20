from pydantic import BaseModel, Field

class Diagnosis(BaseModel):
    root_cause: str
    explanation: str
    suggested_fix: str
    kubectl_commands: list[str] = Field(default_factory=list)
    prevention_recommendation: str
    confidence: int = Field(ge=0, le=100)
    confidence_reasoning: str

    def api_payload(self) -> dict:
        payload = self.model_dump()
        payload["kubectl_command"] = self.kubectl_commands[0] if self.kubectl_commands else ""
        return payload
