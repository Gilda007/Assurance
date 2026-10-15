# core/certificate_mode.py
"""
Détection et gestion du mode de certification (DEV / PRODUCTION)
"""
from enum import Enum
from pathlib import Path
import json
from typing import Optional, Dict, Any

class CertificateMode(Enum):
    DEV = "development"
    PRODUCTION = "production"
    UNKNOWN = "unknown"

class CertificateModeDetector:
    """
    Détecte le mode de certification à partir de :
      1. Variable d'environnement LOMETA_CERT_MODE (priorité max)
      2. Fichier de configuration ~/.lometa/certificates/mode.json
      3. Présence des fichiers de dev (developer_public_key.pem, lometa_ca.crt)
      4. Fallback : production
    """
    
    DEV_MARKERS = [
        "developer_public_key.pem",
        "lometa_ca.crt",
        "certificate_chain.pem",
        "developer_private_key.pem",
    ]
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".lometa" / "certificates"
        self._mode: Optional[CertificateMode] = None
        self._details: Dict[str, Any] = {}
    
    def detect(self, force: bool = False) -> CertificateMode:
        if self._mode is not None and not force:
            return self._mode
        
        # 1. Variable d'environnement
        import os
        env_mode = os.environ.get("LOMETA_CERT_MODE", "").lower()
        if env_mode in ("dev", "development"):
            return self._set(CertificateMode.DEV, "env_var")
        if env_mode in ("prod", "production"):
            return self._set(CertificateMode.PRODUCTION, "env_var")
        
        # 2. Fichier mode.json
        mode_file = self.config_dir / "mode.json"
        if mode_file.exists():
            try:
                data = json.loads(mode_file.read_text(encoding="utf-8"))
                mode_str = data.get("mode", "").lower()
                if mode_str in ("dev", "development"):
                    return self._set(CertificateMode.DEV, "mode.json")
                if mode_str in ("prod", "production"):
                    return self._set(CertificateMode.PRODUCTION, "mode.json")
            except Exception:
                pass
        
        # 3. Détection par présence des fichiers
        dev_files_found = [
            f for f in self.DEV_MARKERS if (self.config_dir / f).exists()
        ]
        if dev_files_found:
            return self._set(CertificateMode.DEV, "file_markers", {
                "files": dev_files_found
            })
        
        # 4. Fallback
        return self._set(CertificateMode.PRODUCTION, "default")
    
    def _set(self, mode, source, details=None):
        self._mode = mode
        self._details = {"source": source, **(details or {})}
        return mode
    
    @property
    def details(self):
        return self._details
    
    def is_dev(self) -> bool:
        return self.detect() == CertificateMode.DEV
    
    def is_production(self) -> bool:
        return self.detect() == CertificateMode.PRODUCTION
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "mode": self.detect().value,
            "is_dev": self.is_dev(),
            "is_production": self.is_production(),
            "details": self._details,
        }


# Singleton global
_detector_instance: Optional[CertificateModeDetector] = None

def get_certificate_mode_detector() -> CertificateModeDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = CertificateModeDetector()
    return _detector_instance

def get_certificate_mode() -> CertificateMode:
    return get_certificate_mode_detector().detect()

def is_dev_mode() -> bool:
    return get_certificate_mode_detector().is_dev()