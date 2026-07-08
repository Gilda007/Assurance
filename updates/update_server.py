# update_server.py - Version corrigée avec tous les bugs résolus
"""
Serveur HTTP professionnel pour le téléchargement de modules LOMETA
Authentification via token dans l'URL (?auth=base64_token)
Lit les informations de connexion depuis le fichier .env
"""

import os
import json
import hashlib
import logging
import argparse
import datetime
import base64
import bcrypt
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from urllib.parse import unquote
from psycopg2 import pool, extras


# ============================================================================
# CHARGEMENT DU .ENV
# ============================================================================

def load_env_file(env_path: str = ".env") -> dict:
    """Charge les variables d'environnement depuis un fichier .env"""
    env_vars = {}
    
    possible_paths = [
        Path(env_path),
        Path(os.getcwd()) / env_path,
        Path(os.getcwd()) / ".." / env_path,
        Path(__file__).parent / env_path,
        Path(__file__).parent.parent / env_path,
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"📁 Fichier .env trouvé: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip().strip('"\'').strip()
            break
    else:
        print("⚠️ Aucun fichier .env trouvé, utilisation des valeurs par défaut")
    
    return env_vars


env_vars = load_env_file(".env")


def get_env(key: str, default: str = None) -> str:
    """Récupère une variable d'environnement du .env ou de os.environ"""
    return env_vars.get(key, os.environ.get(key, default))


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ServerConfig:
    """Configuration du serveur"""
    port: int = 5000
    host: str = "localhost"
    title: str = "LOMETA Module Server"
    upload_enabled: bool = False
    auth_enabled: bool = False
    max_upload_size: int = 100 * 1024 * 1024
    allowed_extensions: List[str] = None
    db_host: str = None
    db_port: int = None
    db_name: str = None
    db_user: str = None
    db_password: str = None
    session_timeout_hours: int = 24
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.zip', '.tar.gz', '.whl']
        
        if self.db_host is None:
            self.db_host = get_env('DB_HOST', '')
        if self.db_port is None:
            self.db_port = int(get_env('DB_PORT', ''))
        if self.db_name is None:
            self.db_name = get_env('DB_NAME', '')
        if self.db_user is None:
            self.db_user = get_env('DB_USER')
        if self.db_password is None:
            self.db_password = get_env('DB_PASSWORD')


@dataclass
class ModuleMetadata:
    """Métadonnées d'un module"""
    id: str
    name: str
    version: str
    filename: str
    size: int
    size_mb: float
    download_url: str
    md5: str
    sha256: str
    modified: str
    modified_str: str
    downloads: int
    status: str = "active"
    description: str = ""
    author: str = "LOMETA Team"
    
    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# LOGGING
# ============================================================================

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.RESET)
        return f"{color}{log_message}{self.RESET}"


