

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
from typing import Optional, List, Dict, Any


# ============================================================
# PAGE 2: NOUVEAU SINISTRE
# ============================================================

class NouveauSinistrePage(QWidget):
    """Page de création d'un nouveau sinistre - Version avec recherche client et contrats"""
    
    def __init__(self, sinistre_controller, referentiel_controller, user):
        super().__init__()
        self.sinistre_controller = sinistre_controller
        self.referentiel_controller = referentiel_controller
        
        # ✅ Nouveaux contrôleurs
        from addons.sinistres.controllers.automobile_controller import AutomobileController
        self.automobile_controller = AutomobileController()
        self.automobile_controller.set_current_user(user)
        
        self.user = user
        
        self.setup_ui()
        self.load_referentiels()
    
    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: white;")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # En-tête
        header = QLabel("📝 Nouveau sinistre")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # ============================================================
        # SECTION 1: CLIENT ET CONTRAT (avec recherche)
        # ============================================================
        from addons.sinistres.views.client_search_widget import ClientSearchWidget
        from addons.sinistres.views.contract_selector_widget import ContractSelectorWidget
        
        form_group_client = QGroupBox("Client et contrat")
        form_group_client.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        client_layout = QVBoxLayout(form_group_client)
        
        # Widget de recherche client
        self.client_search = ClientSearchWidget(self.automobile_controller)
        self.client_search.client_selected.connect(self._on_client_selected)
        client_layout.addWidget(self.client_search)
        
        # Widget de sélection de contrat
        self.contract_selector = ContractSelectorWidget(self.automobile_controller)
        self.contract_selector.contract_selected.connect(self._on_contract_selected)
        client_layout.addWidget(self.contract_selector)
        
        layout.addWidget(form_group_client)
        
        # ============================================================
        # SECTION 2: INFORMATIONS GÉNÉRALES
        # ============================================================
        form_group1 = QGroupBox("Informations générales")
        form_group1.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        form_layout1 = QFormLayout(form_group1)
        form_layout1.setSpacing(12)
        
        # Numéro de référence (optionnel)
        self.input_numero_ref = QLineEdit()
        self.input_numero_ref.setPlaceholderText("Ex: REF-2026-001 (optionnel)")
        form_layout1.addRow("Référence:", self.input_numero_ref)
        
        # Compagnie (optionnel)
        self.input_compagnie = QLineEdit()
        self.input_compagnie.setPlaceholderText("ID de la compagnie (optionnel)")
        form_layout1.addRow("Compagnie:", self.input_compagnie)
        
        # Agence (optionnel)
        self.input_agence = QLineEdit()
        self.input_agence.setPlaceholderText("ID de l'agence (optionnel)")
        form_layout1.addRow("Agence:", self.input_agence)
        
        layout.addWidget(form_group1)
        
        # ============================================================
        # SECTION 3: CLASSIFICATION
        # ============================================================
        form_group2 = QGroupBox("Classification")
        form_group2.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        form_layout2 = QFormLayout(form_group2)
        form_layout2.setSpacing(12)
        
        # Branche (obligatoire)
        self.input_branche = QComboBox()
        self.input_branche.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout2.addRow("Branche *:", self.input_branche)
        
        # Catégorie (obligatoire)
        self.input_categorie = QLineEdit()
        self.input_categorie.setPlaceholderText("Ex: Collision, Incendie, Vol...")
        self.input_categorie.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 6px;")
        form_layout2.addRow("Catégorie *:", self.input_categorie)
        
        # Sous-catégorie (optionnel)
        self.input_sous_categorie = QLineEdit()
        self.input_sous_categorie.setPlaceholderText("Ex: Véhicule, Bâtiment... (optionnel)")
        form_layout2.addRow("Sous-catégorie:", self.input_sous_categorie)
        
        layout.addWidget(form_group2)
        
        # ============================================================
        # SECTION 4: CIRCONSTANCES ET RESPONSABILITÉ
        # ============================================================
        form_group3 = QGroupBox("Circonstances et responsabilité")
        form_group3.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        form_layout3 = QFormLayout(form_group3)
        form_layout3.setSpacing(12)
        
        # Circonstance principale (obligatoire)
        self.input_circonstance = QComboBox()
        self.input_circonstance.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout3.addRow("Circonstance *:", self.input_circonstance)
        
        # Circonstance secondaire (optionnel)
        self.input_circonstance_secondaire = QComboBox()
        self.input_circonstance_secondaire.addItem("-- Aucune --", None)
        form_layout3.addRow("Circonstance secondaire:", self.input_circonstance_secondaire)
        
        # Responsabilité (obligatoire)
        self.input_responsabilite = QComboBox()
        self.input_responsabilite.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout3.addRow("Responsabilité *:", self.input_responsabilite)
        
        layout.addWidget(form_group3)
        
        # ============================================================
        # SECTION 5: DATES
        # ============================================================
        form_group4 = QGroupBox("Dates")
        form_group4.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        form_layout4 = QFormLayout(form_group4)
        form_layout4.setSpacing(12)
        
        # Date de survenance (obligatoire)
        self.input_date_survenance = QDateEdit()
        self.input_date_survenance.setDate(QDate.currentDate())
        self.input_date_survenance.setCalendarPopup(True)
        self.input_date_survenance.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout4.addRow("Date de survenance *:", self.input_date_survenance)
        
        # Date de déclaration (obligatoire - auto-remplie)
        self.input_date_declaration = QDateEdit()
        self.input_date_declaration.setDate(QDate.currentDate())
        self.input_date_declaration.setCalendarPopup(True)
        self.input_date_declaration.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout4.addRow("Date de déclaration *:", self.input_date_declaration)
        
        # Information: date d'ouverture est automatique
        info_ouverture = QLabel("⚠️ La date d'ouverture sera générée automatiquement à la création")
        info_ouverture.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        form_layout4.addRow("", info_ouverture)
        
        layout.addWidget(form_group4)
        
        # ============================================================
        # SECTION 6: DESCRIPTION
        # ============================================================
        form_group5 = QGroupBox("Description")
        form_group5.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        form_layout5 = QFormLayout(form_group5)
        form_layout5.setSpacing(12)
        
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("Description détaillée du sinistre...")
        self.input_description.setMaximumHeight(120)
        self.input_description.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
        form_layout5.addRow("Description:", self.input_description)
        
        layout.addWidget(form_group5)
        
        # ============================================================
        # RÉSUMÉ
        # ============================================================
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel {
                color: #0369a1;
                font-size: 12px;
            }
            QLabel.title {
                font-weight: bold;
                font-size: 13px;
            }
        """)
        self.summary_frame.hide()
        summary_layout = QVBoxLayout(self.summary_frame)
        
        summary_title = QLabel("📋 Récapitulatif")
        summary_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0369a1;")
        summary_layout.addWidget(summary_title)
        
        self.summary_text = QLabel("Aucune sélection")
        self.summary_text.setStyleSheet("color: #0369a1;")
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(self.summary_frame)
        
        # ============================================================
        # BOUTONS D'ACTION
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Bouton annuler
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet("""
            QPushButton {
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: bold;
                background-color: #f1f5f9;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_annuler.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.btn_annuler)
        
        # Bouton créer
        self.btn_creer = QPushButton("✅ Créer le sinistre")
        self.btn_creer.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 12px 40px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_creer.clicked.connect(self.creer_sinistre)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
        
        # Message d'information
        info_layout = QHBoxLayout()
        info_layout.addStretch()
        info_label = QLabel("📌 Les champs marqués d'un * sont obligatoires")
        info_label.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(info_label)
        layout.addLayout(info_layout)
        
        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _on_client_selected(self, client: dict):
        """Gère la sélection d'un client"""
        client_id = client.get('id')
        if client_id:
            self.contract_selector.set_client(client_id)
            self._update_summary()
    
    def _on_contract_selected(self, contract: dict):
        """Gère la sélection d'un contrat"""
        self._update_summary()
    
    def _update_summary(self):
        """Met à jour le résumé"""
        client = self.client_search.get_selected_client()
        contract = self.contract_selector.get_selected_contract()
        
        if client or contract:
            self.summary_frame.show()
            lines = []
            
            if client:
                nom_complet = f"{client.get('nom', '')} {client.get('prenom', '')}".strip()
                lines.append(f"👤 Client: {nom_complet} ({client.get('code_client', 'N/A')})")
            
            if contract:
                lines.append(f"📄 Contrat: {contract.get('numero_police', 'N/A')} ({contract.get('statut', 'N/A')})")
            
            self.summary_text.setText("\n".join(lines))
        else:
            self.summary_frame.hide()
    
    def load_referentiels(self):
        """Charge les référentiels pour les combobox"""
        try:
            # Branches
            branches = self.referentiel_controller.get_referentiels_by_famille("branches")
            for b in branches:
                self.input_branche.addItem(b.get('libelle', ''), b.get('code', ''))
            
            # Circonstances principales
            circonstances = self.referentiel_controller.get_referentiels_by_famille("circonstances")
            for c in circonstances:
                self.input_circonstance.addItem(c.get('libelle', ''), c.get('code', ''))
            
            # Circonstances secondaires
            self.input_circonstance_secondaire.clear()
            self.input_circonstance_secondaire.addItem("-- Aucune --", None)
            for c in circonstances:
                self.input_circonstance_secondaire.addItem(c.get('libelle', ''), c.get('code', ''))
            
            # Responsabilités
            responsabilites = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
            for r in responsabilites:
                self.input_responsabilite.addItem(
                    f"{r.get('libelle', '')} ({int(r.get('valeur', 0) * 100)}%)",
                    r.get('code', '')
                )
            
        except Exception as e:
            print(f"Erreur chargement référentiels: {e}")
    
    def creer_sinistre(self):
        """Crée un nouveau sinistre"""
        try:
            from datetime import datetime
            
            # Récupérer les sélections
            client = self.client_search.get_selected_client()
            contract = self.contract_selector.get_selected_contract()
            
            if not client:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un client")
                return
            
            if not contract:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un contrat")
                return
            
            categorie = self.input_categorie.text().strip()
            if not categorie:
                QMessageBox.warning(self, "Validation", "Veuillez saisir une catégorie")
                return
            
            # Construire les données
            data = {
                # Client et contrat
                'client_id': client.get('id'),
                'contrat_id': contract.get('id'),
                
                # Informations générales
                'numero_reference': self.input_numero_ref.text().strip() or None,
                'compagnie_id': int(self.input_compagnie.text()) if self.input_compagnie.text() else None,
                'agence_id': int(self.input_agence.text()) if self.input_agence.text() else None,
                
                # Classification
                'branche': self.input_branche.currentData(),
                'categorie': categorie,
                'sous_categorie': self.input_sous_categorie.text().strip() or None,
                
                # Circonstances et responsabilité
                'circonstance_principale': self.input_circonstance.currentData(),
                'circonstance_secondaire': self.input_circonstance_secondaire.currentData(),
                'taux_responsabilite': self._get_responsabilite_taux(),
                
                # Dates
                'date_survenance': self.input_date_survenance.date().toPython(),
                'date_declaration': self.input_date_declaration.date().toPython(),
                
                # Description
                'description': self.input_description.toPlainText().strip() or None,
                
                # Créateur
                'created_by': self.user.id if self.user else None
            }
            
            # Validation
            if not data['branche']:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner une branche")
                return
            if not data['circonstance_principale']:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner une circonstance")
                return
            
            # Envoyer
            result = self.sinistre_controller.creer_sinistre(data)
            
            if result:
                self.clear_form()
                QMessageBox.information(
                    self, 
                    "Succès", 
                    f"✅ Sinistre {result.get('numero_sinistre')} créé avec succès !\n\n"
                    f"👤 Client: {client.get('nom')} {client.get('prenom', '')}\n"
                    f"📄 Contrat: {contract.get('numero_police')}\n"
                    f"📅 Date de survenance: {result.get('date_survenance', '')[:10]}\n"
                    f"📌 Statut: OUVERT"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")
    
    def _get_responsabilite_taux(self) -> float:
        """Récupère le taux de responsabilité"""
        code = self.input_responsabilite.currentData()
        referentiels = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
        for r in referentiels:
            if r.get('code') == code:
                return r.get('valeur', 0)
        return 0.0
    
    def clear_form(self):
        """Réinitialise le formulaire"""
        self.client_search.clear_selection()
        self.contract_selector.clear_selection()
        self.input_numero_ref.clear()
        self.input_compagnie.clear()
        self.input_agence.clear()
        self.input_branche.setCurrentIndex(0)
        self.input_categorie.clear()
        self.input_sous_categorie.clear()
        self.input_circonstance.setCurrentIndex(0)
        self.input_circonstance_secondaire.setCurrentIndex(0)
        self.input_responsabilite.setCurrentIndex(0)
        self.input_date_survenance.setDate(QDate.currentDate())
        self.input_date_declaration.setDate(QDate.currentDate())
        self.input_description.clear()
        self.summary_frame.hide()

