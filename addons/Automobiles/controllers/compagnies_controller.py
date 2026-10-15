from operator import or_
import socket
import requests
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from addons.Automobiles.models.compagnies_models import Compagnie  # Assurez-vous que le chemin est correct
import logging
from typing import Tuple, Optional, Dict, List
import pandas as pd
from addons.Automobiles.models.tarif_models import AutomobileTarif  # Assurez-vous du chemin d'import

class CompagnieController:
    def __init__(self, db_session, current_user_id):
        self.db = db_session
        # Accepte soit l'ID utilisateur, soit l'objet User.
        # Dans le second cas, on prend simplement l'attribut .id pour éviter
        # d'essayer d'insérer tout l'objet dans la colonne created_by.
        self.current_user_id = getattr(current_user_id, 'id', current_user_id)
        self.logger = logging.getLogger(__name__)

    def _get_audit_data(self, user_login):
        """
        Méthode privée pour capturer les données système (Audit).
        Cette méthode garantit que l'utilisateur ne peut pas falsifier sa trace.
        """
        local_ip = "127.0.0.1"
        network_ip = "127.0.0.1"
        
        try:
            # Récupération de l'IP Locale
            local_ip = socket.gethostbyname(socket.gethostname())
            # Récupération de l'IP Publique (via API externe avec timeout 1s)
            network_ip = requests.get('https://api.ipify.org', timeout=1).text
        except Exception:
            # En cas d'échec (pas d'internet), on utilise l'IP locale
            network_ip = local_ip

        return {
            "user": user_login,
            "local_ip": local_ip,
            "network_ip": network_ip,
            "now": datetime.now()
        }

    def create_compagnie(self, data, user_id):
        """
        :param data: dict venant de get_data()
        :param user_id: int (ID de l'utilisateur connecté)
        """
        print(user_id)
        try:
            # Récupération des IPs
            local_ip = socket.gethostbyname(socket.gethostname())
            try:
                net_ip = requests.get('https://api.ipify.org', timeout=1).text
            except:
                net_ip = local_ip

            nouvelle_cie = Compagnie(
                **data,  # Injecte nom, code, email, telephone, adresse, num_debut, num_fin
                create_by=user_id,
                modify_by=user_id,
                local_ip=local_ip,
                network_ip=net_ip,
                created_at=datetime.now(),
                modify_at=datetime.now(),
                is_active=True
            )
            
            self.db.add(nouvelle_cie)
            self.db.commit()
            return True, "Enregistré"
        except Exception as e:
            self.db.rollback()
            return False, str(e)
        
    def update_compagnie(self, compagnie_id, form_data, user_login):
        """
        Met à jour une compagnie et trace l'auteur de la modification.
        """
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not cie:
                return False, "Compagnie introuvable."

            audit = self._get_audit_data(user_login)

            # Mise à jour des informations
            cie.nom = form_data.get('nom', cie.nom).upper()
            cie.email = form_data.get('email', cie.email)
            cie.telephone = form_data.get('telephone', cie.telephone)
            cie.adresse = form_data.get('adresse', cie.adresse)
            cie.num_debut = form_data.get('num_debut', cie.num_debut)
            cie.num_fin = form_data.get('num_fin', cie.num_fin)

            # Mise à jour de l'audit de modification
            cie.modify_by = audit['user']
            cie.modify_at = audit['now']
            cie.local_ip = audit['local_ip']
            cie.network_ip = audit['network_ip']

            self.db.commit()
            return True, "Mise à jour effectuée."

        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def delete_compagnie(self, compagnie_id, user_login):
        """
        Suppression logique (is_active = False) avec audit de qui a 'supprimé'.
        """
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not cie:
                return False, "Compagnie introuvable."

            audit = self._get_audit_data(user_login)

            cie.is_active = False
            cie.modify_by = audit['user']
            cie.modify_at = audit['now']
            cie.local_ip = audit['local_ip']
            cie.network_ip = audit['network_ip']

            self.db.commit()
            return True, "Compagnie archivée."
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def get_contacts_for_combo(self, text=""):
        """Récupère les compagnies pour le combo de filtrage."""
        query = self.db.query(Compagnie).filter(Compagnie.is_active == True)
        if text:
            query = query.filter(Compagnie.nom.ilike(f"%{text}%"))
        return query.all()
    
    def get_all_active_compagnies(self):
        """Retourne la liste des objets Compagnie actifs."""
        try:
            # Assurez-vous que le nom de la classe est 'Compagnie'
            return self.db.query(Compagnie).filter(Compagnie.is_active == True).all()
        except Exception as e:
            print(f"Erreur DB get_all: {e}")
            return []

    def get_by_id(self, compagnie_id):
        """
        Récupère une compagnie spécifique par son ID.
        """
        try:
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if compagnie:
                # On retourne un dictionnaire pour faciliter le remplissage du formulaire
                return {
                    "id": compagnie.id,
                    "code": compagnie.code,
                    "nom": compagnie.nom,
                    "email": compagnie.email,
                    "telephone": compagnie.telephone,
                    "adresse": compagnie.adresse,
                    "num_debut": compagnie.num_debut,
                    "num_fin": compagnie.num_fin
                }
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de la compagnie {compagnie_id}: {e}")
            return None
        
    def delete_compagnie_logic(self, compagnie_id, user_id):
        """Désactive une compagnie au lieu de la supprimer."""
        try:
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not compagnie:
                return False, "Compagnie introuvable."

            compagnie.is_active = False # Elle ne s'affichera plus dans le tableau
            compagnie.modify_by = user_id
            compagnie.modify_at = datetime.now()

            self.db.commit()
            return True, "La compagnie a été désactivée."
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def update_compagnie(self, cie_id, data, user_id):
        try:
            cie = self.db.query(Compagnie).filter(Compagnie.id == cie_id).first()
            if not cie:
                return False, "Compagnie introuvable"

            # Mise à jour des champs
            cie.code = data.get('code', cie.code).upper()
            cie.nom = data.get('nom', cie.nom).upper()
            cie.email = data.get('email', cie.email)
            cie.telephone = data.get('telephone', cie.telephone)
            cie.adresse = data.get('adresse', cie.adresse)
            cie.num_debut = data.get('num_debut', cie.num_debut)
            cie.num_fin = data.get('num_fin', cie.num_fin)
            
            # Audit
            cie.modify_by = user_id
            cie.modify_at = datetime.now()
            # cie.local_ip = ... (récupérer IP comme dans le create)

            self.db.commit()
            return True, "Mise à jour réussie"
        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def search_compagnies(self, search_text=""):
        """
        Recherche des compagnies par nom ou par ID.
        Retourne une liste d'objets Compagnie.
        """
        try:
            
            query = self.db.query(Compagnie)

            if search_text:
                # On cherche si le texte est dans le nom OU si c'est l'ID exact
                search_filter = f"%{search_text}%"
                
                # Construction du filtre (Nom contient OU ID égal)
                if search_text.isdigit():
                    query = query.filter(
                        (Compagnie.nom.ilike(search_filter)) | 
                        (Compagnie.id == int(search_text)) |
                        (Compagnie.code == int(search_filter)) |
                        (Compagnie.email.ilike(search_filter))
                    )
                else:
                    print(Compagnie.id)
                    query = query.filter(Compagnie.id.ilike(search_filter))

            # On limite à 50 résultats pour la performance et on trie par nom
            return query.order_by(Compagnie.nom).limit(50).all()

        except Exception as e:
            print(f"Erreur recherche compagnie: {e}")
            return []

    def get_available_numbers(self, compagnie_id):
        """Récupère les numéros disponibles dans la plage de la compagnie"""
        try:
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not compagnie or not compagnie.num_debut or not compagnie.num_fin:
                return [], 0, 0
            
            debut = int(compagnie.num_debut)
            fin = int(compagnie.num_fin)
            
            # Récupérer les numéros déjà utilisés
            from addons.Automobiles.models.contract_models import Contrat
            used_numbers = self.db.query(Contrat.numero_police_attribue).filter(
                Contrat.company_id == compagnie_id,
                Contrat.numero_police_attribue.isnot(None)
            ).all()
            
            used_set = {n[0] for n in used_numbers if n[0]}
            
            # Calculer les numéros disponibles
            available = [n for n in range(debut, fin + 1) if n not in used_set]
            total = fin - debut + 1
            used_count = len(used_set)
            
            return available, total, used_count
            
        except Exception as e:
            print(f"Erreur get_available_numbers: {e}")
            return [], 0, 0
    
    def get_next_available_number(self, compagnie_id):
        """Récupère le prochain numéro disponible pour une compagnie"""
        available, total, used = self.get_available_numbers(compagnie_id)
        if available:
            return available[0], total, used
        return None, total, used
    
    def generate_police_number(self, compagnie_id, attribued_number):
        """Génère le numéro de police complet"""
        try:
            compagnie = self.db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
            if not compagnie:
                return f"POL-{attribued_number:05d}"
            
            # Utiliser le code de la compagnie comme préfixe
            prefix = compagnie.code or "POL"
            return f"{prefix}-{attribued_number:05d}"
            
        except Exception as e:
            print(f"Erreur generate_police_number: {e}")
            return f"POL-{attribued_number:05d}"
        
    def search_companies(self, search_term: str) -> List[Compagnie]:
        """
        Recherche des compagnies par nom, code ou téléphone
        
        Args:
            search_term: Terme de recherche
            
        Returns:
            List[Compagnie]: Liste des compagnies correspondantes
        """
        if not search_term or len(search_term) < 2:
            return []
        
        search = f"%{search_term}%"
        
        try:
            # SOLUTION 1: Utiliser or_ avec des conditions combinées par paires
            # Ceci fonctionne avec toutes les versions de SQLAlchemy
            return self.db.query(Compagnie).filter(
                or_(
                    or_(
                        Compagnie.nom.ilike(search),
                        Compagnie.code.ilike(search)
                    ),
                    or_(
                        Compagnie.telephone.ilike(search),
                        Compagnie.email.ilike(search)
                    )
                )
            ).limit(50).all()
            
        except Exception as e:
            print(f"Erreur search_companies (méthode 1): {e}")
            
            try:
                # SOLUTION 2: Utiliser une approche alternative avec des filtres séparés
                from sqlalchemy import func
                
                return self.db.query(Compagnie).filter(
                    (Compagnie.nom.ilike(search)) | 
                    (Compagnie.code.ilike(search)) | 
                    (Compagnie.telephone.ilike(search)) | 
                    (Compagnie.email.ilike(search))
                ).limit(50).all()
                
            except Exception as e2:
                print(f"Erreur search_companies (méthode 2): {e2}")
                
                try:
                    # SOLUTION 3: Requête avec UNION (plus lente mais compatible)
                    from sqlalchemy import union_all
                    
                    q1 = self.db.query(Compagnie).filter(Compagnie.nom.ilike(search))
                    q2 = self.db.query(Compagnie).filter(Compagnie.code.ilike(search))
                    q3 = self.db.query(Compagnie).filter(Compagnie.telephone.ilike(search))
                    q4 = self.db.query(Compagnie).filter(Compagnie.email.ilike(search))
                    
                    # Union des résultats
                    union_query = union_all(q1, q2, q3, q4)
                    result = self.db.query(Compagnie).from_self().union(union_query).limit(50).all()
                    
                    # Supprimer les doublons
                    seen = set()
                    unique_results = []
                    for r in result:
                        if r.id not in seen:
                            seen.add(r.id)
                            unique_results.append(r)
                    
                    return unique_results
                    
                except Exception as e3:
                    print(f"Erreur search_companies (méthode 3): {e3}")
                    return []
    
    def get_company_by_id(self, company_id: int) -> Optional[Compagnie]:
        """Récupère une compagnie par son ID"""
        return self.db.query(Compagnie).filter(Compagnie.id == company_id).first()
    