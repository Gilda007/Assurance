# batch_print_thread.py
"""
Thread pour l'impression groupée des documents - Version thread-safe
"""

from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication
import time


class BatchPrintThread(QThread):
    """Thread pour l'impression groupée des documents - Thread-safe"""
    
    progress = Signal(int, int, str)
    finished = Signal(bool, str)
    document_printed = Signal(str, bool)
    
    def __init__(self, controller, vehicles_data, selected_documents, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.vehicles_data = vehicles_data
        self.selected_documents = selected_documents
        self.is_cancelled = False
        self._mutex = None  # Pour les accès concurrents
    
    def cancel(self):
        """Annule l'impression (appelable depuis le thread principal)"""
        self.is_cancelled = True
    
    def run(self):
        """Exécute l'impression groupée - tout doit être fait dans ce thread"""
        try:
            total = len(self.vehicles_data) * len(self.selected_documents)
            current = 0
            success_count = 0
            error_count = 0
            
            for vehicle in self.vehicles_data:
                if self.is_cancelled:
                    self._emit_signal_safe(self.finished, False, "Impression annulée")
                    return
                
                # S'assurer que les données sont complètes
                complete_vehicle_data = self._ensure_complete_data(vehicle)
                
                if not complete_vehicle_data:
                    error_count += len(self.selected_documents)
                    self._emit_signal_safe(self.progress, current, total, 
                        f"⚠️ Impossible de charger les données du véhicule {vehicle.get('immatriculation', 'inconnu')}")
                    continue
                
                for doc_type in self.selected_documents:
                    if self.is_cancelled:
                        self._emit_signal_safe(self.finished, False, "Impression annulée")
                        return
                    
                    current += 1
                    doc_name = self._get_document_name(doc_type)
                    self._emit_signal_safe(self.progress, current, total, 
                        f"Génération de {doc_name} pour {complete_vehicle_data.get('immatriculation', 'véhicule')}")
                    
                    # Utiliser QTimer pour ne pas bloquer
                    QApplication.processEvents()
                    
                    try:
                        success = self._print_document(complete_vehicle_data, doc_type)
                        self._emit_signal_safe(self.document_printed, doc_name, success)
                        if success:
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Erreur impression {doc_type}: {e}")
            
            if error_count == 0:
                self._emit_signal_safe(self.finished, True, f"✅ {success_count} document(s) généré(s) avec succès")
            else:
                self._emit_signal_safe(self.finished, True, f"⚠️ {success_count} succès, {error_count} erreur(s)")
                
        except Exception as e:
            self._emit_signal_safe(self.finished, False, f"Erreur: {str(e)}")
    
    def _emit_signal_safe(self, signal, *args):
        """Émet un signal de manière thread-safe"""
        try:
            signal.emit(*args)
        except RuntimeError:
            pass  # Ignorer les erreurs de destruction
    
    def _ensure_complete_data(self, vehicle):
        """S'assure que toutes les données nécessaires sont présentes"""
        try:
            # Si les données sont déjà complètes (contiennent 'owner' non vide)
            if vehicle.get('owner') and vehicle.get('owner') != 'Propriétaire non renseigné':
                return vehicle
            
            # Sinon, charger depuis la base
            vehicle_id = vehicle.get('id')
            if not vehicle_id:
                return None
            
            # Créer une nouvelle session pour ce thread
            from core.database import SessionLocal
            session = SessionLocal()
            
            try:
                from addons.Automobiles.models import Vehicle
                db_vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
                
                if not db_vehicle:
                    return None
                
                # Récupérer le contrat
                contrat = None
                if hasattr(db_vehicle, 'contract') and db_vehicle.contract:
                    contrat = db_vehicle.contract
                elif hasattr(self.controller, 'contracts'):
                    contrat = self.controller.contracts.get_active_contract_by_vehicle(vehicle_id)
                
                # Récupérer le propriétaire
                owner = None
                if hasattr(db_vehicle, 'owner') and db_vehicle.owner:
                    owner = db_vehicle.owner
                elif db_vehicle.owner_id and hasattr(self.controller, 'contacts'):
                    owner = self.controller.contacts.get_contact_by_id(db_vehicle.owner_id)
                
                # Construire les données complètes
                complete_data = {
                    'id': db_vehicle.id,
                    'immatriculation': db_vehicle.immatriculation,
                    'marque': db_vehicle.marque,
                    'modele': db_vehicle.modele,
                    'annee': db_vehicle.annee,
                    'energie': db_vehicle.energie,
                    'usage': db_vehicle.usage,
                    'places': db_vehicle.places,
                    'zone': db_vehicle.zone,
                    'categorie': db_vehicle.categorie,
                    'valeur_neuf': db_vehicle.valeur_neuf,
                    'valeur_venale': db_vehicle.valeur_venale,
                    'prime_nette': db_vehicle.prime_nette,
                    'prime_brute': db_vehicle.prime_brute,
                    'carte_rose': db_vehicle.carte_rose,
                    'vignette': db_vehicle.vignette,
                    'fichier_asac': db_vehicle.fichier_asac,
                    'tva': db_vehicle.tva,
                    'pttc': db_vehicle.pttc,
                    'amt_rc': db_vehicle.amt_rc,
                    'amt_dr': db_vehicle.amt_dr,
                    'amt_vol': db_vehicle.amt_vol,
                    'amt_vb': db_vehicle.amt_vb,
                    'amt_in': db_vehicle.amt_in,
                    'amt_bris': db_vehicle.amt_bris,
                    'amt_ar': db_vehicle.amt_ar,
                    'amt_dta': db_vehicle.amt_dta,
                    'amt_ipt': db_vehicle.amt_ipt,
                    'numero_police': getattr(contrat, 'numero_police', 'N/A') if contrat else 'N/A',
                    'owner': f"{getattr(owner, 'nom', '')} {getattr(owner, 'prenom', '')}".strip() if owner else 'Propriétaire non renseigné',
                    'owner_phone': getattr(owner, 'telephone', 'N/A') if owner else 'N/A',
                    'owner_email': getattr(owner, 'email', 'N/A') if owner else 'N/A',
                    'owner_address': getattr(owner, 'adresse', 'N/A') if owner else 'N/A',
                    'owner_city': getattr(owner, 'ville', 'Yaoundé') if owner else 'Yaoundé',
                }
                
                return complete_data
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Erreur _ensure_complete_data: {e}")
            return None
    
    def _get_document_name(self, doc_type):
        """Retourne le nom lisible du document"""
        names = {
            'vignette': 'Vignette',
            'carte_rose': 'Carte Rose',
            'attestation': 'Attestation',
            'devis': 'Devis',
            'quittance': 'Quittance'
        }
        return names.get(doc_type, doc_type)

    def _print_document(self, vehicle_data, doc_type):
        """Imprime un document spécifique avec délai"""
        try:
            # Petit délai pour éviter la saturation
            time.sleep(0.5)
            
            # Utiliser une session dédiée pour chaque impression
            from core.database import SessionLocal
            session = SessionLocal()
            
            try:
                from addons.Automobiles.controllers.automobile_controller import VehicleController
                local_controller = VehicleController(session)
                
                if doc_type == 'vignette':
                    local_controller.print_vignette(vehicle_data, None)
                elif doc_type == 'carte_rose':
                    local_controller.print_carte_rose(vehicle_data, None)
                elif doc_type == 'attestation':
                    local_controller.print_attestation(vehicle_data, None)
                elif doc_type == 'devis':
                    local_controller.print_devis(vehicle_data, None)
                return True
            finally:
                session.close()
                
        except Exception as e:
            print(f"Erreur impression {doc_type}: {e}")
            return False