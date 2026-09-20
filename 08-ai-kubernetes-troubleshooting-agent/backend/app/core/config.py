from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "ai-kubernetes-agent"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    kubeconfig_path: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
