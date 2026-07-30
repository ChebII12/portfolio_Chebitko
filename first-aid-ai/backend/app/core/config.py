from typing import List
from pydantic import BaseSettings, Field, root_validator, validator


INSECURE_DEVELOPMENT_SECRETS = {
    "dev-secret-key-change-in-production",
    "change-me-in-production",
    "your-secret-key-generate-a-strong-random-key-in-production",
}

class Settings(BaseSettings):
    database_url: str = "sqlite:///./firstaidai.db"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    groq_api_key: str = ""
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_model: str = "llama-3.1-8b-instant"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])
    
    # BigQuery Migration Configuration (Phase 1-6 per runbook)
    bigquery_project_id: str = ""
    bigquery_dataset_id: str = "first_aid_ai_module1"
    bigquery_credentials_path: str = ""
    bigquery_write_enabled: bool = False
    bigquery_read_source: str = "legacy"  # Options: "legacy", "bigquery", "shadow"
    bigquery_backfill_watermark: str = ""
    
    # Email / SMTP Configuration
    app_environment: str = "development"
    email_delivery_mode: str = "console"  # console for local demos, smtp for real email delivery
    smtp_host: str = ""
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@firstaid.ai"
    smtp_from_name: str = "First Aid AI"
    smtp_use_tls: bool = True
    email_log_codes: bool = False

    @validator("cors_origins", pre=True, allow_reuse=True)
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @validator("bigquery_read_source", pre=True, allow_reuse=True)
    def validate_read_source(cls, value):
        if value not in ["legacy", "bigquery", "shadow"]:
            raise ValueError("bigquery_read_source must be one of: legacy, bigquery, shadow")
        return value

    @validator("email_delivery_mode", pre=True, allow_reuse=True)
    def validate_email_delivery_mode(cls, value):
        normalized = str(value or "console").strip().lower()
        if normalized not in ["console", "smtp"]:
            raise ValueError("email_delivery_mode must be one of: console, smtp")
        return normalized

    @root_validator(allow_reuse=True)
    def validate_production_secret(cls, values):
        environment = str(values.get("app_environment") or "").strip().lower()
        secret_key = str(values.get("secret_key") or "")
        if environment == "production" and (
            len(secret_key) < 32 or secret_key in INSECURE_DEVELOPMENT_SECRETS
        ):
            raise ValueError(
                "Production requires a strong SECRET_KEY of at least 32 characters; "
                "generate one instead of using a development placeholder."
            )
        return values

    class Config:
        env_file = ".env"
        case_sensitive = False

        @classmethod
        def parse_env_var(cls, field_name, raw_value):
            if field_name == "cors_origins":
                return raw_value
            return cls.json_loads(raw_value)

settings = Settings()
