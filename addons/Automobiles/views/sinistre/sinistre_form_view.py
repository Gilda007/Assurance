# # addons/Automobiles/views/sinistre/sinistre_form_view.py
# """
# Formulaire de création et d'édition d'un sinistre
# """

# from PySide6.QtWidgets import (
#     QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
#     QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QDoubleSpinBox,
#     QGroupBox, QFormLayout, QFrame, QMessageBox, QSpinBox,
#     QCheckBox, QTabWidget, QScrollArea
# )
# from PySide6.QtCore import Qt, QDateTime, Signal
# from PySide6.QtGui import QColor, QFont

# from datetime import datetime

# from addons.Automobiles.views.style import Colors, Fonts, Spacing
# from addons.Automobiles.models.sinistre_models import TypeSinistre, StatutSinistre, Responsabilite


# class SinistreFormView(QDialog):
#     """Formulaire de création/édition d'un sinistre"""
    
#     # Signal émis quand le sinistre est sauvegardé
#     sinistre_saved = Signal(object)  # Sinistre
    
#     def __init__(self, controller, user=None, sinistre=None, parent=None):
#         super().__init__(parent)
#         self.controller = controller
#         self.user = user
#         self.sinistre = sinistre  # None pour création, objet pour édition
#         self.is_edit = sinistre is not None
#         self.setWindowTitle("📋 Déclaration de Sinistre" if not self.is_edit else "✏️ Modification du Sinistre")
#         self.setModal(True)
#         self.setMinimumSize(800, 700)
        
#         self.setup_ui()
#         self.load_data()
    
#     def setup_ui(self):
#         """Configure l'interface du formulaire"""
#         main_layout = QVBoxLayout(self)
#         main_layout.setSpacing(Spacing.LG)
#         main_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        
#         # Titre
#         title = QLabel("📋 Déclaration de Sinistre" if not self.is_edit else "✏️ Modification du Sinistre")
#         title.setStyleSheet(f"""
#             font-size: {Fonts.H2}px;
#             font-weight: {Fonts.BOLD};
#             color: {Colors.TEXT_PRIMARY};
#         """)
#         main_layout.addWidget(title)
        
#         # Onglets
#         self.tabs = QTabWidget()
#         self.tabs.setStyleSheet(f"""
#             QTabWidget::pane {{
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 8px;
#                 background-color: {Colors.WHITE};
#             }}
#             QTabBar::tab {{
#                 padding: 10px 20px;
#                 border-radius: 6px 6px 0 0;
#                 font-weight: {Fonts.MEDIUM};
#             }}
#             QTabBar::tab:selected {{
#                 background-color: {Colors.PRIMARY};
#                 color: white;
#             }}
#             QTabBar::tab:hover:!selected {{
#                 background-color: {Colors.GRAY_100};
#             }}
#         """)
        
#         # Onglet 1 : Informations générales
#         general_tab = self.create_general_tab()
#         self.tabs.addTab(general_tab, "📋 Informations générales")
        
#         # Onglet 2 : Détails du sinistre
#         details_tab = self.create_details_tab()
#         self.tabs.addTab(details_tab, "🔍 Détails")
        
#         # Onglet 3 : Tiers et témoins
#         tiers_tab = self.create_tiers_tab()
#         self.tabs.addTab(tiers_tab, "👤 Tiers et témoins")
        
#         # Onglet 4 : Finances
#         finances_tab = self.create_finances_tab()
#         self.tabs.addTab(finances_tab, "💰 Finances")
        
#         main_layout.addWidget(self.tabs)
        
#         # Boutons
#         buttons = self.create_buttons()
#         main_layout.addWidget(buttons)
    
#     def create_general_tab(self):
#         """Crée l'onglet des informations générales"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(Spacing.MD)
        
#         # Scroll area
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setStyleSheet("border: none; background: transparent;")
        
#         content = QWidget()
#         form_layout = QFormLayout(content)
#         form_layout.setSpacing(Spacing.MD)
#         form_layout.setLabelAlignment(Qt.AlignRight)
        
#         # --- Contrat ---
#         self.contrat_combo = QComboBox()
#         self.contrat_combo.addItem("Sélectionner un contrat...")
#         self.load_contrats()
#         form_layout.addRow("Contrat *:", self.contrat_combo)
        
#         # --- Véhicule ---
#         self.vehicule_combo = QComboBox()
#         self.vehicule_combo.addItem("Sélectionner un véhicule...")
#         self.vehicule_combo.setEnabled(False)
#         form_layout.addRow("Véhicule *:", self.vehicule_combo)
        
#         # --- Client ---
#         self.client_combo = QComboBox()
#         self.client_combo.addItem("Sélectionner un client...")
#         self.load_clients()
#         self.client_combo.currentIndexChanged.connect(self.on_client_changed)
#         form_layout.addRow("Client *:", self.client_combo)
        
#         # --- Type de sinistre ---
#         self.type_combo = QComboBox()
#         self.type_combo.addItem("Sélectionner un type...")
#         for type_ in TypeSinistre:
#             self.type_combo.addItem(self._get_type_label(type_), type_.value)
#         form_layout.addRow("Type *:", self.type_combo)
        
#         # --- Date de survenue ---
#         self.date_survenue = QDateTimeEdit()
#         self.date_survenue.setCalendarPopup(True)
#         self.date_survenue.setDateTime(QDateTime.currentDateTime())
#         self.date_survenue.setDisplayFormat("dd/MM/yyyy HH:mm")
#         form_layout.addRow("Date de survenue *:", self.date_survenue)
        
#         # --- Lieu ---
#         self.lieu_edit = QLineEdit()
#         self.lieu_edit.setPlaceholderText("Ex: Carrefour Bastos, Yaoundé")
#         form_layout.addRow("Lieu:", self.lieu_edit)
        
#         # --- Ville ---
#         self.ville_edit = QLineEdit()
#         self.ville_edit.setPlaceholderText("Ex: Yaoundé")
#         form_layout.addRow("Ville:", self.ville_edit)
        
#         # --- Pays ---
#         self.pays_edit = QLineEdit("Cameroun")
#         form_layout.addRow("Pays:", self.pays_edit)
        
#         # --- Conditions météo ---
#         self.meteo_combo = QComboBox()
#         self.meteo_combo.addItems(["", "Ensoleillé", "Pluvieux", "Nuageux", "Brouillard", "Nuit"])
#         form_layout.addRow("Conditions météo:", self.meteo_combo)
        
#         # --- Assigné à ---
#         self.assignee_combo = QComboBox()
#         self.assignee_combo.addItem("Non assigné")
#         self.load_assignees()
#         form_layout.addRow("Assigné à:", self.assignee_combo)
        
#         scroll.setWidget(content)
#         layout.addWidget(scroll)
        
#         return tab
    
#     def create_details_tab(self):
#         """Crée l'onglet des détails du sinistre"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(Spacing.MD)
        
#         # Scroll area
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setStyleSheet("border: none; background: transparent;")
        
#         content = QWidget()
#         form_layout = QFormLayout(content)
#         form_layout.setSpacing(Spacing.MD)
#         form_layout.setLabelAlignment(Qt.AlignRight)
        
