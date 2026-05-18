# from core.database import SessionLocal
# from core.local_db import cache, cached
# from addons.Paramètres.models.models import User, AuditUserLog
# import socket
# import threading
# from PySide6.QtCore import QObject, Signal


# class UserController:
#     users_loaded = Signal(list)
#     user_created = Signal(dict)
#     user_updated = Signal(dict)
#     user_deleted = Signal(int)
#     error_occurred = Signal(str)
#     loading_started = Signal()
#     loading_finished = Signal()

#     # def __init__(self, db_session, current_user_id=None):
#     #     # C'est ici qu'on crée l'attribut 'db'
#     #     self.db = db_session 
#     #     self.current_user_id = current_user_id
#     #     self._cached_role = None
#     #     print(f"DEBUG: Contrôleur prêt. DB: {self.db is not None}, UserID: {self.current_user_id}")
#     #     print(f"DEBUG: Contrôleur initialisé avec la session : {self.db}")

#     def __init__(self, db_session, current_user_id=None):
#         super().__init__()
#         self.db = db_session 
#         self.current_user_id = current_user_id
#         self._cached_role = None
#         self._loading_thread = None
        
#         print(f"DEBUG: Contrôleur UserController initialisé")
#         print(f"DEBUG: DB: {self.db is not None}, UserID: {self.current_user_id}")
    
#     # ============================================================================
#     # MÉTHODES AVEC CACHE (LECTURE)
#     # ============================================================================

#     def get_audit_logs(self, limit=100):
#         """Récupère les logs UNIQUEMENT si l'utilisateur est admin"""
#         try:
#             # VERIFICATION DU RÔLE (Condition de sécurité)
#             if self.current_user_role != "admin":
#                 print(f"Tentative d'accès non autorisé aux logs par ID: {self.current_user_id}")
#                 return [] # On renvoie une liste vide au lieu des logs
                
#             return self.db.query(AuditUserLog).order_by(AuditUserLog.created_at.desc()).limit(limit).all()
#         except Exception as e:
#             print(f"Erreur lors de la récupération des logs : {e}")
#             return []

#     def _log_action(self, action, details):

#         if not self.current_user_id:
#             print("CRITICAL: Tentative d'action sans ID utilisateur !")
#             return # Ou lever une exception
#         try:
#             # Récupération de l'IP
#             hostname = socket.gethostname()
#             ip_address = socket.gethostbyname(hostname)
            
#             # Création de l'entrée d'audit
#             new_log = AuditUserLog(
#                 user_id=self.current_user_id,
#                 action=action,
#                 details=details,
#                 ip_address=ip_address
#             )
            
#             # AJOUT ET VALIDATION
#             self.db.add(new_log)
#             self.db.commit() # <--- TRÈS IMPORTANT
#             print(f"DEBUG: Log enregistré : {action}")
#         except Exception as e:
#             self.db.rollback()
#             print(f"DEBUG: Erreur enregistrement Log : {e}")

#         if not self.current_user_id:
#             print("CRITICAL: Tentative d'action sans ID utilisateur !")
#             return # Ou lever une exception

#     def get_all_users(self):
#         db = SessionLocal()
#         try:
#             return db.query(User).all()
#         finally:
#             db.close()
        
#     def create_user(self, data):
#         allowed_roles = ['admin', 'superviseur', 'agent']
#         if data['role'] not in allowed_roles:
#             return False, "Rôle non autorisé."
        
#         try:
#             new_user = User(
#                 username=data['username'],
#                 email=data['email'],     
#                 role=data['role'],
#                 is_active=True
#             )
#             if data.get('password'):
#                 new_user.set_password(data['password'])
            
#             self.db.add(new_user)
#             self.db.commit()
#             self._log_action("CRÉATION", f"Nouvel utilisateur créé : {data['username']} (Rôle: {data['role']})")
#             return True, "Utilisateur créé !"
#         except Exception as e:
#             self.db.rollback()
#             return False, str(e)

#     def delete_user(self, user_id):
#         try:
#             # 1. Rechercher l'utilisateur
#             user = self.db.query(User).filter(User.id == user_id).first()
            
#             if not user:
#                 return False, "Utilisateur introuvable."

