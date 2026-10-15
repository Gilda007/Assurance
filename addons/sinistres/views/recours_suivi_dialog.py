"""
Dialogue de suivi de l'évolution d'un recours.
Affiche : timeline + détails + onglets (encaissements, répartitions, reversements, relances, écritures)
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QGridLayout, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from addons.sinistres.views.widgets.recours_timeline_widget import RecoursTimelineWidget


class RecoursSuiviDialog(QDialog):
    """Dialogue de suivi complet d'un recours"""
    
    def __init__(self, recours_id, recours_info, recours_controller, comptabilite_controller, user, parent=None):
        super().__init__(parent)
        self.recours_id = recours_id
        self.recours_info = recours_info or {}
        self.recours_controller = recours_controller
        self.comptabilite_controller = comptabilite_controller
        self.user = user
        
        self.setWindowTitle(f"Suivi du recours {self.recours_info.get('numero_recours', 'N/A')}")
        self.setModal(True)
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ============================================================
        # EN-TÊTE
        # ============================================================
        layout.addWidget(self._make_header())
        
        # ============================================================
        # KPI CARDS
        # ============================================================
        layout.addWidget(self._make_kpi_row())
        
        # ============================================================
        # ONGLETS
        # ============================================================
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 2px;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                font-weight: 500;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1a73e8;
                color: #1a73e8;
            }
            QTabBar::tab:hover { background-color: #f1f5f9; }
        """)
        
        # Onglet 1 : Timeline
        self.timeline_widget = RecoursTimelineWidget()
        self.tabs.addTab(self.timeline_widget, "📅 Timeline")
        
        # Onglet 2 : Encaissements
        self.tabs.addTab(self._make_tab_encaissements(), "💰 Encaissements")
        
        # Onglet 3 : Répartitions
        self.tabs.addTab(self._make_tab_repartitions(), "📊 Répartitions")
        
        # Onglet 4 : Reversements
        self.tabs.addTab(self._make_tab_reversements(), "💸 Reversements")
        
        # Onglet 5 : Relances
        self.tabs.addTab(self._make_tab_relances(), "🔔 Relances")
        
        # Onglet 6 : Écritures comptables
        self.tabs.addTab(self._make_tab_ecritures(), "📒 Écritures")
        
        layout.addWidget(self.tabs, 1)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_close = QPushButton("Fermer")
        btn_close.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
                background-color: #f1f5f9;
                color: #64748b;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    # ============================================================
    # EN-TÊTE
    # ============================================================
    
    def _make_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 14px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        # Icône
        icon = QLabel("⚖️")
        icon.setStyleSheet("font-size: 28px;")
        header_layout.addWidget(icon)
        
        # Infos
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        title = QLabel(f"Recours {self.recours_info.get('numero_recours', 'N/A')}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        info_layout.addWidget(title)
        
        debiteur = self.recours_info.get('debiteur_nom', 'N/A')
        type_rec = self.recours_info.get('type_recours', 'N/A')
        info_layout.addWidget(QLabel(f"👤 Débiteur: {debiteur} | 📌 Type: {type_rec}"))
        
        header_layout.addLayout(info_layout, 1)
        
        # Statut
        statut = self.recours_info.get('statut', 'OUVERT')
        statut_colors = {
            'OUVERT': '#f59e0b', 'EN_INSTRUCTION': '#3b82f6', 'RELANCE': '#8b5cf6',
            'ABOUTI': '#06b6d4', 'EN_ATTENTE_ENCAISSEMENT': '#f97316',
            'PARTIELLEMENT_ENCAISSE': '#f97316', 'ENCAISSE': '#22c55e',
            'REVERSEMENT_EN_COURS': '#8b5cf6', 'PAYE': '#22c55e',
            'COMPTABILISE': '#22c55e', 'CLOTURE': '#64748b',
        }
        statut_color = statut_colors.get(statut, '#64748b')
        statut_lbl = QLabel(statut)
        statut_lbl.setStyleSheet(f"""
            background-color: {statut_color};
            color: white;
            padding: 6px 16px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 11px;
        """)
        statut_lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(statut_lbl)
        
        return header
    
    # ============================================================
    # KPI
    # ============================================================
    
    def _make_kpi_row(self) -> QFrame:
        container = QFrame()
        container.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # KPI 1 : Montant réclamé
        self.kpi_reclame = self._make_kpi(
            "💰 Montant réclamé",
            f"{float(self.recours_info.get('montant_reclame', 0) or 0):,.0f}",
            "#1a73e8"
        )
        layout.addWidget(self.kpi_reclame)
        
        # KPI 2 : Montant accepté
        self.kpi_accepte = self._make_kpi(
            "✅ Montant accepté",
            f"{float(self.recours_info.get('montant_accepte', 0) or 0):,.0f}",
            "#22c55e"
        )
        layout.addWidget(self.kpi_accepte)
        
        # KPI 3 : Montant encaissé
        self.kpi_encaisse = self._make_kpi(
            "💵 Montant encaissé",
            f"{float(self.recours_info.get('montant_encaisse', 0) or 0):,.0f}",
            "#06b6d4"
        )
        layout.addWidget(self.kpi_encaisse)
        
        # KPI 4 : Solde
        solde = float(self.recours_info.get('solde', 0) or 0)
        self.kpi_solde = self._make_kpi(
            "📊 Solde restant",
            f"{solde:,.0f}",
            "#f59e0b" if solde > 0 else "#22c55e"
        )
        layout.addWidget(self.kpi_solde)
        
        return container
    
    def _make_kpi(self, label: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
        """)
        card.setMinimumHeight(70)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600;")
        layout.addWidget(lbl)
        
        val = QLabel(f"{value} FCFA")
        val.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")
        layout.addWidget(val)
        
        return card
    
    # ============================================================
    # ONGLETS
    # ============================================================
    
    def _make_tab_encaissements(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.table_encaissements = QTableWidget()
        self.table_encaissements.setColumnCount(6)
        self.table_encaissements.setHorizontalHeaderLabels([
            "Date", "Montant", "Mode", "Référence", "Partiel", "Solde après"
        ])
        self.table_encaissements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_encaissements.setAlternatingRowColors(True)
        self.table_encaissements.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_encaissements.verticalHeader().setVisible(False)
        self.table_encaissements.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        layout.addWidget(self.table_encaissements)
        return widget
    
    def _make_tab_repartitions(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.table_repartitions = QTableWidget()
        self.table_repartitions.setColumnCount(5)
        self.table_repartitions.setHorizontalHeaderLabels([
            "Type bénéficiaire", "Quote-part (%)", "Montant", "Reversé", "Date reversement"
        ])
        self.table_repartitions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_repartitions.setAlternatingRowColors(True)
        self.table_repartitions.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_repartitions.verticalHeader().setVisible(False)
        self.table_repartitions.setStyleSheet(self.table_encaissements.styleSheet())
        
        layout.addWidget(self.table_repartitions)
        return widget
    
    def _make_tab_reversements(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.table_reversements = QTableWidget()
        self.table_reversements.setColumnCount(6)
        self.table_reversements.setHorizontalHeaderLabels([
            "Date", "Bénéficiaire", "Montant", "Quote-part", "Mode", "Statut"
        ])
        self.table_reversements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_reversements.setAlternatingRowColors(True)
        self.table_reversements.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_reversements.verticalHeader().setVisible(False)
        self.table_reversements.setStyleSheet(self.table_encaissements.styleSheet())
        
        layout.addWidget(self.table_reversements)
        return widget
    
    def _make_tab_relances(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.table_relances = QTableWidget()
        self.table_relances.setColumnCount(5)
        self.table_relances.setHorizontalHeaderLabels([
            "Date", "Type", "Contenu", "Réponse reçue", "Prochaine relance"
        ])
        self.table_relances.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_relances.setAlternatingRowColors(True)
        self.table_relances.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_relances.verticalHeader().setVisible(False)
        self.table_relances.setStyleSheet(self.table_encaissements.styleSheet())
        
        layout.addWidget(self.table_relances)
        return widget
    
    def _make_tab_ecritures(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.table_ecritures = QTableWidget()
        self.table_ecritures.setColumnCount(6)
        self.table_ecritures.setHorizontalHeaderLabels([
            "N° écriture", "Date", "Journal", "Libellé", "Débit / Crédit", "Montant"
        ])
        self.table_ecritures.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_ecritures.setAlternatingRowColors(True)
        self.table_ecritures.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_ecritures.verticalHeader().setVisible(False)
        self.table_ecritures.setStyleSheet(self.table_encaissements.styleSheet())
        
        layout.addWidget(self.table_ecritures)
        return widget
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def charger_donnees(self):
        """Charge toutes les données de suivi"""
        try:
            # 1. Timeline
            historique = self.recours_controller.get_historique_recours(self.recours_id)
            self.timeline_widget.set_evenements(historique)
            
            # 2. Encaissements
            self._charger_encaissements()
            
            # 3. Répartitions
            self._charger_repartitions()
            
            # 4. Reversements
            self._charger_reversements()
            
            # 5. Relances
            self._charger_relances()
            
            # 6. Écritures comptables
            self._charger_ecritures()
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement : {e}")
    
    def _charger_encaissements(self):
        """Charge les encaissements"""
        try:
            encaissements = self.recours_controller.get_encaissements(self.recours_id)
            self.table_encaissements.setRowCount(len(encaissements))
            
            for i, e in enumerate(encaissements):
                date = e.get('date_encaissement', '')[:16].replace('T', ' ') if e.get('date_encaissement') else '—'
                self.table_encaissements.setItem(i, 0, QTableWidgetItem(date))
                self.table_encaissements.setItem(i, 1, QTableWidgetItem(f"{float(e.get('montant', 0)):,.0f}"))
                self.table_encaissements.setItem(i, 2, QTableWidgetItem(e.get('mode_encaissement', '')))
                self.table_encaissements.setItem(i, 3, QTableWidgetItem(e.get('reference_bancaire', '') or '—'))
                
                partiel_item = QTableWidgetItem("✅ Partiel" if e.get('est_partiel') else "Complet")
                self.table_encaissements.setItem(i, 4, partiel_item)
                
                self.table_encaissements.setItem(i, 5, QTableWidgetItem(f"{float(e.get('solde_apres_encaissement', 0)):,.0f}"))
        except Exception as ex:
            print(f"⚠️ Erreur encaissements: {ex}")
    
    def _charger_repartitions(self):
        """Charge les répartitions"""
        try:
            repartitions = self.recours_controller.get_repartitions(self.recours_id)
            self.table_repartitions.setRowCount(len(repartitions))
            
            for i, r in enumerate(repartitions):
                self.table_repartitions.setItem(i, 0, QTableWidgetItem(r.get('type_beneficiaire', '')))
                self.table_repartitions.setItem(i, 1, QTableWidgetItem(f"{r.get('quote_part', 0)}%"))
                self.table_repartitions.setItem(i, 2, QTableWidgetItem(f"{float(r.get('montant', 0)):,.0f}"))
                
                reverse_item = QTableWidgetItem("✅ Oui" if r.get('est_reverse') else "⏳ Non")
                self.table_repartitions.setItem(i, 3, reverse_item)
                
                date_rev = r.get('date_reversement', '')
                if date_rev:
                    date_rev = date_rev[:16].replace('T', ' ')
                else:
                    date_rev = '—'
                self.table_repartitions.setItem(i, 4, QTableWidgetItem(date_rev))
        except Exception as ex:
            print(f"⚠️ Erreur répartitions: {ex}")
    
    def _charger_reversements(self):
        """Charge les reversements"""
        try:
            reversements = self.recours_controller.get_reversements_by_recours(self.recours_id)
            self.table_reversements.setRowCount(len(reversements))
            
            for i, r in enumerate(reversements):
                date = r.get('date_reversement', '')[:16].replace('T', ' ') if r.get('date_reversement') else '—'
                self.table_reversements.setItem(i, 0, QTableWidgetItem(date))
                self.table_reversements.setItem(i, 1, QTableWidgetItem(r.get('beneficiaire_nom', '')))
                self.table_reversements.setItem(i, 2, QTableWidgetItem(f"{float(r.get('montant', 0)):,.0f}"))
                self.table_reversements.setItem(i, 3, QTableWidgetItem(f"{r.get('quote_part', 0)}%"))
                self.table_reversements.setItem(i, 4, QTableWidgetItem(r.get('mode_paiement', '')))
                
                statut_item = QTableWidgetItem("✅ Payé" if r.get('est_paye') else "⏳ En attente")
                statut_item.setForeground(QColor("#22c55e" if r.get('est_paye') else "#f59e0b"))
                self.table_reversements.setItem(i, 5, statut_item)
        except Exception as ex:
            print(f"⚠️ Erreur reversements: {ex}")
    
    def _charger_relances(self):
        """Charge les relances"""
        try:
            relances = self.recours_controller.get_relances(self.recours_id)
            self.table_relances.setRowCount(len(relances))
            
            for i, r in enumerate(relances):
                date = r.get('date_relance', '')[:16].replace('T', ' ') if r.get('date_relance') else '—'
                self.table_relances.setItem(i, 0, QTableWidgetItem(date))
                self.table_relances.setItem(i, 1, QTableWidgetItem(r.get('type_relance', '')))
                self.table_relances.setItem(i, 2, QTableWidgetItem((r.get('contenu') or '')[:80]))
                
                reponse_item = QTableWidgetItem("✅ Oui" if r.get('reponse_recue') else "⏳ Non")
                self.table_relances.setItem(i, 3, reponse_item)
                
                prochaine = r.get('prochaine_relance', '')
                if prochaine:
                    prochaine = prochaine[:10]
                else:
                    prochaine = '—'
                self.table_relances.setItem(i, 4, QTableWidgetItem(prochaine))
        except Exception as ex:
            print(f"⚠️ Erreur relances: {ex}")
    
    def _charger_ecritures(self):
        """Charge les écritures comptables"""
        try:
            ecritures = self.comptabilite_controller.get_ecritures_by_recours(self.recours_id)
            self.table_ecritures.setRowCount(len(ecritures))
            
            for i, e in enumerate(ecritures):
                date = e.get('date_ecriture', '')[:16].replace('T', ' ') if e.get('date_ecriture') else '—'
                self.table_ecritures.setItem(i, 0, QTableWidgetItem(e.get('numero_ecriture', '')))
                self.table_ecritures.setItem(i, 1, QTableWidgetItem(date))
                self.table_ecritures.setItem(i, 2, QTableWidgetItem(e.get('journal', '')))
                self.table_ecritures.setItem(i, 3, QTableWidgetItem(e.get('libelle', '')))
                self.table_ecritures.setItem(i, 4, QTableWidgetItem(f"D:{e.get('compte_debit')} / C:{e.get('compte_credit')}"))
                self.table_ecritures.setItem(i, 5, QTableWidgetItem(f"{float(e.get('montant', 0)):,.0f}"))
        except Exception as ex:
            print(f"⚠️ Erreur écritures: {ex}")