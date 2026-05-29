from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Call Center Control"
    app_env: str = "development"
    app_secret_key: str = "change-this-secret-key"
    app_public_url: str = "http://localhost:8080"
    database_url: str = "postgresql+psycopg://callcenter:callcenter@localhost:5432/callcenter"
    redis_url: str = "redis://localhost:6379/0"
    jwt_expire_minutes: int = 720

    fusionpbx_db_url: str | None = None
    freeswitch_esl_host: str | None = None
    freeswitch_esl_port: int = 8021
    freeswitch_esl_password: str | None = None

    seed_admin_email: str = "admin@example.com"
    seed_admin_password: str = "ChangeMe123!"

    @cached_property
    def cors_origins(self) -> list[str]:
        return ["http://localhost:8080", "http://localhost:5173", self.app_public_url]


settings = Settings()

