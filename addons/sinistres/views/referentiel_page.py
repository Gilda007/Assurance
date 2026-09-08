

"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des sinistres
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton,
    QListWidget, QFrame, QMessageBox,
    QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
from PySide6.QtGui import QColor, QIcon, QFont

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# ============================================================
# PAGE 8: RÉFÉRENTIELS
# ============================================================

class ReferentielsPage(QWidget):
    """Page de gestion des référentiels"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.selected_referentiel_id = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel("⚙️ Gestion des Référentiels")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # Sélecteur de famille
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Famille:"))
        self.famille_combo = QComboBox()
        self.famille_combo.currentIndexChanged.connect(self.on_famille_changed)
        select_layout.addWidget(self.famille_combo)
        
        select_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(35, 35)
        self.btn_refresh.setStyleSheet("border-radius: 17px;")
        self.btn_refresh.clicked.connect(self.load_data)
        select_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(select_layout)
        
        # Tableau des référentiels
        self.table_referentiels = QTableWidget()
        self.table_referentiels.setColumnCount(5)
        self.table_referentiels.setHorizontalHeaderLabels([
            "Code", "Libellé", "Description", "Valeur", "Actif"
        ])
        self.table_referentiels.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_referentiels.setAlternatingRowColors(True)
        self.table_referentiels.setStyleSheet("""
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
        layout.addWidget(self.table_referentiels)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        self.btn_creer = QPushButton("➕ Ajouter")
        self.btn_creer.setStyleSheet("""
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
        self.btn_creer.clicked.connect(self.ajouter_referentiel)
        btn_layout.addWidget(self.btn_creer)
        
        self.btn_importer = QPushButton("📥 Importer")
        self.btn_importer.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_importer.clicked.connect(self._importer_donnees)
        btn_layout.addWidget(self.btn_importer)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Charge les familles de référentiels"""
        try:
            self.famille_combo.clear()
            familles = [
                "sinistres_types", "circonstances", "responsabilites", "dommages",
                "branches", "garanties", "types_experts", "types_avocats",
                "modes_paiement", "statuts_sinistre", "suites_a_donner"
            ]
            for f in familles:
                self.famille_combo.addItem(f.replace("_", " ").title(), f)
            
            if self.famille_combo.count() > 0:
                self.famille_combo.setCurrentIndex(0)
        except Exception as e:
            print(f"Erreur chargement familles: {e}")
    
    def on_famille_changed(self, index):
        """Charge les référentiels de la famille sélectionnée"""
        if index >= 0:
            famille = self.famille_combo.currentData()
            if famille:
                self.load_referentiels(famille)
    
    def load_referentiels(self, famille: str):
        """Charge les référentiels d'une famille"""
        try:
            referentiels = self.controller.get_referentiels_by_famille(famille)
            self.table_referentiels.setRowCount(len(referentiels))
            
            for i, ref in enumerate(referentiels):
                self.table_referentiels.setItem(i, 0, QTableWidgetItem(ref.get('code', '')))
                self.table_referentiels.setItem(i, 1, QTableWidgetItem(ref.get('libelle', '')))
                self.table_referentiels.setItem(i, 2, QTableWidgetItem(ref.get('description', '')[:50] + ('...' if len(ref.get('description', '')) > 50 else '')))
                self.table_referentiels.setItem(i, 3, QTableWidgetItem(str(ref.get('valeur', '')) if ref.get('valeur') is not None else '-'))
                
                actif_item = QTableWidgetItem("✅" if ref.get('est_actif') else "❌")
                actif_item.setForeground(QColor("#22c55e" if ref.get('est_actif') else "#ef4444"))
                self.table_referentiels.setItem(i, 4, actif_item)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement référentiels: {str(e)}")
    
    def ajouter_referentiel(self):
        """Ajoute un nouveau référentiel"""
        QMessageBox.information(self, "Ajout", "Dialogue d'ajout de référentiel (à implémenter)")
    
    def _importer_donnees(self):
        """Importe les données initiales des référentiels"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous importer les données initiales des référentiels ?\n"
            "Cela créera les données par défaut (types de sinistres, circonstances, etc.)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.init_donnees_initiales()
                QMessageBox.information(
                    self,
                    "Import terminé",
                    f"✅ {result.get('crees', 0)} référentiels créés\n"
                    f"📝 {result.get('mis_a_jour', 0)} mis à jour\n"
                    f"{'⚠️ ' + str(result.get('erreurs', [])) if result.get('erreurs') else ''}"
                )
                self.load_referentiels(self.famille_combo.currentData())
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _on_referentiel_cell_clicked(self, row: int, col: int):
        """Gère le clic sur une ligne de référentiel"""
        referentiel_id = self.table_referentiels.item(row, 0).data(Qt.UserRole)
        if referentiel_id:
            self.selected_referentiel_id = referentiel_id
        self.table_referentiels.selectRow(row)

    def get_selected_referentiel_id(self) -> Optional[int]:
        """Retourne l'ID du référentiel sélectionné"""
        row = self.table_referentiels.currentRow()
        if row >= 0:
            return self.table_referentiels.item(row, 0).data(Qt.UserRole)
        return None
