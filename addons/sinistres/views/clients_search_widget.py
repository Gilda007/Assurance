"""
Widget de recherche de client avec autocomplétion
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QFrame,
    QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QColor
from typing import Dict, List, Optional


class ClientSearchWidget(QWidget):
    """Widget de recherche de client avec autocomplétion"""
    
    client_selected = Signal(dict)  # Émis quand un client est sélectionné
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._current_client = None
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self.setup_ui()
        self._load_initial()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un client (nom, code, téléphone)...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._perform_search)
        search_layout.addWidget(self.search_input)
        
        self.btn_search = QPushButton("Rechercher")
        self.btn_search.setStyleSheet("""
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
        self.btn_search.clicked.connect(self._perform_search)
        search_layout.addWidget(self.btn_search)
        
        layout.addLayout(search_layout)
        
        # Résultats
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 5px;
                max-height: 150px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
        """)
        self.results_list.setMaximumHeight(150)
        self.results_list.itemClicked.connect(self._on_client_selected)
        layout.addWidget(self.results_list)
        
        # Informations client sélectionné
        self.client_info_frame = QFrame()
        self.client_info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #e2e8f0;
            }
            QLabel {
                color: #1e293b;
                font-size: 12px;
            }
            QLabel.title {
                font-weight: bold;
                color: #1a73e8;
                font-size: 14px;
            }
        """)
        self.client_info_frame.hide()
        
        info_layout = QVBoxLayout(self.client_info_frame)
        
        # Nom et code client
        self.lbl_client_name = QLabel("Client non sélectionné")
        self.lbl_client_name.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        info_layout.addWidget(self.lbl_client_name)
        
        # Informations détaillées
        details_layout = QHBoxLayout()
        
        self.lbl_client_code = QLabel("Code: -")
        details_layout.addWidget(self.lbl_client_code)
        
        self.lbl_client_phone = QLabel("📞 -")
        details_layout.addWidget(self.lbl_client_phone)
        
        self.lbl_client_email = QLabel("✉️ -")
        details_layout.addWidget(self.lbl_client_email)
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        # Adresse
        self.lbl_client_address = QLabel("📍 -")
        self.lbl_client_address.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(self.lbl_client_address)
        
        layout.addWidget(self.client_info_frame)
        
        # Connexion des signaux
        self.controller.contacts_loaded.connect(self._on_contacts_loaded)
    
    def _load_initial(self):
        """Charge les premiers contacts"""
        self.controller.rechercher_contacts(limit=20)
    
    def _on_search_text_changed(self, text: str):
        """Déclenche la recherche après un délai"""
        if len(text) >= 2:
            self._search_timer.start(300)  # 300ms de délai
        elif len(text) == 0:
            self._search_timer.start(100)
    
    def _perform_search(self):
        """Exécute la recherche"""
        text = self.search_input.text().strip()
        self.controller.rechercher_contacts(text if text else None)
    
    def _on_contacts_loaded(self, contacts: list):
        """Met à jour la liste des résultats"""
        self.results_list.clear()
        
        if not contacts:
            item = QListWidgetItem("Aucun client trouvé")
            item.setFlags(Qt.NoItemFlags)
            self.results_list.addItem(item)
            return
        
        for contact in contacts:
            display = contact.get('display', f"{contact.get('nom', '')} {contact.get('prenom', '')}")
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, contact)
            self.results_list.addItem(item)
    
    def _on_client_selected(self, item: QListWidgetItem):
        """Sélectionne un client"""
        contact = item.data(Qt.UserRole)
        if contact:
            self._current_client = contact
            self._update_client_info(contact)
            self.client_selected.emit(contact)
    
    def _update_client_info(self, contact: dict):
        """Met à jour l'affichage des informations du client"""
        nom_complet = f"{contact.get('civilite', '')} {contact.get('nom', '')} {contact.get('prenom', '')}".strip()
        self.lbl_client_name.setText(f"👤 {nom_complet}")
        self.lbl_client_code.setText(f"Code: {contact.get('code_client', '-')}")
        self.lbl_client_phone.setText(f"📞 {contact.get('telephone', '-') or contact.get('tel_portable', '-')}")
        self.lbl_client_email.setText(f"✉️ {contact.get('email', '-')}")
        
        adresse = contact.get('adresse', '')
        ville = contact.get('ville', '')
        adresse_complete = f"{adresse}, {ville}" if adresse and ville else adresse or ville or '-'
        self.lbl_client_address.setText(f"📍 {adresse_complete}")
        
        self.client_info_frame.show()
    
    def get_selected_client(self) -> Optional[dict]:
        """Retourne le client sélectionné"""
        return self._current_client
    
    def get_selected_client_id(self) -> Optional[int]:
        """Retourne l'ID du client sélectionné"""
        return self._current_client.get('id') if self._current_client else None
    
    def clear_selection(self):
        """Efface la sélection"""
        self._current_client = None
        self.client_info_frame.hide()
        self.search_input.clear()
        self.results_list.clear()