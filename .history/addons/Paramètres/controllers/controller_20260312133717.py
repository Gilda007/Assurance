from core.database import SessionLocal
from addons.Paramètres.models import User, AuditUserLog
import socket

class UserController:
    def __init__(self, db_session, current_user_id=None):
        # C'est ici qu'on crée l'attribut 'db'
        self.db = db_session 
        self.current_user_id = current_user_id
        self._cached_role = None
        print(f"DEBUG: Contrôleur prêt. DB: {self.db is not None}, UserID: {self.current_user_id}")
        print(f"DEBUG: Contrôleur initialisé avec la session : {self.db}")

    def get_audit_logs(self, limit=100):
        """Récupère les logs UNIQUEMENT si l'utilisateur est admin"""
        try:
            # VERIFICATION DU RÔLE (Condition de sécurité)
            if self.current_user_role != "admin":
                print(f"Tentative d'accès non autorisé aux logs par ID: {self.current_user_id}")
                return [] # On renvoie une liste vide au lieu des logs
                
            return self.db.query(AuditUserLog).order_by(AuditUserLog.created_at.desc()).limit(limit).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des logs : {e}")
            return []

    def _log_action(self, action, details):

        if not self.current_user_id:
            print("CRITICAL: Tentative d'action sans ID utilisateur !")
            return # Ou lever une exception
        try:
            # Récupération de l'IP
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            # Création de l'entrée d'audit
            new_log = AuditUserLog(
                user_id=self.current_user_id,
                action=action,
                details=details,
                ip_address=ip_address
            )
            
            # AJOUT ET VALIDATION
            self.db.add(new_log)
            self.db.commit() # <--- TRÈS IMPORTANT
            print(f"DEBUG: Log enregistré : {action}")
        except Exception as e:
            self.db.rollback()
            print(f"DEBUG: Erreur enregistrement Log : {e}")

        if not self.current_user_id:
            print("CRITICAL: Tentative d'action sans ID utilisateur !")
            return # Ou lever une exception

    def get_all_users(self):
        db = SessionLocal()
        try:
            return db.query(User).all()
        finally:
            db.close()
        
    def create_user(self, data):
        allowed_roles = ['admin', 'superviseur', 'agent']
        if data['role'] not in allowed_roles:
            return False, "Rôle non autorisé."
        
        try:
            new_user = User(
                username=data['username'],
                email=data['email'],     
                role=data['role'],
                is_active=True
            )
            if data.get('password'):
                new_user.set_password(data['password'])
            
            self.db.add(new_user)
            self.db.commit()
            self._log_action("CRÉATION", f"Nouvel utilisateur créé : {data['username']} (Rôle: {data['role']})")
            return True, "Utilisateur créé !"
        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def delete_user(self, user_id):
        try:
            # 1. Rechercher l'utilisateur
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Utilisateur introuvable."

            # 2. Supprimer l'objet
            username_deleted = user.username
            self.db.delete(user)
            
            # 3. VALIDER (Indispensable pour PostgreSQL)
            self.db.commit()

            self._log_action(
            "SUPPRESSION", 
            f"L'utilisateur '{username_deleted}' (ID: {user_id}) a été supprimé du système."
            )
            return True, "Utilisateur supprimé avec succès."
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erreur lors de la suppression : {str(e)}"

    def get_by_id(self, user_id):
        """Récupère un utilisateur spécifique par son identifiant unique"""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id, data):

        try:
            # 1. Récupérer l'utilisateur existant
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Utilisateur non trouvé."

            # 2. Mettre à jour les champs
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.role = data.get('role', user.role)
            
            # 3. Gérer le mot de passe (uniquement s'il est saisi)
            password = data.get('password')
            if password and password.strip():
                user.set_password(password)

            # 4. LE PLUS IMPORTANT : Envoyer vers la DB
            self.db.commit() 
            old_name = user.username

            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.role = data.get('role', user.role)
            
            self.db.commit()

            # --- AJOUT DE L'AUDIT ICI ---
            return True, "Utilisateur mis à jour avec succès !"
            
        except Exception as e:
            self.db.rollback() # Annule en cas d'erreur
            return False, str(e)

    
    @property # Assure-toi d'avoir le décorateur property
    def current_user_role(self):
        """Récupère le rôle de l'utilisateur connecté depuis la DB"""
        if self._cached_role:
            return self._cached_role
            
        if self.current_user_id:
            try:
                print(f"utilisateur d'ID {self.current_user_id} trouvé")
                # AJOUT DE .first() ICI pour exécuter la requête
                user = self.db.query(User).filter(User.id == self.current_user_id).first()
                
                if user:
                    self._cached_role = user.role
                    print(f"DEBUG: Rôle trouvé en DB : {self._cached_role}")
                    return self._cached_role
            except Exception as e:
                print(f"Erreur lors de la récupération du rôle : {e}")
                
        # SÉCURITÉ : Renvoyer 'agent' ou 'guest' par défaut, JAMAIS 'admin'
        return "guest"