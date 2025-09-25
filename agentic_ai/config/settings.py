from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """

    OPENAI_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="API key for accessing the OpenAPI service.",
    )
    API_BASE_URL: str = Field(
        default="http://localhost:8000", description="Base URL for the API service"
    )

    LANGFUSE_PUBLIC_KEY: str = Field(
        default="",
        description="Public key for Langfuse integration.",
    )
    LANGFUSE_SECRET_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Secret key for Langfuse integration.",
    )
    LANGFUSE_HOST: str = Field(
        default="cloud.langfuse.com",
        description="Host for Langfuse integration.",
    )
    LANGFUSE_PORT: int = Field(
        default=443,
        description="Port for Langfuse integration.",
    )
    LANGFUSE_USE_SSL: bool = Field(
        default=False,
        description="Whether to use SSL for Langfuse integration.",
    )
    OTEL_EXPORTER_OTLP_TRACES_PROTOCOL: str = Field(
        default="http/protobuf",
        description="Protocol for OpenTelemetry traces exporter.",
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


settings: Settings = Settings()
