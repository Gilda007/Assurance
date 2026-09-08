

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
# PAGE 5: ÉVALUATIONS
# ============================================================



class EvaluationsPage(QWidget):
    """Page de gestion des évaluations"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.current_sinistre_id = None
        self.selected_evaluation_id = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("💰 Gestion des Évaluations")
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
        
        self.lbl_total = QLabel("Total évalué: 0 FCFA")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 14px;")
        stats_layout.addWidget(self.lbl_total)
        
        stats_layout.addStretch()
        
        self.lbl_validees = QLabel("✅ Validées: 0")
        self.lbl_validees.setStyleSheet("color: #22c55e;")
        stats_layout.addWidget(self.lbl_validees)
        
        self.lbl_non_validees = QLabel("❌ Non validées: 0")
        self.lbl_non_validees.setStyleSheet("color: #ef4444;")
        stats_layout.addWidget(self.lbl_non_validees)
        
        layout.addWidget(stats_frame)
        
        # Sous-onglets
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 0 0 8px 8px;
            }
            QTabBar::tab {
                padding: 8px 15px;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1a73e8;
            }
        """)
        
        # Onglet Évaluations
        eval_tab = QWidget()
        eval_layout = QVBoxLayout(eval_tab)
        
        self.table_evaluations = QTableWidget()
        self.table_evaluations.setColumnCount(7)
        self.table_evaluations.setHorizontalHeaderLabels([
            "N°", "Type", "Brut", "Franchise", "Taux", "Net", "Validée"
        ])
        self.table_evaluations.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_evaluations.setAlternatingRowColors(True)
        self.table_evaluations.setStyleSheet("""
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
        self.table_evaluations.doubleClicked.connect(self._on_evaluation_double_clicked)
        eval_layout.addWidget(self.table_evaluations)
        
        eval_btn_layout = QHBoxLayout()
        self.btn_creer_eval = QPushButton("➕ Nouvelle évaluation")
        self.btn_creer_eval.setStyleSheet("""
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
        self.btn_creer_eval.clicked.connect(self.creer_evaluation)
        eval_btn_layout.addWidget(self.btn_creer_eval)
        
        eval_btn_layout.addStretch()
        eval_layout.addLayout(eval_btn_layout)

        eval_btn_layout = QHBoxLayout()
        
        # ✅ AJOUTER LE BOUTON RÉVISER
        self.btn_reviser_eval = QPushButton("✏️ Réviser")
        self.btn_reviser_eval.setStyleSheet("""
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
        self.btn_reviser_eval.clicked.connect(self.reviser_evaluation)
        eval_btn_layout.addWidget(self.btn_reviser_eval)
        
        # ✅ AJOUTER LE BOUTON VALIDER
        self.btn_valider_eval = QPushButton("✅ Valider")
        self.btn_valider_eval.setStyleSheet("""
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
        self.btn_valider_eval.clicked.connect(self.valider_evaluation)
        eval_btn_layout.addWidget(self.btn_valider_eval)
        
        eval_btn_layout.addStretch()
        eval_layout.addLayout(eval_btn_layout)
        
        self.sub_tabs.addTab(eval_tab, "📊 Évaluations")
        
        # Onglet Provisions
        prov_tab = QWidget()
        prov_layout = QVBoxLayout(prov_tab)
        
        self.table_provisions = QTableWidget()
        self.table_provisions.setColumnCount(5)
        self.table_provisions.setHorizontalHeaderLabels([
            "N° Provision", "Type", "Montant", "Active", "Comptabilisée"
        ])
        self.table_provisions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_provisions.setAlternatingRowColors(True)
        self.table_provisions.setStyleSheet("""
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
        prov_layout.addWidget(self.table_provisions)
        
        self.sub_tabs.addTab(prov_tab, "📦 Provisions")
        
        layout.addWidget(self.sub_tabs)
    
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
                self.load_evaluations(sinistre_id)
                self.load_provisions(sinistre_id)
    
    def load_evaluations(self, sinistre_id: int):
        """Charge les évaluations d'un sinistre"""
        try:
            evaluations = self.controller.get_evaluations_by_sinistre(sinistre_id)
            self.table_evaluations.setRowCount(len(evaluations))
            
            total = 0
            validees = 0
            
            for i, eval_ in enumerate(evaluations):
                self.table_evaluations.setItem(i, 0, QTableWidgetItem(eval_.get('numero_evaluation', '')))
                self.table_evaluations.setItem(i, 1, QTableWidgetItem(eval_.get('type_evaluation', '')))
                self.table_evaluations.setItem(i, 2, QTableWidgetItem(f"{eval_.get('montant_brut', 0):,.0f}"))
                self.table_evaluations.setItem(i, 3, QTableWidgetItem(f"{eval_.get('franchise', 0):,.0f}"))
                self.table_evaluations.setItem(i, 4, QTableWidgetItem(f"{eval_.get('taux_responsabilite', 1) * 100:.0f}%"))
                
                montant_net = eval_.get('montant_net', 0)
                total += montant_net
                if eval_.get('est_validee'):
                    validees += 1
                
                self.table_evaluations.setItem(i, 5, QTableWidgetItem(f"{montant_net:,.0f}"))
                
                validee_item = QTableWidgetItem("✅" if eval_.get('est_validee') else "❌")
                validee_item.setForeground(QColor("#22c55e" if eval_.get('est_validee') else "#ef4444"))
                self.table_evaluations.setItem(i, 6, validee_item)
            
            self.lbl_total.setText(f"Total évalué: {total:,.0f} FCFA")
            self.lbl_validees.setText(f"✅ Validées: {validees}")
            self.lbl_non_validees.setText(f"❌ Non validées: {len(evaluations) - validees}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement évaluations: {str(e)}")
    
    def load_provisions(self, sinistre_id: int):
        """Charge les provisions d'un sinistre"""
        try:
            provisions = self.controller.get_provisions_by_sinistre(sinistre_id)
            self.table_provisions.setRowCount(len(provisions))
            
            for i, prov in enumerate(provisions):
                self.table_provisions.setItem(i, 0, QTableWidgetItem(prov.get('numero_provision', '')))
                self.table_provisions.setItem(i, 1, QTableWidgetItem(prov.get('type_provision', '')))
                self.table_provisions.setItem(i, 2, QTableWidgetItem(f"{prov.get('montant', 0):,.0f}"))
                
                active_item = QTableWidgetItem("✅" if prov.get('est_active') else "❌")
                active_item.setForeground(QColor("#22c55e" if prov.get('est_active') else "#ef4444"))
                self.table_provisions.setItem(i, 3, active_item)
                
                comptabilisee_item = QTableWidgetItem("✅" if prov.get('est_comptabilisee') else "❌")
                comptabilisee_item.setForeground(QColor("#22c55e" if prov.get('est_comptabilisee') else "#ef4444"))
                self.table_provisions.setItem(i, 4, comptabilisee_item)
                
        except Exception as e:
            print(f"Erreur chargement provisions: {e}")
    
    # def creer_evaluation(self):
    #     """Crée une nouvelle évaluation"""
    #     if not self.current_sinistre_id:
    #         QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
    #         return
    #     QMessageBox.information(self, "Création", "Dialogue de création d'évaluation (à implémenter)")

    def creer_evaluation(self):
        """Crée une nouvelle évaluation"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        # Récupérer les informations du sinistre
        sinistre_info = {}
        try:
            sinistre_data = self.controller.get_sinistre_info(self.current_sinistre_id)
            if sinistre_data:
                sinistre_info = {
                    'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
                    'client_nom': 'N/A',  # À récupérer si disponible
                    'branche': sinistre_data.get('branche', 'N/A')
                }
        except:
            pass
        
        from addons.sinistres.views.evaluation_dialog import EvaluationDialog
        dialog = EvaluationDialog(
            sinistre_id=self.current_sinistre_id,
            evaluation_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            parent=self
        )
        
        dialog.evaluation_created.connect(self._on_evaluation_created)
        dialog.exec()

    def _on_evaluation_created(self, data: dict):
        """Appelé après la création d'une évaluation"""
        self.load_evaluations(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Évaluation créée avec succès !"
        )

    def get_sinistre_info(self, sinistre_id: int) -> dict:
        """Récupère les informations d'un sinistre"""
        try:
            return self.controller.get_sinistre_info(sinistre_id)
        except:
            return {}

    def reviser_evaluation(self):
        """Révisé l'évaluation sélectionnée"""
        row = self.table_evaluations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une évaluation")
            return
        
        # Récupérer les informations de l'évaluation
        eval_numero = self.table_evaluations.item(row, 0).text()
        est_validee = self.table_evaluations.item(row, 6).text() == "✅"
        
        if est_validee:
            QMessageBox.warning(
                self,
                "Attention",
                "Cette évaluation est déjà validée et ne peut plus être révisée.\n"
                "Seules les évaluations non validées peuvent être révisées."
            )
            return
        
        try:
            # Récupérer les données de l'évaluation
            eval_data = self.controller.get_evaluation_by_numero(eval_numero)
            if not eval_data:
                QMessageBox.warning(self, "Erreur", "Évaluation non trouvée")
                return
            
            eval_id = eval_data.get('id')
            eval_info = self.controller.get_evaluation(eval_id)
            
            # Ouvrir le dialogue de révision
            from addons.sinistres.views.reviser_evaluation_dialog import ReviserEvaluationDialog
            dialog = ReviserEvaluationDialog(
                evaluation_id=eval_id,
                evaluation_info=eval_info,
                evaluation_controller=self.controller,
                user=self.user,
                parent=self
            )
            
            dialog.evaluation_revised.connect(self._on_evaluation_revised)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _on_evaluation_revised(self, data: dict):
        """Appelé après la révision d'une évaluation"""
        self.load_evaluations(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Évaluation révisée avec succès !\n"
            f"💰 Nouveau montant: {data.get('nouveau_net', 0):,.0f} FCFA"
        )

    # def _on_evaluation_double_clicked(self, index):
    #     """Affiche l'historique des révisions d'une évaluation"""
    #     row = index.row()
    #     if row < 0:
    #         return
        
    #     eval_numero = self.table_evaluations.item(row, 0).text()
        
    #     try:
    #         eval_data = self.controller.get_evaluation_by_numero(eval_numero)
    #         if not eval_data:
    #             return
            
    #         revisions = self.controller.get_revisions_by_evaluation(eval_data.get('id'))
            
    #         if not revisions:
    #             QMessageBox.information(
    #                 self,
    #                 "Historique",
    #                 f"Aucune révision pour l'évaluation {eval_numero}"
    #             )
    #             return
            
    #         # Afficher l'historique des révisions
    #         self._show_revisions_history(eval_numero, revisions)
            
    #     except Exception as e:
    #         QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _on_evaluation_double_clicked(self, index):
        """Affiche l'historique des révisions"""
        row = index.row()
        if row < 0:
            return
        eval_numero = self.table_evaluations.item(row, 0).text()
        self._show_revisions_history(eval_numero, [])

    def _show_revisions_history(self, eval_numero: str, revisions: List[dict]):
        """Affiche l'historique des révisions"""
        # Créer une boîte de dialogue simple
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Historique des révisions - {eval_numero}")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Date", "Ancien brut", "Nouveau brut", "Ancien net", "Nouveau net"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
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
        
        table.setRowCount(len(revisions))
        for i, rev in enumerate(revisions):
            table.setItem(i, 0, QTableWidgetItem(rev.get('date_revision', '')[:16] if rev.get('date_revision') else ''))
            table.setItem(i, 1, QTableWidgetItem(f"{rev.get('ancien_montant_brut', 0):,.0f}"))
            table.setItem(i, 2, QTableWidgetItem(f"{rev.get('nouveau_montant_brut', 0):,.0f}"))
            table.setItem(i, 3, QTableWidgetItem(f"{rev.get('ancien_montant_net', 0):,.0f}"))
            table.setItem(i, 4, QTableWidgetItem(f"{rev.get('nouveau_montant_net', 0):,.0f}"))
        
        layout.addWidget(table)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)
        
        dialog.exec()

    def _on_evaluation_cell_clicked(self, row: int, col: int):
        """Gère le clic sur une ligne d'évaluation"""
        eval_numero = self.table_evaluations.item(row, 0).text()
        try:
            eval_data = self.controller.get_evaluation_by_numero(eval_numero)
            if eval_data:
                self.selected_evaluation_id = eval_data.get('id')
        except:
            pass
        self.table_evaluations.selectRow(row)

    def get_selected_evaluation_id(self) -> Optional[int]:
        """Retourne l'ID de l'évaluation sélectionnée"""
        row = self.table_evaluations.currentRow()
        if row >= 0:
            eval_numero = self.table_evaluations.item(row, 0).text()
            try:
                eval_data = self.controller.get_evaluation_by_numero(eval_numero)
                if eval_data:
                    return eval_data.get('id')
            except:
                pass
        return None

    def valider_evaluation(self):
        """Valide l'évaluation sélectionnée"""
        row = self.table_evaluations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une évaluation")
            return
        
        eval_numero = self.table_evaluations.item(row, 0).text()
        est_validee = self.table_evaluations.item(row, 6).text() == "✅"
        
        if est_validee:
            QMessageBox.warning(
                self,
                "Attention",
                "Cette évaluation est déjà validée."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous valider l'évaluation {eval_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                eval_data = self.controller.get_evaluation_by_numero(eval_numero)
                if not eval_data:
                    QMessageBox.warning(self, "Erreur", "Évaluation non trouvée")
                    return
                
                result = self.controller.valider_evaluation(eval_data.get('id'))
                if result:
                    QMessageBox.information(self, "Succès", "Évaluation validée avec succès")
                    self.load_evaluations(self.current_sinistre_id)
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
