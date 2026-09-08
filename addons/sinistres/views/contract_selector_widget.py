"""
Widget de sélection de contrat pour un client
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QPushButton, QFrame, QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, Slot
from typing import Dict, List, Optional


class ContractSelectorWidget(QWidget):
    """Widget de sélection de contrat"""
    
    contract_selected = Signal(dict)  # Émis quand un contrat est sélectionné
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._current_client_id = None
        self._current_contract = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Groupe de sélection
        group = QGroupBox("Contrat")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        group_layout = QVBoxLayout(group)
        
        # Sélecteur de contrat
        select_layout = QHBoxLayout()
        select_layout.setSpacing(10)
        
        self.contract_combo = QComboBox()
        self.contract_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #1a73e8;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.contract_combo.currentIndexChanged.connect(self._on_contract_changed)
        select_layout.addWidget(self.contract_combo)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(35, 35)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                border-radius: 17px;
                border: 1px solid #e2e8f0;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.btn_refresh.clicked.connect(self._refresh_contrats)
        select_layout.addWidget(self.btn_refresh)
        
        group_layout.addLayout(select_layout)
        
        # Informations du contrat
        self.contract_info_frame = QFrame()
        self.contract_info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 6px;
                padding: 8px;
                margin-top: 5px;
            }
            QLabel {
                color: #1e293b;
                font-size: 11px;
            }
        """)
        contract_info_layout = QVBoxLayout(self.contract_info_frame)
        
        self.lbl_contract_details = QLabel("Aucun contrat sélectionné")
        self.lbl_contract_details.setStyleSheet("color: #64748b; font-size: 12px;")
        contract_info_layout.addWidget(self.lbl_contract_details)
        
        # Détails supplémentaires
        details_layout = QHBoxLayout()
        
        self.lbl_contract_status = QLabel("Statut: -")
        details_layout.addWidget(self.lbl_contract_status)
        
        self.lbl_contract_dates = QLabel("Période: -")
        details_layout.addWidget(self.lbl_contract_dates)
        
        self.lbl_contract_prime = QLabel("Prime: -")
        details_layout.addWidget(self.lbl_contract_prime)
        
        details_layout.addStretch()
        contract_info_layout.addLayout(details_layout)
        
        group_layout.addWidget(self.contract_info_frame)
        
        layout.addWidget(group)
    
    def set_client(self, client_id: int):
        """Définit le client et charge ses contrats"""
        self._current_client_id = client_id
        self._refresh_contrats()
    
    # def _refresh_contrats(self):
    #     """Rafraîchit la liste des contrats"""
    #     if not self._current_client_id:
    #         self.contract_combo.clear()
    #         self.contract_combo.addItem("Sélectionnez d'abord un client")
    #         self.contract_combo.setEnabled(False)
    #         return
        
    #     self.contract_combo.setEnabled(True)
    #     self.contract_combo.clear()
    #     self.contract_combo.addItem("-- Sélectionner un contrat --", None)
        
    #     try:
    #         contrats = self.controller.get_contrats_by_client(self._current_client_id)
    #         print(f"Voici les contrats récupérés pour le client {self._current_client_id}: {contrats}")
    #         if not contrats:
    #             self.contract_combo.addItem("Aucun contrat trouvé", None)
    #             return
            
    #         for c in contrats:
    #             display = c.get('display', c.get('numero_police', 'Contrat'))
    #             self.contract_combo.addItem(display, c)
            
    #     except Exception as e:
    #         QMessageBox.critical(self, "Erreur", f"Erreur chargement contrats: {str(e)}")
    
    def _refresh_contrats(self):
        """Rafraîchit la liste des contrats"""
        print(f"🔍 _refresh_contrats: client_id={self._current_client_id}")
        
        if not self._current_client_id:
            self.contract_combo.clear()
            self.contract_combo.addItem("Sélectionnez d'abord un client")
            self.contract_combo.setEnabled(False)
            return
        
        self.contract_combo.setEnabled(True)
        self.contract_combo.clear()
        self.contract_combo.addItem("-- Sélectionner un contrat --", None)
        
        try:
            contrats = self.controller.get_contrats_by_client(self._current_client_id)
            print(f"📊 Contrats reçus dans le widget: {len(contrats) if contrats else 0}")
            
            if not contrats:
                self.contract_combo.addItem("Aucun contrat trouvé", None)
                return
            
            for c in contrats:
                display = c.get('display', c.get('numero_police', 'Contrat'))
                print(f"  - Ajout: {display}")
                self.contract_combo.addItem(display, c)
            
            print(f"✅ {self.contract_combo.count()} items dans le combo")
            
        except Exception as e:
            print(f"❌ Erreur chargement contrats: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur chargement contrats: {str(e)}")

    def _on_contract_changed(self, index: int):
        """Gère le changement de contrat sélectionné"""
        if index < 0:
            return
        
        contract = self.contract_combo.currentData()
        if contract:
            self._current_contract = contract
            self._update_contract_info(contract)
            self.contract_selected.emit(contract)
        else:
            self._current_contract = None
            self.lbl_contract_details.setText("Aucun contrat sélectionné")
            self.lbl_contract_status.setText("Statut: -")
            self.lbl_contract_dates.setText("Période: -")
            self.lbl_contract_prime.setText("Prime: -")
    
    def _update_contract_info(self, contract: dict):
        """Met à jour l'affichage des informations du contrat"""
        police = contract.get('numero_police', 'N/A')
        statut = contract.get('statut', 'N/A')
        date_debut = contract.get('date_debut', '')
        date_fin = contract.get('date_fin', '')
        prime = contract.get('prime_totale_ttc', 0)
        
        self.lbl_contract_details.setText(f"📄 Contrat: {police}")
        self.lbl_contract_status.setText(f"Statut: {statut.upper()}")
        
        periode = f"{date_debut[:10] if date_debut else '--'} → {date_fin[:10] if date_fin else '--'}"
        self.lbl_contract_dates.setText(f"Période: {periode}")
        self.lbl_contract_prime.setText(f"Prime: {prime:,.0f} FCFA")
    
    def get_selected_contract(self) -> Optional[dict]:
        """Retourne le contrat sélectionné"""
        return self._current_contract
    
    def get_selected_contract_id(self) -> Optional[int]:
        """Retourne l'ID du contrat sélectionné"""
        return self._current_contract.get('id') if self._current_contract else None
    
    def clear_selection(self):
        """Efface la sélection"""
        self._current_client_id = None
        self._current_contract = None
        self.contract_combo.clear()
        self.contract_combo.addItem("Sélectionnez d'abord un client")
        self.contract_combo.setEnabled(False)
        self.lbl_contract_details.setText("Aucun contrat sélectionné")
        self.lbl_contract_status.setText("Statut: -")
        self.lbl_contract_dates.setText("Période: -")
        self.lbl_contract_prime.setText("Prime: -")