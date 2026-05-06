# auth_db.py
"""
Module d'authentification avec PostgreSQL pour le serveur de modules
"""

import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import pool, extras
from contextlib import contextmanager


class DatabaseAuth:
    """Gestionnaire d'authentification PostgreSQL"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_config: Configuration PostgreSQL
                {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'ams_db',
                    'user': 'postgres',
                    'password': 'password'
                }
        """
        self.db_config = db_config
        self.connection_pool = None
        self._init_pool()
    
    def _init_pool(self):
        """Initialise le pool de connexions"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 10,
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                database=self.db_config.get('database', 'ams_db'),
                user=self.db_config.get('user', 'postgres'),
                password=self.db_config.get('password', '')
            )
            print("✅ Connexion à PostgreSQL établie")
        except Exception as e:
            print(f"❌ Erreur de connexion à PostgreSQL: {e}")
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """Récupère une connexion du pool"""
        conn = None
        try:
            if self.connection_pool:
                conn = self.connection_pool.getconn()
                yield conn
            else:
                yield None
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    def authenticate_user(self, username: str, password: str) -> tuple:
        """
        Authentifie un utilisateur via PostgreSQL
        
        Returns:
            (success: bool, user_info: dict, message: str)
        """
        try:
            with self.get_connection() as conn:
                if not conn:
                    return False, None, "Erreur de connexion à la base de données"
                
                with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                    # Vérifier les identifiants
                    query = """
                        SELECT 
                            id, 
                            username, 
                            nom, 
                            prenom, 
                            email, 
                            role,
                            active,
                            last_login
                        FROM utilisateurs 
                        WHERE username = %s AND active = true
                    """
                    cur.execute(query, (username,))
                    user = cur.fetchone()
                    
                    if not user:
                        return False, None, "Nom d'utilisateur incorrect"
                    
                    # Vérifier le mot de passe (support des hash bcrypt et plain text)
                    if self._verify_password(password, user.get('password_hash', '')):
                        # Mettre à jour la date de dernière connexion
                        update_query = """
                            UPDATE utilisateurs 
                            SET last_login = %s 
                            WHERE id = %s
                        """
                        cur.execute(update_query, (datetime.now(), user['id']))
                        conn.commit()
                        
                        return True, dict(user), "Connexion réussie"
                    else:
                        return False, None, "Mot de passe incorrect"
                        
        except Exception as e:
            print(f"Erreur authentification: {e}")
            return False, None, f"Erreur système: {str(e)}"
    
    def _verify_password(self, input_password: str, stored_hash: str) -> bool:
        """Vérifie le mot de passe (supporte différents formats)"""
        if not stored_hash:
            return False
        
        # Si le mot de passe est stocké en clair (ancienne version)
        if len(stored_hash) < 30 and not stored_hash.startswith('$2'):
            return input_password == stored_hash
        
        # Format bcrypt
        try:
            import bcrypt
            return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False
    
    def create_session_token(self, user_id: int) -> str:
        """Crée un token de session pour l'utilisateur"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return None
                
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO sessions (user_id, token, expires_at, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (token) DO UPDATE 
                        SET expires_at = EXCLUDED.expires_at
                    """
                    cur.execute(query, (user_id, token, expires_at, datetime.now()))
                    conn.commit()
                    
                    return token
        except Exception as e:
            print(f"Erreur création session: {e}")
            return None
    
    def get_user_by_token(self, token: str) -> Optional[Dict]:
        """Récupère un utilisateur à partir d'un token"""
        try:
            with self.get_connection() as conn:
                if not conn:
                    return None
                
                with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                    query = """
                        SELECT u.* 
                        FROM utilisateurs u
                        JOIN sessions s ON s.user_id = u.id
                        WHERE s.token = %s 
                        AND s.expires_at > %s
                        AND u.active = true
                    """
                    cur.execute(query, (token, datetime.now()))
                    return dict(cur.fetchone()) if cur.rowcount > 0 else None
        except Exception as e:
            print(f"Erreur récupération utilisateur: {e}")
            return None
    
    def has_permission(self, user: Dict, action: str) -> bool:
        """
        Vérifie les permissions d'un utilisateur
        
        Args:
            user: Informations utilisateur
            action: 'download', 'upload', 'delete', 'admin'
        """
        if not user:
            return False
        
        role = user.get('role', 'user')
        
        # Admin a tous les droits
        if role == 'admin':
            return True
        
        # Définir les permissions par rôle
        permissions = {
            'user': ['download'],
            'manager': ['download', 'upload'],
            'admin': ['download', 'upload', 'delete', 'admin']
        }
        
        return action in permissions.get(role, [])


class SimpleAuth:
    """Authentification simplifiée sans base de données (fallback)"""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username or "admin"
        self.password = password or "admin123"
    
    def authenticate_user(self, username: str, password: str) -> tuple:
        """Authentification simple"""
        if username == self.username and password == self.password:
            return True, {
                'id': 1,
                'username': username,
                'nom': 'Administrateur',
                'prenom': '',
                'email': 'admin@lomenta.com',
                'role': 'admin',
                'active': True
            }, "Connexion réussie"
        return False, None, "Identifiants incorrects"
    
    def has_permission(self, user: Dict, action: str) -> bool:
        """Vérification des permissions"""
        if not user:
            return False
        return user.get('role') == 'admin'
    
    def create_session_token(self, user_id: int) -> str:
        return secrets.token_urlsafe(32)
    
    def get_user_by_token(self, token: str) -> Optional[Dict]:
        return None


def get_auth_handler(db_config: Dict[str, Any] = None):
    """
    Factory pour créer le handler d'authentification approprié
    
    Args:
        db_config: Configuration PostgreSQL (optionnel)
    """
    if db_config and db_config.get('database'):
        try:
            return DatabaseAuth(db_config)
        except Exception as e:
            print(f"⚠️ Auth DB indisponible, fallback sur auth simple: {e}")
            return SimpleAuth()
    else:
        return SimpleAuth()