from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QFrame, 
                             QGraphicsDropShadowEffect, QTextEdit, QCheckBox, 
                             QScrollArea, QListWidget, QListWidgetItem, QWidget, QMessageBox, QDateEdit)
from PySide6.QtCore import QDate, Qt, QPoint
from PySide6.QtGui import QColor, QIcon

class FleetForm(QDialog):
    def __init__(self, fleet_controller, vehicle_controller, current_fleet=None, parent=None, contacts_list=None, compagnies_list=None, mode="add"):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.fleet_controller = fleet_controller
        self.vehicle_controller = vehicle_controller 
        self.current_fleet = current_fleet
        self.contacts_list = contacts_list or []
        self.compagnies_list = compagnies_list or []
        self.mode = "update" if current_fleet else mode
        self.drag_pos = QPoint()
        
        self.setup_ui()

        if self.current_fleet:
            self.load_data(self.current_fleet)
            self.setWindowTitle(f"Modifier la Flotte : {self.current_fleet.name}")
            self.btn_save.setText("💾 METTRE À JOUR LA FLOTTE")

        if self.mode == "view":
            self.freeze_ui()

    def setup_ui(self):
        # Taille augmentée pour accueillir la liste des véhicules
        self.setFixedSize(700, 850)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.card = QFrame()
        self.card.setObjectName("FleetCard")
        self.card.setStyleSheet("""
            QFrame#FleetCard {
                background-color: #ffffff;
                border-radius: 20px;
                border: 1px solid #dfe6e9;
            }
            QLabel { color: #2d3436; font-weight: bold; font-size: 13px; }
            QLineEdit, QComboBox, QTextEdit, QDateEdit {
                border: 1px solid #dcdde1;
                border-radius: 10px;
                padding: 10px;
                background-color: #f5f6fa;
                font-size: 13px;
                color: #2f3640;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QScrollArea { border: none; background-color: transparent; }
            
            QListWidget {
                border: 1px solid #f1f2f6;
                border-radius: 10px;
                background-color: #ffffff;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f2f6;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: bold;
                border-radius: 8px;
            }
            
            /* ScrollBar Stylée */
            QScrollBar:vertical {
                border: none; background: #f1f2f6; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7; border-radius: 4px; min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #95a5a6; }

            QPushButton#SaveBtn {
                background-color: #00b894;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 12px;
                padding: 15px;
            }
            QPushButton#SaveBtn:hover { background-color: #00947a; }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30); shadow.setColor(QColor(0, 0, 0, 50)); shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 20, 30, 30)

        # --- HEADER ---
        header = QHBoxLayout()
        title_icon = "🏢" if self.mode != "view" else "🔍"
        title_text = QLabel(f"{title_icon} Configuration de la Flotte")
        title_text.setStyleSheet("font-size: 20px; color: #2d3436; font-weight: 800;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("background: transparent; color: #b2bec3; font-size: 22px; border: none;")
        self.btn_close.clicked.connect(self.reject)

        header.addWidget(title_text)
        header.addStretch()
        header.addWidget(self.btn_close)
        card_layout.addLayout(header)

        # --- SCROLL AREA POUR LE CONTENU ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        form_layout = QVBoxLayout(content_widget)
        form_layout.setSpacing(20)

        # 1. Infos Générales
        form_grid = QGridLayout()
        form_grid.setSpacing(15)

        form_grid.addWidget(QLabel("Nom de la Flotte"), 0, 0)
        form_grid.addWidget(QLabel("Code / Référence Unique"), 0, 1)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: SABC Logistique")
        form_grid.addWidget(self.name_input, 1, 0)


        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: FL-SABC-2024")
        form_grid.addWidget(self.code_input, 1, 1)

        form_layout.addLayout(form_grid)

        form_grid.addWidget(QLabel("Client / Entreprise Associée"), 2, 0, 1, 2)
        self.combo_owner = QComboBox()
        for cid, name in self.contacts_list:
            self.combo_owner.addItem(name, cid)
        form_grid.addWidget(self.combo_owner, 3, 0, 1, 2)

        # Ligne 4 & 5 : Assureur et Facturation
        form_grid.addWidget(QLabel("Assureur Principal"), 4, 0)
        form_grid.addWidget(QLabel("Mode de Facturation"), 4, 1)
        
        self.assureur_input = QComboBox()
        for cid, name in self.compagnies_list:
            self.assureur_input.addItem(name, cid)
        self.assureur_input.setPlaceholderText("Ex: AXA, ALLIANZ...")
        form_grid.addWidget(self.assureur_input, 5, 0)

        self.combo_mgmt = QComboBox()
        self.combo_mgmt.addItem("🚗 Individuelle (Par véhicule)", "PAR_VEHICULE")
        self.combo_mgmt.addItem("🌍 Globale (Prime de flotte)", "GLOBAL")
        form_grid.addWidget(self.combo_mgmt, 5, 1)

        # Ligne 6 & 7 : Dates de validité (Nouveau)
        form_grid.addWidget(QLabel("Début Contrat"), 6, 0)
        form_grid.addWidget(QLabel("Fin Contrat"), 6, 1)
        
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        form_grid.addWidget(self.date_debut, 7, 0)

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addYears(1))
        form_grid.addWidget(self.date_fin, 7, 1)

        # Ligne 8 & 9 : Statut et Remise (Nouveau)
        form_grid.addWidget(QLabel("Statut de la Flotte"), 8, 0)
        form_grid.addWidget(QLabel("Remise Commerciale (%)"), 8, 1)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Actif", "En attente", "Résilié", "Bloqué"])
        form_grid.addWidget(self.status_combo, 9, 0)

        self.remise_input = QLineEdit()
        self.remise_input.setPlaceholderText("0.00")
        form_grid.addWidget(self.remise_input, 9, 1)

        # 2. Section Véhicules (MODERNE)
        veh_section = QVBoxLayout()
        veh_header = QHBoxLayout()
        veh_header.addWidget(QLabel("🚗 Véhicules de la flotte"))
        self.count_lbl = QLabel("0 sélectionné(s)")
        self.count_lbl.setStyleSheet("color: #0984e3; font-weight: normal;")
        veh_header.addStretch()
        veh_header.addWidget(self.count_lbl)
        veh_section.addLayout(veh_header)

        self.vehicle_search = QLineEdit()
        self.vehicle_search.setPlaceholderText("🔍 Filtrer par immatriculation ou marque...")
        self.vehicle_search.textChanged.connect(self.filter_vehicles)
        veh_section.addWidget(self.vehicle_search)

        self.vehicle_list = QListWidget()
        self.vehicle_list.setSelectionMode(QListWidget.MultiSelection)
        self.vehicle_list.itemSelectionChanged.connect(self.update_selection_count)
        self.vehicle_list.setMinimumHeight(250)
        veh_section.addWidget(self.vehicle_list)
        
        form_layout.addLayout(veh_section)

        # 3. Observations
        form_layout.addWidget(QLabel("Note de couverture / Observations"))
        self.obs_input = QTextEdit()
        self.obs_input.setMaximumHeight(80)
        form_layout.addWidget(self.obs_input)

        scroll.setWidget(content_widget)
        card_layout.addWidget(scroll)

        # --- FOOTER ---
        self.btn_save = QPushButton("💾 Enregistrer les données")
        self.btn_save.setObjectName("SaveBtn")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.validate_and_save)
        card_layout.addWidget(self.btn_save)

        main_layout.addWidget(self.card)
        
        self.populate_vehicles()

    def populate_vehicles(self):
        """Remplit la liste via le vehicle_controller."""
        self.vehicle_list.clear()
        try:
            vehicles = self.vehicle_controller.get_all_vehicles()
            for v in vehicles:
                item = QListWidgetItem(f"🚘  {v.immatriculation}  |  {v.marque or 'N/A'}")
                item.setData(Qt.UserRole, v.id)
                
                # Cocher si appartient déjà à la flotte
                if self.current_fleet and v.fleet_id == self.current_fleet.id:
                    item.setSelected(True)
                self.vehicle_list.addItem(item)
            self.update_selection_count()
        except Exception as e:
            print(f"Erreur populate_vehicles: {e}")

    def filter_vehicles(self, text):
        for i in range(self.vehicle_list.count()):
            item = self.vehicle_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def update_selection_count(self):
        count = len(self.vehicle_list.selectedItems())
        self.count_lbl.setText(f"{count} sélectionné(s)")

    def get_selected_vehicle_ids(self):
        return [self.vehicle_list.item(i).data(Qt.UserRole) 
                for i in range(self.vehicle_list.count()) 
                if self.vehicle_list.item(i).isSelected()]

    def load_data(self, fleet):
        self.name_input.setText(fleet.name)
        self.code_input.setText(getattr(fleet, 'code', ""))
        self.obs_input.setPlainText(getattr(fleet, 'observations', ""))

    def validate_and_save(self):
        try:
            data = self.get_form_data()
            
            vehicle_ids = self.get_selected_vehicle_ids()

            if not data["nom_flotte"]:
                QMessageBox.warning(self, "Attention", "Le nom de la flotte est requis.")
                return

            vehicle_ids = self.get_selected_vehicle_ids()
            user_id = getattr(self.parent(), 'current_user_id', 1) 

            if self.mode == "update":
                success, msg = self.fleet_controller.update_fleet(self.current_fleet.id, data, user_id)
                if success:
                    self.fleet_controller.update_fleet_vehicles(self.current_fleet.id, vehicle_ids, user_id)
            else:
                success, msg = self.fleet_controller.create_fleet(data, user_id)
                # Si création réussie, on lie les véhicules à la nouvelle flotte
                if success and isinstance(msg, int):
                    self.fleet_controller.update_fleet_vehicles(msg, vehicle_ids, user_id)

            if success:
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", f"Erreur contrôleur: {msg}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", str(e))

    # --- LOGIQUE DE DÉPLACEMENT ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def get_form_data(self):
        return {
            "nom_flotte": self.name_input.text().strip(), # Doit correspondre au data.get('nom_flotte') du contrôleur
            "code_flotte": self.code_input.text().strip(),
            "owner_id": self.combo_owner.currentData(),
            "assureur": self.assureur_input.currentData(),
            "type_gestion": self.combo_mgmt.currentText(),
            "remise_flotte": self.remise_input.text(),
            "statut": self.status_combo.currentText(),
            "is_active": self.status_combo.currentText() == "Actif",
            "date_debut": self.date_debut.date().toPython(),
            "date_fin": self.date_fin.date().toPython(),
            "observations": self.obs_input.toPlainText().strip()
        }
    
    def get_selected_vehicle_ids(self):
        """Retourne la liste des IDs [1, 5, 12...] sélectionnés dans la liste."""
        selected_ids = []
        for i in range(self.vehicle_list.count()):
            item = self.vehicle_list.item(i)
            if item.isSelected():
                selected_ids.append(item.data(Qt.UserRole)) # On récupère l'ID stocké
        return selected_ids