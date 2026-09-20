from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "ai-kubernetes-agent"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout_seconds: float = 30.0
    kubeconfig_path: str = ""
    backend_internal_token: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
