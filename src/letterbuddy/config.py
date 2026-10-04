"""
Letter Buddy – Configuration loader.

Reads config.yaml once at startup and provides typed access to all settings.
GPU tier, model tags, thresholds, and paths are all set here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


# ── Locate project root ─────────────────────────────────
def _find_project_root() -> Path:
    """Walk up from this file to find config.yaml."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "config.yaml").exists():
            return current
        current = current.parent
    # Fallback: assume CWD
    return Path.cwd()


PROJECT_ROOT = _find_project_root()


# ── Pydantic settings models ────────────────────────────

class GpuConfig(BaseModel):
    name: str = "unknown"
    vram_mb: int = 0
    driver: str = "unknown"
    tier: str = "CPU"  # T4 | T6 | T8 | CPU


class LlmConfig(BaseModel):
    primary: str = "qwen2.5:7b"
    candidates: list[str] = Field(default_factory=lambda: ["qwen2.5:7b"])
    num_ctx: int = 4096
    temperature: float = 0.15
    max_predict: int = 1024
    think: bool = False


class OllamaConfig(BaseModel):
    max_loaded_models: int = 1
    num_parallel: int = 1
    host: str = "http://127.0.0.1:11434"


class OcrConfig(BaseModel):
    engine: str = "tesseract"
    langs: str = "eng"
    min_confidence: int = 55
    min_readable_ratio: float = 0.4


class LanguageConfig(BaseModel):
    source: str = "en"
    target: str = "te"
    target_name: str = "Telugu"
    target_script: str = "Telugu"


class TtsConfig(BaseModel):
    engine: str = "espeak-ng"
    voice: str = "te"
    speed: int = 130
    fallback_reason: str | None = None


class SafetyConfig(BaseModel):
    trusted_contact: dict[str, str] = Field(
        default_factory=lambda: {"name": "[TO BE FILLED]", "phone": "[TO BE FILLED]"}
    )
    scam_keywords: list[str] = Field(default_factory=list)
    high_stakes_doc_types: list[str] = Field(default_factory=lambda: ["legal", "tax", "medical"])


class PrivacyConfig(BaseModel):
    purge_hours: int = 1
    bind_host: str = "127.0.0.1"
    lan_mode: bool = False
    lan_pin: str | None = None


class PathsConfig(BaseModel):
    uploads: str = "uploads/"
    output: str = "output/"
    private_data: str = "data/private/"
    samples: str = "data/samples/"
    i18n: str = "i18n/"
    fonts: str = "static/fonts/"


class AppConfig(BaseModel):
    """Top-level configuration container."""
    gpu: GpuConfig = Field(default_factory=GpuConfig)
    llm: LlmConfig = Field(default_factory=LlmConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    ocr: OcrConfig = Field(default_factory=OcrConfig)
    language: LanguageConfig = Field(default_factory=LanguageConfig)
    tts: TtsConfig = Field(default_factory=TtsConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)

    def resolve_path(self, rel: str) -> Path:
        """Resolve a relative path against the project root."""
        return PROJECT_ROOT / rel

    @property
    def uploads_dir(self) -> Path:
        p = self.resolve_path(self.paths.uploads)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def output_dir(self) -> Path:
        p = self.resolve_path(self.paths.output)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def trusted_contact_str(self) -> str:
        """Format trusted contact for display."""
        name = self.safety.trusted_contact.get("name", "a trusted person")
        phone = self.safety.trusted_contact.get("phone", "")
        if phone and phone != "[TO BE FILLED]":
            return f"{name}: {phone}"
        return name


# ── Load config ──────────────────────────────────────────

def load_config(config_path: Path | None = None) -> AppConfig:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = PROJECT_ROOT / "config.yaml"

    if not config_path.exists():
        return AppConfig()

    with open(config_path, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    return AppConfig(**raw)


# ── i18n loader ──────────────────────────────────────────

_i18n_cache: dict[str, dict[str, Any]] = {}


def load_i18n(lang: str | None = None, config: AppConfig | None = None) -> dict[str, Any]:
    """Load i18n labels for a language. Falls back to English."""
    if config is None:
        config = load_config()
    if lang is None:
        lang = config.language.target

    if lang in _i18n_cache:
        return _i18n_cache[lang]

    i18n_dir = config.resolve_path(config.paths.i18n)

    # Try target language first, fall back to English
    for try_lang in [lang, "en"]:
        path = i18n_dir / f"{try_lang}.yaml"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            _i18n_cache[lang] = data
            return data

    # If nothing found, return empty
    return {}


def get_label(key_path: str, lang: str | None = None, **kwargs: str) -> str:
    """
    Get a localized label by dot-separated path.
    Example: get_label("safety.disclaimer", lang="te")
    Supports {placeholder} formatting with kwargs.
    """
    data = load_i18n(lang)
    keys = key_path.split(".")
    value: Any = data
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            value = None
            break

    if value is None:
        # Fall back to English
        en_data = load_i18n("en")
        value = en_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = key_path  # Last resort: return the key itself
                break

    if isinstance(value, str) and kwargs:
        try:
            value = value.format(**kwargs)
        except KeyError:
            pass  # Leave unformatted if placeholder missing

    return str(value) if value is not None else key_path


# ── Module-level singleton ───────────────────────────────
# Import `from letterbuddy.config import cfg` for quick access
cfg = load_config()
