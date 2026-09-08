

"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des sinistres
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
    QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
    QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
from PySide6.QtGui import QColor, QIcon, QFont

from datetime import datetime, timedelta
from typing import Optional, List


# ============================================================
# PAGE 7: RECOURS
# ============================================================

class RecoursPage(QWidget):
    """Page de gestion des recours"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.current_sinistre_id = None
        self.selected_recours_id = None

        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("⚖️ Gestion des Recours")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Sinistre:"))
        self.sinistre_combo = QComboBox()
        self.sinistre_combo.setMinimumWidth(200)
        self.sinistre_combo.currentIndexChanged.connect(self.on_sinistre_changed)
        header_layout.addWidget(self.sinistre_combo)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(35, 35)
        self.btn_refresh.setStyleSheet("border-radius: 17px;")
        self.btn_refresh.clicked.connect(self.load_data)
        header_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(header_layout)
        
        # Statistiques
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.lbl_total = QLabel("Total recours: 0")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1e293b;")
        stats_layout.addWidget(self.lbl_total)
        
        stats_layout.addStretch()
        
        self.lbl_aboutis = QLabel("✅ Aboutis: 0")
        self.lbl_aboutis.setStyleSheet("color: #22c55e;")
        stats_layout.addWidget(self.lbl_aboutis)
        
        self.lbl_encours = QLabel("🟡 En cours: 0")
        self.lbl_encours.setStyleSheet("color: #f59e0b;")
        stats_layout.addWidget(self.lbl_encours)
        
        self.lbl_taux_recup = QLabel("📊 Taux récupération: 0%")
        self.lbl_taux_recup.setStyleSheet("color: #3b82f6;")
        stats_layout.addWidget(self.lbl_taux_recup)
        
        layout.addWidget(stats_frame)
        
        self.table_recours = QTableWidget()
        self.table_recours.setColumnCount(8)  # Augmenter de 7 à 8
        self.table_recours.setHorizontalHeaderLabels([
            "N°", "Débiteur", "Réclamé", "Accepté", "Encaissé", "Solde", "Prochaine relance", "Statut"
        ])
   
        self.table_recours.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recours.setAlternatingRowColors(True)
        self.table_recours.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(self.table_recours)
        
        btn_layout = QHBoxLayout()

        self.btn_creer_rec = QPushButton("➕ Nouveau recours")
        self.btn_creer_rec.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_creer_rec.clicked.connect(self.creer_recours)
        btn_layout.addWidget(self.btn_creer_rec)

        # ✅ AJOUTER LE BOUTON ENCAISSER
        self.btn_encaisser = QPushButton("💰 Encaisser")
        self.btn_encaisser.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.btn_encaisser.clicked.connect(self.encaisser_recours)
        btn_layout.addWidget(self.btn_encaisser)

        # ✅ AJOUTER LE BOUTON RELANCE
        self.btn_relance = QPushButton("🔔 Relancer")
        self.btn_relance.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        self.btn_relance.clicked.connect(self.ajouter_relance)
        btn_layout.addWidget(self.btn_relance)

        # ✅ AJOUTER LE BOUTON PLANIFICATION AUTO
        self.btn_planifier = QPushButton("📅 Planifier relances")
        self.btn_planifier.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.btn_planifier.clicked.connect(self.planifier_relances_auto)
        btn_layout.addWidget(self.btn_planifier)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Charge les sinistres"""
        try:
            self.sinistre_combo.clear()
            sinistres = self.controller.get_sinistres_recents()
            for s in sinistres:
                self.sinistre_combo.addItem(
                    f"{s.get('numero_sinistre')} - {s.get('branche', '')}",
                    s.get('id')
                )
        except Exception as e:
            print(f"Erreur chargement sinistres: {e}")
    
    def on_sinistre_changed(self, index):
        """Charge les données du sinistre sélectionné"""
        if index > 0:
            sinistre_id = self.sinistre_combo.currentData()
            if sinistre_id:
                self.current_sinistre_id = sinistre_id
                self.load_recours(sinistre_id)
    
    # def load_recours(self, sinistre_id: int):
    #     """Charge les recours d'un sinistre"""
    #     try:
    #         recours = self.controller.get_recours_by_sinistre(sinistre_id)
    #         self.table_recours.setRowCount(len(recours))
            
    #         total = len(recours)
    #         aboutis = sum(1 for r in recours if r.get('statut') in ['ABOUTI', 'ENCAISSE', 'PAYE', 'COMPTABILISE', 'CLOTURE'])
    #         encours = total - aboutis
            
    #         total_reclame = sum(r.get('montant_reclame', 0) for r in recours)
    #         total_encaisse = sum(r.get('montant_encaisse', 0) for r in recours)
    #         taux = (total_encaisse / total_reclame * 100) if total_reclame > 0 else 0
            
    #         self.lbl_total.setText(f"Total recours: {total}")
    #         self.lbl_aboutis.setText(f"✅ Aboutis: {aboutis}")
    #         self.lbl_encours.setText(f"🟡 En cours: {encours}")
    #         self.lbl_taux_recup.setText(f"📊 Taux récupération: {taux:.1f}%")
            
    #         statut_colors = {
    #             'OUVERT': '#f59e0b',
    #             'EN_INSTRUCTION': '#3b82f6',
    #             'RELANCE': '#8b5cf6',
    #             'CONTESTE': '#ef4444',
    #             'REFUSE': '#ef4444',
    #             'ABOUTI': '#06b6d4',
    #             'EN_ATTENTE_ENCAISSEMENT': '#f97316',
    #             'PARTIELLEMENT_ENCAISSE': '#f97316',
    #             'ENCAISSE': '#22c55e',
    #             'REVERSEMENT_EN_COURS': '#8b5cf6',
    #             'PAYE': '#22c55e',
    #             'COMPTABILISE': '#22c55e',
    #             'CLOTURE': '#64748b'
    #         }
            
    #         for i, rec in enumerate(recours):
    #             self.table_recours.setItem(i, 0, QTableWidgetItem(rec.get('numero_recours', '')))
    #             self.table_recours.setItem(i, 1, QTableWidgetItem(rec.get('debiteur_nom', '')))
    #             self.table_recours.setItem(i, 2, QTableWidgetItem(f"{rec.get('montant_reclame', 0):,.0f}"))
    #             self.table_recours.setItem(i, 3, QTableWidgetItem(f"{rec.get('montant_accepte', 0):,.0f}" if rec.get('montant_accepte') else '-'))
    #             self.table_recours.setItem(i, 4, QTableWidgetItem(f"{rec.get('montant_encaisse', 0):,.0f}"))
    #             self.table_recours.setItem(i, 5, QTableWidgetItem(f"{rec.get('solde', 0):,.0f}"))
                
    #             statut = rec.get('statut', '')
    #             statut_item = QTableWidgetItem(statut)
    #             color = statut_colors.get(statut, '#64748b')
    #             statut_item.setBackground(QColor(color))
    #             statut_item.setForeground(QColor('white'))
    #             self.table_recours.setItem(i, 6, statut_item)
                
    #     except Exception as e:
    #         QMessageBox.critical(self, "Erreur", f"Erreur chargement recours: {str(e)}")

    def load_recours(self, sinistre_id: int):
        """Charge les recours d'un sinistre"""
        try:
            recours = self.controller.get_recours_by_sinistre(sinistre_id)
            self.table_recours.setRowCount(len(recours))
            
            total = len(recours)
            aboutis = sum(1 for r in recours if r.get('statut') in ['ABOUTI', 'ENCAISSE', 'PAYE', 'COMPTABILISE', 'CLOTURE'])
            encours = total - aboutis
            
            total_reclame = sum(r.get('montant_reclame', 0) for r in recours)
            total_encaisse = sum(r.get('montant_encaisse', 0) for r in recours)
            taux = (total_encaisse / total_reclame * 100) if total_reclame > 0 else 0
            
            self.lbl_total.setText(f"Total recours: {total}")
            self.lbl_aboutis.setText(f"✅ Aboutis: {aboutis}")
            self.lbl_encours.setText(f"🟡 En cours: {encours}")
            self.lbl_taux_recup.setText(f"📊 Taux récupération: {taux:.1f}%")
            
            statut_colors = {
                'OUVERT': '#f59e0b',
                'EN_INSTRUCTION': '#3b82f6',
                'RELANCE': '#8b5cf6',
                'CONTESTE': '#ef4444',
                'REFUSE': '#ef4444',
                'ABOUTI': '#06b6d4',
                'EN_ATTENTE_ENCAISSEMENT': '#f97316',
                'PARTIELLEMENT_ENCAISSE': '#f97316',
                'ENCAISSE': '#22c55e',
                'REVERSEMENT_EN_COURS': '#8b5cf6',
                'PAYE': '#22c55e',
                'COMPTABILISE': '#22c55e',
                'CLOTURE': '#64748b'
            }
            
            for i, rec in enumerate(recours):
                self.table_recours.setItem(i, 0, QTableWidgetItem(rec.get('numero_recours', '')))
                self.table_recours.setItem(i, 1, QTableWidgetItem(rec.get('debiteur_nom', '')))
                self.table_recours.setItem(i, 2, QTableWidgetItem(f"{rec.get('montant_reclame', 0):,.0f}"))
                self.table_recours.setItem(i, 3, QTableWidgetItem(f"{rec.get('montant_accepte', 0):,.0f}" if rec.get('montant_accepte') else '-'))
                self.table_recours.setItem(i, 4, QTableWidgetItem(f"{rec.get('montant_encaisse', 0):,.0f}"))
                self.table_recours.setItem(i, 5, QTableWidgetItem(f"{rec.get('solde', 0):,.0f}"))
                
                # ✅ Ajouter la date de prochaine relance
                prochaine = rec.get('date_prochaine_relance', '')
                if prochaine:
                    date_obj = datetime.fromisoformat(prochaine[:10])
                    if date_obj.date() <= datetime.now().date():
                        prochaine_display = f"⚠️ {prochaine[:10]}"
                    else:
                        prochaine_display = prochaine[:10]
                else:
                    prochaine_display = "-"
                self.table_recours.setItem(i, 6, QTableWidgetItem(prochaine_display))
                
                statut = rec.get('statut', '')
                statut_item = QTableWidgetItem(statut)
                color = statut_colors.get(statut, '#64748b')
                statut_item.setBackground(QColor(color))
                statut_item.setForeground(QColor('white'))
                self.table_recours.setItem(i, 7, statut_item)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement recours: {str(e)}")

    def creer_recours(self):
        """Crée un nouveau recours"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        # Récupérer les informations du sinistre
        sinistre_info = {}
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.user)
            sinistre_data = sc.get_sinistre(self.current_sinistre_id)
            if sinistre_data:
                # Récupérer le montant total réglé
                montant_regle = 0
                reglements = self.controller.get_reglements_by_sinistre(self.current_sinistre_id)
                for reg in reglements:
                    if reg.get('statut') == 'PAYE':
                        montant_regle += reg.get('montant', 0)
                
                sinistre_info = {
                    'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
                    'client_nom': 'N/A',
                    'branche': sinistre_data.get('branche', 'N/A'),
                    'montant_regle': montant_regle
                }
        except:
            pass
        
        from addons.sinistres.views.recours_dialog import RecoursDialog
        dialog = RecoursDialog(
            sinistre_id=self.current_sinistre_id,
            recours_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            parent=self
        )
        
        dialog.recours_created.connect(self._on_recours_created)
        dialog.exec()

    def _on_recours_created(self, data: dict):
        """Appelé après la création d'un recours"""
        self.load_recours(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Recours créé avec succès !"
        )

    def get_reglements_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère les règlements d'un sinistre"""
        try:
            from addons.sinistres.controllers.reglement_controller import ReglementController
            rc = ReglementController()
            rc.set_current_user(self.user)
            return rc.get_reglements_by_sinistre(sinistre_id)
        except Exception as e:
            print(f"Erreur chargement règlements: {e}")
            return []

    def encaisser_recours(self):
        """Enregistre un encaissement pour le recours sélectionné"""
        row = self.table_recours.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
            return
        
        recours_numero = self.table_recours.item(row, 0).text()
        statut = self.table_recours.item(row, 6).text()
        
        # Vérifier que le recours peut être encaissé
        if statut not in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
            QMessageBox.warning(
                self,
                "Attention",
                f"Seul un recours en attente d'encaissement peut être encaissé (statut: {statut})"
            )
            return
        
        try:
            recours_data = self.controller.get_recours_by_numero(recours_numero)
            if not recours_data:
                QMessageBox.warning(self, "Erreur", "Recours non trouvé")
                return
            
            recours_id = recours_data.get('id')
            recours_info = self.controller.get_recours(recours_id)
            
            from addons.sinistres.views.encaissement_dialog import EncaissementDialog
            dialog = EncaissementDialog(
                recours_id=recours_id,
                recours_info=recours_info,
                recours_controller=self.controller,
                user=self.user,
                parent=self
            )
            
            dialog.encaissement_added.connect(self._on_encaissement_added)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _on_encaissement_added(self, data: dict):
        """Appelé après un encaissement"""
        self.load_recours(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Encaissement de {data.get('montant', 0):,.0f} FCFA enregistré !\n"
            f"📊 Solde restant: {data.get('solde_restant', 0):,.0f} FCFA"
        )

    def ajouter_relance(self):
        """Ajoute une relance au recours sélectionné"""
        row = self.table_recours.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
            return
        
        recours_numero = self.table_recours.item(row, 0).text()
        
        # TODO: Ouvrir dialogue de relance
        QMessageBox.information(
            self,
            "Relance",
            f"Dialogue de relance pour le recours {recours_numero}\n(Fonctionnalité à implémenter)"
        )

    def ajouter_relance(self):
        """Ajoute une relance au recours sélectionné"""
        row = self.table_recours.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
            return
        
        recours_numero = self.table_recours.item(row, 0).text()
        
        try:
            recours_data = self.controller.get_recours_by_numero(recours_numero)
            if not recours_data:
                QMessageBox.warning(self, "Erreur", "Recours non trouvé")
                return
            
            recours_id = recours_data.get('id')
            recours_info = self.controller.get_recours(recours_id)
            
            from addons.sinistres.views.relance_dialog import RelanceDialog
            dialog = RelanceDialog(
                recours_id=recours_id,
                recours_info=recours_info,
                recours_controller=self.controller,
                user=self.user,
                parent=self
            )
            
            dialog.relance_added.connect(self._on_relance_added)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _on_relance_added(self, data: dict):
        """Appelé après l'ajout d'une relance"""
        self.load_recours(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Relance ajoutée avec succès !\n"
            f"📅 Prochaine relance: {data.get('prochaine_relance', 'Non planifiée')}"
        )

    def planifier_relances_auto(self):
        """Planifie automatiquement les relances"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous planifier automatiquement les relances pour tous les recours ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.planifier_relances_auto()
                QMessageBox.information(
                    self,
                    "Planification terminée",
                    f"✅ {result.get('planifiees', 0)} relances planifiées\n"
                    f"❌ {result.get('erreurs', 0)} erreurs"
                )
                self.load_recours(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _on_recours_cell_clicked(self, row: int, col: int):
        """Gère le clic sur une ligne de recours"""
        rec_numero = self.table_recours.item(row, 0).text()
        try:
            rec_data = self.controller.get_recours_by_numero(rec_numero)
            if rec_data:
                self.selected_recours_id = rec_data.get('id')
        except:
            pass
        self.table_recours.selectRow(row)

    def get_selected_recours_id(self) -> Optional[int]:
        """Retourne l'ID du recours sélectionné"""
        row = self.table_recours.currentRow()
        if row >= 0:
            rec_numero = self.table_recours.item(row, 0).text()
            try:
                rec_data = self.controller.get_recours_by_numero(rec_numero)
                if rec_data:
                    return rec_data.get('id')
            except:
                pass
        return None

