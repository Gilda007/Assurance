# fleet_batch_print_manager.py
"""
Gestionnaire d'impression groupée pour les flottes
Génère directement les rapports PDF sans dialogue de sélection
"""

from PySide6.QtCore import QObject, Signal, QTimer, Qt
from PySide6.QtWidgets import QApplication, QProgressDialog, QMessageBox
import os
import tempfile
import subprocess
import platform


class FleetBatchPrintManager(QObject):
    """Gestionnaire d'impression groupée pour les flottes"""
    
    progress = Signal(int, int, str)
    finished = Signal(bool, str)
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.fleets_queue = []
        self.current_index = 0
        self.total_items = 0
        self.success_count = 0
        self.error_count = 0
        self.is_running = False
        self.is_cancelled = False
        self.progress_dialog = None
    
    def start_batch_print(self, fleets_data):
        """Démarre l'impression groupée des flottes (sans choix de document)"""
        if self.is_running:
            return
        
        self.fleets_queue = fleets_data
        self.total_items = len(self.fleets_queue)
        self.current_index = 0
        self.success_count = 0
        self.error_count = 0
        self.is_running = True
        self.is_cancelled = False
        
        # Créer la boîte de progression
        self.progress_dialog = QProgressDialog(
            "Préparation de l'impression des rapports de flotte...",
            "Annuler",
            0,
            self.total_items,
            self.parent
        )
        self.progress_dialog.setWindowTitle("Impression groupée - Flottes")
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
                    stop:0 #8b5cf6, stop:1 #c084fc);
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
        
        fleet = self.fleets_queue[self.current_index]
        
        # Mettre à jour la progression
        self.progress_dialog.setValue(self.current_index)
        self.progress_dialog.setLabelText(
            f"Génération du rapport pour la flotte {fleet.get('nom', 'flotte')}..."
        )
        
        QApplication.processEvents()
        
        # Exécuter l'impression du rapport
        try:
            success = self._print_fleet_report(fleet.get('id'), fleet.get('nom', 'flotte'))
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
        except Exception as e:
            print(f"Erreur impression rapport flotte: {e}")
            self.error_count += 1
        
        self.current_index += 1
        
        # Programmer l'impression suivante
        QTimer.singleShot(500, self._print_next)
    
    def _print_fleet_report(self, fleet_id, fleet_name):
        """Génère et ouvre le rapport PDF d'une flotte"""
        try:
            # Créer un fichier temporaire pour le PDF
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            
            # Générer le PDF via le contrôleur
            success, message = self.controller.fleets.generate_fleet_pdf(fleet_id, temp_file.name)
            
            if success and os.path.exists(temp_file.name):
                # Ouvrir le PDF avec l'application par défaut
                if platform.system() == 'Windows':
                    os.startfile(temp_file.name)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', temp_file.name])
                else:  # Linux
                    subprocess.run(['xdg-open', temp_file.name])
                
                print(f"✅ Rapport généré pour la flotte {fleet_name}")
                return True
            else:
                print(f"❌ Erreur génération rapport pour {fleet_name}: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'impression de la flotte {fleet_name}: {e}")
            return False
    
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
                f"✅ {self.success_count} rapport(s) de flotte généré(s) avec succès"
            )
        else:
            QMessageBox.warning(
                self.parent, 
                "Impression terminée", 
                f"⚠️ {self.success_count} succès, {self.error_count} erreur(s)"
            )
        
        self.finished.emit(self.error_count == 0, "")