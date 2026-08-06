from sqlalchemy.orm import selectinload

from addons.Automobiles.models.contact_models import Contact, ContactAuditLog
from addons.Automobiles.models.driver_models import Driver
from addons.Automobiles.models import Fleet
from core import logger
import socket
from sqlalchemy import func, or_  # <--- C'est cette ligne qui manque
from datetime import datetime
import os

from core.workers.query_cache import query_cache

class ContactController:
    def __init__(self, db_session, current_user_id):
        self.db = db_session
        # Accepte soit l'ID utilisateur, soit l'objet User.
        # Dans le second cas, on prend simplement l'attribut .id pour éviter
        # d'essayer d'insérer tout l'objet dans la colonne created_by.
        self.current_user_id = getattr(current_user_id, 'id', current_user_id)

    def get_all_contacts(self, force_refresh: bool = False):
        """Récupère tous les contacts avec cache simple"""
        
        cache_key = "contacts_all"
        
        if not force_refresh:
            cached = query_cache.get(cache_key)
            if cached is not None:
                logger.info(f"📦 Cache hit: {len(cached)} contacts")
                return cached
        
        # Charger depuis la base
        try:
            contacts = self.db.query(Contact).all()
            query_cache.set(cache_key, contacts, ttl=300)
            logger.info(f"💾 Cache miss: {len(contacts)} contacts chargés")
            return contacts
        except Exception as e:
            logger.error(f"Erreur chargement contacts: {e}")
            return []

    def get_contact_by_id(self, contact_id):
        """Récupère un contact précis par son ID unique"""
        try:
            return self.db.query(Contact).filter(Contact.id == contact_id).first()
        except Exception as e:
            print(f"ERREUR get_by_id: {e}")
            return None

    def get_driver_by_id(self, driver_id):
            """Récupère un chauffeur précis par son ID unique"""
            try:
                return self.db.query(Driver).filter(Driver.id == driver_id).first()
            except Exception as e:
                print(f"ERREUR get_driver_by_id: {e}")
                return None

    def load_contacts(self):
        """Charge les contacts (souscripteurs + chauffeurs)"""
        try:
            self.set_status("Chargement...", "info")
            
            # ✅ Vider le cache pour forcer le rechargement
            from core.workers.query_cache import query_cache
            query_cache.invalidate('all_contacts_drivers')
            query_cache.invalidate('contacts_all')
            
            # ✅ Utiliser la nouvelle méthode
            self.all_contacts = self.controller.contacts.get_all_contacts_with_drivers(force_refresh=True)
            self.filtered_contacts = self.all_contacts.copy()
            self.display_contacts()
            self.update_statistics()
            self.update_last_update_time()
            
            count = len(self.all_contacts)
            self.set_status(f"{count} contact(s) chargé(s)", "success")
            
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
            logger.error(f"Erreur chargement contacts: {e}")
            import traceback
            traceback.print_exc()

    def get_contacts_by_type_and_nature(self, type_client: str, nature: str = None):
        """
        Récupère les contacts par type et nature.
        """
        try:
            # ✅ Clé de cache
            cache_key = f"contacts_type_{type_client}_nature_{nature}"
            cached = query_cache.get(cache_key)
            if cached is not None:
                return cached
            
            query = self.db.query(Contact).filter(Contact.type_client == type_client)
            
            if nature:
                query = query.filter(Contact.nature == nature)
            
            results = query.all()
            
            # Mettre en cache
            query_cache.set(cache_key, results, ttl=300)
            
            print(f"🔍 get_contacts_by_type_and_nature({type_client}, {nature}) → {len(results)} contacts")
            return results
        except Exception as e:
            print(f"❌ Erreur get_contacts_by_type_and_nature: {e}")
            return []

    def get_contacts_by_type(self, type_client: str):
        """
        Récupère les contacts par type de client (Souscripteur, Chauffeur, etc.)
        
        Args:
            type_client: Type de client (ex: "Souscripteur", "Chauffeur")
        
        Returns:
            list: Liste des contacts correspondant au type
        """
        try:
            from addons.Automobiles.models.contact_models import Contact
            
            contacts = self.db.query(Contact).filter(
                Contact.type_client == type_client
            ).all()
            
            print(f"🔍 get_contacts_by_type({type_client}) → {len(contacts)} contacts trouvés")
            return contacts
        except Exception as e:
            print(f"❌ Erreur get_contacts_by_type({type_client}): {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_contacts_by_nature(self, nature: str):
        """
        Récupère les contacts par nature (Particulier, Société, etc.)
        
        Args:
            nature: Nature du contact (ex: "Particulier", "Société")
        
        Returns:
            list: Liste des contacts correspondant à la nature
        """
        try:
            from addons.Automobiles.models.contact_models import Contact
            
            contacts = self.db.query(Contact).filter(
                Contact.nature == nature
                #Contact.is_active == T#rue
            ).all()
            
            print(f"🔍 get_contacts_by_nature({nature}) → {len(contacts)} contacts trouvés")
            return contacts
        except Exception as e:
            print(f"❌ Erreur get_contacts_by_nature({nature}): {e}")
            return []

    def get_subscribers(self):
        """
        Récupère tous les souscripteurs (Personnes Physiques et Morales).
        
        Returns:
            list: Liste des contacts de type "Souscripteur"
        """
        try:
            cache_key = "contacts_subscribers"
            cached = query_cache.get(cache_key)
            if cached is not None:
                return cached
            
            subscribers = self.db.query(Contact).filter(
                Contact.type_client == "Souscripteur"
            ).all()
            
            query_cache.set(cache_key, subscribers, ttl=300)
            print(f"🔍 {len(subscribers)} souscripteurs trouvés")
            return subscribers
        except Exception as e:
            print(f"❌ Erreur get_subscribers: {e}")
            return []

    def get_contact_summary(self, contact_id: int):
        """
        Récupère un résumé complet d'un contact avec ses relations.
        
        Args:
            contact_id: ID du contact
        
        Returns:
            dict: Résumé du contact avec ses relations
        """
        try:
            contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                return None
            
            summary = {
                'id': contact.id,
                'nom': contact.nom,
                'prenom': contact.prenom,
                'type_client': contact.type_client,
                'nature': contact.nature,
                'statut': contact.statut,
                'telephone': contact.telephone,
                'email': contact.email,
                'created_at': contact.created_at,
            }
            
            # Si c'est un chauffeur, ajouter les infos du souscripteur
            if contact.type_client == "Chauffeur" and contact.subscriber_id:
                subscriber = self.get_contact_by_id(contact.subscriber_id)
                if subscriber:
                    summary['subscriber_nom'] = subscriber.nom
                    summary['subscriber_prenom'] = subscriber.prenom
                    summary['subscriber_id'] = subscriber.id
            
            # Si c'est un souscripteur, ajouter ses chauffeurs
            if contact.type_client == "Souscripteur":
                drivers = self.get_drivers_by_subscriber(contact.id)
                summary['drivers_count'] = len(drivers)
                summary['drivers'] = [{'id': d.id, 'nom': d.nom, 'prenom': d.prenom} for d in drivers]
            
            return summary
        except Exception as e:
            print(f"❌ Erreur get_contact_summary({contact_id}): {e}")
            return None

    # --- CRÉATION ---
    def get_client_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"

    # addons/Automobiles/controllers/contact_controller.py

    def get_all_contacts_with_drivers(self, force_refresh: bool = False):
        """
        Récupère tous les souscripteurs (Contact) et les chauffeurs (Driver)
        et les fusionne dans une liste unique pour l'affichage.
        """
        try:
            from addons.Automobiles.models.driver_models import Driver
            from addons.Automobiles.views.contact_list_item import ContactListItem
            
            cache_key = "all_contacts_drivers"
            
            if not force_refresh:
                cached = query_cache.get(cache_key)
                if cached is not None:
                    print(f"📦 Cache hit: {len(cached)} entrées")
                    return cached
            
            # ✅ Récupérer les souscripteurs (type_client = "Souscripteur")
            contacts = self.db.query(Contact).all()
            print(f"🔍 {len(contacts)} souscripteurs trouvés")
            
            # ✅ Récupérer les chauffeurs
            drivers = self.db.query(Driver).all()
            print(f"🔍 {len(drivers)} chauffeurs trouvés")
            
            # ✅ Créer des wrappers pour chaque élément
            all_entries = []
            
            for contact in contacts:
                all_entries.append(ContactListItem('contact', contact))
            
            for driver in drivers:
                all_entries.append(ContactListItem('driver', driver))
            
            # ✅ Trier par ID
            all_entries.sort(key=lambda x: x.id if x.id else 0)
            
            # ✅ Mettre en cache
            query_cache.set(cache_key, all_entries, ttl=300)
            
            print(f"✅ {len(all_entries)} entrées chargées (Contacts: {len(contacts)}, Drivers: {len(drivers)})")
            return all_entries
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erreur get_all_contacts_with_drivers: {e}")
            import traceback
            traceback.print_exc()
            return []

    def create_contact(self, data):
        """Crée un contact (souscripteur uniquement)"""
        try:
            # Supprimer l'image brute
            data.pop("image_brute", None)
            
            # ✅ Forcer le type_client à "Souscripteur"
            data["type_client"] = "Souscripteur"
            
            # Filtrer les données
            allowed_keys = [c.key for c in Contact.__table__.columns]
            filtered_data = {}
            for k, v in data.items():
                if k in allowed_keys:
                    if k.endswith('_date') and v == '':
                        filtered_data[k] = None
                    else:
                        filtered_data[k] = v
                else:
                    print(f"⚠️ Clé ignorée: {k} = {v}")
            
            # Créer l'objet Contact
            new_contact = Contact(**filtered_data)
            
            # Traçabilité
            new_contact.created_by = self.current_user_id
            new_contact.created_ip = self.get_client_ip()
            
            # Sauvegarder
            self.db.add(new_contact)
            self.db.commit()
            self.db.refresh(new_contact)
            
            # Invalider le cache
            query_cache.invalidate('contacts_all')
            
            print(f"✅ Souscripteur créé: {new_contact.nom} (ID: {new_contact.id})")
            return new_contact, True, "Souscripteur créé avec succès"
            
        except Exception as e:
            self.db.rollback()
            print(f"--- ERREUR CRÉATION CONTACT ---")
            print(f"Détails : {str(e)}")
            import traceback
            traceback.print_exc()
            return None, False, f"Erreur technique : {str(e)}"

    def create_driver(self, data):
        """Crée un chauffeur dans la table Driver"""
        try:
            from addons.Automobiles.models.driver_models import Driver
            
            # Supprimer l'image brute
            data.pop("image_brute", None)
            
            # Vérifier que le souscripteur existe
            subscriber_id = data.get('subscriber_id')
            if not subscriber_id:
                return None, False, "Un souscripteur est obligatoire pour un chauffeur"
            
            subscriber = self.db.query(Contact).filter(Contact.id == subscriber_id).first()
            if not subscriber:
                return None, False, f"Souscripteur ID {subscriber_id} non trouvé"
            
            # Filtrer les données pour Driver
            allowed_keys = [c.key for c in Driver.__table__.columns]
            filtered_data = {}
            for k, v in data.items():
                if k in allowed_keys:
                    if k.endswith('_date') and v == '':
                        filtered_data[k] = None
                    else:
                        filtered_data[k] = v
                else:
                    print(f"⚠️ Clé ignorée pour Driver: {k} = {v}")
            
            # Créer l'objet Driver
            new_driver = Driver(**filtered_data)
            
            # Traçabilité
            new_driver.created_by = self.current_user_id
            
            # Sauvegarder
            self.db.add(new_driver)
            self.db.commit()
            self.db.refresh(new_driver)
            
            # Invalider le cache
            query_cache.invalidate('drivers_all')
            
            print(f"✅ Chauffeur créé: {new_driver.nom} (ID: {new_driver.id}) pour le souscripteur {subscriber.nom}")
            return new_driver, True, "Chauffeur créé avec succès"
            
        except Exception as e:
            self.db.rollback()
            print(f"--- ERREUR CRÉATION CHAUFFEUR ---")
            print(f"Détails : {str(e)}")
            import traceback
            traceback.print_exc()
            return None, False, f"Erreur technique : {str(e)}"

    def get_drivers_by_subscriber(self, subscriber_id):
        """Récupère tous les chauffeurs d'un souscripteur"""
        try:
            from addons.Automobiles.models.driver_models import Driver
            return self.db.query(Driver).filter(Driver.subscriber_id == subscriber_id).all()
        except Exception as e:
            print(f"Erreur get_drivers_by_subscriber: {e}")
            return []    

    def update_contact(self, contact_id, data):
        try:
            # 1. Supprimer l'image brute
            data.pop("image_brute", None)
            
            # 2. Récupérer le contact
            contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                return None, False, "Contact non trouvé"
            
            # 3. Définir les champs autorisés
            allowed_keys = [c.key for c in Contact.__table__.columns]
            
            # 4. Mettre à jour uniquement les champs autorisés
            for key, value in data.items():
                if key in allowed_keys:
                    setattr(contact, key, value)
                    print(f"   ✅ Mise à jour: {key} = {value}")
                else:
                    print(f"⚠️ Champ ignoré: {key}")
            
            # 5. Traçabilité
            if hasattr(self, 'current_user_id') and self.current_user_id:
                contact.updated_by = self.current_user_id
            if hasattr(self, 'get_client_ip'):
                contact.last_ip = self.get_client_ip()
            else:
                contact.last_ip = "127.0.0.1"
            
            # 6. Sauvegarder (INDISPENSABLE)
            self.db.commit()
            self.db.refresh(contact)
            
            print(f"✅ Contact mis à jour avec succès: {contact.nom} (ID: {contact.id})")
            return contact, True, "Contact mis à jour avec succès"
            
        except Exception as e:
            self.db.rollback()
            print(f"--- ERREUR MISE À JOUR CONTACT ---")
            print(f"Détails : {str(e)}")
            import traceback
            traceback.print_exc()
            return None, False, f"Erreur technique : {str(e)}"

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
        try:
            from addons.Automobiles.models.driver_models import Driver
            
            # Statistiques pour les contacts (souscripteurs)
            stats = {}
            
            # Total des souscripteurs
            stats['souscripteurs'] = self.db.query(Contact).filter(
                Contact.type_client == "Souscripteur"
            ).count()
            
            # Total des chauffeurs
            stats['chauffeurs'] = self.db.query(Driver).count()
            
            # Total général
            stats['total'] = stats['souscripteurs'] + stats['chauffeurs']
            
            # Actifs (souscripteurs)
            stats['actifs'] = self.db.query(Contact).filter(
                Contact.type_client == "Souscripteur",
                Contact.statut == 'Actif'
            ).count()
            
            # Inactifs (souscripteurs)
            stats['inactifs'] = self.db.query(Contact).filter(
                Contact.type_client == "Souscripteur",
                Contact.statut == 'Inactif'
            ).count()
            
            # Sociétés
            stats['societes'] = self.db.query(Contact).filter(
                Contact.type_client == "Souscripteur",
                Contact.nature == 'Société'
            ).count()
            
            # Particuliers
            stats['particuliers'] = self.db.query(Contact).filter(
                Contact.type_client == "Souscripteur",
                Contact.nature == 'Particulier'
            ).count()
            
            # Statistiques des chauffeurs par spécialité (depuis Driver)
            specialites = self.db.query(
                Driver.specialite, 
                func.count(Driver.id)
            ).group_by(Driver.specialite).all()
            stats['specialites'] = {row[0] if row[0] else "Non défini": row[1] for row in specialites}
            
            return stats
        except Exception as e:
            self.db.rollback()
            print(f"Erreur stats : {e}")
            import traceback
            traceback.print_exc()
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

    def get_contacts_for_combo(self, text=""):
        """Récupère les compagnies pour le combo de filtrage."""
        query = self.db.query(Contact)
        if text:
            query = query.filter(Contact.nom.ilike(f"%{text}%"))
        return query.all()

    def search_contacts(self, search_text):
        if not self.db:
            print("Erreur : Aucune session DB dans ContactController")
            return []
            
        # On sécurise le pattern de recherche
        pattern = f"%{search_text}%"
        
        return self.db.query(Contact).filter(
            Contact.nom.ilike(pattern) | 
            Contact.prenom.ilike(pattern) | 
            Contact.telephone.ilike(pattern) | 
            Contact.email.ilike(pattern) | 
            Contact.nature.ilike(pattern) |
            Contact.type_client.ilike(pattern) |  # ✅ Ajout du type_client
            Contact.code_client.ilike(pattern) |   # ✅ Ajout du code_client
            Contact.code_chauffeur.ilike(pattern)  # ✅ Ajout du code_chauffeur
        ).limit(10).all()

    def search_drivers(self, search_text):
            if not self.db:
                print("Erreur : Aucune session DB dans ContactController")
                return []
                
            # On sécurise le pattern de recherche
            pattern = f"%{search_text}%"
            
            return self.db.query(Driver).filter(
                Driver.nom.ilike(pattern) | 
                Driver.prenom.ilike(pattern) | 
                Driver.telephone.ilike(pattern) | 
                Driver.email.ilike(pattern) | 
                Driver.specialite.ilike(pattern) |
                Driver.num_permis.ilike(pattern) |  # ✅ Ajout du Numéro du permis du chauffeur
                Driver.id.ilike(pattern) |   # ✅ Ajout du code_client
                Driver.subscriber_id.ilike(pattern)  # ✅ Ajout du Numéro du souscripteur au quel le client est lié
            ).limit(10).all()
    
    def get_report_data(self):
        """Prépare les données groupées pour le PDF."""
        contacts = self.get_all_contacts()
        stats = self.get_contact_stats()
        return contacts, stats
    
    # Dans le contrôleur des contacts
    def get_all(self):
        return self.db.query(Contact).all()

    def count_by_type(self, client_type):
        return self.db.query(Contact).filter(Contact.nature == client_type).count()