#             # 2. Supprimer l'objet
#             username_deleted = user.username
#             self.db.delete(user)
            
#             # 3. VALIDER (Indispensable pour PostgreSQL)
#             self.db.commit()

#             self._log_action(
#             "SUPPRESSION", 
#             f"L'utilisateur '{username_deleted}' (ID: {user_id}) a été supprimé du système."
#             )
#             return True, "Utilisateur supprimé avec succès."
            
#         except Exception as e:
#             self.db.rollback()
#             return False, f"Erreur lors de la suppression : {str(e)}"

#     def get_by_id(self, user_id):
#         """Récupère un utilisateur spécifique par son identifiant unique"""
#         return self.db.query(User).filter(User.id == user_id).first()

#     def update_user(self, user_id, data):

#         try:
#             # 1. Récupérer l'utilisateur existant
#             user = self.db.query(User).filter(User.id == user_id).first()
            
#             if not user:
#                 return False, "Utilisateur non trouvé."

#             # 2. Mettre à jour les champs
#             user.username = data.get('username', user.username)
#             user.email = data.get('email', user.email)
#             user.role = data.get('role', user.role)
            
#             # 3. Gérer le mot de passe (uniquement s'il est saisi)
#             password = data.get('password')
#             if password and password.strip():
#                 user.set_password(password)

#             # 4. LE PLUS IMPORTANT : Envoyer vers la DB
#             self.db.commit() 
#             old_name = user.username

#             user.username = data.get('username', user.username)
#             user.email = data.get('email', user.email)
#             user.role = data.get('role', user.role)
            
#             self.db.commit()

#             # --- AJOUT DE L'AUDIT ICI ---
#             return True, "Utilisateur mis à jour avec succès !"
            
#         except Exception as e:
#             self.db.rollback() # Annule en cas d'erreur
#             return False, str(e)

    
#     @property # Assure-toi d'avoir le décorateur property
#     def current_user_role(self):
#         """Récupère le rôle de l'utilisateur connecté depuis la DB"""
#         if self._cached_role:
#             return self._cached_role
            
#         if self.current_user_id:
#             try:
#                 print(f"utilisateur d'ID {self.current_user_id} trouvé")
#                 # AJOUT DE .first() ICI pour exécuter la requête
#                 user = self.db.query(User).filter(User.id == self.current_user_id).first()
                
#                 if user:
#                     self._cached_role = user.role
#                     print(f"DEBUG: Rôle trouvé en DB : {self._cached_role}")
#                     return self._cached_role
#             except Exception as e:
#                 print(f"Erreur lors de la récupération du rôle : {e}")
                
#         # SÉCURITÉ : Renvoyer 'agent' ou 'guest' par défaut, JAMAIS 'admin'
#         return "guest"


# addons/Paramètres/controllers/controller.py
"""
Contrôleur utilisateur optimisé - Retourne des objets SQLAlchemy
"""

from core.database import SessionLocal
from core.local_db import cache
from addons.Paramètres.models.models import User, AuditUserLog
import socket
import threading
from PySide6.QtCore import QObject, Signal


