# core/local_cache.py
"""
Cache local SQLite pour LOMETA
- Persistant entre les sessions
- Supporte les collections paginées
- Gère l'expiration des données
- Thread-safe
"""

import sqlite3
import json
import hashlib
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from PySide6.QtCore import QObject, Signal, QTimer

from core.logger import logger


# ============================================================================
# DÉCORATEUR POUR CACHER LES DONNÉES
# ============================================================================

def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """
    Décorateur pour mettre automatiquement en cache les résultats d'une fonction
    
    Usage:
        @cached(ttl_seconds=600)
        def get_compagnies():
            return db.query(Compagnie).all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer une clé unique basée sur le nom de la fonction et les arguments
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Essayer le cache
            cached_result = LocalCache.instance().get(cache_key)
            if cached_result is not None:
                logger.debug(f"📦 Cache hit: {func.__name__}")
                return cached_result
            
            # Exécuter la fonction
            result = func(*args, **kwargs)
            
            # Mettre en cache
            LocalCache.instance().set(cache_key, result, ttl_seconds=ttl_seconds)
            logger.debug(f"💾 Cache miss: {func.__name__}")
            
            return result
        return wrapper
    return decorator


# ============================================================================
# CLASSE PRINCIPALE DU CACHE
# ============================================================================

class LocalCache(QObject):
    """Cache local SQLite - Singleton thread-safe"""
    
    # Signaux
    cache_cleared = Signal(str)  # module
    cache_updated = Signal(str, str)  # key, action
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._init_db()
        self._start_cleanup_timer()
    
    def _init_db(self):
        """Initialise la base SQLite"""
        # Dossier de cache dans le répertoire utilisateur
        cache_dir = Path.home() / '.lometa' / 'cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = cache_dir / 'cache.db'
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=10)
        self.conn.row_factory = sqlite3.Row
        
        # Activer les bonnes pratiques SQLite
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA cache_size = 10000")
        
        self._create_tables()
        
        logger.info(f"✅ Cache local initialisé: {self.db_path}")
        logger.info(f"   Taille actuelle: {self.get_size():.2f} MB")
    
    def _create_tables(self):
        """Crée les tables nécessaires"""
        
        # Table principale des clés/valeurs
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_items (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                module TEXT,
                tags TEXT,
                created_at REAL,
                expires_at REAL,
                last_access REAL,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Table des collections paginées
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                page INTEGER DEFAULT 0,
                data TEXT NOT NULL,
                total_count INTEGER,
                created_at REAL,
                UNIQUE(name, page)
            )
        """)
        
        # Table des métadonnées
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at REAL
            )
        """)
        
        # Index pour accélérer les recherches
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_module ON cache_items(module)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_items(expires_at)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_collections_name ON cache_collections(name)")
        
        self.conn.commit()
    
    def _start_cleanup_timer(self):
        """Démarre un timer pour nettoyer les entrées expirées"""
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired)
        self.cleanup_timer.start(3600000)  # Toutes les heures
    
    def _cleanup_expired(self):
        """Supprime les entrées expirées"""
        now = time.time()
        deleted = self.conn.execute(
            "DELETE FROM cache_items WHERE expires_at IS NOT NULL AND expires_at < ?",
            (now,)
        ).rowcount
        if deleted > 0:
            self.conn.commit()
            logger.debug(f"🗑️ {deleted} entrées expirées supprimées du cache")
    
    # ============================================================================
    # MÉTHODES PRINCIPALES
    # ============================================================================
    
    def set(self, key: str, value: Any, module: str = None, 
            tags: List[str] = None, ttl_seconds: int = None) -> bool:
        """
        Stocke une valeur en cache
        
        Args:
            key: Clé unique
            value: Valeur à stocker (sera sérialisée en JSON)
            module: Nom du module (pour suppression par module)
            tags: Tags pour recherche par groupe
            ttl_seconds: Durée de vie (None = permanent)
        """
        try:
            now = time.time()
            expires_at = now + ttl_seconds if ttl_seconds else None
            
            # Calculer un hash pour détecter les changements
            value_json = json.dumps(value, default=str, ensure_ascii=False)
            value_hash = hashlib.md5(value_json.encode()).hexdigest()
            
            # Vérifier si la valeur a changé
            existing = self.conn.execute(
                "SELECT value FROM cache_items WHERE key = ?", (key,)
            ).fetchone()
            
            if existing and json.loads(existing['value']) == value:
                # Même valeur, juste mettre à jour l'accès
                self.conn.execute("""
                    UPDATE cache_items 
                    SET last_access = ?, access_count = access_count + 1
                    WHERE key = ?
                """, (now, key))
            else:
                # Nouvelle valeur ou valeur modifiée
                tags_json = json.dumps(tags) if tags else None
                self.conn.execute("""
                    INSERT OR REPLACE INTO cache_items 
                    (key, value, module, tags, created_at, expires_at, last_access, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 
                        COALESCE((SELECT access_count + 1 FROM cache_items WHERE key = ?), 1))
                """, (key, value_json, module, tags_json, now, expires_at, now, key))
            
            self.conn.commit()
            self.cache_updated.emit(key, 'set')
            return True
            
        except Exception as e:
            logger.error(f"Erreur cache set {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            now = time.time()
            cursor = self.conn.execute("""
                SELECT value, expires_at FROM cache_items WHERE key = ?
            """, (key,))
            row = cursor.fetchone()
            
            if row:
                # Vérifier expiration
                if row['expires_at'] and now > row['expires_at']:
                    self.delete(key)
                    return default
                
                # Mettre à jour les statistiques d'accès
                self.conn.execute("""
                    UPDATE cache_items SET last_access = ?, access_count = access_count + 1
                    WHERE key = ?
                """, (now, key))
                self.conn.commit()
                
                return json.loads(row['value'])
            
            return default
            
        except Exception as e:
            logger.error(f"Erreur cache get {key}: {e}")
            return default
    
    def get_or_compute(self, key: str, compute_func: Callable, 
                       ttl_seconds: int = None, **kwargs) -> Any:
        """
        Récupère du cache ou calcule si absent
        
        Usage:
            value = cache.get_or_compute("compagnies", get_compagnies_from_db, ttl_seconds=600)
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = compute_func(**kwargs)
        self.set(key, value, ttl_seconds=ttl_seconds)
        return value
    
    def delete(self, key: str) -> bool:
        """Supprime une entrée du cache"""
        try:
            self.conn.execute("DELETE FROM cache_items WHERE key = ?", (key,))
            self.conn.commit()
            self.cache_updated.emit(key, 'delete')
            return True
        except Exception as e:
            logger.error(f"Erreur cache delete {key}: {e}")
            return False
    
    def delete_by_module(self, module: str) -> int:
        """Supprime toutes les entrées d'un module"""
        try:
            deleted = self.conn.execute(
                "DELETE FROM cache_items WHERE module = ?", (module,)
            ).rowcount
            self.conn.commit()
            self.cache_cleared.emit(module)
            logger.info(f"🗑️ Cache du module '{module}' vidé ({deleted} entrées)")
            return deleted
        except Exception as e:
            logger.error(f"Erreur delete_by_module {module}: {e}")
            return 0
    
    def delete_by_tag(self, tag: str) -> int:
        """Supprime toutes les entrées avec un tag spécifique"""
        try:
            deleted = self.conn.execute(
                "DELETE FROM cache_items WHERE tags LIKE ?", (f'%"{tag}"%',)
            ).rowcount
            self.conn.commit()
            return deleted
        except Exception as e:
            logger.error(f"Erreur delete_by_tag {tag}: {e}")
            return 0
    
    def clear_all(self) -> int:
        """Vide complètement le cache"""
        try:
            deleted = self.conn.execute("DELETE FROM cache_items").rowcount
            self.conn.execute("DELETE FROM cache_collections")
            self.conn.commit()
            self.cache_cleared.emit('all')
            logger.info(f"🗑️ Cache complètement vidé ({deleted} entrées)")
            return deleted
        except Exception as e:
            logger.error(f"Erreur clear_all: {e}")
            return 0
    
    # ============================================================================
    # COLLECTIONS PAGINÉES
    # ============================================================================
    
    def save_collection(self, name: str, data: List[Dict], 
                        page: int = 0, total_count: int = None) -> bool:
        """Sauvegarde une collection paginée"""
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO cache_collections (name, page, data, total_count, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (name, page, json.dumps(data, default=str), total_count, time.time()))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erreur save_collection {name}: {e}")
            return False
    
    def get_collection(self, name: str, page: int = 0) -> Optional[List[Dict]]:
        """Récupère une collection paginée"""
        try:
            cursor = self.conn.execute(
                "SELECT data FROM cache_collections WHERE name = ? AND page = ?",
                (name, page)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row['data'])
            return None
        except Exception as e:
            logger.error(f"Erreur get_collection {name}: {e}")
            return None
    
    def invalidate_collection(self, name: str):
        """Invalide toutes les pages d'une collection"""
        try:
            deleted = self.conn.execute(
                "DELETE FROM cache_collections WHERE name = ?", (name,)
            ).rowcount
            self.conn.commit()
            if deleted > 0:
                logger.debug(f"🗑️ Collection '{name}' invalidée ({deleted} pages)")
        except Exception as e:
            logger.error(f"Erreur invalidate_collection {name}: {e}")
    
    # ============================================================================
    # STATISTIQUES ET MAINTENANCE
    # ============================================================================
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques du cache"""
        try:
            total = self.conn.execute("SELECT COUNT(*) FROM cache_items").fetchone()[0]
            expired = self.conn.execute(
                "SELECT COUNT(*) FROM cache_items WHERE expires_at IS NOT NULL AND expires_at < ?",
                (time.time(),)
            ).fetchone()[0]
            
            return {
                'total_entries': total,
                'expired_entries': expired,
                'db_size_mb': self.get_size(),
                'modules': self.get_modules_stats()
            }
        except Exception as e:
            logger.error(f"Erreur get_stats: {e}")
            return {}
    
    def get_modules_stats(self) -> Dict:
        """Statistiques par module"""
        try:
            cursor = self.conn.execute("""
                SELECT module, COUNT(*) as count 
                FROM cache_items 
                WHERE module IS NOT NULL 
                GROUP BY module
            """)
            return {row['module']: row['count'] for row in cursor.fetchall()}
        except Exception as e:
            return {}
    
    def get_size(self) -> float:
        """Taille de la base de cache en MB"""
        try:
            return self.db_path.stat().st_size / (1024 * 1024)
        except:
            return 0
    
    def vacuum(self):
        """Optimise la base de données"""
        try:
            self.conn.execute("VACUUM")
            logger.info(f"✅ Base de cache optimisée (taille: {self.get_size():.2f} MB)")
        except Exception as e:
            logger.error(f"Erreur vacuum: {e}")
    
    def close(self):
        """Ferme la connexion"""
        if hasattr(self, 'cleanup_timer'):
            self.cleanup_timer.stop()
        if hasattr(self, 'conn'):
            self.vacuum()
            self.conn.close()
            logger.info("✅ Cache local fermé")


# Instance unique (singleton)
_cache_instance = None

def LocalCacheInstance() -> LocalCache:
    """Retourne l'instance unique du cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LocalCache()
    return _cache_instance


# Alias court pour faciliter l'utilisation
cache = LocalCacheInstance()