#         # --- Description ---
#         self.description_edit = QTextEdit()
#         self.description_edit.setPlaceholderText("Décrivez les circonstances du sinistre...")
#         self.description_edit.setMaximumHeight(120)
#         form_layout.addRow("Description:", self.description_edit)
        
#         # --- Circonstances ---
#         self.circonstances_edit = QTextEdit()
#         self.circonstances_edit.setPlaceholderText("Détails des circonstances...")
#         self.circonstances_edit.setMaximumHeight(100)
#         form_layout.addRow("Circonstances:", self.circonstances_edit)
        
#         # --- Responsabilité ---
#         self.responsabilite_combo = QComboBox()
#         self.responsabilite_combo.addItems(["", "assure", "tiers", "partage", "indeterminee"])
#         form_layout.addRow("Responsabilité:", self.responsabilite_combo)
        
#         # --- Notes ---
#         self.notes_edit = QTextEdit()
#         self.notes_edit.setPlaceholderText("Notes internes...")
#         self.notes_edit.setMaximumHeight(80)
#         form_layout.addRow("Notes:", self.notes_edit)
        
#         # --- Statut (uniquement en édition) ---
#         if self.is_edit:
#             self.statut_combo = QComboBox()
#             for statut in StatutSinistre:
#                 self.statut_combo.addItem(statut.value, statut.value)
#             form_layout.addRow("Statut:", self.statut_combo)
        
#         scroll.setWidget(content)
#         layout.addWidget(scroll)
        
#         return tab
    
#     def create_tiers_tab(self):
#         """Crée l'onglet des tiers et témoins"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(Spacing.MD)
        
#         # Scroll area
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setStyleSheet("border: none; background: transparent;")
        
#         content = QWidget()
#         form_layout = QFormLayout(content)
#         form_layout.setSpacing(Spacing.MD)
#         form_layout.setLabelAlignment(Qt.AlignRight)
        
#         # --- Tiers ---
#         form_layout.addRow(QLabel("<b>Tiers impliqué</b>"))
        
#         self.tiers_nom_edit = QLineEdit()
#         form_layout.addRow("Nom:", self.tiers_nom_edit)
        
#         self.tiers_prenom_edit = QLineEdit()
#         form_layout.addRow("Prénom:", self.tiers_prenom_edit)
        
#         self.tiers_telephone_edit = QLineEdit()
#         form_layout.addRow("Téléphone:", self.tiers_telephone_edit)
        
#         self.tiers_assurance_edit = QLineEdit()
#         form_layout.addRow("Assurance:", self.tiers_assurance_edit)
        
#         self.tiers_police_edit = QLineEdit()
#         form_layout.addRow("N° Police:", self.tiers_police_edit)
        
#         self.tiers_vehicule_edit = QLineEdit()
#         form_layout.addRow("Véhicule:", self.tiers_vehicule_edit)
        
#         # --- Séparateur ---
#         separator = QFrame()
#         separator.setFrameShape(QFrame.HLine)
#         separator.setStyleSheet(f"background-color: {Colors.BORDER};")
#         form_layout.addRow(separator)
        
#         # --- Témoins ---
#         form_layout.addRow(QLabel("<b>Témoins</b>"))
        
#         self.temoins_noms_edit = QTextEdit()
#         self.temoins_noms_edit.setPlaceholderText("Noms des témoins (un par ligne)...")
#         self.temoins_noms_edit.setMaximumHeight(80)
#         form_layout.addRow("Noms:", self.temoins_noms_edit)
        
#         self.temoins_nombre_spin = QSpinBox()
#         self.temoins_nombre_spin.setRange(0, 99)
#         self.temoins_nombre_spin.setValue(0)
#         form_layout.addRow("Nombre:", self.temoins_nombre_spin)
        
#         scroll.setWidget(content)
#         layout.addWidget(scroll)
        
#         return tab
    
#     def create_finances_tab(self):
#         """Crée l'onglet des finances"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
#         layout.setSpacing(Spacing.MD)
        
#         # Scroll area
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setStyleSheet("border: none; background: transparent;")
        
#         content = QWidget()
#         form_layout = QFormLayout(content)
#         form_layout.setSpacing(Spacing.MD)
#         form_layout.setLabelAlignment(Qt.AlignRight)
        
#         # --- Estimation préliminaire ---
#         self.estimation_preliminaire = QDoubleSpinBox()
#         self.estimation_preliminaire.setRange(0, 999999999)
#         self.estimation_preliminaire.setPrefix("FCFA ")
#         self.estimation_preliminaire.setSingleStep(1000)
#         self.estimation_preliminaire.setDecimals(0)
#         form_layout.addRow("Estimation préliminaire:", self.estimation_preliminaire)
        
#         # --- Estimation finale (uniquement en édition) ---
#         if self.is_edit:
#             self.estimation_finale = QDoubleSpinBox()
#             self.estimation_finale.setRange(0, 999999999)
#             self.estimation_finale.setPrefix("FCFA ")
#             self.estimation_finale.setSingleStep(1000)
#             self.estimation_finale.setDecimals(0)
#             form_layout.addRow("Estimation finale:", self.estimation_finale)
        
#         # --- Franchise ---
#         self.franchise_spin = QDoubleSpinBox()
#         self.franchise_spin.setRange(0, 999999999)
#         self.franchise_spin.setPrefix("FCFA ")
#         self.franchise_spin.setSingleStep(1000)
#         self.franchise_spin.setDecimals(0)
#         form_layout.addRow("Franchise:", self.franchise_spin)
        
#         # --- Montant indemnisé (uniquement en édition) ---
#         if self.is_edit:
#             self.montant_indemnise = QDoubleSpinBox()
#             self.montant_indemnise.setRange(0, 999999999)
#             self.montant_indemnise.setPrefix("FCFA ")
#             self.montant_indemnise.setSingleStep(1000)
#             self.montant_indemnise.setDecimals(0)
#             form_layout.addRow("Montant indemnisé:", self.montant_indemnise)
        
#         scroll.setWidget(content)
#         layout.addWidget(scroll)
        
#         return tab
    
#     def create_buttons(self):
#         """Crée les boutons d'action"""
#         buttons = QFrame()
#         layout = QHBoxLayout(buttons)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(Spacing.MD)
        
#         # Bouton Annuler
#         btn_annuler = QPushButton("❌ Annuler")
#         btn_annuler.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {Colors.GRAY_100};
#                 color: {Colors.TEXT_SECONDARY};
#                 border: none;
#                 border-radius: 8px;
#                 padding: 10px 24px;
#                 font-weight: {Fonts.MEDIUM};
#             }}
#             QPushButton:hover {{
#                 background-color: {Colors.GRAY_200};
#             }}
#         """)
#         btn_annuler.clicked.connect(self.close)
#         layout.addWidget(btn_annuler)
        
#         layout.addStretch()
        
#         # Bouton Enregistrer
#         self.btn_save = QPushButton("💾 Enregistrer" if not self.is_edit else "💾 Mettre à jour")
#         self.btn_save.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {Colors.PRIMARY};
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 padding: 10px 32px;
#                 font-weight: {Fonts.MEDIUM};
#             }}
#             QPushButton:hover {{
#                 background-color: {Colors.PRIMARY_DARK};
#             }}
#         """)
#         self.btn_save.clicked.connect(self.save_sinistre)
#         layout.addWidget(self.btn_save)
        
