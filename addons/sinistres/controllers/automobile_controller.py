"""
Contrôleur pour interagir avec le module Automobile
"""
from PySide6.QtCore import Signal
from typing import Optional, List, Dict, Any

from addons.sinistres.controllers.controleur_base import BaseController
from addons.sinistres.services.automobile_service import AutomobileService


class AutomobileController(BaseController):
    """Contrôleur pour les données du module Automobile"""
    
    # Signaux
    contacts_loaded = Signal(list)
    contrats_loaded = Signal(list)
    contact_selected = Signal(dict)
    vehicules_loaded = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.service = AutomobileService()
        self._contacts_cache = []
        self._contrats_cache = []
    
    # ============================================================
    # CLIENTS
    # ============================================================
    
    def rechercher_contacts(self, search: str = None, limit: int = 50) -> List[dict]:
        """Recherche des contacts"""
        try:
            contacts = self.service.get_contacts(search, limit)
            result = [
                {
                    'id': c.id,
                    'code_client': c.code_client,
                    'nom': c.nom,
                    'prenom': c.prenom,
                    'civilite': c.civilite,
                    'telephone': c.telephone,
                    'tel_portable': c.tel_portable,
                    'email': c.email,
                    'adresse': c.adresse,
                    'ville': c.ville,
                    'profession': c.profession,
                    'display': self.service.format_contact_display(c)
                }
                for c in contacts
            ]
            self._contacts_cache = result
            self.contacts_loaded.emit(result)
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_contact(self, contact_id: int) -> Optional[dict]:
        """Récupère un contact par son ID"""
        try:
            contact = self.service.get_contact_by_id(contact_id)
            if contact:
                return {
                    'id': contact.id,
                    'code_client': contact.code_client,
                    'nom': contact.nom,
                    'prenom': contact.prenom,
                    'civilite': contact.civilite,
                    'telephone': contact.telephone,
                    'tel_portable': contact.tel_portable,
                    'email': contact.email,
                    'adresse': contact.adresse,
                    'ville': contact.ville,
                    'profession': contact.profession,
                    'display': self.service.format_contact_display(contact)
                }
            return None
        except Exception as e:
            self.handle_error(e)
            return None
    
    def get_contacts_by_ids(self, ids: List[int]) -> List[dict]:
        """Récupère plusieurs contacts par leurs IDs"""
        try:
            result = []
            for cid in ids:
                contact = self.service.get_contact_by_id(cid)
                if contact:
                    result.append({
                        'id': contact.id,
                        'code_client': contact.code_client,
                        'nom': contact.nom,
                        'prenom': contact.prenom,
                        'display': self.service.format_contact_display(contact)
                    })
            return result
        except Exception as e:
            self.handle_error(e)
            return []

    def is_contrat_flotte(self, contrat: dict) -> bool:
        """Vérifie si un contrat est une flotte"""
        return self.service.is_contrat_fleet(contrat)

    def get_vehicules_by_contrat(self, contrat_id: int) -> List[dict]:
        """Récupère les véhicules d'un contrat flotte"""
        try:
            return self.service.get_vehicules_by_contrat(contrat_id)
        except Exception as e:
            self.handle_error(e)
            return []
    # ============================================================
    # CONTRATS
    # ============================================================
    
    def get_contrats_by_client(self, client_id: int, statut: str = None) -> List[dict]:
        """Récupère les contrats d'un client"""
        try:
            print(f"🔍 get_contrats_by_client (controller): client_id={client_id}")
            
            contrats = self.service.get_contrats_by_client(client_id, statut)
            print(f"📊 Contrats reçus du service: {len(contrats)}")
            
            if not contrats:
                print("⚠️ Aucun contrat trouvé")
                return []
            
            result = []
            for c in contrats:
                print(f"  - Traitement contrat: {c.numero_police}")
                
                # ✅ Récupérer le statut correctement
                if hasattr(c.statut, 'value'):
                    statut_value = c.statut.value
                else:
                    statut_value = str(c.statut)
                
                # ✅ Formater l'affichage
                display = self.service.format_contrat_display(c)
                print(f"    display: {display}")
                
                result.append({
                    'id': c.id,
                    'numero_police': c.numero_police,
                    'statut': statut_value,
                    'date_debut': c.date_debut.isoformat() if c.date_debut else None,
                    'date_fin': c.date_fin.isoformat() if c.date_fin else None,
                    'prime_totale_ttc': c.prime_totale_ttc,
                    'montant_paye': c.montant_paye,
                    'type_contrat': c.type_contrat,
                    'vehicle_id': c.vehicle_id,
                    'display': display
                })
            
            print(f"✅ {len(result)} contrats formatés")
            self.contrats_loaded.emit(result)
            return result
            
        except Exception as e:
            print(f"❌ Erreur get_contrats_by_client: {e}")
            import traceback
            traceback.print_exc()
            self.handle_error(e)
            return []
        
    def get_contrat(self, contrat_id: int) -> Optional[dict]:
        """Récupère un contrat par son ID"""
        try:
            contrat = self.service.get_contrat_by_id(contrat_id)
            if contrat:
                return {
                    'id': contrat.id,
                    'numero_police': contrat.numero_police,
                    'statut': contrat.statut.value if hasattr(contrat.statut, 'value') else str(contrat.statut),
                    'date_debut': contrat.date_debut.isoformat() if contrat.date_debut else None,
                    'date_fin': contrat.date_fin.isoformat() if contrat.date_fin else None,
                    'prime_totale_ttc': contrat.prime_totale_ttc,
                    'montant_paye': contrat.montant_paye,
                    'type_contrat': contrat.type_contrat,
                    'vehicle_id': contrat.vehicle_id,
                    'display': self.service.format_contrat_display(contrat)
                }
            return None
        except Exception as e:
            self.handle_error(e)
            return None