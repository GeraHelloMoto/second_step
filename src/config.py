
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    database_url: str | None = None
    postgres_connection_string: str | None = None
    postgres_database_name: str | None = None
    postgres_host: str | None = None
    postgres_port: str | None = None
    postgres_username: str | None = None
    postgres_password: str | None = None
    provider_base_url: str = ""
    provider_api_key: str = ""
    sync_interval_hours: int = 24
    cache_seats_ttl: int = 30


    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.postgres_connection_string:

            return self.postgres_connection_string.replace(
                "postgres://",
                "postgresql+asyncpg://", 1)
        if all([self.postgres_username,
            self.postgres_password,
            self.postgres_host,
            self.postgres_port,
            self.postgres_database_name]
        ):
            return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"
        raise ValueError("Cant make DATABASE_URL")

settings = Settings()
settings.database_url = settings.get_database_url()
