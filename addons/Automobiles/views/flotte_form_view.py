from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QFrame, 
                             QGraphicsDropShadowEffect, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QScrollArea, QListWidget, QListWidgetItem, QWidget, QMessageBox, QDateEdit,
                             QSplitter, QGroupBox)
from PySide6.QtCore import QDate, Qt, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QIcon, QPixmap, QFont, QPalette, QLinearGradient, QBrush
import os

class FleetForm(QDialog):
    def __init__(self, controller, current_fleet=None, parent=None, contacts_list=None, compagnies_list=None, mode="add"):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.controller = controller 
        self.current_fleet = current_fleet
        self.contacts_list = contacts_list or []
        self.compagnies_list = compagnies_list or []
        self.mode = "update" if current_fleet else mode
        self.drag_pos = QPoint()
        self.is_maximized = False
        self.normal_geometry = None
        
        self.setup_ui()
        
        # Supprimer l'animation problématique
        # Utiliser un effet d'apparition simple via show() normal

        if self.current_fleet:
            self.load_data(self.current_fleet)
            self.setWindowTitle(f"Modifier la Flotte : {self.current_fleet.nom_flotte}")
            self.btn_save.setText("💾 METTRE À JOUR LA FLOTTE")

        if self.mode == "view":
            self.freeze_ui()

    def setup_ui(self):
        # Taille dynamique
        self.resize(1000, 850)
        self.setMinimumSize(900, 700)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Carte principale
        self.card = QFrame()
        self.card.setObjectName("FleetCard")
        self.card.setStyleSheet("""
            QFrame#FleetCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-radius: 24px;
                border: 1px solid rgba(0,0,0,0.08);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # --- HEADER MODERNE ---
        header_widget = QFrame()
        header_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-top-left-radius: 24px;
                border-top-right-radius: 24px;
            }
        """)
        header_widget.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 20, 0)
        
        # Titre avec icône
        title_icon = "🏢" if self.mode != "view" else "🔍"
        title_text = QLabel(f"{title_icon} Configuration de la Flotte")
        title_text.setStyleSheet("""
            font-size: 20px;
            font-weight: 800;
            color: white;
            font-family: 'Segoe UI', 'Arial';
            letter-spacing: 0.5px;
        """)
        
        # Boutons de contrôle
        btn_style = """
            QPushButton {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
            QPushButton#closeBtn:hover {
                background: #ff4757;
            }
        """
        
        self.btn_minimize = QPushButton("─")
        self.btn_minimize.setFixedSize(32, 32)
        self.btn_minimize.setStyleSheet(btn_style)
        self.btn_minimize.clicked.connect(self.showMinimized)
        
        self.btn_maximize = QPushButton("□")
        self.btn_maximize.setFixedSize(32, 32)
        self.btn_maximize.setStyleSheet(btn_style)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setStyleSheet(btn_style)
        self.btn_close.clicked.connect(self.reject)
        
        header_layout.addWidget(title_text)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_minimize)
        header_layout.addWidget(self.btn_maximize)
        header_layout.addWidget(self.btn_close)
        
        card_layout.addWidget(header_widget)

        # --- CONTENU SCROLLABLE ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0aec0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(content_widget)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(25)

        # Style commun pour les groupes
        group_style = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #4a5568;
            }
        """
        
        # Styles des champs
        field_style = """
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
                color: #2d3748;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #667eea;
                background-color: #faf5ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 13px;
                margin-bottom: 5px;
            }
        """
        
        # === SECTION 1: INFORMATIONS GÉNÉRALES ===
        group_info = QGroupBox("📋 Informations Générales")
        group_info.setStyleSheet(group_style)
        info_layout = QGridLayout(group_info)
        info_layout.setSpacing(20)
        info_layout.setContentsMargins(25, 25, 25, 25)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: SABC Logistique")
        self.name_input.setStyleSheet(field_style)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: FL-SABC-2024")
        self.code_input.setStyleSheet(field_style)
        
        info_layout.addWidget(self.create_label_with_icon("🏷️", "Nom de la Flotte"), 0, 0)
        info_layout.addWidget(self.create_label_with_icon("🔢", "Code / Référence"), 0, 1)
        info_layout.addWidget(self.name_input, 1, 0)
        info_layout.addWidget(self.code_input, 1, 1)
        
        form_layout.addWidget(group_info)
        
        # === SECTION 2: CLIENT ===
        group_client = QGroupBox("👤 Client")
        group_client.setStyleSheet(group_style)
        client_layout = QVBoxLayout(group_client)
        client_layout.setSpacing(15)
        client_layout.setContentsMargins(25, 25, 25, 25)
        
        # Barre de recherche stylisée
        self.owner_search = QLineEdit()
        self.owner_search.setPlaceholderText("🔍 Rechercher un client (Nom, téléphone, ou n° de pièce)...")
        self.owner_search.setStyleSheet(field_style + """
            QLineEdit {
                background: #f7fafc;
                font-size: 13px;
            }
        """)
        self.owner_search.textChanged.connect(self.filter_contacts)
        client_layout.addWidget(self.owner_search)
        
        # Splitter moderne pour liste et carte
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; width: 2px; margin: 10px 0; }")
        
        # Liste des clients
        self.client_list_widget = QListWidget()
        self.client_list_widget.setStyleSheet("""
            QListWidget {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background: white;
                outline: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background: #f7fafc;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
        """)
        self.client_list_widget.currentRowChanged.connect(self.display_client_details)
        splitter.addWidget(self.client_list_widget)
        
        # Carte client moderne
        self.client_card = QFrame()
        self.client_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fef9e7, stop:1 #faf5ff);
                border-radius: 16px;
                border: 2px solid #e2e8f0;
            }
        """)
        card_layout_client = QHBoxLayout(self.client_card)
        card_layout_client.setContentsMargins(20, 20, 20, 20)
        card_layout_client.setSpacing(15)
        
        # Photo
        self.client_photo = QLabel()
        self.client_photo.setFixedSize(100, 100)
        self.client_photo.setStyleSheet("""
            QLabel {
                background: white;
                border-radius: 50px;
                border: 3px solid #e2e8f0;
            }
        """)
        self.client_photo.setAlignment(Qt.AlignCenter)
        card_layout_client.addWidget(self.client_photo)
        
        # Détails
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(8)
        
        self.lbl_card_name = QLabel("SÉLECTIONNEZ UN CLIENT")
        self.lbl_card_name.setStyleSheet("font-size: 16px; font-weight: 800; color: #2d3748;")
        
        self.lbl_card_info = QLabel("Détails : ---\nTel : ---\nAdresse : ---")
        self.lbl_card_info.setStyleSheet("font-size: 12px; color: #718096; line-height: 1.5;")
        self.lbl_card_info.setWordWrap(True)
        
        details_layout.addWidget(self.lbl_card_name)
        details_layout.addWidget(self.lbl_card_info)
        details_layout.addStretch()
        
        card_layout_client.addWidget(details_widget, 1)
        splitter.addWidget(self.client_card)
        
        splitter.setSizes([350, 450])
        client_layout.addWidget(splitter)
        form_layout.addWidget(group_client)
        
        # === SECTION 3: ASSURANCE ET CONTRAT ===
        group_contract = QGroupBox("📄 Contrat & Assurance")
        group_contract.setStyleSheet(group_style)
        contract_layout = QGridLayout(group_contract)
        contract_layout.setSpacing(20)
        contract_layout.setContentsMargins(25, 25, 25, 25)
        
        # Assureur
        contract_layout.addWidget(self.create_label_with_icon("🏦", "Assureur Principal"), 0, 0)
        self.assureur_input = QComboBox()
        self.assureur_input.setStyleSheet(field_style)
        for cie in self.compagnies_list:
            self.assureur_input.addItem(cie.nom, cie.id)
        contract_layout.addWidget(self.assureur_input, 1, 0)
        
        # Mode de facturation
        contract_layout.addWidget(self.create_label_with_icon("💰", "Mode de Facturation"), 0, 1)
        self.combo_mgmt = QComboBox()
        self.combo_mgmt.setStyleSheet(field_style)
        self.combo_mgmt.addItem("🚗 Individuelle (Par véhicule)", "PAR_VEHICULE")
        self.combo_mgmt.addItem("🌍 Globale (Prime de flotte)", "GLOBAL")
        contract_layout.addWidget(self.combo_mgmt, 1, 1)
        
        # Dates
        contract_layout.addWidget(self.create_label_with_icon("📅", "Début Contrat"), 2, 0)
        contract_layout.addWidget(self.create_label_with_icon("📅", "Fin Contrat"), 2, 1)
        
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setStyleSheet(field_style)
        contract_layout.addWidget(self.date_debut, 3, 0)
        
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addYears(1))
        self.date_fin.setStyleSheet(field_style)
        contract_layout.addWidget(self.date_fin, 3, 1)
        
        # Statut et Remise
        contract_layout.addWidget(self.create_label_with_icon("📊", "Statut de la Flotte"), 4, 0)
        contract_layout.addWidget(self.create_label_with_icon("🎁", "Remise Commerciale (%)"), 4, 1)
        
        self.status_combo = QComboBox()
        self.status_combo.setStyleSheet(field_style)
        self.status_combo.addItems(["Actif", "En attente", "Résilié", "Bloqué"])
        contract_layout.addWidget(self.status_combo, 5, 0)
        
        self.remise_input = QLineEdit()
        self.remise_input.setPlaceholderText("0.00")
        self.remise_input.setStyleSheet(field_style)
        contract_layout.addWidget(self.remise_input, 5, 1)
        
        form_layout.addWidget(group_contract)
        
        # === SECTION 4: VÉHICULES ===
        group_vehicles = QGroupBox("🚗 Véhicules")
        group_vehicles.setStyleSheet(group_style)
        vehicles_layout = QVBoxLayout(group_vehicles)
        vehicles_layout.setSpacing(15)
        vehicles_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header avec total
        header_vehicles = QHBoxLayout()
        header_vehicles.addWidget(QLabel("Sélectionnez les véhicules de la flotte"))
        header_vehicles.addStretch()
        
        self.total_prime_lbl = QLabel("Total Primes : 0 FCFA")
        self.total_prime_lbl.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            color: #48bb78;
            background: #f0fff4;
            padding: 8px 16px;
            border-radius: 12px;
        """)
        header_vehicles.addWidget(self.total_prime_lbl)
        vehicles_layout.addLayout(header_vehicles)
        
        # Barre de recherche
        self.vehicle_search = QLineEdit()
        self.vehicle_search.setPlaceholderText("🔍 Rechercher un véhicule à ajouter...")
        self.vehicle_search.setStyleSheet(field_style)
        self.vehicle_search.textChanged.connect(self.filter_vehicles)
        vehicles_layout.addWidget(self.vehicle_search)
        
        # Tableau moderne
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background: white;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #4a5568;
            }
        """)
        self.vehicle_table.setColumnCount(10)
        self.vehicle_table.setHorizontalHeaderLabels(["Sélection", "Immatriculation", " 💰 R.Civile", "⚖️ Déf.Recours", "🚗 V.partie", 
                                                      "🔫 V.Braquage", "🔥 Incendie", "🪟 B.Glace", "🔧 A.Réparation", "💥 D.Accidents", "👥 IPT"])
        self.vehicle_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vehicle_table.setAlternatingRowColors(True)
        self.vehicle_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicle_table.setMinimumHeight(300)
        self.vehicle_table.itemChanged.connect(self.calculate_totals)
        
        vehicles_layout.addWidget(self.vehicle_table)
        form_layout.addWidget(group_vehicles)
        self.vehicle_table.itemChanged.connect(self.calculate_totals_on_change)
        
        # === SECTION 5: OBSERVATIONS ===
        group_obs = QGroupBox("📝 Observations")
        group_obs.setStyleSheet(group_style)
        obs_layout = QVBoxLayout(group_obs)
        obs_layout.setContentsMargins(25, 25, 25, 25)
        
        self.obs_input = QTextEdit()
        self.obs_input.setPlaceholderText("Notes de couverture, remarques particulières...")
        self.obs_input.setStyleSheet(field_style + """
            QTextEdit {
                min-height: 80px;
            }
        """)
        obs_layout.addWidget(self.obs_input)
        form_layout.addWidget(group_obs)
        
        # === BOUTON D'ACTION ===
        self.btn_save = QPushButton("💾 ENREGISTRER LA FLOTTE")
        self.btn_save.setObjectName("SaveBtn")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 16px;
                padding: 16px;
                margin-top: 10px;
                font-family: 'Segoe UI';
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            QPushButton:pressed {
                padding-top: 17px;
                padding-bottom: 15px;
            }
        """)
        self.btn_save.clicked.connect(self.validate_and_save)
        form_layout.addWidget(self.btn_save)
        
        scroll.setWidget(content_widget)
        card_layout.addWidget(scroll)
        main_layout.addWidget(self.card)
        
        self.populate_vehicles()

    def create_label_with_icon(self, icon, text):
        """Crée un label avec icône et texte"""
        label = QLabel(f"{icon} {text}")
        label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 4px;
        """)
        return label

    def toggle_maximize(self):
        """Bascule entre mode normal et plein écran"""
        if self.is_maximized:
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.btn_maximize.setText("□")
        else:
            self.normal_geometry = self.geometry()
            # Obtenir la géométrie de l'écran actuel
            screen_geometry = self.screen().availableGeometry()
            self.setGeometry(screen_geometry)
            self.btn_maximize.setText("❐")
        self.is_maximized = not self.is_maximized

    def mousePressEvent(self, event):
        """Gère le déplacement de la fenêtre"""
        if event.button() == Qt.LeftButton and not self.is_maximized:
            # Vérifier qu'on n'est pas sur un bouton ou un champ interactif
            child = self.childAt(event.pos())
            if not isinstance(child, (QPushButton, QLineEdit, QComboBox, QTextEdit, QTableWidget, QListWidget)):
                self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """Déplace la fenêtre"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos') and not self.is_maximized:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    # ... (toutes les autres méthodes existantes restent identiques)
    def populate_vehicles(self):
        """
        Remplit le tableau, calcule les totaux par ligne et ajoute 
        une ligne de pied de page avec les totaux par colonne.
        """
        try:
            # 1. Préparation de la table
            self.vehicle_table.blockSignals(True)
            self.vehicle_table.clearSpans() # Important pour réinitialiser les fusions
            self.vehicle_table.setRowCount(0)
            
            # Récupération des données depuis le contrôleur
            vehicles = self.controller.fleets.get_all_vehicles()
            num_v = len(vehicles)
            
            # On définit le nombre de lignes : Véhicules + 1 ligne pour le TOTAL
            self.vehicle_table.setRowCount(num_v + 1)

            # Dictionnaire pour stocker les sommes verticales (Colonnes 3 à 11)
            col_totals = {i: 0.0 for i in range(3, 12)}

            # 2. Remplissage des lignes de véhicules
            for row, v in enumerate(vehicles):
                # --- Colonne 0 : Checkbox ---
                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                # On vérifie si le véhicule appartient déjà à la flotte actuelle
                state = Qt.Checked if (self.current_fleet and v.fleet_id == self.current_fleet.id) else Qt.Unchecked
                check_item.setCheckState(state)
                check_item.setData(Qt.UserRole, v.id) # Stocke l'ID du véhicule
                self.vehicle_table.setItem(row, 0, check_item)

                # --- Colonnes 1 & 2 : Infos ---
                self.vehicle_table.setItem(row, 1, QTableWidgetItem(str(v.immatriculation)))
                self.vehicle_table.setItem(row, 2, QTableWidgetItem(str(v.marque or "N/A")))

                # --- Colonnes 3 à 10 : Garanties ---
                # Mapping pour simplifier la boucle (Index Col : Valeur)
                guarantees = {
                    3: v.amt_rc, 4: v.amt_dr, 5: v.amt_vol, 6: v.amt_vb,
                    7: v.amt_in, 8: v.amt_bris, 9: v.amt_ar, 10: v.amt_dta
                }

                row_sum = 0.0
                for col_idx, val in guarantees.items():
                    amt = float(val or 0)
                    self.vehicle_table.setItem(row, col_idx, self.create_num_item(amt))
                    row_sum += amt
                    # On cumule pour le total vertical si coché (optionnel au chargement)
                    if state == Qt.Checked:
                        col_totals[col_idx] += amt

                # --- Colonne 11 : Total par Véhicule ---
                total_item = self.create_num_item(row_sum)
                total_item.setFont(QFont("Arial", 9, QFont.Bold))
                self.vehicle_table.setItem(row, 11, total_item)
                if state == Qt.Checked:
                    col_totals[11] += row_sum

            # --- 3. CONFIGURATION DE LA LIGNE DE PIED DE PAGE (FOOTER) ---
            last_row = num_v
            
            # Fusion des colonnes 0 et 1 pour le design
            self.vehicle_table.setSpan(last_row, 0, 1, 2)
            
            # Cellule vide fusionnée (style)
            empty_item = QTableWidgetItem("")
            empty_item.setBackground(QColor("#f8fafc"))
            empty_item.setFlags(Qt.NoItemFlags)
            self.vehicle_table.setItem(last_row, 0, empty_item)

            # Label "TOTAL FLOTTE" en colonne 2
            lbl_footer = QTableWidgetItem("TOTAL SÉLECTION")
            lbl_footer.setFont(QFont("Arial", 10, QFont.Bold))
            lbl_footer.setTextAlignment(Qt.AlignCenter)
            lbl_footer.setBackground(QColor("#f1f5f9"))
            self.vehicle_table.setItem(last_row, 2, lbl_footer)

            # Remplissage des totaux verticaux (Colonnes 3 à 11)
            for col_idx, total_val in col_totals.items():
                footer_item = self.create_num_item(total_val)
                footer_item.setBackground(QColor("#e2e8f0")) # Fond plus sombre pour le pied
                footer_item.setFont(QFont("Arial", 10, QFont.Bold))
                footer_item.setForeground(QColor("#1e293b"))
                self.vehicle_table.setItem(last_row, col_idx, footer_item)

            self.vehicle_table.blockSignals(False)
            
            # Mise à jour du résumé textuel externe
            self.calculate_totals_on_change(None) 

        except Exception as e:
            print(f"❌ Erreur critique populate_vehicles : {e}")
            if hasattr(self, 'vehicle_table'):
                self.vehicle_table.blockSignals(False)

    def create_num_item(self, val):
        """
        Méthode utilitaire pour créer un item de tableau formaté pour la monnaie.
        """
        # On formate avec séparateur de milliers (espace)
        formatted_val = f"{val:,.0f}".replace(",", " ")
        item = QTableWidgetItem(formatted_val)
        
        # Alignement à droite pour les chiffres
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Stockage de la valeur brute pour les calculs (évite les erreurs NoneType)
        item.setData(Qt.UserRole, float(val or 0))
        
        return item
    
    def calculate_totals(self, item=None):
        """Additionne les montants des véhicules cochés sans crasher sur None."""
        total_global = 0
        count = 0
        
        for row in range(self.vehicle_table.rowCount()):
            check_item = self.vehicle_table.item(row, 0)
            
            # On vérifie si la ligne est cochée
            if check_item and check_item.checkState() == Qt.Checked:
                # On récupère l'item du montant (colonne 3)
                amt_item = self.vehicle_table.item(row, 3)
                
                if amt_item:
                    # On récupère la donnée brute stockée dans UserRole
                    raw_data = amt_item.data(Qt.UserRole)
                    
                    # Sécurité : si la donnée est None ou invalide, on prend 0
                    try:
                        amt_value = int(raw_data) if raw_data is not None else 0
                    except (ValueError, TypeError):
                        amt_value = 0
                    
                    total_global += amt_value
                    count += 1
        
        # Affichage formaté
        formatted_total = f"{total_global:,.0f}".replace(",", " ")
        self.total_prime_lbl.setText(f"Total Primes ({count}) : {formatted_total} FCFA")

    def filter_vehicles(self, text):
        """Filtre les véhicules dans le tableau"""
        for row in range(self.vehicle_table.rowCount()):
            immat = self.vehicle_table.item(row, 1).text().lower()
            marque = self.vehicle_table.item(row, 2).text().lower()
            show = text.lower() in immat or text.lower() in marque
            self.vehicle_table.setRowHidden(row, not show)

    def get_selected_vehicle_ids(self):
        """Retourne la liste des IDs des véhicules sélectionnés"""
        selected_ids = []
        for row in range(self.vehicle_table.rowCount()):
            item = self.vehicle_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                selected_ids.append(item.data(Qt.UserRole))
        return selected_ids

    def load_data(self, fleet):
        """Charge les données d'une flotte existante"""
        self.name_input.setText(fleet.nom_flotte)
        self.code_input.setText(getattr(fleet, 'code', ""))
        self.obs_input.setPlainText(getattr(fleet, 'observations', ""))

    def validate_and_save(self):
        """Valide et sauvegarde les données"""
        try:
            data = self.get_form_data()

            if not data["nom_flotte"]:
                QMessageBox.warning(self, "Attention", "Le nom de la flotte est requis.")
                return

            if not data["code_flotte"]:
                QMessageBox.warning(self, "Attention", "Le code de la flotte est requis pour garantir l'unicité.")
                return
            
            vehicle_ids = self.get_selected_vehicle_ids()
            user_id = getattr(self.parent(), 'current_user_id', 1) 

            if self.mode == "update":
                success, msg = self.controller.fleets.update_fleet_data(self.current_fleet.id, data)
                
                if success:
                    self.controller.fleets.update_fleet_vehicles(self.current_fleet.id, vehicle_ids, user_id)
            else:
                success, msg = self.controller.fleets.create_fleet(data, user_id)
                if success and isinstance(msg, int):
                    self.controller.fleets.update_fleet_vehicles(msg, vehicle_ids, user_id)

            if success:
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", f"Erreur contrôleur: {msg}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", str(e))

    def get_form_data(self):
        """Récupère les données du formulaire"""
        remise_text = self.remise_input.text().strip()
        try:
            remise_val = float(remise_text) if remise_text else 0.0
        except ValueError:
            remise_val = 0.0

        return {
            "nom_flotte": self.name_input.text().strip(),
            "code_flotte": self.code_input.text().strip(),
            "owner_id": self.owner_search.text().strip(),
            "assureur": self.assureur_input.currentData(),
            "type_gestion": self.combo_mgmt.currentText(),
            "remise_flotte": remise_val,
            "statut": self.status_combo.currentText(),
            "is_active": self.status_combo.currentText() == "Actif",
            "date_debut": self.date_debut.date().toPython(),
            "date_fin": self.date_fin.date().toPython(),
            "observations": self.obs_input.toPlainText().strip()
        }
    
    def filter_contacts(self, text):
        """Filtre les contacts selon la recherche"""
        self.client_list_widget.clear()
        if len(text) < 2:
            return
        
        clients = self.controller.contacts.get_contacts_for_combo(text)
        
        for client in clients:
            if isinstance(client, tuple):
                name_display = f"{client[0]} {client[1] if len(client) > 1 else ''}"
            else:
                name_display = f"{client.nom} {client.nature or ''}"
                
            item = QListWidgetItem(name_display)
            item.setData(Qt.UserRole, client)
            self.client_list_widget.addItem(item)

    def display_client_details(self, row):
        """Affiche les détails du client sélectionné"""
        if row < 0:
            return
        
        item = self.client_list_widget.currentItem()
        if not item:
            return
        client = item.data(Qt.UserRole)
        
        self.selected_cie_id = client.id
        
        name_html = (
            f"<div style='color: #2c3e50; font-size: 18px; font-weight: bold;'>"
            f"{client.nom.upper()}</div>"
            f"<div style='color: #7f8c8d; font-size: 12px;'>ID: {client.id or 'N/A'}</div>"
        )
        self.lbl_card_name.setText(name_html)

        info_text = f"""
            <table width="100%" style="margin-top: 10px;">
                <tr>
                    <td style="color: #95a5a6; font-size: 11px;">📌 NATURE</td>
                    <td style="color: #34495e; font-weight: 500;">{getattr(client, 'nature', 'Compagnie')}</td>
                </tr>
                <tr>
                    <td style="color: #95a5a6; font-size: 11px; padding-top: 5px;">📞 TÉLÉPHONE</td>
                    <td style="color: #34495e; font-weight: 500; padding-top: 5px;">{client.telephone or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="color: #95a5a6; font-size: 11px; padding-top: 5px;">📧 EMAIL</td>
                    <td style="color: #34495e; font-weight: 500; padding-top: 5px;">{client.email or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="color: #95a5a6; font-size: 11px; padding-top: 5px;">📍 ADRESSE</td>
                    <td style="color: #34495e; font-weight: 500; padding-top: 5px;">{client.adresse or 'N/A'}</td>
                </tr>
            </table>
        """
        self.lbl_card_info.setText(info_text)

        if hasattr(client, 'photo_path') and client.photo_path and os.path.exists(client.photo_path):
            pixmap = QPixmap(client.photo_path)
            self.client_photo.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.client_photo.setAlignment(Qt.AlignCenter)
            self.client_photo.setStyleSheet("""
                background-color: #ecf0f1; 
                border-radius: 50px; 
                color: #bdc3c7; 
                font-size: 50px;
                border: 3px solid #e2e8f0;
            """)
            self.client_photo.setText("👤")

    def freeze_ui(self):
        """Désactive tous les champs pour le mode visualisation"""
        for widget in self.findChildren((QLineEdit, QComboBox, QTextEdit, QDateEdit, QTableWidget)):
            widget.setEnabled(False)
        self.btn_save.setEnabled(False)

    def calculate_totals_on_change(self, item):
        """Réagit au cochage/décochage d'une ligne."""
        # On ne réagit que si c'est la colonne 0 (la checkbox) qui change
        if item is None or item.column() != 0:
            return

        try:
            self.vehicle_table.blockSignals(True) # Évite les boucles infinies
            
            num_rows = self.vehicle_table.rowCount()
            if num_rows <= 1: return # Pas de données ou juste le footer
            
            last_row = num_rows - 1
            # Initialisation des compteurs pour les colonnes 3 à 11
            new_totals = {i: 0.0 for i in range(3, 12)}
            selected_count = 0

            # Parcourir toutes les lignes sauf la dernière (le footer)
            for row in range(last_row):
                check_item = self.vehicle_table.item(row, 0)
                if check_item and check_item.checkState() == Qt.Checked:
                    selected_count += 1
                    # Sommer les valeurs de chaque colonne de montant
                    for col in range(3, 12):
                        cell = self.vehicle_table.item(row, col)
                        if cell:
                            # On récupère la valeur brute stockée dans UserRole
                            val = float(cell.data(Qt.UserRole) or 0)
                            new_totals[col] += val

            # Mettre à jour la ligne de Pied de Page (Footer)
            for col, total_val in new_totals.items():
                footer_item = self.vehicle_table.item(last_row, col)
                if footer_item:
                    formatted_val = f"{total_val:,.0f}".replace(",", " ")
                    footer_item.setText(formatted_val)
                    footer_item.setData(Qt.UserRole, total_val)

            # Mettre à jour le label de résumé global en bas de l'écran
            total_global = new_totals[11]
            self.total_prime_lbl.setText(
                f"Total Primes ({selected_count} véhicules) : {total_global:,.0f} FCFA".replace(",", " ")
            )

            self.vehicle_table.blockSignals(False)

            self.refresh_footer_totals()
            
        except Exception as e:
            print(f"❌ Erreur lors de l'actualisation : {e}")
            self.vehicle_table.blockSignals(False)

    def refresh_footer_totals(self):
        """Calcule les sommes de la table et met à jour la ligne de pied de page."""
        try:
            self.vehicle_table.blockSignals(True)
            
            num_rows = self.vehicle_table.rowCount()
            if num_rows <= 1: 
                self.vehicle_table.blockSignals(False)
                return
            
            last_row = num_rows - 1
            new_totals = {i: 0.0 for i in range(3, 12)}
            selected_count = 0

            # Boucle sur les véhicules (on ignore la dernière ligne qui est le total)
            for row in range(last_row):
                check_item = self.vehicle_table.item(row, 0)
                if check_item and check_item.checkState() == Qt.Checked:
                    selected_count += 1
                    for col in range(3, 12):
                        cell = self.vehicle_table.item(row, col)
                        if cell:
                            val = float(cell.data(Qt.UserRole) or 0)
                            new_totals[col] += val

            # Mise à jour graphique de la dernière ligne (Footer)
            for col, total_val in new_totals.items():
                footer_item = self.vehicle_table.item(last_row, col)
                if footer_item:
                    txt = f"{total_val:,.0f}".replace(",", " ")
                    footer_item.setText(txt)
                    footer_item.setData(Qt.UserRole, total_val)

            # Mise à jour du label externe
            total_global = new_totals[11]
            self.total_prime_lbl.setText(
                f"Total Primes ({selected_count} véhicules) : {total_global:,.0f} FCFA".replace(",", " ")
            )

            self.vehicle_table.blockSignals(False)
        except Exception as e:
            print(f"Erreur refresh_footer: {e}")
            self.vehicle_table.blockSignals(False)