#         return buttons
    
#     def load_data(self):
#         """Charge les données si en mode édition"""
#         if not self.is_edit or not self.sinistre:
#             return
        
#         # Remplir les champs avec les données du sinistre
#         sinistre = self.sinistre
        
#         # Contrat
#         index = self.contrat_combo.findData(sinistre.contrat_id)
#         if index >= 0:
#             self.contrat_combo.setCurrentIndex(index)
        
#         # Véhicule
#         self.load_vehicules(sinistre.contrat_id)
#         index = self.vehicule_combo.findData(sinistre.vehicule_id)
#         if index >= 0:
#             self.vehicule_combo.setCurrentIndex(index)
        
#         # Client
#         index = self.client_combo.findData(sinistre.client_id)
#         if index >= 0:
#             self.client_combo.setCurrentIndex(index)
        
#         # Type
#         index = self.type_combo.findData(sinistre.type.value if sinistre.type else "")
#         if index >= 0:
#             self.type_combo.setCurrentIndex(index)
        
#         # Date
#         if sinistre.date_survenue:
#             self.date_survenue.setDateTime(QDateTime.fromPython(sinistre.date_survenue))
        
#         # Lieu
#         self.lieu_edit.setText(sinistre.lieu or "")
#         self.ville_edit.setText(sinistre.ville or "")
#         self.pays_edit.setText(sinistre.pays or "Cameroun")
        
#         # Description
#         self.description_edit.setText(sinistre.description or "")
#         self.circonstances_edit.setText(sinistre.circonstances or "")
        
#         # Responsabilité
#         if sinistre.responsabilite:
#             index = self.responsabilite_combo.findText(sinistre.responsabilite.value)
#             if index >= 0:
#                 self.responsabilite_combo.setCurrentIndex(index)
        
#         # Tiers
#         self.tiers_nom_edit.setText(sinistre.tiers_nom or "")
#         self.tiers_prenom_edit.setText(sinistre.tiers_prenom or "")
#         self.tiers_telephone_edit.setText(sinistre.tiers_telephone or "")
#         self.tiers_assurance_edit.setText(sinistre.tiers_assurance or "")
#         self.tiers_police_edit.setText(sinistre.tiers_police or "")
#         self.tiers_vehicule_edit.setText(sinistre.tiers_vehicule or "")
        
#         # Témoins
#         self.temoins_noms_edit.setText(sinistre.temoins_noms or "")
#         self.temoins_nombre_spin.setValue(sinistre.temoins_nombre or 0)
        
#         # Finances
#         self.estimation_preliminaire.setValue(sinistre.estimation_preliminaire or 0)
#         self.franchise_spin.setValue(sinistre.franchise or 0)
        
#         # Assigné à
#         if sinistre.assigned_to:
#             index = self.assignee_combo.findData(sinistre.assigned_to)
#             if index >= 0:
#                 self.assignee_combo.setCurrentIndex(index)
        
#         # Notes
#         self.notes_edit.setText(sinistre.notes or "")
        
#         # Statut
#         if hasattr(self, 'statut_combo') and sinistre.statut:
#             index = self.statut_combo.findText(sinistre.statut.value)
#             if index >= 0:
#                 self.statut_combo.setCurrentIndex(index)
        
#         # Estimations en édition
#         if hasattr(self, 'estimation_finale'):
#             self.estimation_finale.setValue(sinistre.estimation_finale or 0)
#         if hasattr(self, 'montant_indemnise'):
#             self.montant_indemnise.setValue(sinistre.montant_indemnise or 0)
    
#     def load_contrats(self):
#         """Charge les contrats disponibles"""
#         try:
#             from addons.Automobiles.controllers.contract_controller import ContractController
#             contract_ctrl = ContractController(self.controller.session)
#             contrats = contract_ctrl.get_all_contracts()
            
#             for contrat in contrats:
#                 label = f"{contrat.numero_police} - {contrat.vehicle.immatriculation if contrat.vehicle else 'N/A'}"
#                 self.contrat_combo.addItem(label, contrat.id)
#         except Exception as e:
#             print(f"Erreur chargement contrats: {e}")
    
#     def load_vehicules(self, contrat_id=None):
#         """Charge les véhicules pour un contrat donné"""
#         self.vehicule_combo.clear()
#         self.vehicule_combo.addItem("Sélectionner un véhicule...")
        
#         try:
#             if contrat_id:
#                 from addons.Automobiles.models.contract_models import Contrat
#                 contrat = self.controller.session.contracts.get_contract_by_id(contrat_id)
#                 if contrat and contrat.vehicle:
#                     self.vehicule_combo.addItem(
#                         f"{contrat.vehicle.immatriculation} - {contrat.vehicle.marque} {contrat.vehicle.modele}",
#                         contrat.vehicle.id
#                     )
#                     self.vehicule_combo.setEnabled(True)
#                 else:
#                     self.vehicule_combo.setEnabled(False)
#             else:
#                 self.vehicule_combo.setEnabled(False)
#         except Exception as e:
#             print(f"Erreur chargement véhicules: {e}")
    
#     def load_clients(self):
#         """Charge les clients disponibles"""
#         try:
#             clients = self.controller.session.contacts.get_all_contacts()
#             for client in clients:
#                 label = f"{client.nom} {client.prenom or ''} - {client.telephone or ''}"
#                 self.client_combo.addItem(label.strip(), client.id)
#         except Exception as e:
#             print(f"Erreur chargement clients: {e}")
    
#     def load_assignees(self):
#         """Charge les utilisateurs disponibles"""
#         try:
#             from addons.Paramètres.models.models import User
#             users = self.controller.session.query(User).all()
#             for user in users:
#                 self.assignee_combo.addItem(f"{user.username} ({user.role})", user.id)
#         except Exception as e:
#             print(f"Erreur chargement assignees: {e}")
    
#     def on_client_changed(self, index):
#         """Quand le client change, on charge ses véhicules"""
#         # Pour l'instant, on garde simple
#         pass
    
#     def _get_type_label(self, type_enum):
#         """Retourne le libellé d'un type de sinistre"""
#         labels = {
#             TypeSinistre.ACCIDENT: "Accident",
#             TypeSinistre.VOL: "Vol",
#             TypeSinistre.INCENDIE: "Incendie",
#             TypeSinistre.DEGAT_NATUREL: "Dégât naturel",
#             TypeSinistre.BRIS_GLACE: "Bris de glace",
#             TypeSinistre.VANDALISME: "Vandalisme",
#             TypeSinistre.COLLISION: "Collision",
#             TypeSinistre.AUTRE: "Autre"
#         }
#         return labels.get(type_enum, str(type_enum))
    
#     def save_sinistre(self):
#         """Sauvegarde le sinistre"""
#         # 1. Validation des champs obligatoires
#         if not self.validate_form():
#             return
        
#         # 2. Construction des données
#         data = self.get_form_data()
        
#         # 3. Sauvegarde
#         try:
#             if self.is_edit:
#                 success = self.controller.update(self.sinistre.id, data)
#                 message = "Sinistre mis à jour avec succès"
#             else:
#                 sinistre = self.controller.create(data)
#                 success = sinistre is not None
#                 message = "Sinistre déclaré avec succès"
            
