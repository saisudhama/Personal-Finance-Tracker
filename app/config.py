from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "poc-02-finance-tracker"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = None
    database_url: str = "sqlite:///./app.db"

    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")

    # LangSmith (used from Phase 2 onward, harmless to declare now)
    langchain_tracing_v2: bool = True
    langchain_api_key: str | None = os.getenv("LANGCHAIN_API_KEY")
    langchain_project: str | None = "personal-finance-tracker"

    otel_service_name: str = "poc-02-phase-1"
    otel_exporter_otlp_endpoint: str | None = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    associate_id: str = "sai-sudhama"
    poc_id: str = "POC-01"
    phase: int = 1

    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()