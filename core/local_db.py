# core/local_db.py
"""
Base de données locale SQLite pour le mode hors-ligne
Lecture instantanée, écriture différée, synchronisation automatique
"""

import sqlite3
import json
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from PySide6.QtCore import QObject, Signal, QTimer

from core.logger import logger


# ============================================================================
# CONSTANTES ET CONFIGURATION
# ============================================================================

class SyncStatus(Enum):
    """Statut de synchronisation d'un élément"""
    SYNCED = "synced"       # Synchronisé avec le serveur
    PENDING = "pending"     # En attente de synchronisation
    CONFLICT = "conflict"   # Conflit à résoudre
    DELETED = "deleted"     # Marqué pour suppression


@dataclass
class SyncMetadata:
    """Métadonnées de synchronisation"""
    last_sync: datetime
    items_synced: int
    items_pending: int
    items_conflict: int
    last_error: Optional[str] = None


# ============================================================================
# CACHE LOCAL SQLITE
# ============================================================================

class LocalDatabase(QObject):
    """Base de données locale SQLite pour le travail hors-ligne"""
    
    # Signaux
    sync_started = Signal()
    sync_finished = Signal(int, int)  # success, errors
    data_changed = Signal(str, str)   # table, action
    cache_ready = Signal()
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
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
        self._init_sync_timer()
    
    def _init_db(self):
        """Initialise la base SQLite locale"""
        # Dossier de cache
        cache_dir = Path.home() / '.lometa_cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = cache_dir / 'lometa_local.db'
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=10)
        self.conn.row_factory = sqlite3.Row
        
        # Activer les contraintes FK et WAL pour performance
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA cache_size = 10000")
        
        self._create_tables()
        self._create_indexes()
        
        logger.info(f"✅ Base locale initialisée: {self.db_path}")
    
    def _create_tables(self):
        """Crée toutes les tables du cache local"""
        
        # Table des contrats
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS contrats (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                hash TEXT,
                status TEXT DEFAULT 'synced',
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Table des véhicules
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vehicules (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                hash TEXT,
                status TEXT DEFAULT 'synced',
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des clients
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                hash TEXT,
                status TEXT DEFAULT 'synced',
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des compagnies (référentiel)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS compagnies (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                last_sync TIMESTAMP
            )
        """)
        
        # Table des flottes
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS flottes (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                hash TEXT,
                status TEXT DEFAULT 'synced',
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des paiements
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS paiements (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                hash TEXT,
                status TEXT DEFAULT 'synced',
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des sinistres
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sinistres (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                hash TEXT,
                status TEXT DEFAULT 'synced',
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Métadonnées de synchronisation
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP
            )
        """)
        
        # Queue de synchronisation
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                retry_count INTEGER DEFAULT 0
            )
        """)
        
        self.conn.commit()
        logger.info("✅ Tables du cache local créées")
    
    def _create_indexes(self):
        """Crée les index pour accélérer les recherches"""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_contrats_status ON contrats(status)",
            "CREATE INDEX IF NOT EXISTS idx_contrats_last_sync ON contrats(last_sync)",
            "CREATE INDEX IF NOT EXISTS idx_vehicules_status ON vehicules(status)",
            "CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status)",
            "CREATE INDEX IF NOT EXISTS idx_flottes_status ON flottes(status)",
            "CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(retry_count, created_at)",
        ]
        
        for idx in indexes:
            try:
                self.conn.execute(idx)
            except Exception as e:
                logger.warning(f"Erreur création index: {e}")
        
        self.conn.commit()
    
    def _init_sync_timer(self):
        """Initialise le timer de synchronisation automatique"""
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_with_server)
        self.sync_timer.start(300000)  # Sync toutes les 5 minutes
        logger.info("✅ Timer de synchronisation actif (5 minutes)")
    
    # ============================================================================
    # MÉTHODES DE LECTURE (ULTRA RAPIDES)
    # ============================================================================
    
    def get_contrats(self, page: int = 0, page_size: int = 50, 
                     filters: Dict = None) -> List[Dict]:
        """Récupère les contrats du cache local (instantané)"""
        start = time.time()
        
        try:
            # Construction de la requête
            query = "SELECT data FROM contrats WHERE status != 'deleted' ORDER BY id DESC LIMIT ? OFFSET ?"
            params = [page_size, page * page_size]
            
            cursor = self.conn.execute(query, params)
            contrats = [json.loads(row['data']) for row in cursor.fetchall()]
            
            elapsed = (time.time() - start) * 1000
            logger.debug(f"📖 Lecture {len(contrats)} contrats: {elapsed:.2f}ms")
            
            return contrats
            
        except Exception as e:
            logger.error(f"Erreur lecture contrats: {e}")
            return []
    
    def get_vehicules(self, page: int = 0, page_size: int = 50) -> List[Dict]:
        """Récupère les véhicules du cache local"""
        start = time.time()
        
        try:
            cursor = self.conn.execute("""
                SELECT data FROM vehicules 
                WHERE status != 'deleted' 
                ORDER BY id DESC 
                LIMIT ? OFFSET ?
            """, (page_size, page * page_size))
            
            vehicules = [json.loads(row['data']) for row in cursor.fetchall()]
            
            elapsed = (time.time() - start) * 1000
            logger.debug(f"📖 Lecture {len(vehicules)} véhicules: {elapsed:.2f}ms")
            
            return vehicules
            
        except Exception as e:
            logger.error(f"Erreur lecture vehicules: {e}")
            return []
    
    def get_compagnies(self) -> List[Dict]:
        """Récupère les compagnies (référentiel complet)"""
        try:
            cursor = self.conn.execute("SELECT data FROM compagnies")
            return [json.loads(row['data']) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erreur lecture compagnies: {e}")
            return []
    
    def get_by_id(self, table: str, record_id: int) -> Optional[Dict]:
        """Récupère un enregistrement par ID"""
        try:
            cursor = self.conn.execute(
                f"SELECT data FROM {table} WHERE id = ? AND status != 'deleted'",
                (record_id,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row['data'])
            return None
        except Exception as e:
            logger.error(f"Erreur lecture {table} id {record_id}: {e}")
            return None
    
    def search(self, table: str, search_text: str, fields: List[str], limit: int = 50) -> List[Dict]:
        """Recherche textuelle dans le cache local (ultra rapide)"""
        try:
            # Construction de la condition WHERE
            conditions = " OR ".join([f"json_extract(data, '$.{f}') LIKE ?" for f in fields])
            query = f"""
                SELECT data FROM {table} 
                WHERE status != 'deleted' AND ({conditions})
                LIMIT ?
            """
            params = [f"%{search_text}%" for _ in fields] + [limit]
            
            cursor = self.conn.execute(query, params)
            return [json.loads(row['data']) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Erreur recherche dans {table}: {e}")
            return []
    
    # ============================================================================
    # MÉTHODES D'ÉCRITURE (AVEC QUEUE DE SYNCHRO)
    # ============================================================================
    
    def save(self, table: str, data: Dict, immediate_sync: bool = False) -> bool:
        """Sauvegarde un enregistrement en local"""
        try:
            record_id = data.get('id')
            if not record_id:
                logger.error(f"Impossible de sauvegarder {table}: pas d'ID")
                return False
            
            # Calcul du hash pour détecter les modifications
            import hashlib
            data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
            
            # Vérifier si l'enregistrement existe déjà
            existing = self.conn.execute(
                f"SELECT hash, status FROM {table} WHERE id = ?",
                (record_id,)
            ).fetchone()
            
            if existing:
                # Mise à jour
                self.conn.execute(f"""
                    UPDATE {table} 
                    SET data = ?, hash = ?, updated_at = ?,
                        status = CASE WHEN status = 'synced' THEN 'pending' ELSE status END
                    WHERE id = ?
                """, (json.dumps(data), data_hash, datetime.now(), record_id))
            else:
                # Insertion
                self.conn.execute(f"""
                    INSERT INTO {table} (id, data, hash, status, created_at, updated_at)
                    VALUES (?, ?, ?, 'pending', ?, ?)
                """, (record_id, json.dumps(data), data_hash, datetime.now(), datetime.now()))
            
            # Ajouter à la queue de synchronisation
            self.conn.execute("""
                INSERT INTO sync_queue (table_name, record_id, action, data)
                VALUES (?, ?, 'upsert', ?)
            """, (table, record_id, json.dumps(data)))
            
            self.conn.commit()
            self.data_changed.emit(table, 'saved')
            
            logger.debug(f"💾 Sauvegarde locale: {table}/{record_id}")
            
            if immediate_sync:
                self.sync_with_server()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde {table}: {e}")
            self.conn.rollback()
            return False
    
    def delete(self, table: str, record_id: int, soft_delete: bool = True) -> bool:
        """Supprime un enregistrement (soft ou hard)"""
        try:
            if soft_delete:
                # Soft delete: marquer comme supprimé
                self.conn.execute(f"""
                    UPDATE {table} SET status = 'deleted', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(), record_id))
                
                # Ajouter à la queue
                self.conn.execute("""
                    INSERT INTO sync_queue (table_name, record_id, action)
                    VALUES (?, ?, 'delete')
                """, (table, record_id))
            else:
                # Hard delete: suppression pure
                self.conn.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
            
            self.conn.commit()
            self.data_changed.emit(table, 'deleted')
            
            logger.debug(f"🗑️ Suppression locale: {table}/{record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression {table}: {e}")
            self.conn.rollback()
            return False
    
    # ============================================================================
    # SYNCHRONISATION AVEC LE SERVEUR
    # ============================================================================
    
    def sync_with_server(self):
        """Synchronise les données locales avec le serveur distant"""
        import threading
        from core.database import SessionLocal
        from sqlalchemy import text
        
        def sync():
            self.sync_started.emit()
            logger.info("🔄 Début de la synchronisation...")
            
            success_count = 0
            error_count = 0
            
            db = None
            try:
                db = SessionLocal()
                
                # 1. Envoyer les modifications locales (queue)
                pending = self.conn.execute("""
                    SELECT id, table_name, record_id, action, data 
                    FROM sync_queue 
                    ORDER BY created_at
                    LIMIT 100
                """).fetchall()
                
                for item in pending:
                    try:
                        if item['action'] == 'upsert' and item['data']:
                            data = json.loads(item['data'])
                            # Mettre à jour sur le serveur
                            table = item['table_name']
                            record_id = item['record_id']
                            
                            # Construction dynamique de l'UPDATE
                            # (à adapter selon vos tables)
                            if table == 'contrats':
                                db.execute(text("""
                                    UPDATE contrats SET 
                                        numero_police = :numero_police,
                                        prime_totale_ttc = :prime_totale_ttc,
                                        updated_at = NOW()
                                    WHERE id = :id
                                """), data)
                            
                            db.commit()
                            
                            # Marquer comme synchronisé
                            self.conn.execute("""
                                UPDATE sync_queue SET retry_count = 0 WHERE id = ?
                            """, (item['id'],))
                            self.conn.execute(f"""
                                UPDATE {item['table_name']} 
                                SET status = 'synced', last_sync = ? 
                                WHERE id = ?
                            """, (datetime.now(), item['record_id']))
                            
                            success_count += 1
                            
                        elif item['action'] == 'delete':
                            # Suppression sur le serveur
                            db.execute(text(f"""
                                UPDATE {item['table_name']} SET is_active = false, updated_at = NOW()
                                WHERE id = {item['record_id']}
                            """))
                            db.commit()
                            
                            self.conn.execute("DELETE FROM sync_queue WHERE id = ?", (item['id'],))
                            success_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Erreur synchro item {item['id']}: {e}")
                        # Incrémenter le compteur de retry
                        self.conn.execute("""
                            UPDATE sync_queue SET retry_count = retry_count + 1
                            WHERE id = ?
                        """, (item['id'],))
                
                # 2. Récupérer les nouvelles données du serveur
                last_sync = self.conn.execute(
                    "SELECT value FROM sync_metadata WHERE key = 'last_full_sync'"
                ).fetchone()
                
                last_sync_time = last_sync['value'] if last_sync else '2000-01-01'
                
                # Récupérer les contrats récents
                contrats = db.execute(text("""
                    SELECT * FROM contrats 
                    WHERE updated_at > :last_sync OR created_at > :last_sync
                    LIMIT 500
                """), {"last_sync": last_sync_time}).fetchall()
                
                for contrat in contrats:
                    self.conn.execute("""
                        INSERT OR REPLACE INTO contrats (id, data, last_sync, status)
                        VALUES (?, ?, ?, 'synced')
                    """, (contrat.id, json.dumps(dict(contrat)), datetime.now()))
                
                # Mettre à jour la métadonnée
                self.conn.execute("""
                    INSERT OR REPLACE INTO sync_metadata (key, value, updated_at)
                    VALUES ('last_full_sync', ?, ?)
                """, (datetime.now().isoformat(), datetime.now()))
                
                self.conn.commit()
                
                logger.info(f"✅ Synchronisation terminée: {success_count} succès, {error_count} erreurs")
                self.sync_finished.emit(success_count, error_count)
                
            except Exception as e:
                logger.error(f"❌ Erreur synchronisation: {e}")
                self.sync_finished.emit(success_count, error_count)
            finally:
                if db:
                    db.close()
        
        thread = threading.Thread(target=sync, daemon=True)
        thread.start()
    
    # ============================================================================
    # INITIALISATION ET MAINTENANCE
    # ============================================================================
    
    def load_initial_data(self):
        """Charge les données initiales depuis le serveur"""
        import threading
        from core.database import SessionLocal
        from addons.Automobiles.models import Compagnie, Contrat, Vehicle, Contact
        
        def load():
            logger.info("📥 Chargement initial des données...")
            db = SessionLocal()
            try:
                # 1. Compagnies (référentiel essentiel)
                compagnies = db.query(Compagnie).filter(Compagnie.is_active == True).all()
                for c in compagnies:
                    self.conn.execute("""
                        INSERT OR REPLACE INTO compagnies (id, data, last_sync)
                        VALUES (?, ?, ?)
                    """, (c.id, json.dumps({
                        'id': c.id,
                        'code': c.code,
                        'nom': c.nom,
                        'email': c.email,
                        'telephone': c.telephone,
                        'num_debut': c.num_debut,
                        'num_fin': c.num_fin
                    }), datetime.now()))
                
                # 2. Contrats des 3 derniers mois
                from datetime import timedelta
                three_months_ago = datetime.now() - timedelta(days=90)
                contrats = db.query(Contrat).filter(
                    Contrat.created_at > three_months_ago
                ).limit(1000).all()
                
                for c in contrats:
                    self.save('contrats', {
                        'id': c.id,
                        'numero_police': c.numero_police,
                        'prime_totale_ttc': c.prime_totale_ttc,
                        'statut_paiement': c.statut_paiement,
                        'created_at': c.created_at.isoformat() if c.created_at else None
                    })
                
                # 3. Véhicules
                vehicules = db.query(Vehicle).limit(500).all()
                for v in vehicules:
                    self.save('vehicules', {
                        'id': v.id,
                        'immatriculation': v.immatriculation,
                        'marque': v.marque,
                        'modele': v.modele,
                        'annee': v.annee
                    })
                
                self.conn.commit()
                
                logger.info(f"✅ Chargement initial terminé:")
                logger.info(f"   - {len(compagnies)} compagnies")
                logger.info(f"   - {len(contrats)} contrats")
                logger.info(f"   - {len(vehicules)} véhicules")
                
                self.cache_ready.emit()
                
            except Exception as e:
                logger.error(f"❌ Erreur chargement initial: {e}")
            finally:
                db.close()
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques du cache local"""
        try:
            stats = {}
            tables = ['contrats', 'vehicules', 'clients', 'compagnies', 'flottes', 'paiements']
            
            for table in tables:
                cursor = self.conn.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                        SUM(CASE WHEN status = 'synced' THEN 1 ELSE 0 END) as synced
                    FROM {table}
                """)
                row = cursor.fetchone()
                stats[table] = {
                    'total': row['total'] or 0,
                    'pending': row['pending'] or 0,
                    'synced': row['synced'] or 0
                }
            
            # Queue de synchronisation
            cursor = self.conn.execute("SELECT COUNT(*) as count FROM sync_queue")
            stats['sync_queue'] = cursor.fetchone()['count']
            
            # Taille de la base
            import os
            stats['db_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur stats cache: {e}")
            return {}
    
    def clear_cache(self):
        """Vide complètement le cache"""
        try:
            tables = ['contrats', 'vehicules', 'clients', 'compagnies', 'flottes', 'paiements', 'sinistres', 'sync_queue']
            for table in tables:
                self.conn.execute(f"DELETE FROM {table}")
            self.conn.execute("DELETE FROM sync_metadata")
            self.conn.commit()
            logger.info("🗑️ Cache vidé")
        except Exception as e:
            logger.error(f"Erreur vidage cache: {e}")
    
    def close(self):
        """Ferme la connexion SQLite"""
        if hasattr(self, 'sync_timer'):
            self.sync_timer.stop()
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.info("✅ Base locale fermée")


# Instance globale unique
local_db = LocalDatabase()