class UserController(QObject):
    """Contrôleur utilisateur avec cache (retourne des objets)"""
    
    # Signaux
    users_loaded = Signal(list)
    user_created = Signal(object)
    user_updated = Signal(object)
    user_deleted = Signal(int)
    error_occurred = Signal(str)
    loading_started = Signal()
    loading_finished = Signal()
    
    def __init__(self, db_session, current_user_id=None):
        super().__init__()
        self.db = db_session 
        self.current_user_id = current_user_id
        self._cached_role = None
        self._loading_thread = None
    
    # ============================================================================
    # MÉTHODES AVEC CACHE (RETOURNENT DES OBJETS)
    # ============================================================================
    
    def get_all_users(self, force_refresh: bool = False, async_callback: callable = None) -> list:
        """
        Récupère tous les utilisateurs (objets SQLAlchemy)
        Premier chargement = base de données, suivants = cache mémoire
        """
        cache_key = "parametres:users:objects"
        
        if not force_refresh:
            # Essayer le cache d'objets (stockés en mémoire, pas en SQLite)
            cached_users = self._get_cached_objects(cache_key)
            if cached_users is not None:
                print(f"📦 Cache hit: {len(cached_users)} utilisateurs (objets)")
                if async_callback:
                    async_callback(cached_users)
                return cached_users
        
        # Charger depuis la base
        print(f"💾 Cache miss: Chargement depuis la base")
        
        if async_callback:
            self._load_users_async(cache_key, async_callback)
            return []
        else:
            return self._load_users_sync(cache_key)
    
    def _get_cached_objects(self, cache_key: str) -> list:
        """
        Récupère les objets depuis le cache mémoire
        (Les objets SQLAlchemy ne peuvent pas être sérialisés en JSON)
        """
        # Utiliser un cache mémoire simple pour les objets
        if not hasattr(self, '_object_cache'):
            self._object_cache = {}
        
        cached = self._object_cache.get(cache_key)
        if cached:
            # Vérifier expiration (5 minutes)
            import time
            if time.time() - cached['timestamp'] < 300:
                return cached['objects']
            else:
                del self._object_cache[cache_key]
        return None
    
    def _save_to_object_cache(self, cache_key: str, objects: list):
        """Sauvegarde les objets dans le cache mémoire"""
        if not hasattr(self, '_object_cache'):
            self._object_cache = {}
        
        import time
        self._object_cache[cache_key] = {
            'objects': objects,
            'timestamp': time.time()
        }
    
    def _load_users_sync(self, cache_key: str) -> list:
        """Chargement synchrone des utilisateurs"""
        try:
            users = self.db.query(User).all()
            
            # Sauvegarder en cache mémoire
            self._save_to_object_cache(cache_key, users)
            
            return users
        except Exception as e:
            self.error_occurred.emit(str(e))
            return []
    
    def _load_users_async(self, cache_key: str, callback: callable):
        """Chargement asynchrone des utilisateurs"""
        def load():
            self.loading_started.emit()
            
            try:
                users = self.db.query(User).all()
                
                # Sauvegarder en cache mémoire
                self._save_to_object_cache(cache_key, users)
                
                # Callback dans le thread principal
                from PySide6.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(
                    self,
                    "_emit_users_loaded",
                    Qt.QueuedConnection,
                    Qt.Argument(lambda: callback(users))
                )
            except Exception as e:
                self.error_occurred.emit(str(e))
            finally:
                self.loading_finished.emit()
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def _emit_users_loaded(self, users, callback):
        """Émet les utilisateurs chargés"""
        self.users_loaded.emit(users)
        if callback:
            callback(users)
    
    def get_user_by_id(self, user_id: int, force_refresh: bool = False) -> User:
        """Récupère un utilisateur par ID (objet)"""
        cache_key = f"parametres:user:object:{user_id}"
        
        if not force_refresh:
            cached = self._get_cached_objects(cache_key)
            if cached:
                return cached[0] if cached else None
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self._save_to_object_cache(cache_key, [user])
        return user
    
    def get_user_by_username(self, username: str, force_refresh: bool = False) -> User:
        """Récupère un utilisateur par nom d'utilisateur (objet)"""
        cache_key = f"parametres:user:username:object:{username}"
        
        if not force_refresh:
            cached = self._get_cached_objects(cache_key)
            if cached:
                return cached[0] if cached else None
        
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            self._save_to_object_cache(cache_key, [user])
        return user
    
    # ============================================================================
    # MÉTHODES D'ÉCRITURE
    # ============================================================================
    
    def create_user(self, data: dict) -> tuple:
        """Crée un utilisateur et invalide le cache"""
        allowed_roles = ['admin', 'superviseur', 'agent']
        if data.get('role') not in allowed_roles:
            return False, "Rôle non autorisé."
        
        try:
            new_user = User(
                username=data['username'],
                email=data['email'],     
                role=data.get('role', 'agent'),
                full_name=data.get('full_name', ''),
                is_active=data.get('is_active', True)
            )
            
            if data.get('password'):
                new_user.set_password(data['password'])
            
            self.db.add(new_user)
            self.db.commit()
            
            # ⭐ INVALIDER LE CACHE
            self._invalidate_user_cache()
            
            # Log d'audit
            self._log_action("CRÉATION", f"Nouvel utilisateur créé : {data['username']} (Rôle: {data['role']})")
            
            # Émettre le signal
            self.user_created.emit(new_user)
            
            return True, "Utilisateur créé avec succès !"
            
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def update_user(self, user_id: int, data: dict) -> tuple:
        """Met à jour un utilisateur et invalide le cache"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Utilisateur non trouvé."
            
            old_username = user.username
            
            # Mettre à jour les champs
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'role' in data:
                user.role = data['role']
            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            password = data.get('password')
            if password and password.strip():
                user.set_password(password)
            
            self.db.commit()
            
            # ⭐ INVALIDER LE CACHE
            self._invalidate_user_cache()
            
            # Log d'audit
            self._log_action("MODIFICATION", f"Utilisateur modifié : {old_username} → {user.username}")
            
            # Émettre le signal
            self.user_updated.emit(user)
            
            return True, "Utilisateur mis à jour avec succès !"
            
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def delete_user(self, user_id: int) -> tuple:
        """Supprime un utilisateur et invalide le cache"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Utilisateur introuvable."
            
            username_deleted = user.username
            self.db.delete(user)
            self.db.commit()
            
            # ⭐ INVALIDER LE CACHE
            self._invalidate_user_cache()
            
            # Log d'audit
            self._log_action(
                "SUPPRESSION", 
                f"L'utilisateur '{username_deleted}' (ID: {user_id}) a été supprimé."
            )
            
            # Émettre le signal
            self.user_deleted.emit(user_id)
            
            return True, "Utilisateur supprimé avec succès."
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erreur lors de la suppression : {str(e)}"
    
    # ============================================================================
    # MÉTHODES D'INVALIDATION
    # ============================================================================
    
    def _invalidate_user_cache(self):
        """Invalide toutes les entrées de cache mémoire"""
        if hasattr(self, '_object_cache'):
            # Supprimer seulement les clés liées aux utilisateurs
            keys_to_delete = [k for k in self._object_cache.keys() if k.startswith('parametres:user')]
            for key in keys_to_delete:
                del self._object_cache[key]
        
        print("🗑️ Cache mémoire des utilisateurs invalidé")
    
    def refresh_cache(self):
        """Force le rafraîchissement du cache"""
        self._invalidate_user_cache()
        return self.get_all_users(force_refresh=True)
    
    # ============================================================================
    # MÉTHODES D'AUDIT
    # ============================================================================
    
    def get_audit_logs(self, limit: int = 100) -> list:
        """Récupère les logs d'audit"""
        if self.current_user_role != "admin":
            print(f"Tentative d'accès non autorisé aux logs")
            return []
        
        try:
            return self.db.query(AuditUserLog).order_by(
                AuditUserLog.created_at.desc()
            ).limit(limit).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des logs : {e}")
            return []
    
    def _log_action(self, action: str, details: str):
        """Enregistre une action dans les logs d'audit"""
        if not self.current_user_id:
            print("CRITICAL: Tentative d'action sans ID utilisateur !")
            return
        
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            new_log = AuditUserLog(
                user_id=self.current_user_id,
                action=action,
                details=details,
                ip_address=ip_address
            )
            
            self.db.add(new_log)
            self.db.commit()
            print(f"DEBUG: Log enregistré : {action}")
        except Exception as e:
            self.db.rollback()
            print(f"DEBUG: Erreur enregistrement Log : {e}")
    
    # ============================================================================
    # PROPRIÉTÉS
    # ============================================================================
    
    @property
    def current_user_role(self) -> str:
        """Récupère le rôle de l'utilisateur connecté"""
        if self._cached_role:
            return self._cached_role
        
        if self.current_user_id:
            try:
                user = self.db.query(User).filter(User.id == self.current_user_id).first()
                if user:
                    self._cached_role = user.role
                    return self._cached_role
            except Exception as e:
                print(f"Erreur lors de la récupération du rôle : {e}")
        
        return "guest"
    
    def get_cache_stats(self) -> dict:
        """Retourne les statistiques du cache mémoire"""
        if hasattr(self, '_object_cache'):
            return {
                'total_entries': len(self._object_cache),
                'keys': list(self._object_cache.keys())
            }
        return {'total_entries': 0, 'keys': []}