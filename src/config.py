from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    postgres_username: str = "postgres"
    postgres_password: str = "pass"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_database_name: str = "events"
    database_url: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"

settings = Settings()
settings.database_url = settings.get_database_url()