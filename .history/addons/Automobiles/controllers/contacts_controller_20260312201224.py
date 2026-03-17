from addons.Automobiles.models.models import Contact, ContactAuditLog
import socket
from sqlalchemy import func  # <--- C'est cette ligne qui manque

class ContactController:
    def __init__(self, db_session, current_user_id):
        self.db = db_session
        self.current_user_id = current_user_id

    # --- LECTURE ---
    def get_all_contacts(self):
        """Récupère tous les contacts (Assurés, Prospects, etc.)"""
        try:
            return self.db.query(Contact).all()
        except Exception as e:
            print(f"ERREUR get_all: {e}")
            return []

    def get_contact_by_id(self, contact_id):
        """Récupère un contact précis par son ID unique"""
        try:
            return self.db.query(Contact).filter(Contact.id == contact_id).first()
        except Exception as e:
            print(f"ERREUR get_by_id: {e}")
            return None

    # --- CRÉATION ---
    def get_client_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"
    
    def create_contact(self, data):
        try:
            # 1. Nettoyage et préparation des données
            # On s'assure que les champs obligatoires ne sont pas vides
            if not data.get('nom'):
                return None, False, "Le nom est obligatoire."

            # 2. Instanciation
            data.pop('dossier_client', None)
            new_contact = Contact(**data)
            
            # 3. Traçabilité (Correction des noms de variables)
            # Vérifiez si vous utilisez 'current_user' ou 'current_user_id'
            user_id = getattr(self, 'current_user_id', None) 
            if not user_id and hasattr(self, 'current_user') and self.current_user:
                user_id = self.current_user.id

            if user_id:
                new_contact.created_by = user_id
                new_contact.updated_by = user_id
            
            # Ajout de l'IP (nécessaire pour nos nouveaux modèles)
            client_ip = self.get_client_ip()
            new_contact.created_ip = client_ip
            new_contact.last_ip = client_ip
            
            # 4. Sauvegarde
            self.db.add(new_contact)
            self.db.commit()
            
            # 5. Rafraîchir pour obtenir l'ID généré
            self.db.refresh(new_contact)
            
            # 6. Audit (Optionnel : si vous avez gardé ContactAuditLog)
            # self.log_audit(user_id, "CREATE", new_contact.id)
            
            return new_contact, True, "Contact créé avec succès"
            
        except Exception as e:
            self.db.rollback()
            # Très important pour le debug : voir l'erreur précise dans la console
            import traceback
            traceback.print_exc() 
            return None, False, f"Erreur base de données : {str(e)}"

    # --- MISE À JOUR ---
    def update_contact(self, contact_id, data):
        try:
            # ... logique de mise à jour ...
            self.db.commit()  # <--- INDISPENSABLE
            return True
        except:
            self.db.rollback()
        return False

    # --- SUPPRESSION ---
    def delete_contact(self, contact_id):
        try:
            contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
            if contact:
                self.db.delete(contact)
                self.db.commit()  # <--- INDISPENSABLE
                return True
            return False
        except Exception as e:
            print(f"Erreur : {e}")
            self.db.rollback() # Annule en cas d'erreur pour ne pas bloquer la session
            return False
        
    def log_contact_action(self, action, contact_id, details=""):
        try:
            # Récupération de l'adresse IP locale
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            new_log = ContactAuditLog(
                user_id=self.current_user_id,
                contact_id=contact_id,
                action=action,
                details=details,
                ip_address=ip_address # On enregistre l'IP ici
            )
            self.db.add(new_log)
            self.db.commit()
        except Exception as e:
            print(f"Erreur d'audit (IP) : {e}")

    def get_audit_logs(self):
        """Récupère tous les logs pour l'affichage (Aucun argument requis)"""
        try:
            return self.db.query(ContactAuditLog).order_by(ContactAuditLog.created_at.desc()).all()
        except Exception as e:
            print(f"Erreur de lecture audit : {e}")
            return []
        
    def get_contact_stats(self):
        """
        Récupère le nombre de contacts par type.
        Retourne un dictionnaire : {'Assuré': 12, 'Prospect': 5}
        """
        try:
            # Requête SQL : SELECT type_contact, count(id) FROM contacts GROUP BY type_contact
            results = self.db.query(
                Contact.type_contact, 
                func.count(Contact.id)
            ).group_by(Contact.type_contact).all()
            
            # Conversion du résultat (liste de tuples) en dictionnaire
            return {row[0] if row[0] else "Inconnu": row[1] for row in results}
        except Exception as e:
            print(f"Erreur stats : {e}")
            return {}
        
    def on_search_changed(self, text):
        """Filtre les contacts affichés en fonction de la saisie."""
        search_text = text.lower()
        
        # 1. Récupérer tous les contacts depuis le contrôleur (ou un cache local)
        all_contacts = self.controller.get_all_contacts()
        
        # 2. Filtrer la liste
        filtered_contacts = []
        for c in all_contacts:
            # On cherche dans le nom, le prénom, le téléphone ou le type
            match_found = (
                search_text in (c.nom or "").lower() or 
                search_text in (c.prenom or "").lower() or
                search_text in (c.telephone or "").lower() or
                search_text in (c.type_contact or "").lower()
            )
            if match_found:
                filtered_contacts.append(c)
        
        # 3. Rafraîchir l'affichage des cartes et des stats
        self.display_contacts(filtered_contacts)

    def get_report_data(self):
        """Prépare les données groupées pour le PDF."""
        contacts = self.get_all_contacts()
        stats = self.get_contact_stats()
        return contacts, stats