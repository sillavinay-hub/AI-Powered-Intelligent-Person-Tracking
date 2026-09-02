import os
import torch
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "ResortVision AI"
    APP_SUBTITLE: str = "Intelligent Multi-Camera Person Tracking & Analytics"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./resortvision.db"

    # Security & Auth
    SECRET_KEY: str = "resortvision-ai-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Hardware & Inference
    DEVICE: str = "auto"
    AI_FRAME_RATE: int = 10
    MAX_TRACKING_AGE: int = 30

    # Multimodal Identity Fusion Weights
    W_FACE: float = 0.40
    W_REID: float = 0.35
    W_TEMPORAL: float = 0.15
    W_CAMERA: float = 0.10

    # Decision Thresholds
    FACE_THRESHOLD: float = 0.60
    REID_THRESHOLD: float = 0.55
    IDENTITY_THRESHOLD: float = 0.65
    UNKNOWN_THRESHOLD: float = 0.45

    # Demo & Storage
    DEMO_MODE: bool = True
    ENABLE_SYNTHETIC_CAMERAS: bool = True
    DATA_RETENTION_DAYS: int = 30
    LOG_LEVEL: str = "INFO"

    # Paths
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    REF_IMAGE_DIR: Path = BASE_DIR / "uploads" / "references"
    LOGS_DIR: Path = BASE_DIR / "logs"

    @property
    def resolved_device(self) -> str:
        if self.DEVICE.lower() == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        elif self.DEVICE.lower() in ["cuda", "gpu"]:
            return "cuda" if torch.cuda.is_available() else "cpu"
        return "cpu"

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REF_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
