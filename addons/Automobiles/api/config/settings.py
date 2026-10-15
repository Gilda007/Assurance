# addons/Automobiles/api/config/settings.py (ajout des configs JWT)

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # ========== BASE ==========
    PROJECT_NAME: str = "ASAC API"
    VERSION: str = "1.2.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = Field(default=False, env="ASAC_DEBUG")
    
    # ========== SERVEUR ==========
    HOST: str = Field(default="127.0.0.1", env="ASAC_HOST")
    PORT: int = Field(default=8001, env="ASAC_PORT")
    RELOAD: bool = Field(default=True, env="ASAC_RELOAD")
    
    # ========== BASE DE DONNÉES ==========
    DATABASE_URL: str = Field(
        default="sqlite:///./addons/Automobiles/api/storage/asac.db",
        env="ASAC_DATABASE_URL"
    )
    
    # ========== SÉCURITÉ JWT ==========
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production-2024",
        env="ASAC_SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = Field(default=365, env="ASAC_TOKEN_EXPIRE_DAYS")
    
    # ========== ASAC CREDENTIALS ==========
    ASAC_APP_KEY: Optional[str] = Field(default=None, env="ASAC_APP_KEY")
    ASAC_USERNAME: Optional[str] = Field(default=None, env="ASAC_USERNAME")
    ASAC_API_URL: str = Field(
        default="https://ppeatt-api.asac.cm",
        env="ASAC_API_URL"
    )
    
    # ========== BUREAUX PAR DÉFAUT ==========
    DEFAULT_OFFICE_CODE: str = Field(default="AG-DLA-001", env="ASAC_OFFICE_CODE")
    DEFAULT_ORGANIZATION_CODE: str = Field(default="ACTIVA", env="ASAC_ORGANIZATION_CODE")
    
    # ========== STOCKAGE ==========
    STORAGE_PATH: Path = Path(
        os.getenv("ASAC_STORAGE_PATH", "./addons/Automobiles/api/storage/certificates")
    )
    MAX_CERTIFICATES_PER_PRODUCTION: int = 1000
    
    # ========== CORS ==========
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],
        env="ASAC_ALLOWED_ORIGINS"
    )
    
    # ========== LIMITES ==========
    MAX_PRODUCTION_DAYS: int = 365
    MIN_PRODUCTION_DAYS: int = 1
    
    # ========== CONFIGURATION PYDANTIC ==========
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Instance globale des settings
settings = Settings()


def ensure_storage_path():
    """Crée le dossier de stockage s'il n'existe pas"""
    try:
        settings.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"⚠️ Impossible de créer le dossier de stockage: {e}")


# Créer les dossiers nécessaires
ensure_storage_path()


# Configuration pour le logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "addons/Automobiles/api/storage/asac_api.log",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}