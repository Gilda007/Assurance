# batch_print_manager.py
"""
Gestionnaire d'impression groupée
"""

import os
import re
from datetime import datetime

from PySide6.QtCore import QObject, Signal, QThread, QTimer, Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QProgressDialog, QMessageBox


def _get_document_name(doc_type):
    names = {
        "vignette": "Vignette",
        "carte_rose": "Carte Rose",
        "attestation": "Attestation",
        "devis": "Devis",
        "quittance": "Quittance",
    }
    return names.get(doc_type, doc_type)


class BatchPdfExportWorker(QThread):
    """Génère les PDF du lot sans bloquer l'interface."""

    progress = Signal(int, int, str)
    completed = Signal(int, int, bool, object)

    def __init__(self, controller, vehicles, documents, output_dir):
        super().__init__()
        self.controller = controller
        self.vehicles = vehicles
        self.documents = documents
        self.output_dir = output_dir
        self.cancel_requested = False

    def cancel(self):
        self.cancel_requested = True

    def run(self):
        success_count = 0
        errors = []
        total = len(self.vehicles) * len(self.documents)
        batch_stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        for vehicle_index, vehicle in enumerate(self.vehicles):
            for document_index, doc_type in enumerate(self.documents):
                if self.cancel_requested:
                    self.completed.emit(success_count, len(errors), True, errors)
                    return

                current = vehicle_index * len(self.documents) + document_index + 1
                vehicle_name = vehicle.get("immatriculation") or "véhicule"
                document_name = _get_document_name(doc_type)
                self.progress.emit(
                    current,
                    total,
                    f"Génération de {document_name} pour {vehicle_name}..."
                )

                try:
                    output_path = self._get_output_path(
                        vehicle, doc_type, batch_stamp, current
                    )
                    if self._generate_pdf(vehicle, doc_type, output_path):
                        success_count += 1
                    else:
                        raise RuntimeError("Le générateur n'a pas confirmé la création du PDF.")
                except Exception as error:
                    message = f"{document_name} — {vehicle_name}: {error}"
                    print(f"Erreur génération PDF: {message}")
                    errors.append(message)

        self.completed.emit(success_count, len(errors), False, errors)

    def _get_output_path(self, vehicle, doc_type, batch_stamp, index):
        immatriculation = str(vehicle.get("immatriculation") or "vehicule")
        safe_immatriculation = re.sub(r"[^\w.-]+", "_", immatriculation).strip("._")
        safe_immatriculation = safe_immatriculation or "vehicule"
        vehicle_id = vehicle.get("id", "sans_id")
        filename = (
            f"{doc_type}_{safe_immatriculation}_{vehicle_id}_"
            f"{batch_stamp}_{index}.pdf"
        )
        return os.path.join(self.output_dir, filename)

    def _generate_pdf(self, vehicle, doc_type, output_path):
        if doc_type == "vignette":
            from addons.Automobiles.views.vignette_printer import VignettePrinter

            printer = VignettePrinter(vehicle, export_dir=self.output_dir)
            printer.generate_pdf(output_path)
        elif doc_type == "carte_rose":
            from addons.Automobiles.views.carte_rose_printer import CarteRosePrinter

            CarteRosePrinter(vehicle).save_pdf(output_path)
        elif doc_type == "attestation":
            from addons.Automobiles.views.attestation_print import AttestationPrinter

            AttestationPrinter(vehicle).save_pdf(output_path)
        elif doc_type == "devis":
            required_fields = ("immatriculation", "marque", "modele", "owner")
            missing_fields = [
                field for field in required_fields if not vehicle.get(field)
            ]
            if missing_fields:
                raise ValueError(
                    f"Champs manquants : {', '.join(missing_fields)}"
                )

            from addons.Automobiles.views.devis_printer import DevisPrinter

            printer = DevisPrinter(vehicle, export_dir=self.output_dir)
            printer.generate_pdf(output_path, show_progress=False)
        elif doc_type == "quittance":
            generator = getattr(self.controller.vehicles, "print_quittance", None)
            if not callable(generator):
                raise RuntimeError("Le générateur de quittance n'est pas disponible.")
            if not generator(vehicle, output_path=output_path):
                return False
        else:
            raise ValueError(f"Type de document inconnu : {doc_type}")

        return os.path.isfile(output_path) and os.path.getsize(output_path) > 0


