# addons/Automobiles/api/__init__.py
"""
Module API ASAC - Édition d'attestations d'assurance automobile
"""

from addons.Automobiles.api.main import app
from addons.Automobiles.api.config import settings

__version__ = "1.2.0"
__all__ = ["app", "settings"]