#             if success:
#                 QMessageBox.information(self, "Succès", message)
#                 self.sinistre_saved.emit(self.sinistre if self.is_edit else sinistre)
#                 self.close()
#             else:
#                 QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement du sinistre")
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
#     def validate_form(self):
#         """Valide les champs obligatoires"""
#         # Contrat
#         if self.contrat_combo.currentIndex() <= 0:
#             QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un contrat")
#             self.tabs.setCurrentIndex(0)
#             self.contrat_combo.setFocus()
#             return False
        
#         # Véhicule
#         if self.vehicule_combo.currentIndex() <= 0:
#             QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un véhicule")
#             self.tabs.setCurrentIndex(0)
#             self.vehicule_combo.setFocus()
#             return False
        
#         # Client
#         if self.client_combo.currentIndex() <= 0:
#             QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un client")
#             self.tabs.setCurrentIndex(0)
#             self.client_combo.setFocus()
#             return False
        
#         # Type
#         if self.type_combo.currentIndex() <= 0:
#             QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un type de sinistre")
#             self.tabs.setCurrentIndex(0)
#             self.type_combo.setFocus()
#             return False
        
#         # Date
#         if not self.date_survenue.dateTime().isValid():
#             QMessageBox.warning(self, "Champ requis", "Veuillez saisir une date de survenue valide")
#             self.tabs.setCurrentIndex(0)
#             self.date_survenue.setFocus()
#             return False
        
#         return True
    
#     def get_form_data(self):
#         """Récupère les données du formulaire"""
#         data = {
#             'contrat_id': self.contrat_combo.currentData(),
#             'vehicule_id': self.vehicule_combo.currentData(),
#             'client_id': self.client_combo.currentData(),
#             'type': self.type_combo.currentData() or 'autre',
#             'date_survenue': self.date_survenue.dateTime().toPython(),
#             'lieu': self.lieu_edit.text().strip() or None,
#             'ville': self.ville_edit.text().strip() or None,
#             'pays': self.pays_edit.text().strip() or "Cameroun",
#             'conditions_meteo': self.meteo_combo.currentText() or None,
#             'description': self.description_edit.toPlainText().strip() or None,
#             'circonstances': self.circonstances_edit.toPlainText().strip() or None,
#             'responsabilite': self.responsabilite_combo.currentText() or None,
#             'tiers_nom': self.tiers_nom_edit.text().strip() or None,
#             'tiers_prenom': self.tiers_prenom_edit.text().strip() or None,
#             'tiers_telephone': self.tiers_telephone_edit.text().strip() or None,
#             'tiers_assurance': self.tiers_assurance_edit.text().strip() or None,
#             'tiers_police': self.tiers_police_edit.text().strip() or None,
#             'tiers_vehicule': self.tiers_vehicule_edit.text().strip() or None,
#             'temoins_noms': self.temoins_noms_edit.toPlainText().strip() or None,
#             'temoins_nombre': self.temoins_nombre_spin.value(),
#             'estimation_preliminaire': self.estimation_preliminaire.value(),
#             'franchise': self.franchise_spin.value(),
#             'assigned_to': self.assignee_combo.currentData() or None,
#             'notes': self.notes_edit.toPlainText().strip() or None,
#             'creer_expertise': True
#         }
        
#         # Champs en mode édition
#         if self.is_edit:
#             data['statut'] = self.statut_combo.currentText() if hasattr(self, 'statut_combo') else None
#             if hasattr(self, 'estimation_finale'):
#                 data['estimation_finale'] = self.estimation_finale.value()
#             if hasattr(self, 'montant_indemnise'):
#                 data['montant_indemnise'] = self.montant_indemnise.value()
        
#         return data
    
#     def close(self):
#         """Ferme le formulaire"""
#         self.deleteLater()


