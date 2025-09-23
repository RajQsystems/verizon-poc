from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default_factory=str, description="Database connection URL"
    )
    DATABASE_USERNAME: str = Field(default="", description="Database username")
    DATABASE_PASSWORD: str = Field(default="", description="Database password")
    DATABASE_HOST: str = Field(default="", description="Database host")
    DATABASE_NAME: str = Field(default="", description="Database name")

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


settings: Settings = Settings()
