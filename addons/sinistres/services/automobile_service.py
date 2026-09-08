"""
Service pour interagir avec les modèles du module Automobile
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService
from addons.Automobiles.models.contact_models import Contact
from addons.Automobiles.models.contract_models import Contrat


class AutomobileService(BaseService):
    """Service pour récupérer les données du module Automobile"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # CLIENTS (Contacts)
    # ============================================================
    
    def get_contacts(self, search: str = None, limit: int = 50) -> List[Contact]:
        """Récupère la liste des contacts avec recherche"""
        try:
            query = self.session.query(Contact).filter(
                Contact.statut == "Actif"
            )
            
            if search:
                search = f"%{search}%"
                query = query.filter(
                    (Contact.nom.ilike(search)) |
                    (Contact.prenom.ilike(search)) |
                    (Contact.code_client.ilike(search)) |
                    (Contact.telephone.ilike(search)) |
                    (Contact.email.ilike(search))
                )
            
            return query.order_by(Contact.nom).limit(limit).all()
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        """Récupère un contact par son ID"""
        try:
            return self.session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.statut == "Actif"
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_contact_by_code(self, code: str) -> Optional[Contact]:
        """Récupère un contact par son code client"""
        try:
            return self.session.query(Contact).filter(
                Contact.code_client == code,
                Contact.statut == "Actif"
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def format_contact_display(self, contact: Contact) -> str:
        """Formate l'affichage d'un contact pour les combobox"""
        nom_complet = f"{contact.nom} {contact.prenom or ''}".strip()
        code = contact.code_client or f"ID:{contact.id}"
        infos = []
        
        if contact.telephone:
            infos.append(contact.telephone)
        if contact.email:
            infos.append(contact.email)
        if contact.ville:
            infos.append(contact.ville)
        
        info_str = f" - {' | '.join(infos)}" if infos else ""
        return f"{code} - {nom_complet}{info_str}"
    
    # ============================================================
    # CONTRATS
    # ============================================================
    
    # def get_contrats_by_client(self, client_id: int) -> List[Contrat]:
    #     """Récupère les contrats d'un client"""
    #     try:
    #         query = self.session.query(Contrat).filter(
    #             Contrat.owner_id == client_id
    #         )
    #         # if statut:
    #         #     query = query.filter(Contrat.statut == statut)
    #         # else:
    #         #     # Par défaut, contrats actifs et proformats
    #         #     query = query.filter(
    #         #         Contrat.statut.in_(["actif", "proformat"])
    #         #     )
            
    #         return query.order_by(Contrat.date_debut.desc()).all()
            
    #     except Exception as e:
    #         self.session.rollback()
    #         raise e
    
    def get_contrats_by_client(self, client_id: int, statut: str = None) -> List[Contrat]:
        """Récupère les contrats d'un client - Version avec débogage"""
        try:
            from addons.Automobiles.models.contract_models import ContractStatus
            
            print(f"🔍 Recherche contrats pour client_id={client_id}")
            
            # Vérifier d'abord si le client existe
            client = self.session.query(Contact).filter(Contact.id == client_id).first()
            if not client:
                print(f"❌ Client {client_id} non trouvé")
                return []
            print(f"✅ Client trouvé: {client.nom} {client.prenom or ''}")
            
            # Requête de base
            query = self.session.query(Contrat).filter(
                Contrat.owner_id == client_id
            )
            
            # Compter tous les contrats du client (sans filtre)
            total_count = query.count()
            print(f"📊 Total contrats pour ce client: {total_count}")
            
            if total_count == 0:
                print("⚠️ Aucun contrat trouvé pour ce client")
                return []
            
            # Afficher tous les contrats avec leurs statuts
            all_contrats = query.all()
            for c in all_contrats:
                statut_value = c.statut.value if hasattr(c.statut, 'value') else str(c.statut)
                print(f"  - Contrat {c.numero_police}: statut={statut_value}")
            
            # Filtrer par statut
            if statut:
                if isinstance(statut, str):
                    try:
                        statut_enum = ContractStatus(statut)
                        query = query.filter(Contrat.statut == statut_enum)
                        print(f"🔍 Filtrage par statut: {statut_enum.value}")
                    except ValueError:
                        query = query.filter(Contrat.statut == statut)
                        print(f"🔍 Filtrage par statut (chaîne): {statut}")
                else:
                    query = query.filter(Contrat.statut == statut)
            # else:
            #     # ✅ Filtrer sur les statuts actifs et proformats
            #     active_statuses = [ContractStatus.ACTIF, ContractStatus.PROFORMAT]
            #     query = query.filter(Contrat.statut.in_(active_statuses))
            #     print(f"🔍 Filtrage par défaut: actif ou proformat")
            
            # Exécuter la requête
            result = query.order_by(Contrat.date_debut.desc()).all()
            print(f"✅ {len(result)} contrats trouvés après filtrage")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
            self.session.rollback()
            raise e

    def get_contrat_by_id(self, contrat_id: int) -> Optional[Contrat]:
        """Récupère un contrat par son ID"""
        try:
            return self.session.query(Contrat).filter(
                Contrat.id == contrat_id
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_contrat_by_police(self, numero_police: str) -> Optional[Contrat]:
        """Récupère un contrat par son numéro de police"""
        try:
            return self.session.query(Contrat).filter(
                Contrat.numero_police == numero_police
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def format_contrat_display(self, contrat: Contrat) -> str:
        """Formate l'affichage d'un contrat pour les combobox"""
        police = contrat.numero_police
        statut = contrat.statut.value if hasattr(contrat.statut, 'value') else str(contrat.statut)
        infos = []
        
        if contrat.vehicle:
            infos.append(f"Véhicule: {contrat.vehicle.immatriculation or 'N/A'}")
        if contrat.date_debut:
            infos.append(f"Début: {contrat.date_debut.strftime('%d/%m/%Y')}")
        if contrat.date_fin:
            infos.append(f"Fin: {contrat.date_fin.strftime('%d/%m/%Y')}")
        if contrat.prime_totale_ttc:
            infos.append(f"Prime: {contrat.prime_totale_ttc:,.0f} FCFA")
        
        info_str = f" - {' | '.join(infos)}" if infos else ""
        return f"{police} [{statut.upper()}]{info_str}"