# addons/Automobiles/views/sinistre/sinistre_form_view.py
"""
Formulaire de création et d'édition d'un sinistre - Version Premium
Design professionnel avec champs obligatoires clairement identifiés
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QDoubleSpinBox,
    QGroupBox, QFormLayout, QFrame, QMessageBox, QSpinBox,
    QCheckBox, QTabWidget, QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QDateTime, Signal, QSize
from PySide6.QtGui import QColor, QFont, QPalette, QIcon, QPixmap

from datetime import datetime

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.models.sinistre_models import TypeSinistre, StatutSinistre, Responsabilite


class SinistreFormView(QDialog):
    """Formulaire de création/édition d'un sinistre - Version Premium"""
    
    sinistre_saved = Signal(object)
    
    def __init__(self, controller, user=None, sinistre=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.sinistre = sinistre
        self.is_edit = sinistre is not None
        
        self.setWindowTitle("📋 Déclaration de Sinistre" if not self.is_edit else "✏️ Modification du Sinistre")
        self.setModal(True)
        self.setMinimumSize(900, 750)
        self.resize(950, 800)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BACKGROUND};
            }}
        """)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configure l'interface du formulaire"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(Spacing.XL)
        main_layout.setContentsMargins(Spacing.XXL, Spacing.XL, Spacing.XXL, Spacing.XL)
        
        # --- En-tête avec icône ---
        header = self.create_header()
        main_layout.addWidget(header)
        
        # --- Onglets ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                background-color: {Colors.WHITE};
                padding: 8px;
            }}
            QTabBar::tab {{
                padding: 12px 24px;
                border-radius: 8px 8px 0 0;
                font-weight: {Fonts.SEMIBOLD};
                font-size: 13px;
                color: {Colors.TEXT_SECONDARY};
                background-color: transparent;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.PRIMARY};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {Colors.GRAY_100};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        # Création des onglets
        self.tabs.addTab(self.create_general_tab(), "📋 Informations générales")
        self.tabs.addTab(self.create_details_tab(), "🔍 Détails du sinistre")
        self.tabs.addTab(self.create_tiers_tab(), "👤 Tiers et témoins")
        self.tabs.addTab(self.create_finances_tab(), "💰 Finances")
        
        main_layout.addWidget(self.tabs)
        
        # --- Séparateur ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {Colors.BORDER}; max-height: 1px;")
        main_layout.addWidget(separator)
        
        # --- Boutons d'action ---
        buttons = self.create_buttons()
        main_layout.addWidget(buttons)
    
    def create_header(self):
        """Crée l'en-tête avec le titre et l'icône"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                margin-bottom: 8px;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre
        title_layout = QVBoxLayout()
        
        title = QLabel("📋 Déclaration de Sinistre" if not self.is_edit else "✏️ Modification du Sinistre")
        title.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        
        subtitle = QLabel(
            "Remplissez les informations ci-dessous pour déclarer un nouveau sinistre."
            if not self.is_edit else
            "Modifiez les informations du sinistre sélectionné."
        )
        subtitle.setStyleSheet(f"""
            font-size: {Fonts.SMALL}px;
            color: {Colors.TEXT_MUTED};
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Badge de statut (si édition)
        if self.is_edit and self.sinistre and self.sinistre.statut:
            status_badge = QFrame()
            status_badge.setStyleSheet(f"""
                QFrame {{
                    background-color: {self._get_statut_color(self.sinistre.statut)};
                    border-radius: 20px;
                    padding: 4px 16px;
                }}
            """)
            status_layout = QHBoxLayout(status_badge)
            status_layout.setContentsMargins(8, 4, 8, 4)
            
            status_label = QLabel(f"📌 {self.sinistre.statut.value.upper()}")
            status_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
            status_layout.addWidget(status_label)
            
            header_layout.addLayout(title_layout)
            header_layout.addStretch()
            header_layout.addWidget(status_badge)
        else:
            header_layout.addLayout(title_layout)
            header_layout.addStretch()
            
            # Badge "Nouveau"
            new_badge = QFrame()
            new_badge.setStyleSheet("""
                QFrame {
                    background-color: #10b981;
                    border-radius: 20px;
                    padding: 4px 16px;
                }
            """)
            new_layout = QHBoxLayout(new_badge)
            new_layout.setContentsMargins(8, 4, 8, 4)
            new_label = QLabel("✨ NOUVEAU")
            new_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
            new_layout.addWidget(new_label)
            header_layout.addWidget(new_badge)
        
        return header
    
    def create_general_tab(self):
        """Crée l'onglet des informations générales"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(Spacing.MD)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        
        # --- Section : Informations principales ---
        section_title = QLabel("🏷️ Informations principales")
        section_title.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
        """)
        content_layout.addWidget(section_title, 0, 0, 1, 2)
        
        # Contrat (obligatoire)
        label_contrat = QLabel("Contrat <span style='color:red;'>*</span>")
        label_contrat.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_contrat, 1, 0)
        
        self.contrat_combo = QComboBox()
        self.contrat_combo.addItem("Sélectionner un contrat...")
        self.contrat_combo.setStyleSheet(self._get_combo_style())
        self.contrat_combo.currentIndexChanged.connect(self.on_contrat_changed)
        self.load_contrats()
        content_layout.addWidget(self.contrat_combo, 1, 1)
        
        # Véhicule (obligatoire)
        label_vehicule = QLabel("Véhicule <span style='color:red;'>*</span>")
        label_vehicule.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_vehicule, 2, 0)
        
        self.vehicule_combo = QComboBox()
        self.vehicule_combo.addItem("Sélectionner un véhicule...")
        self.vehicule_combo.setStyleSheet(self._get_combo_style())
        self.vehicule_combo.setEnabled(False)
        content_layout.addWidget(self.vehicule_combo, 2, 1)
        
        # Client (obligatoire)
        label_client = QLabel("Client <span style='color:red;'>*</span>")
        label_client.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_client, 3, 0)
        
        self.client_combo = QComboBox()
        self.client_combo.addItem("Sélectionner un client...")
        self.client_combo.setStyleSheet(self._get_combo_style())
        self.load_clients()
        content_layout.addWidget(self.client_combo, 3, 1)
        
        # Type de sinistre (obligatoire)
        label_type = QLabel("Type de sinistre <span style='color:red;'>*</span>")
        label_type.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_type, 4, 0)
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("Sélectionner un type...")
        for type_ in TypeSinistre:
            self.type_combo.addItem(self._get_type_label(type_), type_.value)
        self.type_combo.setStyleSheet(self._get_combo_style())
        content_layout.addWidget(self.type_combo, 4, 1)
        
        # --- Section : Date et lieu ---
        section_title2 = QLabel("📍 Date et lieu")
        section_title2.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(section_title2, 5, 0, 1, 2)
        
        # Date de survenue (obligatoire)
        label_date = QLabel("Date de survenue <span style='color:red;'>*</span>")
        label_date.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_date, 6, 0)
        
        self.date_survenue = QDateTimeEdit()
        self.date_survenue.setCalendarPopup(True)
        self.date_survenue.setDateTime(QDateTime.currentDateTime())
        self.date_survenue.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.date_survenue.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.date_survenue, 6, 1)
        
        # Lieu
        label_lieu = QLabel("Lieu")
        label_lieu.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_lieu, 7, 0)
        
        self.lieu_edit = QLineEdit()
        self.lieu_edit.setPlaceholderText("Ex: Carrefour Bastos, Yaoundé")
        self.lieu_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.lieu_edit, 7, 1)
        
        # Ville
        label_ville = QLabel("Ville")
        label_ville.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_ville, 8, 0)
        
        self.ville_edit = QLineEdit()
        self.ville_edit.setPlaceholderText("Ex: Yaoundé")
        self.ville_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.ville_edit, 8, 1)
        
        # Pays
        label_pays = QLabel("Pays")
        label_pays.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_pays, 9, 0)
        
        self.pays_edit = QLineEdit("Cameroun")
        self.pays_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.pays_edit, 9, 1)
        
        # --- Section : Affectation ---
        section_title3 = QLabel("👤 Affectation")
        section_title3.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(section_title3, 10, 0, 1, 2)
        
        # Conditions météo
        label_meteo = QLabel("Conditions météo")
        label_meteo.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_meteo, 11, 0)
        
        self.meteo_combo = QComboBox()
        self.meteo_combo.addItems(["", "☀️ Ensoleillé", "🌧️ Pluvieux", "☁️ Nuageux", "🌫️ Brouillard", "🌙 Nuit"])
        self.meteo_combo.setStyleSheet(self._get_combo_style())
        content_layout.addWidget(self.meteo_combo, 11, 1)
        
        # Assigné à
        label_assignee = QLabel("Assigné à")
        label_assignee.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_assignee, 12, 0)
        
        self.assignee_combo = QComboBox()
        self.assignee_combo.addItem("Non assigné")
        self.assignee_combo.setStyleSheet(self._get_combo_style())
        self.load_assignees()
        content_layout.addWidget(self.assignee_combo, 12, 1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_details_tab(self):
        """Crée l'onglet des détails du sinistre"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(Spacing.MD)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        
        # --- Section : Description ---
        section_title = QLabel("📝 Description du sinistre")
        section_title.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
        """)
        content_layout.addWidget(section_title, 0, 0, 1, 2)
        
        # Description
        label_desc = QLabel("Description")
        label_desc.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_desc, 1, 0)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Décrivez les circonstances du sinistre en détail...")
        self.description_edit.setMaximumHeight(120)
        self.description_edit.setStyleSheet(self._get_textedit_style())
        content_layout.addWidget(self.description_edit, 1, 1)
        
        # Circonstances
        label_circ = QLabel("Circonstances")
        label_circ.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_circ, 2, 0)
        
        self.circonstances_edit = QTextEdit()
        self.circonstances_edit.setPlaceholderText("Détails des circonstances de l'accident...")
        self.circonstances_edit.setMaximumHeight(100)
        self.circonstances_edit.setStyleSheet(self._get_textedit_style())
        content_layout.addWidget(self.circonstances_edit, 2, 1)
        
        # --- Section : Responsabilité ---
        section_title2 = QLabel("⚖️ Responsabilité")
        section_title2.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(section_title2, 3, 0, 1, 2)
        
        # Responsabilité
        label_resp = QLabel("Responsabilité")
        label_resp.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_resp, 4, 0)
        
        self.responsabilite_combo = QComboBox()
        self.responsabilite_combo.addItem("Non déterminée", None)
        self.responsabilite_combo.addItem("Assuré", "assure")
        self.responsabilite_combo.addItem("Tiers", "tiers")
        self.responsabilite_combo.addItem("Partagée", "partage")
        self.responsabilite_combo.addItem("Indéterminée", "indeterminee")
        self.responsabilite_combo.setStyleSheet(self._get_combo_style())
        content_layout.addWidget(self.responsabilite_combo, 4, 1)
        
        # --- Section : Statut et notes ---
        section_title3 = QLabel("📌 Statut et notes")
        section_title3.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(section_title3, 5, 0, 1, 2)
        
        # Statut (uniquement en édition)
        if self.is_edit:
            label_statut = QLabel("Statut")
            label_statut.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
            content_layout.addWidget(label_statut, 6, 0)
            
            self.statut_combo = QComboBox()
            for statut in StatutSinistre:
                self.statut_combo.addItem(statut.value, statut.value)
            self.statut_combo.setStyleSheet(self._get_combo_style())
            content_layout.addWidget(self.statut_combo, 6, 1)
            row = 7
        else:
            row = 6
        
        # Notes
        label_notes = QLabel("Notes internes")
        label_notes.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_notes, row, 0)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Notes confidentielles (visibles uniquement par l'équipe)...")
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setStyleSheet(self._get_textedit_style())
        content_layout.addWidget(self.notes_edit, row, 1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_tiers_tab(self):
        """Crée l'onglet des tiers et témoins"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(Spacing.MD)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        
        # --- Section : Tiers impliqué ---
        section_title = QLabel("👤 Tiers impliqué")
        section_title.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
        """)
        content_layout.addWidget(section_title, 0, 0, 1, 2)
        
        # Nom
        label_nom = QLabel("Nom")
        label_nom.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_nom, 1, 0)
        
        self.tiers_nom_edit = QLineEdit()
        self.tiers_nom_edit.setPlaceholderText("Nom du tiers")
        self.tiers_nom_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.tiers_nom_edit, 1, 1)
        
        # Prénom
        label_prenom = QLabel("Prénom")
        label_prenom.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_prenom, 2, 0)
        
        self.tiers_prenom_edit = QLineEdit()
        self.tiers_prenom_edit.setPlaceholderText("Prénom du tiers")
        self.tiers_prenom_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.tiers_prenom_edit, 2, 1)
        
        # Téléphone
        label_tel = QLabel("Téléphone")
        label_tel.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_tel, 3, 0)
        
        self.tiers_telephone_edit = QLineEdit()
        self.tiers_telephone_edit.setPlaceholderText("699123456")
        self.tiers_telephone_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.tiers_telephone_edit, 3, 1)
        
        # Assurance
        label_assurance = QLabel("Assurance")
        label_assurance.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_assurance, 4, 0)
        
        self.tiers_assurance_edit = QLineEdit()
        self.tiers_assurance_edit.setPlaceholderText("Nom de la compagnie d'assurance")
        self.tiers_assurance_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.tiers_assurance_edit, 4, 1)
        
        # N° Police
        label_police = QLabel("N° Police")
        label_police.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_police, 5, 0)
        
        self.tiers_police_edit = QLineEdit()
        self.tiers_police_edit.setPlaceholderText("Numéro de police du tiers")
        self.tiers_police_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.tiers_police_edit, 5, 1)
        
        # Véhicule
        label_vehicule_tiers = QLabel("Véhicule")
        label_vehicule_tiers.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_vehicule_tiers, 6, 0)
        
        self.tiers_vehicule_edit = QLineEdit()
        self.tiers_vehicule_edit.setPlaceholderText("Marque, modèle et immatriculation")
        self.tiers_vehicule_edit.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.tiers_vehicule_edit, 6, 1)
        
        # --- Section : Témoins ---
        section_title2 = QLabel("👥 Témoins")
        section_title2.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(section_title2, 7, 0, 1, 2)
        
        # Noms des témoins
        label_temoins = QLabel("Noms")
        label_temoins.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_temoins, 8, 0)
        
        self.temoins_noms_edit = QTextEdit()
        self.temoins_noms_edit.setPlaceholderText("Noms des témoins (un par ligne)...")
        self.temoins_noms_edit.setMaximumHeight(80)
        self.temoins_noms_edit.setStyleSheet(self._get_textedit_style())
        content_layout.addWidget(self.temoins_noms_edit, 8, 1)
        
        # Nombre de témoins
        label_nb_temoins = QLabel("Nombre")
        label_nb_temoins.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_nb_temoins, 9, 0)
        
        self.temoins_nombre_spin = QSpinBox()
        self.temoins_nombre_spin.setRange(0, 99)
        self.temoins_nombre_spin.setValue(0)
        self.temoins_nombre_spin.setStyleSheet(self._get_input_style())
        content_layout.addWidget(self.temoins_nombre_spin, 9, 1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_finances_tab(self):
        """Crée l'onglet des finances"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(Spacing.MD)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        
        # --- Section : Estimations ---
        section_title = QLabel("💰 Estimations financières")
        section_title.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
        """)
        content_layout.addWidget(section_title, 0, 0, 1, 2)
        
        # Estimation préliminaire
        label_prelim = QLabel("Estimation préliminaire")
        label_prelim.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_prelim, 1, 0)
        
        self.estimation_preliminaire = QDoubleSpinBox()
        self.estimation_preliminaire.setRange(0, 999999999)
        self.estimation_preliminaire.setPrefix("FCFA ")
        self.estimation_preliminaire.setSingleStep(1000)
        self.estimation_preliminaire.setDecimals(0)
        self.estimation_preliminaire.setStyleSheet(self._get_input_style())
        self.estimation_preliminaire.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
        content_layout.addWidget(self.estimation_preliminaire, 1, 1)
        
        # Estimation finale (uniquement en édition)
        if self.is_edit:
            label_finale = QLabel("Estimation finale")
            label_finale.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
            content_layout.addWidget(label_finale, 2, 0)
            
            self.estimation_finale = QDoubleSpinBox()
            self.estimation_finale.setRange(0, 999999999)
            self.estimation_finale.setPrefix("FCFA ")
            self.estimation_finale.setSingleStep(1000)
            self.estimation_finale.setDecimals(0)
            self.estimation_finale.setStyleSheet(self._get_input_style())
            self.estimation_finale.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
            content_layout.addWidget(self.estimation_finale, 2, 1)
            row = 3
        else:
            row = 2
        
        # --- Section : Indemnisation ---
        section_title2 = QLabel("💳 Indemnisation")
        section_title2.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
            padding-bottom: 8px;
            border-bottom: 2px solid {Colors.PRIMARY};
            margin-top: 16px;
        """)
        content_layout.addWidget(section_title2, row, 0, 1, 2)
        row += 1
        
        # Franchise
        label_franchise = QLabel("Franchise")
        label_franchise.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
        content_layout.addWidget(label_franchise, row, 0)
        
        self.franchise_spin = QDoubleSpinBox()
        self.franchise_spin.setRange(0, 999999999)
        self.franchise_spin.setPrefix("FCFA ")
        self.franchise_spin.setSingleStep(1000)
        self.franchise_spin.setDecimals(0)
        self.franchise_spin.setStyleSheet(self._get_input_style())
        self.franchise_spin.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
        content_layout.addWidget(self.franchise_spin, row, 1)
        row += 1
        
        # Montant indemnisé (uniquement en édition)
        if self.is_edit:
            label_indemnise = QLabel("Montant indemnisé")
            label_indemnise.setStyleSheet(f"font-weight: {Fonts.MEDIUM};")
            content_layout.addWidget(label_indemnise, row, 0)
            
            self.montant_indemnise = QDoubleSpinBox()
            self.montant_indemnise.setRange(0, 999999999)
            self.montant_indemnise.setPrefix("FCFA ")
            self.montant_indemnise.setSingleStep(1000)
            self.montant_indemnise.setDecimals(0)
            self.montant_indemnise.setStyleSheet(self._get_input_style())
            self.montant_indemnise.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
            content_layout.addWidget(self.montant_indemnise, row, 1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_buttons(self):
        """Crée les boutons d'action"""
        buttons = QFrame()
        buttons.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)
        
        # Indicateur de champs obligatoires
        required_label = QLabel("Les champs marqués <span style='color:red;'>*</span> sont obligatoires")
        required_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(required_label)
        
        layout.addStretch()
        
        # Bouton Annuler
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setCursor(Qt.PointingHandCursor)
        btn_annuler.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_100};
                color: {Colors.TEXT_SECONDARY};
                border: none;
                border-radius: 10px;
                padding: 12px 32px;
                font-weight: {Fonts.MEDIUM};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_200};
            }}
        """)
        btn_annuler.clicked.connect(self.reject)
        layout.addWidget(btn_annuler)
        
        # Bouton Enregistrer
        self.btn_save = QPushButton("Enregistrer" if not self.is_edit else "Mettre à jour")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 40px;
                font-weight: {Fonts.BOLD};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        self.btn_save.clicked.connect(self.save_sinistre)
        layout.addWidget(self.btn_save)
        
        return buttons
    
    # ============================================================================
    # MÉTHODES DE STYLE
    # ============================================================================
    
    def _get_input_style(self):
        """Style pour les champs de saisie"""
        return f"""
            QLineEdit, QDateTimeEdit, QDoubleSpinBox, QSpinBox {{
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
                min-height: 20px;
            }}
            QLineEdit:focus, QDateTimeEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
                border-color: {Colors.PRIMARY};
                outline: none;
            }}
            QLineEdit:disabled, QDateTimeEdit:disabled, QDoubleSpinBox:disabled, QSpinBox:disabled {{
                background-color: {Colors.GRAY_50};
                color: {Colors.TEXT_MUTED};
            }}
        """
    
    def _get_textedit_style(self):
        """Style pour les QTextEdit"""
        return f"""
            QTextEdit {{
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
                min-height: 40px;
            }}
            QTextEdit:focus {{
                border-color: {Colors.PRIMARY};
                outline: none;
            }}
        """
    
    def _get_combo_style(self):
        """Style pour les QComboBox"""
        return f"""
            QComboBox {{
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border-color: {Colors.PRIMARY};
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                background-color: {Colors.WHITE};
                selection-background-color: {Colors.PRIMARY}20;
                selection-color: {Colors.TEXT_PRIMARY};
                padding: 4px;
            }}
        """
    
    def _get_statut_color(self, statut):
        """Retourne la couleur associée à un statut"""
        colors = {
            StatutSinistre.DECLARE: "#2563eb",
            StatutSinistre.EN_INSTRUCTION: "#f59e0b",
            StatutSinistre.EN_ATTENTE: "#f59e0b",
            StatutSinistre.EXPERTISE: "#8b5cf6",
            StatutSinistre.VALIDE: "#16a34a",
            StatutSinistre.REJETE: "#dc2626",
            StatutSinistre.INDEMNISE: "#16a34a",
            StatutSinistre.CLOS: "#64748b",
        }
        return colors.get(statut, "#64748b")
    
    # ============================================================================
    # MÉTHODES DE CHARGEMENT
    # ============================================================================
    
    def load_data(self):
        """Charge les données si en mode édition"""
        if not self.is_edit or not self.sinistre:
            return
        
        sinistre = self.sinistre
        
        # Contrat
        index = self.contrat_combo.findData(sinistre.contrat_id)
        if index >= 0:
            self.contrat_combo.setCurrentIndex(index)
        
        # Véhicule
        self.load_vehicules(sinistre.contrat_id)
        index = self.vehicule_combo.findData(sinistre.vehicule_id)
        if index >= 0:
            self.vehicule_combo.setCurrentIndex(index)
        
        # Client
        index = self.client_combo.findData(sinistre.client_id)
        if index >= 0:
            self.client_combo.setCurrentIndex(index)
        
        # Type
        index = self.type_combo.findData(sinistre.type.value if sinistre.type else "")
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Date
        if sinistre.date_survenue:
            self.date_survenue.setDateTime(QDateTime.fromPython(sinistre.date_survenue))
        
        # Lieu
        self.lieu_edit.setText(sinistre.lieu or "")
        self.ville_edit.setText(sinistre.ville or "")
        self.pays_edit.setText(sinistre.pays or "Cameroun")
        
        # Description
        self.description_edit.setText(sinistre.description or "")
        self.circonstances_edit.setText(sinistre.circonstances or "")
        
        # Responsabilité
        if sinistre.responsabilite:
            index = self.responsabilite_combo.findData(sinistre.responsabilite.value)
            if index >= 0:
                self.responsabilite_combo.setCurrentIndex(index)
        
        # Tiers
        self.tiers_nom_edit.setText(sinistre.tiers_nom or "")
        self.tiers_prenom_edit.setText(sinistre.tiers_prenom or "")
        self.tiers_telephone_edit.setText(sinistre.tiers_telephone or "")
        self.tiers_assurance_edit.setText(sinistre.tiers_assurance or "")
        self.tiers_police_edit.setText(sinistre.tiers_police or "")
        self.tiers_vehicule_edit.setText(sinistre.tiers_vehicule or "")
        
        # Témoins
        self.temoins_noms_edit.setText(sinistre.temoins_noms or "")
        self.temoins_nombre_spin.setValue(sinistre.temoins_nombre or 0)
        
        # Finances
        self.estimation_preliminaire.setValue(sinistre.estimation_preliminaire or 0)
        self.franchise_spin.setValue(sinistre.franchise or 0)
        
        # Assigné à
        if sinistre.assigned_to:
            index = self.assignee_combo.findData(sinistre.assigned_to)
            if index >= 0:
                self.assignee_combo.setCurrentIndex(index)
        
        # Notes
        self.notes_edit.setText(sinistre.notes or "")
        
        # Statut
        if hasattr(self, 'statut_combo') and sinistre.statut:
            index = self.statut_combo.findText(sinistre.statut.value)
            if index >= 0:
                self.statut_combo.setCurrentIndex(index)
        
        # Estimations en édition
        if hasattr(self, 'estimation_finale'):
            self.estimation_finale.setValue(sinistre.estimation_finale or 0)
        if hasattr(self, 'montant_indemnise'):
            self.montant_indemnise.setValue(sinistre.montant_indemnise or 0)
    
    def load_contrats(self):
        """Charge les contrats disponibles"""
        try:
            from addons.Automobiles.controllers.contract_controller import ContractController
            contract_ctrl = ContractController(self.controller.session)
            contrats = contract_ctrl.get_all_contracts()
            
            for contrat in contrats:
                label = f"{contrat.numero_police} - {contrat.vehicle.immatriculation if contrat.vehicle else 'N/A'}"
                self.contrat_combo.addItem(label, contrat.id)
        except Exception as e:
            print(f"Erreur chargement contrats: {e}")
    
    def on_contrat_changed(self, index):
        """Quand le contrat change, charger le véhicule associé"""
        if index > 0:
            contrat_id = self.contrat_combo.currentData()
            self.load_vehicules(contrat_id)
        else:
            self.vehicule_combo.clear()
            self.vehicule_combo.addItem("Sélectionner un véhicule...")
            self.vehicule_combo.setEnabled(False)
    
    def load_vehicules(self, contrat_id=None):
        """Charge les véhicules pour un contrat donné"""
        self.vehicule_combo.clear()
        self.vehicule_combo.addItem("Sélectionner un véhicule...")
        
        try:
            if contrat_id:
                from addons.Automobiles.models.contract_models import Contrat
                contrat = self.controller.session.query(Contrat).filter_by(id=contrat_id).first()
                if contrat and contrat.vehicle:
                    self.vehicule_combo.addItem(
                        f"{contrat.vehicle.immatriculation} - {contrat.vehicle.marque} {contrat.vehicle.modele}",
                        contrat.vehicle.id
                    )
                    self.vehicule_combo.setEnabled(True)
                else:
                    self.vehicule_combo.setEnabled(False)
            else:
                self.vehicule_combo.setEnabled(False)
        except Exception as e:
            print(f"Erreur chargement véhicules: {e}")
    
    def load_clients(self):
        """Charge les clients disponibles"""
        try:
            from addons.Automobiles.models.contact_models import Contact
            clients = self.controller.session.query(Contact).all()
            for client in clients:
                label = f"{client.nom} {client.prenom or ''} - {client.telephone or ''}"
                self.client_combo.addItem(label.strip(), client.id)
        except Exception as e:
            print(f"Erreur chargement clients: {e}")
    
    def load_assignees(self):
        """Charge les utilisateurs disponibles"""
        try:
            from core.models import User
            users = self.controller.session.query(User).all()
            for user in users:
                self.assignee_combo.addItem(f"{user.username} ({user.role})", user.id)
        except Exception as e:
            print(f"Erreur chargement assignees: {e}")
    
    # ============================================================================
    # MÉTHODES UTILITAIRES
    # ============================================================================
    
    def _get_type_label(self, type_enum):
        """Retourne le libellé d'un type de sinistre"""
        labels = {
            TypeSinistre.ACCIDENT: "Accident",
            TypeSinistre.VOL: "Vol",
            TypeSinistre.INCENDIE: "Incendie",
            TypeSinistre.DEGAT_NATUREL: "Dégât naturel",
            TypeSinistre.BRIS_GLACE: "Bris de glace",
            TypeSinistre.VANDALISME: "Vandalisme",
            TypeSinistre.COLLISION: "Collision",
            TypeSinistre.AUTRE: "Autre"
        }
        return labels.get(type_enum, str(type_enum))
    
    # ============================================================================
    # VALIDATION ET SAUVEGARDE
    # ============================================================================
    
    def validate_form(self):
        """Valide les champs obligatoires"""
        # Contrat
        if self.contrat_combo.currentIndex() <= 0:
            QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un contrat")
            self.tabs.setCurrentIndex(0)
            self.contrat_combo.setFocus()
            return False
        
        # Véhicule
        if self.vehicule_combo.currentIndex() <= 0:
            QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un véhicule")
            self.tabs.setCurrentIndex(0)
            self.vehicule_combo.setFocus()
            return False
        
        # Client
        if self.client_combo.currentIndex() <= 0:
            QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un client")
            self.tabs.setCurrentIndex(0)
            self.client_combo.setFocus()
            return False
        
        # Type
        if self.type_combo.currentIndex() <= 0:
            QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un type de sinistre")
            self.tabs.setCurrentIndex(0)
            self.type_combo.setFocus()
            return False
        
        # Date
        if not self.date_survenue.dateTime().isValid():
            QMessageBox.warning(self, "Champ requis", "Veuillez saisir une date de survenue valide")
            self.tabs.setCurrentIndex(0)
            self.date_survenue.setFocus()
            return False
        
        return True
    
    def get_form_data(self):
        """Récupère les données du formulaire"""
        data = {
            'contrat_id': self.contrat_combo.currentData(),
            'vehicule_id': self.vehicule_combo.currentData(),
            'client_id': self.client_combo.currentData(),
            'type': self.type_combo.currentData() or 'autre',
            'date_survenue': self.date_survenue.dateTime().toPython(),
            'lieu': self.lieu_edit.text().strip() or None,
            'ville': self.ville_edit.text().strip() or None,
            'pays': self.pays_edit.text().strip() or "Cameroun",
            'conditions_meteo': self.meteo_combo.currentText().replace("☀️", "").replace("🌧️", "").replace("☁️", "").replace("🌫️", "").replace("🌙", "").strip() or None,
            'description': self.description_edit.toPlainText().strip() or None,
            'circonstances': self.circonstances_edit.toPlainText().strip() or None,
            'responsabilite': self.responsabilite_combo.currentData(),
            'tiers_nom': self.tiers_nom_edit.text().strip() or None,
            'tiers_prenom': self.tiers_prenom_edit.text().strip() or None,
            'tiers_telephone': self.tiers_telephone_edit.text().strip() or None,
            'tiers_assurance': self.tiers_assurance_edit.text().strip() or None,
            'tiers_police': self.tiers_police_edit.text().strip() or None,
            'tiers_vehicule': self.tiers_vehicule_edit.text().strip() or None,
            'temoins_noms': self.temoins_noms_edit.toPlainText().strip() or None,
            'temoins_nombre': self.temoins_nombre_spin.value(),
            'estimation_preliminaire': self.estimation_preliminaire.value(),
            'franchise': self.franchise_spin.value(),
            'assigned_to': self.assignee_combo.currentData() or None,
            'notes': self.notes_edit.toPlainText().strip() or None,
            'creer_expertise': True
        }
        
        # Champs en mode édition
        if self.is_edit:
            data['statut'] = self.statut_combo.currentText() if hasattr(self, 'statut_combo') else None
            if hasattr(self, 'estimation_finale'):
                data['estimation_finale'] = self.estimation_finale.value()
            if hasattr(self, 'montant_indemnise'):
                data['montant_indemnise'] = self.montant_indemnise.value()
        
        return data
    
    def save_sinistre(self):
        """Sauvegarde le sinistre"""
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        
        try:
            if self.is_edit:
                success = self.controller.update(self.sinistre.id, data)
                message = "Sinistre mis à jour avec succès"
                sinistre = self.sinistre
            else:
                sinistre = self.controller.create(data)
                success = sinistre is not None
                message = "Sinistre déclaré avec succès"
            
            if success:
                QMessageBox.information(self, "✅ Succès", message)
                self.sinistre_saved.emit(sinistre)
                self.accept()
            else:
                QMessageBox.critical(self, "❌ Erreur", "Erreur lors de l'enregistrement du sinistre")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Erreur: {str(e)}")