def setup_logging(level=logging.DEBUG):
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    
    file_handler = logging.FileHandler('module_server.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger()




# ============================================================================
# AUTHENTIFICATION VIA SESSION LOMETA
# ============================================================================


class SessionAuth:
    """Authentification via la table sessions de LOMETA (utilise token_encrypted)"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.connection_pool = None
        self._init_pool()
    
    def _init_pool(self):
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 5,
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                database=self.db_config.get('database', 'ams_db'),
                user=self.db_config.get('user', 'postgres'),
                password=self.db_config.get('password', '')
            )
            logger.info("✅ Connexion à PostgreSQL établie (SessionAuth)")
        except Exception as e:
            logger.error(f"❌ Erreur connexion PostgreSQL: {e}")
            self.connection_pool = None
    
    def verify_session_token(self, token: str) -> Optional[dict]:
        """Vérifie un token de session LOMETA dans la colonne token_encrypted"""
        if not self.connection_pool or not token:
            return None
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                # Modification ici : s.token devient s.token_encrypted
                cur.execute("""
                    SELECT s.user_id, u.username, u.full_name, u.email, u.role
                    FROM sessions s
                    JOIN utilisateurs u ON s.user_id = u.id
                    WHERE s.token_encrypted = %s AND s.expires_at > NOW()
                """, (token,))
                session = cur.fetchone()
                
                if session:
                    logger.info(f"✅ Session valide: {session['username']}")
                    return dict(session)
                else:
                    logger.warning(f"❌ Token invalide ou expiré dans la base de données")
                    return None
        except Exception as e:
            logger.error(f"Erreur vérification session: {e}")
            return None
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    def authenticate_user(self, username: str, password: str) -> tuple:
        """Authentifie un utilisateur (pour la page de connexion)"""
        if not self.connection_pool:
            return False, None, "Base de données non disponible"
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, username, full_name, email, role, is_active, password_hash
                    FROM utilisateurs 
                    WHERE username = %s
                """, (username,))
                user = cur.fetchone()
                
                if not user:
                    return False, None, "Nom d'utilisateur incorrect"
                
                if not user.get('is_active', True):
                    return False, None, "Compte désactivé"
                
                stored_hash = user.get('password_hash', '')
                if self._verify_password(password, stored_hash):
                    return True, dict(user), "Connexion réussie"
                else:
                    return False, None, "Mot de passe incorrect"
        except Exception as e:
            logger.error(f"Erreur authentification: {e}")
            return False, None, "Erreur système"
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    def _verify_password(self, input_password: str, stored_hash: str) -> bool:
        if not stored_hash:
            return False
        if stored_hash.startswith('$2'):
            try:
                return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))
            except:
                return False
        return input_password == stored_hash
    
    def create_session(self, user_id: int) -> str:
        """Crée une session temporaire et l'insère dans token_encrypted"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cur:
                token = base64.b64encode(f"{user_id}:{datetime.datetime.now().timestamp()}".encode()).decode()
                expires_at = datetime.datetime.now() + datetime.timedelta(hours=24)
                
                # Modification ici : la colonne token et le ON CONFLICT ciblent désormais token_encrypted
                cur.execute("""
                    INSERT INTO sessions (user_id, token_encrypted, expires_at, created_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (token_encrypted) DO UPDATE SET expires_at = EXCLUDED.expires_at
                """, (user_id, token, expires_at))
                conn.commit()
                return token
        except Exception as e:
            logger.error(f"Erreur création session: {e}")
            return None
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)


# ============================================================================
# AUTHENTIFICATION POSTGRESQL
# ============================================================================

class PostgreSQLAuth:
    """Authentification via PostgreSQL avec gestion de sessions"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.connection_pool = None
        self.sessions = {}  # Stockage des sessions {token: user_data}
        self.password_column = None
        self._init_pool()
        self._detect_table_structure()
    
    def _init_pool(self):
        """Initialise le pool de connexions"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 5,
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                database=self.db_config.get('database', 'ams_db'),
                user=self.db_config.get('user', 'postgres'),
                password=self.db_config.get('password', '')
            )
            logger.info("✅ Connexion à PostgreSQL établie")
        except Exception as e:
            logger.error(f"❌ Erreur connexion PostgreSQL: {e}")
            self.connection_pool = None
    
    def _detect_table_structure(self):
        """Détecte la structure de la table utilisateurs"""
        if not self.connection_pool:
            return
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cur:
                # Vérifier si la table existe
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'utilisateurs'
                    )
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    logger.error("❌ La table 'utilisateurs' n'existe pas dans la base de données!")
                    return
                
                # Récupérer les colonnes
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'utilisateurs'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                logger.info("📊 Structure de la table 'utilisateurs':")
                self.has_last_login = False
                for col_name, col_type in columns:
                    logger.info(f"   - {col_name}: {col_type}")
                    if col_name == 'last_login':
                        self.has_last_login = True
                
                # Détecter la colonne de mot de passe
                password_candidates = ['password_hash', 'password', 'mot_de_passe', 'mdp', 'passwd']
                for candidate in password_candidates:
                    if any(candidate == col[0] for col in columns):
                        self.password_column = candidate
                        logger.info(f"🔑 Colonne mot de passe détectée: '{candidate}'")
                        break
                
                if not self.password_column:
                    logger.warning("⚠️ Aucune colonne de mot de passe trouvée!")
                    logger.warning("   Colonnes disponibles: " + ", ".join([c[0] for c in columns]))
                    
        except Exception as e:
            logger.error(f"Erreur détection structure: {e}")
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    def authenticate(self, username: str, password: str) -> tuple:
        """
        Authentifie un utilisateur avec logs détaillés
        
        Returns:
            (success: bool, user_info: dict, message: str)
        """
        logger.info(f"🔐 Tentative de connexion: username='{username}'")
        
        if not self.connection_pool:
            logger.error("❌ Pool de connexion non disponible")
            return False, None, "Base de données non disponible"
        
        if not self.password_column:
            logger.error("❌ Colonne mot de passe non détectée")
            return False, None, "Erreur de configuration"
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                # Requête avec la bonne colonne
                query = f"""
                    SELECT id, username, full_name, email, role, is_active, 
                           {self.password_column} as password_hash
                    FROM utilisateurs 
                    WHERE username = %s
                """
                cur.execute(query, (username,))
                user = cur.fetchone()
                
                if not user:
                    logger.warning(f"❌ Utilisateur non trouvé: '{username}'")
                    return False, None, "Nom d'utilisateur incorrect"
                
                logger.debug(f"✅ Utilisateur trouvé: id={user['id']}, role={user['role']}, is_active={user['is_active']}")
                
                if not user.get('is_active', True):
                    logger.warning(f"❌ Compte désactivé: {username}")
                    return False, None, "Compte désactivé"
                
                stored_hash = user.get('password_hash', '')
                logger.debug(f"Hash stocké: {stored_hash[:30]}..." if stored_hash else "Hash vide")
                
                # Vérifier le mot de passe
                if self._verify_password(password, stored_hash):
                    logger.info(f"✅ Connexion réussie: {username} (role: {user['role']})")
                    
                    # Mettre à jour last_login seulement si la colonne existe
                    if hasattr(self, 'has_last_login') and self.has_last_login:
                        try:
                            cur.execute(
                                "UPDATE utilisateurs SET last_login = %s WHERE id = %s",
                                (datetime.datetime.now(), user['id'])
                            )
                            conn.commit()
                            logger.debug("📝 Date de dernière connexion mise à jour")
                        except Exception as e:
                            logger.warning(f"Erreur mise à jour last_login: {e}")
                    else:
                        logger.debug("📝 Colonne last_login non trouvée, mise à jour ignorée")
                    
                    return True, dict(user), "Connexion réussie"
                else:
                    logger.warning(f"❌ Mot de passe incorrect pour: {username}")
                    return False, None, "Mot de passe incorrect"
                    
        except Exception as e:
            logger.error(f"❌ Erreur authentification: {e}", exc_info=True)
            return False, None, f"Erreur système"
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    def _verify_password(self, input_password: str, stored_hash: str) -> bool:
        """Vérifie le mot de passe (bcrypt ou clair)"""
        if not stored_hash:
            logger.debug("Hash vide")
            return False
        
        # Format bcrypt (commence par $2a$, $2b$, $2y$)
        if stored_hash.startswith('$2'):
            try:
                result = bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))
                logger.debug(f"Vérification bcrypt: {'✅ OK' if result else '❌ KO'}")
                return result
            except Exception as e:
                logger.error(f"Erreur bcrypt: {e}")
                return False
        
        # Mot de passe en clair (ancienne version)
        elif len(stored_hash) < 30:
            logger.debug("Tentative vérification mot de passe en clair")
            return input_password == stored_hash
        
        else:
            logger.warning(f"Format de hash non reconnu: {stored_hash[:10]}...")
            return False
    
    def create_session(self, user_id: int, user_data: dict = None) -> str:
        """Crée une session et retourne un token"""
        token = base64.b64encode(f"{user_id}:{datetime.datetime.now().timestamp()}".encode()).decode()
        self.sessions[token] = {
            'user_id': user_id,
            'user_data': user_data,
            'expires_at': datetime.datetime.now() + datetime.timedelta(hours=24)
        }
        logger.debug(f"Session créée pour user_id={user_id}, token={token[:20]}...")
        return token
    
    def get_user_from_session(self, token: str) -> Optional[dict]:
        """Récupère l'utilisateur à partir du token"""
        if not token or token not in self.sessions:
            return None
        
        session = self.sessions[token]
        if session['expires_at'] < datetime.datetime.now():
            logger.debug(f"Session expirée: {token[:20]}...")
            del self.sessions[token]
            return None
        
        # Si on a déjà les données utilisateur en cache, les retourner
        if session.get('user_data'):
            return session['user_data']
        
        # Sinon, aller chercher en base
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, username, full_name, email, role FROM utilisateurs WHERE id = %s",
                    (session['user_id'],)
                )
                user = cur.fetchone()
                if user:
                    session['user_data'] = dict(user)
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur: {e}")
            return None
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    def logout(self, token: str):
        """Détruit une session"""
        if token and token in self.sessions:
            del self.sessions[token]
            logger.debug(f"Session supprimée: {token[:20]}...")