class BatchPrintManager(QObject):
    """Gère l'impression papier et l'export PDF groupés."""
    
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
        self.pdf_worker = None
        self.output_dir = None
    
    def start_batch_print(self, vehicles_data, selected_documents, output_mode="paper"):
        """Démarre l'impression groupée"""
        if self.is_running or (self.pdf_worker and self.pdf_worker.isRunning()):
            return
        if not selected_documents:
            QMessageBox.warning(self.parent, "Aucun document", "Sélectionnez au moins un document.")
            return

        self.output_dir = None
        if output_mode == "pdf":
            self.output_dir = QFileDialog.getExistingDirectory(
                self.parent,
                "Choisir le dossier de destination des PDF",
                os.path.expanduser("~"),
                QFileDialog.ShowDirsOnly
            )
            if not self.output_dir:
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
        if output_mode == "pdf" and not self._confirm_pdf_warnings():
            return

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
        self.progress_dialog.show()

        if output_mode == "pdf":
            self.pdf_worker = BatchPdfExportWorker(
                self.controller,
                self.vehicles_queue,
                self.documents_queue,
                self.output_dir
            )
            self.pdf_worker.progress.connect(self._on_pdf_progress)
            self.pdf_worker.completed.connect(self._on_pdf_completed)
            self.pdf_worker.finished.connect(self._on_pdf_worker_stopped)
            self.pdf_worker.finished.connect(self.pdf_worker.deleteLater)
            self.pdf_worker.start()
        else:
            QTimer.singleShot(100, self._print_next)

    def _confirm_pdf_warnings(self):
        """Regroupe les avertissements qui seraient sinon répétés pour chaque véhicule."""
        warnings = []

        if "vignette" in self.documents_queue:
            from addons.Automobiles.views.vignette_printer import VignettePrinter

            try:
                unpaid_count = sum(
                    not VignettePrinter(vehicle, export_dir=self.output_dir).is_paid
                    for vehicle in self.vehicles_queue
                )
                zero_stamp_count = sum(
                    not float(vehicle.get("amt_dta", 0) or 0)
                    for vehicle in self.vehicles_queue
                )
            except (TypeError, ValueError) as error:
                QMessageBox.critical(
                    self.parent,
                    "Vérification du paiement impossible",
                    f"Impossible de vérifier le statut de paiement : {error}"
                )
                return False
            if unpaid_count:
                warnings.append(
                    f"{unpaid_count} véhicule(s) ont un contrat non payé; "
                    "leur vignette portera le filigrane « NON PAYÉ »."
                )
            if zero_stamp_count:
                warnings.append(
                    f"{zero_stamp_count} véhicule(s) ont un montant de vignette à zéro."
                )

        if {"devis", "quittance"}.intersection(self.documents_queue):
            zero_amount_count = 0
            invalid_amount_count = 0
            for vehicle in self.vehicles_queue:
                try:
                    amount = float(
                        vehicle.get("prime_totale", vehicle.get("prime_nette", 0))
                        or 0
                    )
                except (TypeError, ValueError):
                    invalid_amount_count += 1
                else:
                    zero_amount_count += amount == 0
            if zero_amount_count:
                warnings.append(
                    f"{zero_amount_count} véhicule(s) ont une prime à zéro."
                )
            if invalid_amount_count:
                warnings.append(
                    f"Le montant de la prime est invalide pour "
                    f"{invalid_amount_count} véhicule(s)."
                )

        if not warnings:
            return True

        message = "\n\n".join(warnings) + "\n\nContinuer la génération des PDF ?"
        return QMessageBox.question(
            self.parent,
            "Vérification avant export",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) == QMessageBox.Yes

    def _on_pdf_progress(self, current, total, message):
        if self.progress_dialog:
            self.progress_dialog.setLabelText(message)
            self.progress_dialog.setValue(current)
        self.progress.emit(current, total, message)

    def _on_pdf_completed(self, success_count, error_count, was_cancelled, errors):
        self.success_count = success_count
        self.error_count = error_count
        self.is_cancelled = was_cancelled
        self.is_running = False

        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None

        if was_cancelled:
            message = (
                f"Export annulé. {success_count} PDF généré(s), "
                f"{error_count} erreur(s)."
            )
            QMessageBox.information(self.parent, "Export annulé", message)
        elif error_count:
            details = "\n".join(errors[:5])
            if len(errors) > 5:
                details += f"\n… et {len(errors) - 5} autre(s) erreur(s)."
            QMessageBox.warning(
                self.parent,
                "Export terminé avec des erreurs",
                f"{success_count} PDF généré(s), {error_count} erreur(s).\n"
                f"Dossier : {self.output_dir}\n\n{details}"
            )
        else:
            QMessageBox.information(
                self.parent,
                "Export terminé",
                f"{success_count} PDF généré(s).\n\nDossier : {self.output_dir}"
            )

        self.finished.emit(error_count == 0, self.output_dir or "")

    def _on_pdf_worker_stopped(self):
        self.pdf_worker = None

    def cancel(self):
        """Annule l'impression"""
        self.is_cancelled = True
        if self.pdf_worker and self.pdf_worker.isRunning():
            self.pdf_worker.cancel()
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
        doc_name = _get_document_name(doc_type)
        
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
            from addons.Automobiles.models import Vehicle, VehicleFleetGuarantee
            from addons.Automobiles.models.contract_models import Contrat
            
            # Utiliser la session du contrôleur
            session = self.controller.session
            if not session:
                return None
            
            db_vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            db_fleet_guarantee = session.query(VehicleFleetGuarantee).filter(VehicleFleetGuarantee.vehicle_id == vehicle_id).first()
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
                'puissance-fiscale': db_vehicle.puissance_fiscale,
                'tva': db_vehicle.tva,
                'pttc': db_vehicle.pttc,
                # Garanties (lues depuis la relation guarantees si disponibles)
                'amt_rc': getattr(db_vehicle, 'amt_rc', getattr(getattr(db_vehicle, 'guarantees', None), 'rc', 0)),
                'amt_dr': getattr(db_vehicle, 'amt_dr', getattr(getattr(db_vehicle, 'guarantees', None), 'dr', 0)),
                'amt_vol': getattr(db_vehicle, 'amt_vol', getattr(getattr(db_vehicle, 'guarantees', None), 'vol', 0)),
                'amt_vb': getattr(db_vehicle, 'amt_vb', getattr(getattr(db_vehicle, 'guarantees', None), 'vb', 0)),
                'amt_in': getattr(db_vehicle, 'amt_in', getattr(getattr(db_vehicle, 'guarantees', None), 'in_garantie', 0)),
                'amt_bris': getattr(db_vehicle, 'amt_bris', getattr(getattr(db_vehicle, 'guarantees', None), 'bris', 0)),
                'amt_ar': getattr(db_vehicle, 'amt_ar', getattr(getattr(db_vehicle, 'guarantees', None), 'ar', 0)),
                'amt_dta': getattr(db_vehicle, 'amt_dta', getattr(getattr(db_vehicle, 'guarantees', None), 'dta', 0)),
                'amt_ipt': getattr(db_vehicle, 'amt_ipt', getattr(getattr(db_vehicle, 'guarantees', None), 'ipt', 0)),
                'amt_fleet_rc_val': db_fleet_guarantee.rc if db_fleet_guarantee else 0,
                'amt_fleet_dr_val': db_fleet_guarantee.dr if db_fleet_guarantee else 0,
                'amt_fleet_vol_val': db_fleet_guarantee.vol if db_fleet_guarantee else 0,
                'amt_fleet_vb_val': db_fleet_guarantee.vb if db_fleet_guarantee else 0,
                'amt_fleet_in_val': db_fleet_guarantee.in_garantie if db_fleet_guarantee else 0,
                'amt_fleet_bris_val': db_fleet_guarantee.bris if db_fleet_guarantee else 0,
                'amt_fleet_ar_val': db_fleet_guarantee.ar if db_fleet_guarantee else 0,
                'amt_fleet_dta_val': db_fleet_guarantee.dta if db_fleet_guarantee else 0,
                'amt_fleet_ipt_val': db_fleet_guarantee.ipt if db_fleet_guarantee else 0,
                'numero_police': getattr(contrat, 'numero_police', 'N/A') if contrat else 'N/A',
                'statut_paiement': getattr(contrat, 'statut_paiement', 'NON_PAYE') if contrat else 'NON_PAYE',
                'owner': f"{getattr(owner, 'nom', '')} {getattr(owner, 'prenom', '')}".strip() if owner else 'Propriétaire non renseigné',
                'owner_phone': getattr(owner, 'telephone', 'N/A') if owner else 'N/A',
                'owner_email': getattr(owner, 'email', 'N/A') if owner else 'N/A',
                'owner_address': getattr(owner, 'adresse', 'N/A') if owner else 'N/A',
                'owner_city': getattr(owner, 'ville', 'Yaoundé') if owner else 'Yaoundé',
                'profession': getattr(owner, 'profession', 'Null') if owner else 'Null',
                'owner_code': getattr(owner, 'code_client', '') if owner else '',
            }
            
        except Exception as e:
            print(f"Erreur _get_complete_vehicle_data: {e}")
            return None
    
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