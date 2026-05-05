# batch_print_manager.py
"""
Gestionnaire d'impression groupée - Exécute les impressions dans le thread principal
"""

from PySide6.QtCore import QObject, Signal, QTimer, Qt
from PySide6.QtWidgets import QApplication, QProgressDialog, QMessageBox


class BatchPrintManager(QObject):
    """Gestionnaire d'impression groupée - Exécute dans le thread principal"""
    
    progress = Signal(int, int, str)
    finished = Signal(bool, str)
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.vehicles_queue = []
        self.documents_queue = []
        self.current_index = 0
        self.total_items = 0
        self.success_count = 0
        self.error_count = 0
        self.is_running = False
        self.is_cancelled = False
        self.progress_dialog = None
    
    def start_batch_print(self, vehicles_data, selected_documents):
        """Démarre l'impression groupée"""
        if self.is_running:
            return
        
        # Préparer les données complètes des véhicules
        self.vehicles_queue = []
        for vehicle in vehicles_data:
            complete_data = self._get_complete_vehicle_data(vehicle.get('id'))
            if complete_data:
                self.vehicles_queue.append(complete_data)
            else:
                print(f"⚠️ Impossible de charger les données pour {vehicle.get('immatriculation', 'véhicule')}")
        
        if not self.vehicles_queue:
            QMessageBox.warning(self.parent, "Erreur", "Aucun véhicule valide à imprimer")
            return
        
        self.documents_queue = selected_documents
        self.total_items = len(self.vehicles_queue) * len(self.documents_queue)
        self.current_index = 0
        self.success_count = 0
        self.error_count = 0
        self.is_running = True
        self.is_cancelled = False
        
        # Créer la boîte de progression
        self.progress_dialog = QProgressDialog(
            "Préparation de l'impression...",
            "Annuler",
            0,
            self.total_items,
            self.parent
        )
        self.progress_dialog.setWindowTitle("Impression groupée")
        self.progress_dialog.setMinimumWidth(400)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                background: white;
                border-radius: 16px;
            }
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 10px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                border-radius: 10px;
            }
        """)
        self.progress_dialog.canceled.connect(self.cancel)
        
        # Démarrer la première impression
        QTimer.singleShot(100, self._print_next)
        self.progress_dialog.show()
    
    def cancel(self):
        """Annule l'impression"""
        self.is_cancelled = True
        if self.progress_dialog:
            self.progress_dialog.setLabelText("Annulation en cours...")
    
    def _print_next(self):
        """Imprime l'élément suivant (appelé dans le thread principal)"""
        if self.is_cancelled:
            self._finish()
            return
        
        if self.current_index >= self.total_items:
            self._finish()
            return
        
        # Calculer l'élément courant
        vehicle_idx = self.current_index // len(self.documents_queue)
        doc_idx = self.current_index % len(self.documents_queue)
        
        vehicle = self.vehicles_queue[vehicle_idx]
        doc_type = self.documents_queue[doc_idx]
        doc_name = self._get_document_name(doc_type)
        
        # Mettre à jour la progression
        self.progress_dialog.setValue(self.current_index)
        self.progress_dialog.setLabelText(
            f"Génération de {doc_name} pour {vehicle.get('immatriculation', 'véhicule')}..."
        )
        
        # Forcer le traitement des événements
        QApplication.processEvents()
        
        # Exécuter l'impression
        try:
            success = self._print_document(vehicle, doc_type)
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
        except Exception as e:
            print(f"Erreur impression {doc_type}: {e}")
            self.error_count += 1
        
        self.current_index += 1
        
        # Programmer l'impression suivante
        QTimer.singleShot(500, self._print_next)
    
    def _finish(self):
        """Termine l'impression groupée"""
        self.is_running = False
        
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None
        
        if self.is_cancelled:
            QMessageBox.information(self.parent, "Annulé", "L'impression a été annulée.")
        elif self.error_count == 0:
            QMessageBox.information(
                self.parent, 
                "Impression terminée", 
                f"✅ {self.success_count} document(s) généré(s) avec succès"
            )
        else:
            QMessageBox.warning(
                self.parent, 
                "Impression terminée", 
                f"⚠️ {self.success_count} succès, {self.error_count} erreur(s)"
            )
        
        self.finished.emit(self.error_count == 0, "")
    
    def _get_complete_vehicle_data(self, vehicle_id):
        """Récupère les données complètes d'un véhicule"""
        try:
            from addons.Automobiles.models import Vehicle
            from addons.Automobiles.models.contract_models import Contrat
            
            # Utiliser la session du contrôleur
            session = self.controller.session
            if not session:
                return None
            
            db_vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            if not db_vehicle:
                return None
            
            # Récupérer le contrat (utiliser first() pour éviter le warning)
            contrat = session.query(Contrat).filter(
                Contrat.vehicle_id == vehicle_id
            ).first()
            
            # Récupérer le propriétaire
            owner = None
            if db_vehicle.owner_id:
                from addons.Automobiles.models.contact_models import Contact
                owner = session.query(Contact).filter(Contact.id == db_vehicle.owner_id).first()
            
            # Construire les données complètes
            return {
                'id': db_vehicle.id,
                'immatriculation': db_vehicle.immatriculation,
                'chassis': db_vehicle.chassis,
                'marque': db_vehicle.marque,
                'modele': db_vehicle.modele,
                'annee': db_vehicle.annee,
                'energie': db_vehicle.energie,
                'usage': db_vehicle.usage,
                'places': db_vehicle.places,
                'zone': db_vehicle.zone,
                'categorie': db_vehicle.categorie,
                'code_tarif': db_vehicle.code_tarif,
                'libele_tarif': db_vehicle.libele_tarif,
                'statut': db_vehicle.statut,
                'date_debut': db_vehicle.date_debut,
                'date_fin': db_vehicle.date_fin,
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
                'amt_fleet_rc_val': db_vehicle.amt_fleet_rc_val,
                'amt_fleet_dr_val': db_vehicle.amt_fleet_dr_val,
                'amt_fleet_vol_val': db_vehicle.amt_fleet_vol_val,
                'amt_fleet_vb_val': db_vehicle.amt_fleet_vb_val,
                'amt_fleet_in_val': db_vehicle.amt_fleet_in_val,
                'amt_fleet_bris_val': db_vehicle.amt_fleet_bris_val,
                'amt_fleet_ar_val': db_vehicle.amt_fleet_ar_val,
                'amt_fleet_dta_val': db_vehicle.amt_fleet_dta_val,
                'amt_fleet_ipt_val': db_vehicle.amt_fleet_ipt_val,
                'numero_police': getattr(contrat, 'numero_police', 'N/A') if contrat else 'N/A',
                'statut_paiement': getattr(contrat, 'statut_paiement', 'NON_PAYE') if contrat else 'NON_PAYE',
                'owner': f"{getattr(owner, 'nom', '')} {getattr(owner, 'prenom', '')}".strip() if owner else 'Propriétaire non renseigné',
                'owner_phone': getattr(owner, 'telephone', 'N/A') if owner else 'N/A',
                'owner_email': getattr(owner, 'email', 'N/A') if owner else 'N/A',
                'owner_address': getattr(owner, 'adresse', 'N/A') if owner else 'N/A',
                'owner_city': getattr(owner, 'ville', 'Yaoundé') if owner else 'Yaoundé',
            }
            
        except Exception as e:
            print(f"Erreur _get_complete_vehicle_data: {e}")
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
        """Imprime un document - exécuté dans le thread principal"""
        try:
            if doc_type == 'vignette':
                self.controller.vehicles.print_vignette(vehicle_data, self.parent)
            elif doc_type == 'carte_rose':
                self.controller.vehicles.print_carte_rose(vehicle_data, self.parent)
            elif doc_type == 'attestation':
                self.controller.vehicles.print_attestation(vehicle_data, self.parent)
            elif doc_type == 'devis':
                self.controller.vehicles.print_devis(vehicle_data, self.parent)
            elif doc_type == 'quittance':
                if hasattr(self.controller.vehicles, 'print_quittance'):
                    self.controller.vehicles.print_quittance(vehicle_data, self.parent)
                else:
                    print("Quittance - Non implémenté")
            return True
        except Exception as e:
            print(f"Erreur impression {doc_type}: {e}")
            import traceback
            traceback.print_exc()
            return False