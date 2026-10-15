import os
from pathlib import Path

class Settings:
    # Base
    PROJECT_NAME: str = "ASAC API"
    VERSION: str = "1.2.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./asac.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "xyhb7HragP8rYbEMeN4RyEcNdxzFX3kKZA5PBm2bI1o=")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 365
    
    # ASAC Configuration
    ASAC_APP_KEY: str = os.getenv("ASAC_APP_KEY", "")
    ASAC_USERNAME: str = os.getenv("ASAC_USERNAME", "")
    
    # Storage
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", "./storage"))
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
settings = Settings()