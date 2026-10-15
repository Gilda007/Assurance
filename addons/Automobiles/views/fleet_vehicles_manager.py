# fleet_vehicles_manager.py
"""
Gestionnaire des véhicules d'une flotte
Permet d'ajouter, retirer et configurer les véhicules d'une flotte
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget,
    QComboBox, QLineEdit, QGraphicsDropShadowEffect, QScrollArea,
    QSplitter, QCheckBox, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor, QIcon
from datetime import datetime


class FleetVehiclesManager(QDialog):
    """Dialog de gestion des véhicules d'une flotte"""
    
    vehicles_updated = Signal()  # Signal émis quand les véhicules sont modifiés
    
    def __init__(self, controller, fleet, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.fleet = fleet
        
        # Configuration de la fenêtre
        self.setWindowTitle(f"Gestion des véhicules - {fleet.nom_flotte}")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 750)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Variables
        self.all_vehicles = []
        self.fleet_vehicles = []
        self.selected_vehicles = []
        
        # Charger les données
        self.load_data()
        
        # Configurer l'interface
        self.setup_ui()
    
    def load_data(self):
        """Charge les véhicules du client et de la flotte"""
        try:
            # Récupérer tous les véhicules du propriétaire de la flotte
            owner_id = getattr(self.fleet, 'owner_id', None)
            if owner_id:
                result = self.controller.vehicles.get_vehicles_by_owner_id(owner_id)
                if result is None:
                    self.all_vehicles = []
                elif hasattr(result, 'id') and not hasattr(result, '__iter__'):
                    self.all_vehicles = [result]
                else:
                    self.all_vehicles = result
            
            # Récupérer les véhicules déjà dans la flotte
            if hasattr(self.fleet, 'vehicles'):
                self.fleet_vehicles = list(self.fleet.vehicles) if self.fleet.vehicles else []
            else:
                self.fleet_vehicles = []
            
            # IDs des véhicules de la flotte
            self.fleet_vehicle_ids = {v.id for v in self.fleet_vehicles}
            
        except Exception as e:
            print(f"Erreur chargement données: {e}")
            self.all_vehicles = []
            self.fleet_vehicles = []
            self.fleet_vehicle_ids = set()
    
    def setup_ui(self):
        """Configure l'interface principale"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Carte principale
        main_card = QFrame()
        main_card.setObjectName("MainCard")
        main_card.setStyleSheet("""
            QFrame#MainCard {
                background: white;
                border-radius: 24px;
                border: 1px solid rgba(0,0,0,0.05);
            }
        """)
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        main_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # Barre de titre
        card_layout.addWidget(self.create_title_bar())
        
        # Contenu
        content_widget = QWidget()
        content_widget.setStyleSheet("background: #f8fafc;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(20)
        
        # Header avec statistiques
        content_layout.addWidget(self.create_header())
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #e2e8f0;
                width: 2px;
                margin: 10px 0;
            }
        """)
        
        # Panneau gauche - Véhicules disponibles
        left_panel = self.create_available_panel()
        splitter.addWidget(left_panel)
        
        # Panneau droit - Véhicules de la flotte
        right_panel = self.create_fleet_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([550, 550])
        content_layout.addWidget(splitter, 1)
        
        # Barre d'actions
        content_layout.addWidget(self.create_action_bar())
        
        card_layout.addWidget(content_widget)
        main_layout.addWidget(main_card)
    
    def create_title_bar(self):
        """Crée la barre de titre personnalisée"""
        title_bar = QFrame()
        title_bar.setFixedHeight(60)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-top-left-radius: 24px;
                border-top-right-radius: 24px;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(24, 0, 20, 0)
        
        # Titre
        title_icon = QLabel("🚛")
        title_icon.setStyleSheet("font-size: 20px; background: transparent;")
        
        title_text = QLabel(f"Gestion des véhicules - {self.fleet.nom_flotte}")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: white;
            background: transparent;
        """)
        
        # Compteur
        self.vehicle_count_label = QLabel(f"{len(self.fleet_vehicles)} véhicule(s)")
        self.vehicle_count_label.setStyleSheet("""
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        """)
        
        title_layout.addWidget(title_icon)
        title_layout.addSpacing(10)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        title_layout.addWidget(self.vehicle_count_label)
        
        # Bouton fermer
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(32, 32)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.15);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ef4444;
            }
        """)
        btn_close.clicked.connect(self.close)
        title_layout.addWidget(btn_close)
        
        return title_bar
    
    def create_header(self):
        """Crée l'en-tête avec résumé"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(30)
        
        # Statistiques
        stats = [
            ("🚗 Total véhicules client", str(len(self.all_vehicles))),
            ("🚛 Véhicules dans la flotte", str(len(self.fleet_vehicles))),
            ("📊 Taux d'occupation", f"{int(len(self.fleet_vehicles)/len(self.all_vehicles)*100) if self.all_vehicles else 0}%"),
        ]
        
        for label, value in stats:
            stat_widget = QHBoxLayout()
            
            label_lbl = QLabel(label)
            label_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
            
            value_lbl = QLabel(value)
            value_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #8b5cf6;")
            
            stat_widget.addWidget(label_lbl)
            stat_widget.addWidget(value_lbl)
            
            layout.addLayout(stat_widget)
            layout.addStretch()
        
        # Barre de progression
        progress_frame = QFrame()
        progress_frame.setFixedWidth(200)
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        progress_lbl = QLabel("Taux de remplissage")
        progress_lbl.setStyleSheet("font-size: 10px; color: #64748b;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(len(self.fleet_vehicles)/len(self.all_vehicles)*100) if self.all_vehicles else 0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #e2e8f0;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 4px;
            }
        """)
        
        progress_layout.addWidget(progress_lbl)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
        
        return header
    
    def create_available_panel(self):
        """Crée le panneau des véhicules disponibles"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Titre
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: #f1f5f9;
                border-radius: 12px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(16, 12, 16, 12)
        
        title = QLabel("📋 VÉHICULES DISPONIBLES")
        title.setStyleSheet("font-weight: 700; font-size: 14px; color: #1e293b;")
        
        self.available_count = QLabel(f"{len(self.all_vehicles)} véhicules")
        self.available_count.setStyleSheet("color: #64748b; font-size: 12px;")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.available_count)
        
        layout.addWidget(title_frame)
        
        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un véhicule...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #8b5cf6;
            }
        """)
        self.search_input.textChanged.connect(self.filter_available_vehicles)
        layout.addWidget(self.search_input)
        
        # Tableau
        self.available_table = QTableWidget()
        self.available_table.setColumnCount(5)
        self.available_table.setHorizontalHeaderLabels(["", "Immatriculation", "Marque", "Modèle", "Prime (FCFA)"])
        self.available_table.setColumnWidth(0, 40)
        self.available_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.available_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.available_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.available_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.available_table.setAlternatingRowColors(True)
        self.available_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.available_table.setShowGrid(False)
        self.available_table.verticalHeader().setVisible(False)
        self.available_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background: white;
            }
            QTableWidget::item {
                padding: 10px 8px;
            }
        """)
        
        layout.addWidget(self.available_table)
        
        # Bouton ajouter
        btn_add = QPushButton("+ Ajouter à la flotte →")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setMinimumHeight(40)
        btn_add.setStyleSheet("""
            QPushButton {
                background: #8b5cf6;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #7c3aed;
            }
        """)
        btn_add.clicked.connect(self.add_selected_vehicles)
        layout.addWidget(btn_add)
        
        # Remplir le tableau
        self.refresh_available_table()
        
        return panel
    
    def create_fleet_panel(self):
        """Crée le panneau des véhicules de la flotte"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Titre
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: #f3e8ff;
                border-radius: 12px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(16, 12, 16, 12)
        
        title = QLabel("🚛 VÉHICULES DE LA FLOTTE")
        title.setStyleSheet("font-weight: 700; font-size: 14px; color: #7c3aed;")
        
        self.fleet_count = QLabel(f"{len(self.fleet_vehicles)} véhicules")
        self.fleet_count.setStyleSheet("color: #7c3aed; font-size: 12px;")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.fleet_count)
        
        layout.addWidget(title_frame)
        
        # Tableau
        self.fleet_table = QTableWidget()
        self.fleet_table.setColumnCount(5)
        self.fleet_table.setHorizontalHeaderLabels(["", "Immatriculation", "Marque", "Modèle", "Prime (FCFA)"])
        self.fleet_table.setColumnWidth(0, 40)
        self.fleet_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.fleet_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.fleet_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.fleet_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.fleet_table.setAlternatingRowColors(True)
        self.fleet_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fleet_table.setShowGrid(False)
        self.fleet_table.verticalHeader().setVisible(False)
        self.fleet_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background: white;
            }
            QTableWidget::item {
                padding: 10px 8px;
            }
        """)
        
        layout.addWidget(self.fleet_table)
        
        # Bouton retirer
        btn_remove = QPushButton("← Retirer de la flotte")
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setMinimumHeight(40)
        btn_remove.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_remove.clicked.connect(self.remove_selected_vehicles)
        layout.addWidget(btn_remove)
        
        # Remplir le tableau
        self.refresh_fleet_table()
        
        return panel
    
    def create_action_bar(self):
        """Crée la barre d'actions"""
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 16, 20, 16)
        
        layout.addStretch()
        
        # Bouton configurer garanties
        btn_configure = QPushButton("⚙️ Configurer les garanties")
        btn_configure.setCursor(Qt.PointingHandCursor)
        btn_configure.setMinimumHeight(40)
        btn_configure.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        btn_configure.clicked.connect(self.configure_guarantees)
        layout.addWidget(btn_configure)
        
        # Bouton valider
        btn_validate = QPushButton("✓ Valider les modifications")
        btn_validate.setCursor(Qt.PointingHandCursor)
        btn_validate.setMinimumHeight(40)
        btn_validate.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0 24px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_validate.clicked.connect(self.save_changes)
        layout.addWidget(btn_validate)
        
        # Bouton annuler
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 12px;
                padding: 0 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        btn_cancel.clicked.connect(self.close)
        layout.addWidget(btn_cancel)
        
        return bar
    
    def refresh_available_table(self):
        """Rafraîchit le tableau des véhicules disponibles"""
        self.available_table.setRowCount(0)
        
        search_text = self.search_input.text().lower()
        
        for vehicle in self.all_vehicles:
            # Vérifier si déjà dans la flotte
            if vehicle.id in self.fleet_vehicle_ids:
                continue
            
            # Filtrer par recherche
            immat = getattr(vehicle, 'immatriculation', '').lower()
            marque = getattr(vehicle, 'marque', '').lower()
            
            if search_text and search_text not in immat and search_text not in marque:
                continue
            
            row = self.available_table.rowCount()
            self.available_table.insertRow(row)
            
            # Checkbox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            self.available_table.setItem(row, 0, check_item)
            
            # Immatriculation
            self.available_table.setItem(row, 1, QTableWidgetItem(getattr(vehicle, 'immatriculation', '—')))
            
            # Marque
            self.available_table.setItem(row, 2, QTableWidgetItem(getattr(vehicle, 'marque', '—')))
            
            # Modèle
            self.available_table.setItem(row, 3, QTableWidgetItem(getattr(vehicle, 'modele', '—')))
            
            # Prime
            prime = float(getattr(vehicle, 'prime_nette', 0) or 0)
            prime_item = QTableWidgetItem(f"{prime:,.0f}".replace(",", " "))
            prime_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.available_table.setItem(row, 4, prime_item)
            
            # Stocker l'ID du véhicule
            self.available_table.item(row, 0).setData(Qt.UserRole, vehicle.id)
        
        self.available_count.setText(f"{self.available_table.rowCount()} véhicules")
    
    def refresh_fleet_table(self):
        """Rafraîchit le tableau des véhicules de la flotte"""
        self.fleet_table.setRowCount(0)
        
        total_prime = 0
        
        for vehicle in self.fleet_vehicles:
            row = self.fleet_table.rowCount()
            self.fleet_table.insertRow(row)
            
            # Checkbox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            self.fleet_table.setItem(row, 0, check_item)
            
            # Immatriculation
            self.fleet_table.setItem(row, 1, QTableWidgetItem(getattr(vehicle, 'immatriculation', '—')))
            
            # Marque
            self.fleet_table.setItem(row, 2, QTableWidgetItem(getattr(vehicle, 'marque', '—')))
            
            # Modèle
            self.fleet_table.setItem(row, 3, QTableWidgetItem(getattr(vehicle, 'modele', '—')))
            
            # Prime
            prime = float(getattr(vehicle, 'prime_nette', 0) or 0)
            total_prime += prime
            prime_item = QTableWidgetItem(f"{prime:,.0f}".replace(",", " "))
            prime_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.fleet_table.setItem(row, 4, prime_item)
            
            # Stocker l'ID du véhicule
            self.fleet_table.item(row, 0).setData(Qt.UserRole, vehicle.id)
        
        self.fleet_count.setText(f"{self.fleet_table.rowCount()} véhicules")
        self.vehicle_count_label.setText(f"{self.fleet_table.rowCount()} véhicule(s)")
        
        # Mettre à jour le compteur
        self.available_count.setText(f"{self.get_available_count()} véhicules")
        
        # Mettre à jour la progression
        total = len(self.all_vehicles)
        current = len(self.fleet_vehicles)
        self.progress_bar.setValue(int(current/total*100) if total > 0 else 0)
    
    def get_available_count(self):
        """Retourne le nombre de véhicules disponibles"""
        count = 0
        for vehicle in self.all_vehicles:
            if vehicle.id not in self.fleet_vehicle_ids:
                count += 1
        return count
    
    def filter_available_vehicles(self):
        """Filtre les véhicules disponibles"""
        self.refresh_available_table()
    
    def add_selected_vehicles(self):
        """Ajoute les véhicules sélectionnés à la flotte"""
        selected_ids = []
        
        for row in range(self.available_table.rowCount()):
            check_item = self.available_table.item(row, 0)
            if check_item and check_item.checkState() == Qt.Checked:
                vehicle_id = check_item.data(Qt.UserRole)
                if vehicle_id:
                    selected_ids.append(vehicle_id)
        
        if not selected_ids:
            QMessageBox.information(self, "Information", "Veuillez sélectionner au moins un véhicule.")
            return
        
        # Ajouter les véhicules
        for vehicle in self.all_vehicles:
            if vehicle.id in selected_ids and vehicle.id not in self.fleet_vehicle_ids:
                self.fleet_vehicles.append(vehicle)
                self.fleet_vehicle_ids.add(vehicle.id)
        
        # Rafraîchir les tableaux
        self.refresh_available_table()
        self.refresh_fleet_table()
        
        QMessageBox.information(self, "Succès", f"{len(selected_ids)} véhicule(s) ajouté(s) à la flotte.")
    
    def remove_selected_vehicles(self):
        """Retire les véhicules sélectionnés de la flotte"""
        selected_ids = []
        
        for row in range(self.fleet_table.rowCount()):
            check_item = self.fleet_table.item(row, 0)
            if check_item and check_item.checkState() == Qt.Checked:
                vehicle_id = check_item.data(Qt.UserRole)
                if vehicle_id:
                    selected_ids.append(vehicle_id)
        
        if not selected_ids:
            QMessageBox.information(self, "Information", "Veuillez sélectionner au moins un véhicule.")
            return
        
        # Retirer les véhicules
        self.fleet_vehicles = [v for v in self.fleet_vehicles if v.id not in selected_ids]
        self.fleet_vehicle_ids = {v.id for v in self.fleet_vehicles}
        
        # Rafraîchir les tableaux
        self.refresh_available_table()
        self.refresh_fleet_table()
        
        QMessageBox.information(self, "Succès", f"{len(selected_ids)} véhicule(s) retiré(s) de la flotte.")
    
    def configure_guarantees(self):
        """Configure les garanties des véhicules sélectionnés"""
        QMessageBox.information(self, "Configuration", "Fonctionnalité à implémenter pour configurer les garanties des véhicules de la flotte.")
    
    def save_changes(self):
        """Sauvegarde les modifications"""
        try:
            # Mettre à jour la flotte avec les nouveaux véhicules
            vehicle_ids = [v.id for v in self.fleet_vehicles]
            
            user_id = 1  # À adapter selon votre contexte
            success = self.controller.fleets.update_fleet_vehicles(self.fleet.id, vehicle_ids, user_id)
            
            if success:
                self.vehicles_updated.emit()
                QMessageBox.information(self, "Succès", "Les modifications ont été enregistrées avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de l'enregistrement des modifications.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def keyPressEvent(self, event):
        """Gère la touche Escape pour fermer"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)