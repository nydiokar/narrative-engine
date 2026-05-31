"""Configuration and logging for the Narrative Engine."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    # Paths
    contracts_dir: Path = Field(default=Path("contracts"))
    output_dir: Path = Field(default=Path("output"))
    archive_dir: Path | None = None

    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_api_key: str = ""
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.7

    # Pipeline
    pipeline_auto_advance: bool = True
    pipeline_wait_for_input: bool = False
    hard_gate_required_pass_rate: float = 0.8

    # Logging
    log_level: str = "INFO"
    log_file: str = "narrative_engine.log"

    model_config = {"env_prefix": "NE_", "env_file": ".env", "env_file_encoding": "utf-8"}


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def setup_logging(level: str | None = None) -> logging.Logger:
    s = get_settings()
    fmt = logging.Formatter(
        "%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    handler.setLevel(level or s.log_level)

    file_handler = logging.FileHandler(s.log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger("narrative_engine")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    return logger
