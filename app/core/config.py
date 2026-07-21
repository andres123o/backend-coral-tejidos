from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Falls back to a local SQLite file so the API runs out of the box
    # before a Supabase project/connection string exists. In production this
    # is Supabase's session-mode pooler (port 5432), which the running app
    # uses for regular queries too (see backend/.env for why).
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # Only used if a separate connection string is ever needed for Alembic
    # migrations specifically. Falls back to database_url when empty, which
    # is the normal case (see backend/.env), so local SQLite dev is unaffected.
    direct_url: str = ""

    # Comma-separated list of allowed origins, e.g. "https://coral-tejidos.vercel.app,http://localhost:5173"
    cors_origins: str = "http://localhost:5173"

    environment: str = "development"

    # Supabase Auth (panel de administración). Vacíos hasta conectar el
    # proyecto real; el resto de la app (catálogo público) no los necesita.
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
