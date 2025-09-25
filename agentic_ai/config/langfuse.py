from __future__ import annotations

import os
import base64
from dataclasses import dataclass
from functools import lru_cache

from agentic_ai.config.settings import settings


@dataclass(slots=True, frozen=True)
class LangfuseConfig:
    """Immutable configuration for self-hosted Langfuse, CrewAI, and MLflow integration."""

    # Langfuse
    public_key: str
    secret_key: str
    host: str
    port: int
    use_ssl: bool
    protocol: str

    @classmethod
    def from_env(cls) -> "LangfuseConfig":
        """Build config from environment variables with sensible defaults."""
        return cls(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY.get_secret_value(),
            host=settings.LANGFUSE_HOST,
            port=settings.LANGFUSE_PORT,
            use_ssl=os.getenv("LANGFUSE_USE_SSL", "false").lower() == "true",
            protocol=settings.OTEL_EXPORTER_OTLP_TRACES_PROTOCOL,
        )

    @property
    def base_url(self) -> str:
        scheme = "https" if self.use_ssl else "http"
        return f"{scheme}://{self.host}:{self.port}"

    @property
    def otlp_endpoint(self) -> str:
        return f"{self.base_url}/api/public/otel/v1/traces"

    @property
    def auth_header(self) -> str:
        return base64.b64encode(
            f"{self.public_key}:{self.secret_key}".encode()
        ).decode()

    def set_environment_variables(self) -> None:
        """Set all required environment variables for Langfuse, CrewAI, and MLflow."""
        os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = self.otlp_endpoint
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
            f"Authorization=Basic {self.auth_header}"
        )
        os.environ["OTEL_EXPORTER_OTLP_TRACES_PROTOCOL"] = self.protocol

    def validate(self) -> None:
        if not self.public_key or not self.public_key.startswith("pk-lf-"):
            raise ValueError(
                "LANGFUSE_PUBLIC_KEY is required and must start with 'pk-lf-'"
            )
        if not self.secret_key or not self.secret_key.startswith("sk-lf-"):
            raise ValueError(
                "LANGFUSE_SECRET_KEY is required and must start with 'sk-lf-'"
            )
        if self.port < 1 or self.port > 65535:
            raise ValueError("LANGFUSE_PORT must be between 1 and 65535")


@lru_cache(maxsize=1)
def get_langfuse_config() -> LangfuseConfig:
    config = LangfuseConfig.from_env()
    config.validate()
    return config


def setup_langfuse() -> LangfuseConfig:
    config = get_langfuse_config()
    config.set_environment_variables()
    return config
