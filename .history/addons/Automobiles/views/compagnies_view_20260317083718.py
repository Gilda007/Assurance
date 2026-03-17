import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QGraphicsDropShadowEffect, QComboBox, QFileDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QCursor, QTextDocument, QPageLayout, QPageSize
from PySide6.QtPrintSupport import QPrinter
from core.alerts import AlertManager
from addons.Automobiles.views.compagnies_form_view import FormulaireCreationCompagnie
from addons.Automobiles.views.tarif_form_view import CompanyTarifForm
from datetime import datetime

class CompanyTariffView(QWidget):
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.user = current_user
        self.setup_ui()

        self.load_sidebar_compagnies()

    def _add_shadow(self, widget, blur=15, strength=20):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setColor(QColor(0, 0, 0, strength))
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        # Palette Slate 50 pour le fond
        self.setStyleSheet("background-color: #f8fafc; border: none;")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- 1. SIDEBAR : LISTE DES COMPAGNIES ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        self._add_shadow(self.sidebar, 20, 15)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 25, 20, 25)
        
        side_title = QLabel("Compagnies")
        side_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 10px;")
        sidebar_layout.addWidget(side_title)
        
        # Barre de recherche rapide compagnies
        self.comp_search = QLineEdit()
        self.comp_search.setPlaceholderText("Rechercher...")
        self.comp_search.setStyleSheet("""
            QLineEdit {
                background-color: #f1f5f9; border-radius: 8px; padding: 8px 12px; font-size: 13px;
            }
        """)
        sidebar_layout.addWidget(self.comp_search)
        
        # Liste (Simulée ici)
        self.comp_list_scroll = QScrollArea()
        self.comp_list_scroll.setWidgetResizable(True)
        self.comp_list_scroll.setStyleSheet("border: none;")
        
        self.comp_container = QWidget()
        self.comp_vbox = QVBoxLayout(self.comp_container)
        self.comp_vbox.setContentsMargins(0, 10, 0, 0)
        self.comp_vbox.setAlignment(Qt.AlignTop)
        
        # Exemple de items
        for name in ["AXA Assurance", "Allianz", "NSIA Benin", "Saham", "Gras Savoye"]:
            btn = self._create_company_item(name)
            self.comp_vbox.addWidget(btn)
            
        self.comp_list_scroll.setWidget(self.comp_container)
        sidebar_layout.addWidget(self.comp_list_scroll)
        
        self.btn_add_comp = QPushButton("+ Ajouter Compagnie")
        self.btn_add_comp.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9; color: #475569; font-weight: 700; 
                border-radius: 8px; padding: 10px; font-size: 12px;
            }
            QPushButton:hover { background-color: #e2e8f0; color: #1e293b; }
        """)
        sidebar_layout.addWidget(self.btn_add_comp)
        self.btn_add_comp.clicked.connect(self.on_add_click)

        # --- 2. CONTENU PRINCIPAL : TARIFS & CONVENTIONS ---
        self.main_content = QVBoxLayout()
        self.main_content.setSpacing(20)

        # Header de la section droite
        top_header = QHBoxLayout()
        self.selected_label = QLabel("AXA Assurance - Gestion des Tarifs")
        self.selected_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        
        self.btn_save_tariffs = QPushButton("Enregistrer les tarifs")
        self.btn_save_tariffs.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: bold; 
                border-radius: 8px; padding: 10px 20px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        
        top_header.addWidget(self.selected_label)
        top_header.addStretch()
        top_header.addWidget(self.btn_save_tariffs)
        self.btn_save_tariffs.clicked.connect(self.on_add_tarif_click)
        self.main_content.addLayout(top_header)

        # Grille de Tarification (Tableau Moderne)
        self.tariff_card = QFrame()
        self.tariff_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        self._add_shadow(self.tariff_card, 25, 10)
        
        tariff_layout = QVBoxLayout(self.tariff_card)
        tariff_layout.setContentsMargins(20, 20, 20, 20)
        
        # Filtres de catégorie
        filter_box = QHBoxLayout()
        cat_combo = QComboBox()
        cat_combo.addItems(["Automobile", "Santé", "Responsabilité Civile", "Multirisque Habitation"])
        cat_combo.setFixedWidth(200)
        cat_combo.setStyleSheet("""
            QComboBox { 
                background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 5px; 
            }
        """)
        filter_box.addWidget(QLabel("Catégorie :"))
        filter_box.addWidget(cat_combo)
        filter_box.addStretch()
        tariff_layout.addLayout(filter_box)

        # Tableau
        # --- Tableau ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Code", "Compagnie", "Email", "Téléphone", "Actions"
        ])
        
        # Style du tableau
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFrameShape(QTableWidget.NoFrame)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; alternate-background-color: #f8f9fa; }
            QHeaderView::section { 
                background-color: #f1f3f5; padding: 10px; border: none;
                font-weight: bold; color: #495057;
            }
        """)
        
        # Ajustement des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Nom
        header.setSectionResizeMode(5, QHeaderView.Fixed)            # Actions
        self.table.setColumnWidth(5, 160) # Largeur pour 4 boutons

        tariff_layout.addWidget(self.table)

        self.main_content.addWidget(self.tariff_card)

        # Ajout des layouts au main
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addLayout(self.main_content, 1)
        self.load_compagnies_data()

    def load_compagnies_data(self):
        """Charge et affiche les données dans le QTableWidget."""
        try:
            # 1. Récupération des données via le contrôleur
            compagnies = self.controller.compagnies.get_all_active_compagnies()
            
            # DEBUG: Vérifiez dans votre console si cela affiche un nombre > 0
            print(f"DEBUG: Nombre de compagnies récupérées : {len(compagnies)}")

            # 2. Nettoyage du tableau
            self.table.setRowCount(0)

            # 3. Remplissage
            for row_number, cie in enumerate(compagnies):
                self.table.insertRow(row_number)
                
                # Mapping des données (ID, Code, Nom, Email, Téléphone)
                # On s'assure que chaque donnée est convertie en String
                display_data = [
                    str(cie.id),
                    str(cie.code) if cie.code else "",
                    str(cie.nom) if cie.nom else "",
                    str(cie.email) if cie.email else "-",
                    str(cie.telephone) if cie.telephone else "-"
                ]

                for column_number, text in enumerate(display_data):
                    item = QTableWidgetItem(text)
                    # Empêcher l'édition directe dans le tableau
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row_number, column_number, item)

                # 4. Ajout des boutons d'actions (Dernière colonne)
                self._add_action_buttons(row_number, cie.id)
                
            # Ajuster la taille des colonnes au contenu
            self.table.resizeRowsToContents()
            
        except Exception as e:
            print(f"ERREUR lors du chargement du tableau : {str(e)}")

        for cie in compagnies:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Remplissage des données
            items = [
                str(cie.id),
                cie.code,
                cie.nom,
                cie.email or "-",
                cie.telephone or "-"
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)

            # --- Cellule d'Actions ---
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(8)

            # Bouton Visualiser / Modifier
            btn_edit = self._create_action_btn("✏️", "#3498db", "Modifier")
            btn_edit.clicked.connect(lambda _, c=cie.id: self.on_edit_click(c))

            # Bouton Imprimer
            btn_print = self._create_action_btn("🖨️", "#9b59b6", "Imprimer")
            btn_print.clicked.connect(lambda _, c=cie.id: self.on_print_click(c))

            # Bouton Supprimer (Désactiver)
            btn_delete = self._create_action_btn("🗑️", "#e74c3c", "Supprimer")
            btn_delete.clicked.connect(lambda _, c=cie.id: self.on_delete_click(c))

            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_print)
            actions_layout.addWidget(btn_delete)
            
            self.table.setCellWidget(row, 5, actions_widget)

    def _create_company_item(self, name):
        btn = QPushButton(name)
        btn.setCheckable(True)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left; padding-left: 15px; border: none; 
                border-radius: 10px; color: #64748b; font-weight: 600; font-size: 14px;
            }
            QPushButton:checked {
                background-color: #eff6ff; color: #2563eb; font-weight: 800;
            }
            QPushButton:hover:!checked {
                background-color: #f8fafc; color: #1e293b;
            }
        """)
        return btn
    
    def on_add_click(self):
        """Déclenche l'ouverture du formulaire et gère la sauvegarde avec l'ID utilisateur."""
        # 1. Instanciation du formulaire
        dialog = FormulaireCreationCompagnie(self, controller=self.controller, current_user=self.user)
        
        # 2. Exécution du dialogue
        if dialog.exec_():
            # 3. Récupération des données (nom, code, email, téléphone, adresse, num_debut, num_fin)
            data = dialog.get_data()
            
            # 4. EXTRACTION DE L'ID (IMPORTANT)
            # On récupère l'ID numérique pour satisfaire la ForeignKey(utilisateurs.id)
            if hasattr(self.user, 'id'):
                user_id = self.user.id
            elif isinstance(self.user, dict):
                user_id = self.user.get('id')
            else:
                try:
                    # Au cas où self.user serait une chaîne contenant l'ID
                    user_id = int(self.user)
                except (ValueError, TypeError):
                    user_id = None 

            # 5. Appel au contrôleur avec l'ID (Entier)
            # Notez qu'on passe user_id et non user_login
            success, message = self.controller.compagnies.create_compagnie(data, user_id)            
            
            if success:
                # 6. Rafraîchissement de l'affichage
                if hasattr(self, 'load_compagnies_data'):
                    self.load_compagnies_data()
                    self.load_sidebar_compagnies()
                elif hasattr(self, 'refresh_table'):
                    self.refresh_table()
            else:
                # 7. Gestion des erreurs
                AlertManager.show_error(self, "Erreur de sauvegarde", message)

    def on_add_tarif_click(self):
        # Création de l'instance
        dialog = CompanyTarifForm(self, self.controller)
        
        # L'acceptation est déjà gérée à l'intérieur du formulaire (btn_save.clicked.connect(self.accept))
        # Mais vous pouvez aussi le faire ici si vous préférez :
        # dialog.btn_save.clicked.connect(dialog.accept)

        if dialog.exec_():
            # Si l'utilisateur a cliqué sur "ENREGISTRER"
            new_tarif_data = dialog.get_data()
            
            # Envoyer au contrôleur
            result = self.controller.tarifs.create_tarif(new_tarif_data)
            
            if result:
                print("Tarif enregistré avec succès")
                # Rafraîchir votre tableau/liste ici

    def load_compagnies_data(self):
        """Charge et affiche les données dans le QTableWidget."""
        try:
            compagnies = self.controller.compagnies.get_all_active_compagnies()
            self.table.setRowCount(0)

            for row_number, cie in enumerate(compagnies):
                self.table.insertRow(row_number)
                
                # 1. Remplissage des textes
                display_data = [
                    str(cie.id),
                    str(cie.code),
                    str(cie.nom),
                    str(cie.email) if cie.email else "-",
                    str(cie.telephone) if cie.telephone else "-"
                ]

                for col, text in enumerate(display_data):
                    item = QTableWidgetItem(text)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row_number, col, item)

                # 2. Création de la cellule d'actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(10)

                # Bouton Modifier
                btn_edit = self._create_action_btn("✏️", "#3498db", "Modifier")
                # On passe l'ID via le lambda
                btn_edit.clicked.connect(lambda checked=False, c_id=cie.id: self.on_edit_click(c_id))

                # Bouton Imprimer
                btn_print = self._create_action_btn("🖨️", "#9b59b6", "Imprimer")
                btn_print.clicked.connect(lambda checked=False, c_id=cie.id: self.on_print_click(c_id))

                # Bouton Supprimer
                btn_delete = self._create_action_btn("🗑️", "#e74c3c", "Supprimer")
                btn_delete.clicked.connect(lambda checked=False, c_id=cie.id: self.on_delete_click(c_id))

                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_print)
                actions_layout.addWidget(btn_delete)
                actions_layout.addStretch()

                self.table.setCellWidget(row_number, 5, actions_widget)
            
            self.table.resizeRowsToContents()

        except Exception as e:
            print(f"ERREUR lors du chargement du tableau : {str(e)}")

    def _create_action_btn(self, icon_text, color, tooltip):
        """Helper pour créer des boutons d'action stylisés."""
        btn = QPushButton(icon_text)
        btn.setFixedSize(32, 32)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: transparent; border-radius: 6px; 
                font-size: 14px; color: {color}; border: 1px solid {color};
            }}
            QPushButton:hover {{ background-color: {color}; color: white; }}
        """)
        return btn

    def on_edit_click(self, cie_id):
        """Ouvre le formulaire pré-rempli pour modification."""
        # 1. Récupération des données via le contrôleur (méthode ajoutée ci-dessus)
        data = self.controller.compagnies.get_by_id(cie_id)
        
        if not data:
            AlertManager.show_error(self, "Erreur", "Impossible de charger les données de la compagnie.")
            return

        # 2. Ouverture du dialogue avec les données existantes
        # On suppose que votre formulaire accepte un argument 'data'
        dialog = FormulaireCreationCompagnie(
            self, 
            controller=self.controller, 
            current_user=self.user,
            data=data 
        )
        dialog.setWindowTitle("Modifier la Compagnie")

        # 3. Si l'utilisateur clique sur "Enregistrer" (ou équivalent)
        if dialog.exec_():
            updated_data = dialog.get_data()
            
            # Récupération sécurisée de l'ID utilisateur (Integer)
            user_id = self.user.id if hasattr(self.user, 'id') else 1
            
            # 4. Appel à la méthode de mise à jour du contrôleur
            success, message = self.controller.compagnies.update_compagnie(cie_id, updated_data, user_id)
            
            if success:
                self.load_compagnies_data() # Rafraîchir le tableau
                # AlertManager.show_success(self, "Succès", "Compagnie mise à jour avec succès.")
            else:
                AlertManager.show_error(self, "Erreur", message)

    def on_print_click(self, cie_id):
        """Génère une fiche PDF professionnelle de la compagnie."""
        data = self.controller.compagnies.get_by_id(cie_id)
        if not data: return

        # 1. Définir l'emplacement de sauvegarde
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter la fiche", f"Fiche_{data['nom']}.pdf", "PDF Files (*.pdf)"
        )
        if not file_path: return

        # 2. Template HTML pour le PDF (Style professionnel)
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; margin: 40px; }}
                    .header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 10px; margin-bottom: 20px; }}
                    .title {{ color: #1e40af; font-size: 24px; font-weight: bold; }}
                    .section {{ margin-bottom: 20px; }}
                    .section-title {{ background: #f1f5f9; padding: 5px 10px; font-weight: bold; color: #475569; }}
                    table {{ width: 100%; margin-top: 10px; border-collapse: collapse; }}
                    td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                    .label {{ font-weight: bold; color: #64748b; width: 30%; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">FICHE COMPAGNIE PARTENAIRE</div>
                    <p>Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                </div>

                <div class="section">
                    <div class="section-title">IDENTIFICATION</div>
                    <table>
                        <tr><td class="label">Code :</td><td>{data['code']}</td></tr>
                        <tr><td class="label">Nom :</td><td>{data['nom']}</td></tr>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">COORDONNÉES</div>
                    <table>
                        <tr><td class="label">Email :</td><td>{data['email'] or 'N/A'}</td></tr>
                        <tr><td class="label">Téléphone :</td><td>{data['telephone'] or 'N/A'}</td></tr>
                        <tr><td class="label">Adresse :</td><td>{data['adresse'] or 'N/A'}</td></tr>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">PARAMÈTRES FLOTTE</div>
                    <table>
                        <tr><td class="label">Plage de début :</td><td>{data['num_debut'] or 'Non définie'}</td></tr>
                        <tr><td class="label">Plage de fin :</td><td>{data['num_fin'] or 'Non définie'}</td></tr>
                    </table>
                </div>
            </body>
        </html>
        """

        # 3. Génération du PDF
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setOutputFileName(file_path)

        document = QTextDocument()
        document.setHtml(html_content)
        document.print_(printer)

        AlertManager.show_success(self, "Export réussi", "La fiche a été enregistrée avec succès.")

    def load_sidebar_compagnies(self):
        # Nettoyer le layout existant avant de recharger
        while self.comp_vbox.count():
            child = self.comp_vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Récupérer les vraies données
        compagnies = self.controller.compagnies.get_all_active_compagnies()
        
        for cie in compagnies:
            # On passe l'objet complet à la méthode de création
            item_widget = self._create_company_item(cie)
            self.comp_vbox.addWidget(item_widget)

    # --- ACTION VISUALISER ---
    def on_view_click(self, cie_id):
        data = self.controller.compagnies.get_by_id(cie_id)
        if data:
            dialog = FormulaireCreationCompagnie(self, data=data)
            dialog.set_read_only(True) # On active le mode lecture seule
            dialog.exec_()

    # --- ACTION SUPPRIMER ---
    def on_delete_click(self, cie_id):
        from PySide6.QtWidgets import QMessageBox
        
        # 1. Demander confirmation
        confirm = QMessageBox.question(
            self, "Confirmation", 
            "Êtes-vous sûr de vouloir supprimer cette compagnie ?\n"
            "Elle ne sera plus visible mais restera dans les archives.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Extraction de l'ID utilisateur (Integer)
            user_id = self.user.id if hasattr(self.user, 'id') else 1
            
            # 2. Appel au contrôleur
            success, message = self.controller.compagnies.delete_compagnie_logic(cie_id, user_id)
            
            if success:
                # 3. Rafraîchir le tableau immédiatement
                self.load_compagnies_data()
            else:
                QMessageBox.critical(self, "Erreur", message)

    # --- ACTION VISUALISER ---
    def on_view_click(self, cie_id):
        """Affiche les informations sans permettre la modification."""
        data = self.controller.compagnies.get_by_id(cie_id)
        if data:
            dialog = FormulaireCreationCompagnie(self, data=data)
            dialog.set_read_only(True) # Verrouille tout
            dialog.exec_()

    # --- ACTION SUPPRIMER ---
    def on_delete_click(self, cie_id):
        """Suppression après confirmation."""
        from PySide6.QtWidgets import QMessageBox
        
        confirm = QMessageBox.question(
            self, "Confirmation de suppression",
            "Voulez-vous vraiment supprimer cette compagnie ?\n"
            "Cette action est réversible par l'administrateur.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Récupération de l'ID utilisateur pour l'audit
            u_id = self.user.id if hasattr(self.user, 'id') else 1
            
            success, msg = self.controller.compagnies.delete_compagnie_logic(cie_id, u_id)
            if success:
                self.load_compagnies_data() # Rafraîchit le tableau
            else:
                AlertManager.show_error(self, "Erreur", msg)

    def _create_company_item(self, cie):
        """Crée un widget stylisé pour chaque compagnie dans la sidebar."""
        container = QFrame()
        container.setObjectName("CompanyItem")
        container.setCursor(Qt.PointingHandCursor)
        
        # Style de la carte
        container.setStyleSheet("""
            QFrame#CompanyItem {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-bottom: 5px;
            }
            QFrame#CompanyItem:hover {
                background-color: #f8fafc;
                border: 1px solid #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        # --- Ligne 1 : Nom et Code ---
        top_layout = QHBoxLayout()
        
        nom_label = QLabel(cie.nom.upper())
        nom_label.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 13px; border: none;")
        
        code_badge = QLabel(f" {cie.code} ")
        code_badge.setStyleSheet("""
            background-color: #eff6ff; color: #3b82f6; 
            border-radius: 4px; font-size: 10px; font-weight: 800;
            padding: 2px; border: 1px solid #dbeafe;
        """)
        
        top_layout.addWidget(nom_label)
        top_layout.addStretch()
        top_layout.addWidget(code_badge)
        layout.addLayout(top_layout)

        # --- Ligne 2 : Plage de flotte ---
        flotte_info = f"Flotte : {cie.num_debut or '...'} → {cie.num_fin or '...'}"
        flotte_label = QLabel(flotte_info)
        flotte_label.setStyleSheet("color: #64748b; font-size: 11px; border: none;")
        layout.addWidget(flotte_label)

        # Rendre la carte cliquable pour voir les détails
        container.mousePressEvent = lambda event, c_id=cie.id: self.on_view_click(c_id)
        
        return container
    
    