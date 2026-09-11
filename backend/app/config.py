from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://saas_app:saas_app_password@localhost:5432/saas_demo"
    database_admin_url: str = "postgresql+psycopg://saas_owner:saas_owner_password@localhost:5432/saas_demo"
    jwt_secret: str = "local-demo-secret-change-me"
    jwt_ttl_minutes: int = 60
    frontend_origin: str = "http://localhost:5173"
    demo_mode: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

