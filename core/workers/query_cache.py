# core/workers/query_cache.py
"""
Cache pour les résultats de requêtes SQLAlchemy
"""

from datetime import datetime, timedelta
import hashlib
import json
from typing import Any, Optional, Callable


class QueryCache:
    """Cache simple pour les résultats de requêtes"""
    
    _instance = None
    _cache: dict = {}
    _ttl: dict = {}
    _default_ttl = 300  # 5 minutes
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _make_key(self, query: str, params: dict = None) -> str:
        """Génère une clé unique"""
        key = query
        if params:
            key += json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(key.encode()).hexdigest()
    
    def get_or_compute(self, key: str, compute_func: Callable, ttl: int = None) -> Any:
        """
        Récupère du cache ou calcule
        
        Args:
            key: Clé du cache
            compute_func: Fonction à exécuter si pas en cache
            ttl: Durée de vie en secondes
        """
        if key in self._cache:
            if key in self._ttl and datetime.now() < self._ttl[key]:
                return self._cache[key]
            else:
                # Expiré, supprimer
                del self._cache[key]
                if key in self._ttl:
                    del self._ttl[key]
        
        # Calculer la valeur
        result = compute_func()
        
        # Mettre en cache
        self._cache[key] = result
        self._ttl[key] = datetime.now() + timedelta(seconds=ttl or self._default_ttl)
        
        return result
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Définit une valeur dans le cache"""
        self._cache[key] = value
        self._ttl[key] = datetime.now() + timedelta(seconds=ttl or self._default_ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if key in self._cache:
            if key in self._ttl and datetime.now() < self._ttl[key]:
                return self._cache[key]
            else:
                del self._cache[key]
                if key in self._ttl:
                    del self._ttl[key]
        return None
    
    def invalidate(self, pattern: str = None):
        """Invalide le cache"""
        if pattern:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                if key in self._ttl:
                    del self._ttl[key]
        else:
            self._cache.clear()
            self._ttl.clear()
    
    def clear(self):
        """Vide le cache"""
        self._cache.clear()
        self._ttl.clear()


# Instance globale
query_cache = QueryCache()