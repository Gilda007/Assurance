from PySide6.QtWidgets import (QDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
                             QLineEdit, QFrame, QTabWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from addons.Automobiles.views.audit_auto_view import AuditLogDialog
from addons.Automobiles.views.flotte_form_view import FleetForm
from addons.Automobiles.views.automobile_form_view import VehicleForm
from addons.Automobiles.views.vehicle_detail_view import VehicleDetailView
import os
from core.logger import logger

class VehiculeModuleView(QWidget):
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.session = controller
        self.current_user = current_user
        self.controller=controller
        # self.vehicle_service = VehicleController(self.session)
        # self.fleet_service = FleetController(self.session, current_user_id=None)
        # self.vehicle_id = self.on_delete_vehicle if self.on_delete_vehicle else None
        
        # Style réutilisable pour les tableaux
        self.table_style = """
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: transparent;
                alternate-background-color: #fdfdfd;
                font-size: 13px;
            }
            
            QHeaderView::section {
                background-color: #f1f3f5;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                color: #495057;
                text-transform: uppercase;
                font-size: 11px;
            }
            
            QTableWidget::item {
                border-bottom: 1px solid #eee;
                padding: 10px;
                color: #333;
            }
            
            QTableWidget::item:selected {
                background-color: #e7f1ff;
                color: #007bff;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ced4da;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #adb5bd;
            }
        """
        self.setup_ui()

    def setup_ui(self):
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.main_layout.setSpacing(15)
        self.setStyleSheet("background-color: #f8f9fa;")

        # 1. HEADER
        self.create_header()

        # 2. TABS
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #dcdde1; background: white; border-radius: 10px; top: -1px; }
            QTabBar::tab {
                background: #f1f2f6; color: #7f8c8d; padding: 12px 25px;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
                margin-right: 5px; font-weight: bold;
            }
            QTabBar::tab:selected { background: white; color: #3498db; border-bottom-color: white; }
        """)

        # Création des pages d'onglets
        self.tab_vehicules = QWidget()
        self.tab_flottes = QWidget()
        
        # Initialisation du contenu (Tableaux créés ici)
        self.setup_tab_vehicules()
        self.setup_tab_flottes()

        # Application du style APRES création
        self.configure_table(self.table_vehicules)
        self.configure_table(self.table_flottes)

        self.tabs.addTab(self.tab_vehicules, "🚗 Parc Automobile")
        self.tabs.addTab(self.tab_flottes, "🏢 Gestion des Flottes")
        
        self.main_layout.addWidget(self.tabs)
        
        # Chargement initial des données
        self.refresh_data()
        self.refresh_fleets()

    def create_header(self):
        header_layout = QHBoxLayout()
        
        title_container = QVBoxLayout()
        main_title = QLabel("Gestion du Parc & Flottes")
        main_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; border: none; background-color: transparent;")
        sub_title = QLabel("Suivi technique et audit du parc")
        sub_title.setStyleSheet("font-size: 13px; color: #7f8c8d; border: none; background-color: transparent;")
        title_container.addWidget(main_title)
        title_container.addWidget(sub_title)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        self.btn_audit = QPushButton("📋 Audit")
        self.btn_audit.setStyleSheet("background-color: #1e293b; color: white; padding: 10px 18px; border-radius: 8px; font-weight: bold; border: none;")
        self.btn_audit.clicked.connect(self.on_audit_clicked)
        
        self.btn_add_fleet = QPushButton("📁 Nouvelle Flotte")
        self.btn_add_fleet.setStyleSheet("background-color: #ef4444; color: #1e293b; padding: 10px 18px; border-radius: 8px; font-weight: bold; border: none;")
        self.btn_add_fleet.clicked.connect(self.on_add_fleet_click)
        
        self.btn_add_vehicle = QPushButton("🚗 Ajouter Véhicule")
        self.btn_add_vehicle.setStyleSheet("background-color: #10b981; color: #1e293b; padding: 10px 18px; border-radius: 8px; font-weight: bold; border: none;")
        self.btn_add_vehicle.clicked.connect(self.on_add_vehicle_click)

        header_layout.addWidget(self.btn_audit)
        header_layout.addWidget(self.btn_add_fleet)
        header_layout.addWidget(self.btn_add_vehicle)
        self.main_layout.addLayout(header_layout)

    def configure_table(self, table):
        self.table_fleets = table
        self.table_fleets.verticalHeader().setVisible(False)
        self.table_fleets.setAlternatingRowColors(True)
        self.table_fleets.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_fleets.verticalHeader().setDefaultSectionSize(45)
        self.table_fleets.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_fleets.setStyleSheet(self.table_style)

    def setup_tab_vehicules(self):
        layout = QHBoxLayout(self.tab_vehicules)
        left = QVBoxLayout()
        
        self.search_vehicule = QLineEdit()
        self.search_vehicule.setPlaceholderText("🔍 Rechercher une plaque...")
        self.search_vehicule.setStyleSheet("padding: 12px; border-radius: 8px; border: 1px solid #dcdde1; background: #fdfdfd;")
        self.search_vehicule.textChanged.connect(self.filter_vehicles)
        
        self.table_vehicules = QTableWidget(0, 7)
        self.table_vehicules.setHorizontalHeaderLabels(["Plaque", "Marque", "Propriétaire", "Pime Emise", "Valeur Neuve", "Valeur Venale", "Action"])
        self.table_vehicules.setStyleSheet(self.table_style)
        
        left.addWidget(self.search_vehicule)
        left.addWidget(self.table_vehicules)
        
        layout.addLayout(left, 7)
        layout.addWidget(self.create_stats_panel("Aperçu du Parc"), 3)

    def setup_tab_flottes(self):
        layout = QHBoxLayout(self.tab_flottes)
        left = QVBoxLayout()
        self.search_fleet = QLineEdit()
        self.search_fleet.setPlaceholderText("🔍 Rechercher une flotte...")
        self.search_fleet.setStyleSheet("padding: 12px; border-radius: 8px; border: 1px solid #dcdde1; background: #fdfdfd;")
        self.search_fleet.textChanged.connect(self.filter_vehicles)
        
        self.table_flottes = QTableWidget(0, 6)
        self.table_flottes.setHorizontalHeaderLabels(["immatriculation", "Marque", "Propriétaire", "Statut", "date_debut", "Action"])
        # self.table_vehicules.setStyleSheet(self.table_style)
        
        left.addWidget(self.search_fleet)
        
        self.table_flottes = QTableWidget(0, 7)
        self.table_flottes.setHorizontalHeaderLabels([
            "Code", 
            "Nom Flotte", 
            "Propriétaire", 
            "Type Gestion", 
            "Remise (%)", 
            "Date Création", 
            "Actions"
        ])
        # self.table_flottes.setStyleSheet(self.table_style)
        
        left.addWidget(self.table_flottes)
        
        layout.addLayout(left, 7)
        layout.addWidget(self.create_stats_panel("Analyse Flottes"), 3)

    def create_stats_panel(self, title):
        panel = QFrame()
        panel.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e4e8;")
        shadow = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=2, color=QColor(0,0,0,20))
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: bold; color: #34495e; border: none;")
        layout.addWidget(lbl)
        layout.addWidget(self.create_pie_chart())
        return panel

    def create_pie_chart(self):
        series = QPieSeries()
        series.append("Actif", 80); series.append("Alerte", 20)
        chart = QChart()
        chart.addSeries(series)
        chart.setBackgroundVisible(False)
        chart.legend().setAlignment(Qt.AlignBottom)
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent;")
        return view

    def refresh_data(self):
        """Récupère et affiche les données avec boutons d'action groupés."""
        try:
            vehicles = self.controller.vehicles.get_all_vehicles()
            self.table_vehicules.setRowCount(0)
            
            for row_idx, vehicle in enumerate(vehicles):
                self.table_vehicules.insertRow(row_idx)
                
                # 1. Remplissage des données de base
                self.table_vehicules.setItem(row_idx, 0, QTableWidgetItem(str(vehicle.immatriculation)))
                self.table_vehicules.setItem(row_idx, 1, QTableWidgetItem(str(vehicle.marque)))
                self.table_vehicules.setItem(row_idx, 2, QTableWidgetItem(str(vehicle.owner.nom if vehicle.owner else "N/A")))
                self.table_vehicules.setItem(row_idx, 3, QTableWidgetItem(str(vehicle.prime_emise)))
                self.table_vehicules.setItem(row_idx, 4, QTableWidgetItem(str(vehicle.valeur_neuf)))
                self.table_vehicules.setItem(row_idx, 5, QTableWidgetItem(str(vehicle.valeur_venale)))
                
                # Formatage prix (ex: 1 500 000 FCFA)
                price = getattr(vehicle, 'amt_net', 0) or 0
                self.table_vehicules.setItem(row_idx, 3, QTableWidgetItem(f"{price:,.0f} FCFA".replace(",", " ")))

                # 2. Gestion du Badge Statut (Correction de row_idx -> vehicle)
                status = getattr(vehicle, 'statut', "ACTIF") or "ACTIF"
                item_status = QTableWidgetItem(status)
                color = "#2ecc71" if status == "ACTIF" else "#e74c3c"
                item_status.setForeground(QColor(color))
                self.table_vehicules.setItem(row_idx, 4, item_status)
                
                # 3. Création du conteneur d'actions (Correction de l'écrasement)
    
                self.set_action_buttons(row_idx, vehicle)

        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement des données : {e}")

    def set_action_buttons(self, row, vehicle): # Ajout de 'row' ici
        container = QWidget()
        layout = QHBoxLayout(container)
        container.setMinimumHeight(35) # Un peu plus haut pour le confort
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        btns = {
            "view": ("👁️", "#3498db"),
            "edit": ("✏️", "#f1c40f"),
            "delete": ("🗑️", "#e74c3c")
        }

        for key, (icon, color) in btns.items():
            btn = QPushButton(icon)
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 15px;
                    color: {color};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: white;
                }}
            """)
            
            # Capture de l'objet métier 'v' pour éviter le bug de l'entier
            if key == "delete":
                btn.clicked.connect(lambda checked, v=vehicle: self.on_delete_vehicle(v))
            elif key == "edit":
                btn.clicked.connect(lambda checked, v=vehicle: self.on_edit_vehicle(v))
            elif key == "view":
                btn.clicked.connect(lambda checked, v=vehicle: self.show_detail_vehicle(v))
            
            layout.addWidget(btn)

        # CORRECTION : On utilise 'row' (l'index) et non 'vehicle' (l'objet)
        self.table_vehicules.setCellWidget(row, 6, container)
    
    def refresh_fleets(self):
        try:
            fleets = self.controller.fleets.get_all_fleets()
            self.table_fleets.setRowCount(0)
            
            for f in fleets:
                row = self.table_fleets.rowCount()
                self.table_fleets.insertRow(row)
                
                # 0. Code Flotte
                self.table_fleets.setItem(row, 0, QTableWidgetItem(str(f.code_flotte or "")))
                
                # 1. Nom Flotte
                self.table_fleets.setItem(row, 1, QTableWidgetItem(str(f.nom_flotte or "")))
                
                # 2. Propriétaire (Relation owner)
                owner_name = f.owner.nom if f.owner else "N/A"
                self.table_fleets.setItem(row, 2, QTableWidgetItem(owner_name))
                
                # 3. Type Gestion
                self.table_fleets.setItem(row, 3, QTableWidgetItem(str(f.type_gestion or "")))
                
                # 4. Remise
                remise_text = f"{f.remise_flotte}%" if f.remise_flotte else "0%"
                self.table_fleets.setItem(row, 4, QTableWidgetItem(remise_text))
                
                # 5. Date de Création (Formatée proprement)
                date_str = f.created_at.strftime("%d/%m/%Y") if f.created_at else "---"
                self.table_fleets.setItem(row, 5, QTableWidgetItem(date_str))
                

                # À l'intérieur de la boucle 'for f in fleets:' de refresh_fleets
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(4)

                # Bouton Visualiser (Bleu)
                btn_view = QPushButton("👁️")
                btn_view.setStyleSheet("background: #3498db; color: white; border-radius: 50px; padding: 4px;")
                btn_view.clicked.connect(lambda _, f=f: self.handle_fleet_action(f, "view"))

                # Bouton Modifier (Orange)
                btn_edit = QPushButton("✏️")
                btn_edit.setStyleSheet("background: #f39c12; color: white; padding: 4px;")
                btn_edit.clicked.connect(lambda _, f=f: self.handle_fleet_action(f, "edit"))

                # Bouton d'Impression
                btn_print = QPushButton("📄 Imprimer l'État")
                btn_print.setStyleSheet("background: #f39c12; color: white; padding: 4px;")
                btn_print.setCursor(Qt.PointingHandCursor)
                btn_print.clicked.connect(lambda _, fleet=f: self.on_print_fleet_click(fleet))

                # Bouton Bloquer (Rouge)
                btn_lock = QPushButton("🔒")
                btn_lock.setStyleSheet("background: #e74c3c; color: white; border-radius: 50px; padding: 4px;")
                

                layout.addWidget(btn_view)
                layout.addWidget(btn_edit)
                layout.addWidget(btn_lock)
                layout.addWidget(btn_print)
                self.table_flottes.setCellWidget(row, 5, container) # Colonne 5 ou 6 selon votre setup
                
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement des flottes : {e}")

    def on_add_vehicle_click(self):
        # ICI : Assure-toi d'utiliser l'instance du VehicleController
        # et non celle du FleetController
        contacts = self.controller.fleets.get_all_contacts_for_combo()
        dialog = VehicleForm(
            controller=self.controller,
            contacts_list=contacts,
            current_user=getattr(self, 'current_user', None),
            mode="add"
        )
        if dialog.exec():
            self.controller.vehicles.get_all_vehicles()
            self.refresh_data()

    def filter_vehicles(self):
        text = self.search_vehicule.text().lower()
        for i in range(self.table_vehicules.rowCount()):
            match = any(text in (self.table_vehicules.item(i, j).text().lower() if self.table_vehicules.item(i, j) else "") for j in range(3))
            self.table_vehicules.setRowHidden(i, not match)

    def on_add_fleet_click(self):
    # Récupérer la liste des clients pour le combo
    
        contacts = self.controller.fleets.get_all_contacts_for_combo()
        compagnies = self.controller.fleets.get_all_compagnies_for_combo()
        # Dans view.py (on_add_fleet_click)
        dialog = FleetForm(
            controller=self.controller, # On utilise le contrôleur principal ou fleet_service
            current_fleet=None,
            mode="add",
            contacts_list=contacts,
            compagnies_list=compagnies
        )
        if dialog.exec():
            data = dialog.get_form_data()
            self.refresh_fleets()

    def handle_fleet_action(self, fleet_obj, mode):
        """Gère l'ouverture du formulaire selon le mode choisi."""
        # 1. Sécurité : on s'assure que fleet_obj existe
        if not fleet_obj:
            return

        # 2. Correction du Mapping SQL : On passe l'ID (int) et non l'objet complet
        # L'erreur "SQL expression element expected" venait du fait qu'on passait l'objet à get_contact_by_id
        contacts = self.controller.contacts.get_contact_by_id(fleet_obj.id)
        compagnies = self.controller.compagnies.get_all_active_compagnies()
        
        # 3. Ouverture du dialogue avec les bons arguments
        # Note : Vérifiez bien que FleetForm.__init__ accepte 'controller' ou 'fleet_service'
        dialog = FleetForm(
            controller=self.controller, # On utilise le contrôleur principal ou fleet_service
            current_fleet=fleet_obj,
            mode=mode,
            contacts_list=contacts,
            compagnies_list=compagnies
        )
        # (self, fleet_controller, controller, current_fleet=None, parent=None, contacts_list=None, compagnies_list=None, mode="add"):
        
        if dialog.exec():
            self.refresh_fleets()

    def toggle_fleet_status(self, fleet_obj):
        """Bouton Bloquer : Change le statut de la flotte."""
        # On suppose qu'on ajoute un champ 'is_active' au modèle
        new_status = not getattr(fleet_obj, 'is_active', True)
        msg = "bloquer" if not new_status else "débloquer"
        
        from PySide6.QtWidgets import QMessageBox
        confirm = QMessageBox.question(self, "Confirmation", f"Voulez-vous vraiment {msg} cette flotte ?")
        
        if confirm == QMessageBox.Yes:
            success = self.controller.fleets.update_status(fleet_obj.id, new_status)
            if success:
                self.refresh_fleets()

    def on_edit_vehicle(self, vehicle):
        """Gère l'ouverture du formulaire et la sauvegarde des modifications."""
        
        # On passe l'objet complet au formulaire
        dialog = VehicleForm(controller=self.controller, vehicle_to_edit=vehicle)
        dialog.setWindowTitle(f"Modifier le véhicule : {vehicle.immatriculation}")
        
        if dialog.exec() == QDialog.Accepted:
            # Récupérer les données saisies dans le formulaire
            updated_info = dialog.get_form_data()
            
            # ID de l'utilisateur actuel
            user_id = getattr(self.current_user, 'id', 1)
            
            # Appel au service de mise à jour
            success, message = self.controller.vehicles.update_vehicle(vehicle.id, updated_info, user_id)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                self.refresh_data() # On rafraîchit le tableau
                logger.info(f"Activation: {message}")
            else:
                QMessageBox.critical(self, "Erreur", message)
                logger.error(f"Erreur: {message}")

    def show_detail_vehicle(self, vehicle):
        """
        Prépare et affiche l'interface de détails pour un objet Vehicle du modèle SQLAlchemy.
        """
        try:
            # 1. Extraction et formatage des données depuis le modèle SQLAlchemy (automobile_models.py)
            # On utilise getattr par sécurité pour éviter les AttributeError si un champ est None
            
            # Récupération du nom du propriétaire (Contact)
            owner_name = "N/A"
            if hasattr(vehicle, 'owner') and vehicle.owner:
                owner_name = f"{getattr(vehicle.owner, 'nom', '')} {getattr(vehicle.owner, 'prenom', '')}".strip()
            
            # Récupération du nom de la compagnie d'assurance
            compagny_name = "Non définie"
            if hasattr(vehicle, 'compagny') and vehicle.compagny:
                compagny_name = getattr(vehicle.compagny, 'nom', 'N/A')

            vehicle_data = {
                # Identification
                'id': getattr(vehicle, 'id', None),
                'immatriculation': getattr(vehicle, 'immatriculation', 'N/A'),
                'chassis': getattr(vehicle, 'chassis', 'N/A'),
                'marque': getattr(vehicle, 'marque', 'N/A'),
                'modele': getattr(vehicle, 'modele', 'N/A'),
                'annee': str(getattr(vehicle, 'annee', 'N/A')),
                
                'date_debut': vehicle.date_debut.strftime('%d/%m/%Y') if vehicle.date_debut else "",
                'date_fin': vehicle.date_fin.strftime('%d/%m/%Y') if vehicle.date_fin else "",
                
                # Technique
                'energy': getattr(vehicle, 'energie', 'N/A'),
                'usage': getattr(vehicle, 'usage', '0'), # Dans votre code, usage semble porter la puissance
                'places': str(getattr(vehicle, 'places', '5')),
                'zone': getattr(vehicle, 'zone', 'N/A'),
                'categorie': getattr(vehicle, 'categorie', 'N/A'),
                'code_tarif': getattr(vehicle, 'code_tarif', 'N/A'),
                'prime_emise': getattr(vehicle, 'prime_emise', 0),
                'valeur_neuf': getattr(vehicle, 'valeur_neuf', 0),
                'valeur_venale': getattr(vehicle, 'valeur_venale', 0),
                'prime_nette': getattr(vehicle, 'prime_nette', 0),
                'prime_brute': getattr(vehicle, 'prime_brute', 0),
                'réduction': getattr(vehicle, 'reduction', 0),
                'carte_rose': getattr(vehicle, 'carte_rose', 'N/A'),
                'accessoires': getattr(vehicle, 'accessoires', 'N/A'),
                'tva': getattr(vehicle, 'tva', 0),
                'fichier_asac': getattr(vehicle, 'fichier_asac', 'N/A'),
                'vignette': getattr(vehicle, 'vignette', 'N/A'),
                'PTTC': getattr(vehicle, 'pttc', 0),

                # Propriétaire & Assurance
                'owner': owner_name,
                'compagny': compagny_name,
                'phone': getattr(vehicle.owner, 'telephone', 'N/A') if vehicle.owner else "N/A",
                'email': getattr(vehicle.owner, 'email', 'N/A') if vehicle.owner else "N/A",
                'city': getattr(vehicle.owner, 'ville', 'Yaoundé') if vehicle.owner else "Yaoundé",

                # Garanties (Présentées séparément pour faciliter l'affichage dans la vue de détails)

                'check_rc': getattr(vehicle, 'check_rc', False),
                'check_dr': getattr(vehicle, 'check_dr', False),
                'check_vb': getattr(vehicle, 'check_vb', False),
                'check_vol': getattr(vehicle, 'check_vol', False),
                'check_in': getattr(vehicle, 'check_in', False),
                'check_bris': getattr(vehicle, 'check_bris', False),
                'check_ar': getattr(vehicle, 'check_ar', False),
                'check_dta': getattr(vehicle, 'check_dta', False),
                'check_ipt': getattr(vehicle, 'check_ipt', False), 
                
                # Montants des garanties (pour affichage dans les détails)
                'amt_rc': getattr(vehicle, 'amt_rc', 0),
                'amt_dr': getattr(vehicle, 'amt_dr', 0),
                'amt_vb': getattr(vehicle, 'amt_vb', 0),
                'amt_vol': getattr(vehicle, 'amt_vol', 0),
                'amt_in': getattr(vehicle, 'amt_in', 0),
                'amt_bris': getattr(vehicle, 'amt_bris', 0),
                'amt_ar': getattr(vehicle, 'amt_ar', 0),
                'amt_dta': getattr(vehicle, 'amt_dta', 0),
                'amt_ipt': getattr(vehicle, 'amt_ipt', 0),

                # Montants des garanties (pour affichage dans les détails)
                'amt_red_rc': getattr(vehicle, 'amt_red_rc', 0),
                'amt_red_dr': getattr(vehicle, 'amt_red_dr', 0),
                'amt_red_vol': getattr(vehicle, 'amt_red_vol', 0),
                'amt_red_vb': getattr(vehicle, 'amt_red_vb', 0),
                'amt_red_in': getattr(vehicle, 'amt_red_in', 0),
                'amt_red_bris': getattr(vehicle, 'amt_red_bris', 0),
                'amt_red_ar': getattr(vehicle, 'amt_red_ar', 0),
                'amt_red_dta': getattr(vehicle, 'amt_red_dta', 0),
                'amt_red_ipt': getattr(vehicle, 'amt_red_ipt', 0)
            }

            # 2. Importation de la vue de détails
            # (Assurez-vous que le nom du fichier est correct : vehicle_detail_view.py)
            from .vehicle_detail_view import VehicleDetailView
            
            # 3. Création et configuration du dialogue
            from PySide6.QtWidgets import QDialog, QVBoxLayout
            
            detail_dialog = QDialog(self)
            detail_dialog.setWindowTitle(f"Fiche Véhicule : {vehicle_data['immatriculation']}")
            detail_dialog.setMinimumSize(950, 750)
            
            # Design sans bordure ou avec style si nécessaire
            # detail_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog) 

            layout = QVBoxLayout(detail_dialog)
            layout.setContentsMargins(0, 0, 0, 0)

            # Instanciation de la vue avec le contrôleur pour les impressions
            self.view_details = VehicleDetailView(vehicle_data=vehicle_data, controller=self.controller, db_session=self.session)
            layout.addWidget(self.view_details)

            # Connexion du bouton retour (btn_back) pour fermer le dialogue
            if hasattr(self.view_details, 'btn_back'):
                self.view_details.btn_back.clicked.connect(detail_dialog.close)

            # 4. Exécution du dialogue
            detail_dialog.exec()

        except Exception as e:
            print(f"❌ Erreur show_detail_vehicle : {str(e)}")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erreur", f"Impossible d'afficher les détails du véhicule : {e}")
    
    def on_delete_vehicle(self, vehicle):
        """Désactivation logique du véhicule (Soft Delete)."""

        if isinstance(vehicle, int):
            # On pourrait ici récupérer l'objet via le controller si besoin
            logger.error("Erreur: reçu un ID au lieu d'un objet")
            return
        
        # 1. Demander confirmation (Sécurité)
        confirm = QMessageBox.question(
            self, "Confirmation",
            f"Souhaitez-vous vraiment archiver le véhicule {vehicle.immatriculation} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # 2. Appeler le contrôleur (on passe juste l'ID)
            user_id = getattr(self, "current_user_id", 1)
            success, message = self.controller.vehicles.deactivate_vehicle(vehicle.id, user_id)
            
            if success:
                # 3. RAFRAÎCHIR le tableau
                QMessageBox.information(self, "Succès", "Le véhicule a été archivé.")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Erreur", message)

    def display_car(self, users):
        self.table_vehicules.setRowCount(0)
        for user in users:
            row = self.table_vehicules.rowCount()
            self.table_vehicules.insertRow(row)
            self.table_vehicules.setRowHeight(row, 60) # Des lignes plus hautes pour respirer

            # ID (Centré)
            item_id = QTableWidgetItem(str(getattr(user, 'id', '')))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table_vehicules.setItem(row, 0, item_id)

            # Nom d'utilisateur (En gras)
            item_name = QTableWidgetItem(getattr(user, 'username', ''))
            item_name.setFont("font-weight: bold;")
            self.table_vehicules.setItem(row, 1, item_name)

            font = QFont()
            font.setBold(True)
            item_name.setFont(font)
            self.table_vehicules.setItem(row, 1, item_name)

            # Actions
            self.set_action_buttons(row, user)

    def on_audit_clicked(self):
        # On passe le contrôleur qui a accès à la session BD
        dialog = AuditLogDialog(controller=self.controller.vehicles, parent=self)
        dialog.exec()

    def on_print_fleet_click(self, fleet_obj):
        """
        Réagit au clic sur le bouton 'Imprimer l'État' d'une flotte.
        Gère le dialogue de sauvegarde et l'ouverture du PDF généré.
        """
        if not fleet_obj:
            return

        # 1. Préparation du nom de fichier par défaut
        from datetime import datetime
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M")

        # Nettoyage du nom de la flotte pour le nom de fichier (on enlève les caractères spéciaux)
        safe_name = "".join([c for c in fleet_obj.nom_flotte if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        default_filename = f"ETAT_COUVERTURE_{safe_name}_{timestamp}.pdf".replace(' ', '_')

        # 2. Dialogue de sauvegarde de fichier (QFileDialog)
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer l'État de Couverture de Flotte",
            default_filename,
            "Documents PDF (*.pdf)"
        )

        if not path:
            # L'utilisateur a annulé
            return

        # 3. Affichage d'un curseur d'attente (car la génération peut prendre du temps)
        from PySide6.QtGui import QCursor
        from PySide6.QtCore import Qt
        self.setCursor(QCursor(Qt.WaitCursor))
        self.btn_audit.setText("⏳ Génération PDF...") # Feedback visuel temporaire
        self.setEnabled(False) # Désactive l'UI pendant le calcul

        try:
            # 4. Appel au contrôleur pour la génération réelle
            success, message = self.controller.fleets.generate_fleet_pdf(fleet_obj.id, path)

            if success:
                # 5. Ouverture automatique du PDF (si l'OS le permet)
                QMessageBox.information(self, "PDF Généré", "L'état de couverture a été généré avec succès.")

                #os.startfile(path) # Uniquement sous Windows
                # Solution multiplateforme (Windows, macOS, Linux)
                import platform
                import subprocess

                if platform.system() == 'Windows':
                    os.startfile(path)
                elif platform.system() == 'Darwin': # macOS
                    subprocess.call(('open', path))
                else: # Linux
                    subprocess.call(('xdg-open', path))

                logger.info(f"PDF Flotte '{fleet_obj.nom_flotte}' généré: {path}")
            else:
                # Échec
                QMessageBox.critical(self, "Erreur PDF", f"Échec de la génération du document : {message}")
                logger.error(f"Échec PDF Flotte '{fleet_obj.nom_flotte}': {message}")

        except Exception as e:
            # Erreur inattendue
            QMessageBox.critical(self, "Erreur Critique", f"Une erreur inattendue est survenue : {e}")
            logger.critical(f"Crash lors de la génération PDF Flotte '{fleet_obj.nom_flotte}': {e}")

        finally:
            # 6. Rétablissement de l'UI
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.btn_audit.setText("📋 Audit")
            self.setEnabled(True)