# ============================================================================
# SERVEUR PRINCIPAL
# ============================================================================

class ModuleServerHandler(SimpleHTTPRequestHandler):
    """Handler avec authentification par token URL"""
    
    server_version = "LOMETA/3.0"
    config: ServerConfig = None
    auth_handler: PostgreSQLAuth = None
    start_time: datetime.datetime = None
    stats = {
        "total_downloads": 0,
        "total_bytes_sent": 0,
        "total_requests": 0,
    }
    
    def __init__(self, *args, **kwargs):
        if self.__class__.start_time is None:
            self.__class__.start_time = datetime.datetime.now()
        super().__init__(*args, **kwargs)
    
    def log_message(self, format: str, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def log_error(self, format: str, *args):
        logger.error(f"{self.address_string()} - {format % args}")
    
    def send_response(self, code, message=None):
        super().send_response(code, message)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
    
    def _get_auth_token(self):
        """Récupère le token d'authentification depuis l'URL"""
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)
        tokens = query_params.get('auth', [])
        return tokens[0] if tokens else None
    
    def _is_authenticated(self):
        """Vérifie si l'utilisateur est authentifié (priorité à session_auth)"""
        if not self.config.auth_enabled:
            return True
        
        token = self._get_auth_token()
        if not token:
            return False
        
        # PRIORITÉ: Vérifier d'abord avec session_auth (table sessions PostgreSQL)
        if hasattr(self, 'session_auth') and self.session_auth:
            user = self.session_auth.verify_session_token(token)
            if user:
                self.current_user = user
                self._current_user_role = user.get('role')
                return True
        
        # FALLBACK: Vérifier avec l'ancien auth_handler
        if self.auth_handler:
            user = self.auth_handler.get_user_from_session(token)
            if user:
                self.current_user = user
                return True
        
        return False
    
    def _redirect_to_auth(self):
        """Redirige vers la page d'authentification"""
        self.send_response(302)
        self.send_header('Location', '/auth')
        self.end_headers()
    
    def _send_html(self, html):
        """Envoie une réponse HTML avec gestion des erreurs"""
        try:
            self._safe_send_response(200, 'text/html; charset=utf-8', html.encode('utf-8'))
        except Exception as e:
            logger.error(f"Erreur envoi HTML: {e}")
        
    def do_GET(self):
        """Gère les requêtes GET - Version corrigée sans boucle"""
        self.__class__.stats["total_requests"] += 1
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Route de connexion - JAMAIS de redirection
        if path == '/auth':
            self._serve_login_page()
            return
        
        # Route de logout
        if path == '/logout':
            self._handle_logout()
            return
        
        # Route API /api/modules - Vérifier le token
        if path == '/api/modules':
            if self.config.auth_enabled:
                token = self._get_auth_token()
                if not token:
                    self._send_json_response(401, {"error": "Token manquant"})
                    return
                
                # Vérifier le token
                if hasattr(self, 'session_auth') and self.session_auth:
                    user = self.session_auth.verify_session_token(token)
                    if not user:
                        self._send_json_response(401, {"error": "Token invalide"})
                        return
                elif hasattr(self, 'auth_handler') and self.auth_handler:
                    user = self.auth_handler.get_user_from_session(token)
                    if not user:
                        self._send_json_response(401, {"error": "Token invalide"})
                        return
                else:
                    self._send_json_response(401, {"error": "Authentification non configurée"})
                    return
            self._serve_modules_api()
            return
        
        # Route de téléchargement
        if path.startswith('/downloads/'):
            if self.config.auth_enabled:
                token = self._get_auth_token()
                if not token:
                    self.send_response(302)
                    self.send_header('Location', '/auth')
                    self.end_headers()
                    return
                
                if hasattr(self, 'session_auth') and self.session_auth:
                    user = self.session_auth.verify_session_token(token)
                    if not user:
                        self.send_response(302)
                        self.send_header('Location', '/auth')
                        self.end_headers()
                        return
                elif hasattr(self, 'auth_handler') and self.auth_handler:
                    user = self.auth_handler.get_user_from_session(token)
                    if not user:
                        self.send_response(302)
                        self.send_header('Location', '/auth')
                        self.end_headers()
                        return
                else:
                    self.send_response(302)
                    self.send_header('Location', '/auth')
                    self.end_headers()
                    return
            self._handle_download(path)
            return
        
        # Dashboard - Vérifier le token
        token = self._get_auth_token()
        if token:
            is_valid = False
            if hasattr(self, 'session_auth') and self.session_auth:
                user = self.session_auth.verify_session_token(token)
                if user:
                    self.current_user = user
                    is_valid = True
            elif hasattr(self, 'auth_handler') and self.auth_handler:
                user = self.auth_handler.get_user_from_session(token)
                if user:
                    self.current_user = user
                    is_valid = True
            
            if is_valid:
                self._serve_dashboard()
                return
        
        # Pas de token valide - Rediriger vers login UNIQUEMENT si l'authentification est activée
        if path != '/auth':
            if self.config.auth_enabled:
                self.send_response(302)
                self.send_header('Location', '/auth')
                self.end_headers()
            else:
                self._serve_dashboard()
        else:
            if self.config.auth_enabled:
                self._serve_login_page()
            else:
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()

    def do_POST(self):
        """Gère les requêtes POST"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/auth':
            self._handle_login()
            return
        
        # Vérifier l'authentification
        is_auth = False
        token = self._get_auth_token()
        if token and hasattr(self, 'session_auth') and self.session_auth:
            user = self.session_auth.verify_session_token(token)
            if user:
                is_auth = True
        else:
            is_auth = self._is_authenticated() if hasattr(self, '_is_authenticated') else False
        
        if not is_auth and self.config.auth_enabled:
            self._send_json_response(401, {"error": "Non authentifié"})
            return
        
        if path == '/api/upload':
            self._handle_upload()
        elif path == '/api/delete':
            self._handle_delete()
        else:
            self._send_json_response(404, {"error": "Endpoint not found"})
    
    # ========================================================================
    # PAGES D'AUTHENTIFICATION
    # ========================================================================
    
    def _safe_send_response(self, code: int, content_type: str, data: bytes):
        """Envoie une réponse de manière sécurisée (gère les BrokenPipeError)"""
        try:
            self.send_response(code)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(data)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            # Client déconnecté, ignorer silencieusement
            pass
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la réponse: {e}")

    # Ajouter cette méthode pour la compatibilité avec l'ancienne route /auth
    def _handle_login_deprecated(self):
        """Traite la tentative de connexion (ancienne route /auth)"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)
        
        username = params.get('username', [''])[0].strip()
        password = params.get('password', [''])[0].strip()
        
        if not username or not password:
            self._serve_auth_page("Veuillez saisir tous les champs")
            return
        
        success, user, message = self.auth_handler.authenticate(username, password)
        
        if success:
            token = self.auth_handler.create_session(user['id'], user)
            redirect_url = f"/?auth={token}"
            self.send_response(302)
            self.send_header('Location', redirect_url)
            self.end_headers()
        else:
            self._serve_auth_page(message)

    def _serve_auth_page(self, error_message: str = None):
        """Sert la page de connexion"""
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Connexion - {self.config.title}</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                body {{
                    font-family: 'Inter', -apple-system, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                
                .login-container {{
                    background: white;
                    border-radius: 24px;
                    padding: 40px;
                    width: 100%;
                    max-width: 420px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                
                .logo {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                
                .logo h1 {{
                    font-size: 28px;
                    font-weight: 800;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .logo p {{
                    color: #666;
                    font-size: 14px;
                    margin-top: 8px;
                }}
                
                .input-group {{
                    margin-bottom: 20px;
                }}
                
                .input-group label {{
                    display: block;
                    margin-bottom: 8px;
                    color: #333;
                    font-weight: 500;
                    font-size: 14px;
                }}
                
                .input-group input {{
                    width: 100%;
                    padding: 12px 16px;
                    border: 1px solid #ddd;
                    border-radius: 12px;
                    font-size: 14px;
                    transition: all 0.3s;
                }}
                
                .input-group input:focus {{
                    outline: none;
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
                }}
                
                button {{
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s;
                }}
                
                button:hover {{
                    transform: scale(1.02);
                }}
                
                .error {{
                    background: #fee2e2;
                    color: #dc2626;
                    padding: 12px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    font-size: 14px;
                    text-align: center;
                }}
                
                .info {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">
                    <h1>🚀 {self.config.title}</h1>
                    <p>Plateforme de distribution de modules</p>
                </div>
                
                {"<div class='error'>" + error_message + "</div>" if error_message else ""}
                
                <form method="POST" action="/auth">
                    <div class="input-group">
                        <label>Nom d'utilisateur</label>
                        <input type="text" name="username" placeholder="Entrez votre nom d'utilisateur" autocomplete="off" required>
                    </div>
                    
                    <div class="input-group">
                        <label>Mot de passe</label>
                        <input type="password" name="password" placeholder="Entrez votre mot de passe" required>
                    </div>
                    
                    <button type="submit">Se connecter</button>
                </form>
                
                <div class="info">
                    💡 Utilisez vos identifiants de l'application LOMETA
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _handle_login(self):
        """Traite la tentative de connexion"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)
        
        username = params.get('username', [''])[0].strip()
        password = params.get('password', [''])[0].strip()
        
        logger.info(f"📝 Formulaire de connexion reçu pour: {username}")
        
        if not username or not password:
            self._serve_auth_page("Veuillez saisir tous les champs")
            return
        
        success, user, message = self.auth_handler.authenticate(username, password)
        
        if success:
            token = self.auth_handler.create_session(user['id'], user)
            redirect_url = f"/?auth={token}"
            logger.info(f"✅ Authentification réussie, redirection vers {redirect_url[:50]}...")
            
            self.send_response(302)
            self.send_header('Location', redirect_url)
            self.end_headers()
        else:
            logger.warning(f"❌ Échec authentification: {message}")
            self._serve_auth_page(message)
    
    # ========================================================================
    # GESTION DES MODULES
    # ========================================================================
    
    def _get_modules(self) -> List[ModuleMetadata]:
        """Récupère la liste des modules disponibles"""
        modules = []
        current_dir = Path(os.getcwd())
        
        for zip_file in sorted(current_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True):
            stat = zip_file.stat()
            
            md5_hash = sha256_hash = ""
            try:
                with open(zip_file, 'rb') as f:
                    data = f.read()
                    md5_hash = hashlib.md5(data).hexdigest()[:16] + "..."
                    sha256_hash = hashlib.sha256(data).hexdigest()[:32] + "..."
            except:
                pass
            
            module = ModuleMetadata(
                id=zip_file.stem,
                name=zip_file.stem.replace("_", " ").replace("-", " ").title(),
                version="1.0.0",
                filename=zip_file.name,
                size=stat.st_size,
                size_mb=round(stat.st_size / (1024 * 1024), 2),
                download_url=f"/downloads/{zip_file.name}",
                md5=md5_hash,
                sha256=sha256_hash,
                modified=datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                modified_str=datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S"),
                downloads=getattr(self, f"_downloads_{zip_file.name}", 0),
                description=f"Module {zip_file.stem} pour LOMETA"
            )
            modules.append(module)
        
        return modules
    
    def _serve_dashboard(self):
        """Sert le dashboard"""
        modules = self._get_modules()
        uptime = (datetime.datetime.now() - self.start_time).total_seconds()
        uptime_hours = round(uptime / 3600, 1)
        token = self._get_auth_token() or ""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{self.config.title}</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                :root {{
                    --primary: #6366f1;
                    --secondary: #8b5cf6;
                    --success: #10b981;
                    --danger: #ef4444;
                    --dark: #1e293b;
                    --gray: #64748b;
                    --border: #e2e8f0;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                
                .header {{
                    background: white;
                    border-radius: 0 0 30px 30px;
                    padding: 25px 40px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                
                .header-content {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 20px;
                }}
                
                .logo h1 {{
                    font-size: 24px;
                    font-weight: 800;
                    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .logo p {{ font-size: 12px; color: var(--gray); margin-top: 4px; }}
                
                .stats-header {{ display: flex; gap: 30px; }}
                
                .stat-item {{ text-align: center; }}
                .stat-value {{ font-size: 28px; font-weight: 700; color: var(--dark); }}
                .stat-label {{ font-size: 12px; color: var(--gray); }}
                
                .btn-logout {{
                    background: #ef4444;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 12px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 14px;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                }}
                
                .main-content {{ padding: 30px 40px; }}
                
                .modules-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
                    gap: 25px;
                }}
                
                .module-card {{
                    background: white;
                    border-radius: 20px;
                    overflow: hidden;
                    transition: all 0.3s;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }}
                
                .module-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                }}
                
                .module-header {{
                    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                    padding: 20px;
                    color: white;
                }}
                
                .module-name {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
                .module-version {{ font-size: 12px; opacity: 0.9; }}
                
                .module-body {{ padding: 20px; }}
                .module-description {{ color: var(--gray); font-size: 13px; line-height: 1.5; margin-bottom: 15px; }}
                
                .module-meta {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-bottom: 15px;
                }}
                
                .meta-tag {{
                    background: #f8fafc;
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 11px;
                    color: var(--gray);
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }}
                
                .module-footer {{
                    padding: 15px 20px;
                    border-top: 1px solid var(--border);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .btn-download {{
                    background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 12px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                
                .btn-delete {{
                    background: var(--danger);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 12px;
                    cursor: pointer;
                    font-weight: 600;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                
                .upload-area {{
                    background: white;
                    border-radius: 20px;
                    padding: 60px 40px;
                    text-align: center;
                    border: 2px dashed var(--border);
                    cursor: pointer;
                }}
                
                .upload-area:hover {{
                    border-color: var(--primary);
                    background: #f8fafc;
                }}
                
                .upload-icon {{ font-size: 64px; color: var(--primary); margin-bottom: 20px; }}
                .upload-title {{ font-size: 20px; font-weight: 600; color: var(--dark); margin-bottom: 10px; }}
                .upload-subtitle {{ color: var(--gray); font-size: 14px; }}
                
                .tabs {{ display: flex; gap: 10px; margin-bottom: 30px; }}
                
                .tab {{
                    padding: 12px 24px;
                    background: white;
                    border: none;
                    border-radius: 12px;
                    cursor: pointer;
                    font-weight: 600;
                    color: var(--gray);
                }}
                
                .tab.active {{
                    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                    color: white;
                }}
                
                .empty-state {{
                    background: white;
                    border-radius: 20px;
                    padding: 60px;
                    text-align: center;
                    color: var(--gray);
                }}
                
                .empty-icon {{ font-size: 64px; margin-bottom: 20px; }}
                
                .toast {{
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    background: white;
                    border-radius: 12px;
                    padding: 12px 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    transform: translateX(400px);
                    transition: transform 0.3s;
                    z-index: 1100;
                }}
                
                .toast.show {{ transform: translateX(0); }}
                .toast.success {{ border-left: 4px solid var(--success); }}
                .toast.error {{ border-left: 4px solid var(--danger); }}
                
                @media (max-width: 768px) {{
                    .header {{ padding: 20px; }}
                    .main-content {{ padding: 20px; }}
                    .modules-grid {{ grid-template-columns: 1fr; }}
                    .stats-header {{ display: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="header-content">
                    <div class="logo">
                        <h1>🚀 {self.config.title}</h1>
                        <p>Plateforme de distribution de modules</p>
                    </div>
                    <div class="stats-header">
                        <div class="stat-item">
                            <div class="stat-value">{len(modules)}</div>
                            <div class="stat-label">Modules</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{self.stats['total_downloads']}</div>
                            <div class="stat-label">Downloads</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{round(self.stats['total_bytes_sent'] / (1024*1024), 1)}</div>
                            <div class="stat-label">MB sent</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{uptime_hours}h</div>
                            <div class="stat-label">Uptime</div>
                        </div>
                    </div>
                    <a href="/logout?auth={token}" class="btn-logout"><i class="fas fa-sign-out-alt"></i> Déconnexion</a>
                </div>
            </div>
            
            <div class="main-content">
                <div class="tabs">
                    <button class="tab active" onclick="showTab('modules')">📦 Modules</button>
                    <button class="tab" onclick="showTab('upload')">📤 Upload</button>
                </div>
                
                <div id="modulesTab">
                    <div class="modules-grid">
                        {self._generate_module_cards(modules)}
                    </div>
                </div>
                
                <div id="uploadTab" style="display: none;">
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <div class="upload-icon"><i class="fas fa-cloud-upload-alt"></i></div>
                        <div class="upload-title">Déposer un module</div>
                        <div class="upload-subtitle">Glissez-déposez ou cliquez pour sélectionner un fichier ZIP</div>
                        <input type="file" id="fileInput" accept=".zip" style="display: none;" onchange="uploadFile(this.files[0])">
                    </div>
                </div>
            </div>
            
            <div id="toast" class="toast"></div>
            
            <script>
                const AUTH_TOKEN = '{token}';
                
                function showTab(tab) {{
                    const modulesTab = document.getElementById('modulesTab');
                    const uploadTab = document.getElementById('uploadTab');
                    const tabs = document.querySelectorAll('.tab');
                    
                    tabs.forEach(t => t.classList.remove('active'));
                    
                    if (tab === 'modules') {{
                        modulesTab.style.display = 'block';
                        uploadTab.style.display = 'none';
                        tabs[0].classList.add('active');
                    }} else {{
                        modulesTab.style.display = 'none';
                        uploadTab.style.display = 'block';
                        tabs[1].classList.add('active');
                    }}
                }}
                
                function apiCall(url, options = {{}}) {{
                    const separator = url.includes('?') ? '&' : '?';
                    const urlWithAuth = url + separator + 'auth=' + AUTH_TOKEN;
                    return fetch(urlWithAuth, options);
                }}
                
                async function uploadFile(file) {{
                    if (!file) return;
                    if (!file.name.endsWith('.zip')) {{
                        showToast('Veuillez sélectionner un fichier ZIP', 'error');
                        return;
                    }}
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    showToast('Upload en cours...', 'warning');
                    
                    try {{
                        const response = await apiCall('/api/upload', {{ method: 'POST', body: formData }});
                        const result = await response.json();
                        
                        if (result.success) {{
                            showToast('Module uploadé avec succès !', 'success');
                            setTimeout(() => location.reload(), 1500);
                        }} else {{
                            showToast('Erreur: ' + result.error, 'error');
                        }}
                    }} catch (error) {{
                        showToast('Erreur de connexion', 'error');
                    }}
                }}
                
                async function deleteModule(filename) {{
                    if (!confirm(`Supprimer définitivement ${{filename}} ?`)) return;
                    
                    try {{
                        const response = await apiCall('/api/delete', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{filename: filename}})
                        }});
                        const result = await response.json();
                        
                        if (result.success) {{
                            showToast('Module supprimé', 'success');
                            setTimeout(() => location.reload(), 1000);
                        }} else {{
                            showToast('Erreur: ' + result.error, 'error');
                        }}
                    }} catch (error) {{
                        showToast('Erreur de connexion', 'error');
                    }}
                }}
                
                function showToast(message, type = 'info') {{
                    const toast = document.getElementById('toast');
                    toast.innerHTML = message;
                    toast.className = `toast ${{type}} show`;
                    setTimeout(() => toast.classList.remove('show'), 3000);
                }}
                
                const dropZone = document.querySelector('.upload-area');
                if (dropZone) {{
                    dropZone.addEventListener('dragover', (e) => e.preventDefault());
                    dropZone.addEventListener('drop', (e) => {{
                        e.preventDefault();
                        const file = e.dataTransfer.files[0];
                        if (file && file.name.endsWith('.zip')) uploadFile(file);
                        else showToast('Veuillez déposer un fichier ZIP', 'warning');
                    }});
                }}
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _generate_module_cards(self, modules: List[ModuleMetadata]) -> str:
        if not modules:
            return '<div class="empty-state"><div class="empty-icon">📂</div><h3>Aucun module disponible</h3><p>Déposez des fichiers .zip dans le dossier</p></div>'
        
        token = self._get_auth_token() or ""
        cards = ""
        for m in modules:
            cards += f"""
            <div class="module-card">
                <div class="module-header">
                    <div class="module-name">{m.name}</div>
                    <div class="module-version">v{m.version}</div>
                </div>
                <div class="module-body">
                    <div class="module-description">{m.description}</div>
                    <div class="module-meta">
                        <span class="meta-tag"><i class="fas fa-hashtag"></i> {m.id}</span>
                        <span class="meta-tag"><i class="fas fa-calendar"></i> {m.modified_str}</span>
                        <span class="meta-tag"><i class="fas fa-database"></i> {m.size_mb} MB</span>
                    </div>
                </div>
                <div class="module-footer">
                    <a href="{m.download_url}?auth={token}" class="btn-download" download><i class="fas fa-download"></i> Télécharger</a>
                    <button class="btn-delete" onclick="deleteModule('{m.filename}')"><i class="fas fa-trash"></i> Supprimer</button>
                </div>
            </div>
            """
        return cards
    
    # ========================================================================
    # API
    # ========================================================================


    def _serve_modules_api(self):
        """API utilisée par l'application LOMETA - Format JSON attendu par le client"""
        modules = self._get_modules()
        # Le client attend directement une liste, pas un objet avec "success" et "total"
        self._send_json_response(200, [m.to_dict() for m in modules])
    
    def _serve_stats_api(self):
        uptime = (datetime.datetime.now() - self.start_time).total_seconds()
        self._send_json_response(200, {
            "success": True,
            "stats": {
                "total_downloads": self.stats["total_downloads"],
                "total_mb_sent": round(self.stats["total_bytes_sent"] / (1024 * 1024), 2),
                "uptime_hours": round(uptime / 3600, 2)
            }
        })
    
    def _serve_health_api(self):
        self._send_json_response(200, {"status": "healthy"})
    
    # ========================================================================
    # DOWNLOAD, UPLOAD, DELETE
    # ========================================================================

    def _handle_download(self, path: str):
        """Gère le téléchargement avec gestion des erreurs"""
        raw_filename = path.split('/')[-1].split('?')[0]
        filename = unquote(raw_filename)
        file_path = Path(os.getcwd()) / filename
        
        if not file_path.exists():
            self.send_error(404, f"Fichier non trouvé: {filename}")
            return
        
        self.stats["total_downloads"] += 1
        file_size = file_path.stat().st_size
        self.stats["total_bytes_sent"] += file_size
        
        logger.info(f"📥 Téléchargement: {filename}")
        
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            encoded_filename = filename.encode('utf-8').decode('latin-1')
            self.send_header('Content-Disposition', f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{filename}')
            self.send_header('Content-Length', str(file_size))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                # Envoyer par chunks pour éviter les problèmes de mémoire
                chunk_size = 8192
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        logger.debug("Client a interrompu le téléchargement")
                        return
                self.wfile.flush()
        except Exception as e:
            logger.error(f"Erreur téléchargement {filename}: {e}")
    
    def _handle_upload(self):
        if not self.config.upload_enabled:
            self._send_json_response(403, {"error": "Upload désactivé"})
            return
        
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self._send_json_response(400, {"error": "Content-Type invalide"})
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > self.config.max_upload_size:
            self._send_json_response(413, {"error": f"Fichier trop volumineux (max {self.config.max_upload_size // (1024*1024)} MB)"})
            return
        
        post_data = self.rfile.read(content_length)
        
        try:
            boundary = content_type.split('boundary=')[1].encode()
            parts = post_data.split(b'--' + boundary)
            
            for part in parts:
                if b'filename="' in part:
                    filename_start = part.find(b'filename="') + 10
                    filename_end = part.find(b'"', filename_start)
                    filename = part[filename_start:filename_end].decode()
                    
                    if not filename.endswith('.zip'):
                        self._send_json_response(400, {"error": "Seuls les fichiers ZIP sont acceptés"})
                        return
                    
                    content_start = part.find(b'\r\n\r\n') + 4
                    content = part[content_start:-2]
                    
                    file_path = Path(os.getcwd()) / filename
                    counter = 1
                    while file_path.exists():
                        name, ext = os.path.splitext(filename)
                        file_path = Path(os.getcwd()) / f"{name}_{counter}{ext}"
                        counter += 1
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    logger.info(f"📤 Upload: {file_path.name}")
                    self._send_json_response(200, {"success": True, "message": f"Module {file_path.name} uploadé"})
                    return
            
            self._send_json_response(400, {"error": "Aucun fichier trouvé"})
        except Exception as e:
            logger.error(f"Erreur upload: {e}")
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_delete(self):
        if not self.config.upload_enabled:
            self._send_json_response(403, {"error": "Suppression désactivée"})
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(post_data)
            filename = data.get('filename')
        except:
            filename = None
        
        if not filename:
            self._send_json_response(400, {"error": "Nom de fichier requis"})
            return
        
        file_path = Path(os.getcwd()) / filename
        if not file_path.exists():
            self._send_json_response(404, {"error": "Fichier non trouvé"})
            return
        
        try:
            os.remove(file_path)
            logger.info(f"🗑️ Suppression: {filename}")
            self._send_json_response(200, {"success": True, "message": f"Module {filename} supprimé"})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    
    def _send_json_response(self, code: int, data: dict):
        """Envoie une réponse JSON avec gestion des erreurs de connexion"""
        try:
            json_data = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Envoyer par petits morceaux
            chunk_size = 4096
            for i in range(0, len(json_data), chunk_size):
                chunk = json_data[i:i+chunk_size]
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    logger.debug("Client déconnecté pendant l'envoi JSON")
                    return
            self.wfile.flush()
            
        except BrokenPipeError:
            logger.debug("Connexion fermée par le client")
            pass
        except Exception as e:
            logger.error(f"Erreur _send_json_response: {e}")


    def _verify_lometa_session(self, token: str) -> Optional[dict]:
        """Vérifie le token dans la table sessions de LOMETA"""
        if not hasattr(self, 'session_auth') or not self.session_auth:
            return None
        
        conn = None
        try:
            conn = self.session_auth.connection_pool.getconn()
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.user_id, u.username, u.full_name, u.email, u.role
                    FROM sessions s
                    JOIN utilisateurs u ON s.user_id = u.id
                    WHERE s.token = %s AND s.expires_at > NOW()
                """, (token,))
                session = cur.fetchone()
                if session:
                    return dict(session)
                return None
        except Exception as e:
            logger.error(f"Erreur vérification session LOMETA: {e}")
            return None
        finally:
            if conn and self.session_auth and self.session_auth.connection_pool:
                self.session_auth.connection_pool.putconn(conn)

    def _serve_login_page(self, error_message: str = None):
        """Sert la page de connexion pour le navigateur"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Connexion - {self.config.title}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .login-container {{
                    background: white;
                    border-radius: 24px;
                    padding: 40px;
                    width: 400px;
                    text-align: center;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                h1 {{ color: #333; margin-bottom: 10px; }}
                p {{ color: #666; margin-bottom: 30px; }}
                input {{
                    width: 100%;
                    padding: 12px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    font-size: 14px;
                }}
                button {{
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                }}
                button:hover {{ transform: scale(1.02); }}
                .error {{ color: #ef4444; margin-bottom: 15px; }}
                .info {{ margin-top: 20px; font-size: 12px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🔐 {self.config.title}</h1>
                <p>Connectez-vous avec vos identifiants LOMETA</p>
                {"<div class='error'>" + error_message + "</div>" if error_message else ""}
                <form method="POST" action="/auth">
                    <input type="text" name="username" placeholder="Nom d'utilisateur" required>
                    <input type="password" name="password" placeholder="Mot de passe" required>
                    <button type="submit">Se connecter</button>
                </form>
                <div class="info">💡 Utilisez vos identifiants de l'application LOMETA</div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)

    def _handle_login(self):
        """Traite la connexion et redirige avec token"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)
        
        username = params.get('username', [''])[0].strip()
        password = params.get('password', [''])[0].strip()
        
        if not self.config.auth_enabled:
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        
        success = False
        user = None
        message = 'Authentification impossible'
        token = None
        
        if hasattr(self, 'session_auth') and self.session_auth:
            success, user, message = self.session_auth.authenticate_user(username, password)
            if success:
                token = self.session_auth.create_session(user['id'])
        elif hasattr(self, 'auth_handler') and self.auth_handler:
            success, user, message = self.auth_handler.authenticate(username, password)
            if success:
                token = self.auth_handler.create_session(user['id'], user)
        else:
            self._serve_login_page("La configuration d'authentification est manquante.")
            return
        
        if success:
            self.send_response(302)
            self.send_header('Location', f'/?auth={token}')
            self.end_headers()
        else:
            self._serve_login_page(message)

    def _handle_logout(self):
        """Déconnexion - Supprimer la session et rediriger vers login"""
        token = self._get_auth_token()
        
        # Supprimer la session dans session_auth
        if token and hasattr(self, 'session_auth') and self.session_auth and self.session_auth.connection_pool:
            try:
                conn = self.session_auth.connection_pool.getconn()
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
                    conn.commit()
            except Exception as e:
                logger.error(f"Erreur suppression session: {e}")
            finally:
                if conn:
                    self.session_auth.connection_pool.putconn(conn)
        
        # Supprimer la session dans auth_handler
        if token and hasattr(self, 'auth_handler') and self.auth_handler:
            self.auth_handler.logout(token)
        
        # Rediriger vers login (SANS token)
        self.send_response(302)
        self.send_header('Location', '/auth')
        self.end_headers()


# ============================================================================
# DÉMARRAGE
# ============================================================================

def run_server(config: ServerConfig):
    """Démarre le serveur"""
    
    # Initialiser l'authentification PostgreSQL si activée
    if config.auth_enabled:
        db_config = {
            'host': config.db_host,
            'port': config.db_port,
            'database': config.db_name,
            'user': config.db_user,
            'password': config.db_password
        }
        ModuleServerHandler.auth_handler = PostgreSQLAuth(db_config)
        ModuleServerHandler.session_auth = SessionAuth(db_config)
    
    ModuleServerHandler.config = config
    
    server_address = (config.host, config.port)
    httpd = HTTPServer(server_address, ModuleServerHandler)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════=╗
║                         🚀 LOMETA MODULE SERVER v3.0                          ║
╠══════════════════════════════════════════════════════════════════════════════=╣
║                                                                               ║
║  📡 Serveur:     http://{config.host}:{config.port}                           ║        
║  📁 Dossier:     {os.getcwd()}                                                ║
║  🔐 Auth:        {'✅ PostgreSQL' if config.auth_enabled else '❌ Désactivée'}║                                      
║  📤 Upload:      {'✅ Activé' if config.upload_enabled else '❌ Désactivé'}   ║                                    
║                                                                               ║
║  🗄️  Base de données:                                                         ║
║     Host: {config.db_host}:{config.db_port}                                   ║        
║     Database: {config.db_name}                                                ║
║     User: {config.db_user}                                                    ║
║                                                                               ║
╠══════════════════════════════════════════════════════════════════════════════=╣
║  📋 Endpoints:                                                                ║
║     🌐 http://{config.host}:{config.port}/?auth=TOKEN    → Dashboard          ║                      
║     🔐 /auth                         → Page de connexion                      ║         
║     🚪 /logout?auth=TOKEN            → Déconnexion                            ║         
║     📦 /api/modules?auth=TOKEN       → Liste des modules (JSON)               ║         
║     📊 /api/stats?auth=TOKEN         → Statistiques (JSON)                    ║        
║     ❤️ /api/health?auth=TOKEN        → Health check                           ║        
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════=╝
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur...")
        httpd.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serveur de modules LOMETA')
    
    parser.add_argument('port', type=int, nargs='?', default=8000, help='Port')
    parser.add_argument('--host', type=str, default='192.168.100.89', help='Hôte')
    parser.add_argument('--upload', action='store_true', help='Activer upload')
    parser.add_argument('--auth', action='store_true', help='Activer authentification')
    parser.add_argument('--max-size', type=int, default=100, help='Taille max MB')
    parser.add_argument('--title', type=str, default='LOMETA Module Server')
    
    # Options PostgreSQL
    parser.add_argument('--db-host', type=str, help='Hôte PostgreSQL')
    parser.add_argument('--db-port', type=int, help='Port PostgreSQL')
    parser.add_argument('--db-name', type=str, help='Nom base de données')
    parser.add_argument('--db-user', type=str, help='Utilisateur PostgreSQL')
    parser.add_argument('--db-password', type=str, help='Mot de passe PostgreSQL')
    
    args = parser.parse_args()
    
    config = ServerConfig(
        port=args.port,
        host=args.host,
        title=args.title,
        upload_enabled=args.upload,
        auth_enabled=args.auth,
        max_upload_size=args.max_size * 1024 * 1024,
        db_host=args.db_host,
        db_port=args.db_port,
        db_name=args.db_name,
        db_user=args.db_user,
        db_password=args.db_password
    )
    
    if config.auth_enabled:
        print("\n📋 Configuration de la base de données:")
        if args.db_host:
            print("   → Sources: Arguments ligne de commande")
        else:
            print("   → Sources: Fichier .env")
    
    run_server(config)