from email.mime import text

from PySide6.QtWidgets import QDialog, QFileDialog, QGraphicsDropShadowEffect, QLineEdit, QSplitter, QWidget, QVBoxLayout, QTableWidget, QFrame, QLabel, QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView, QMessageBox, QScrollArea, QGridLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QColor, QImageReader
import subprocess, os
from addons.Automobiles.security.access_control import Permissions, SecurityManager
from addons.Automobiles.security.access_control import Permissions
from addons.Automobiles.models.contact_models import ContactAuditLog, Contact
from addons.Automobiles.views.contact_card_view import ContactCard
from addons.Automobiles.views.contact_form_view import ContactForm # Assure-toi de l'import
from core.alerts import AlertManager
from PySide6.QtCharts import QChartView, QPieSeries, QChart, QLegend
from PySide6.QtGui import QPainter, QColor, QFont
from addons.Automobiles.reports.pdf_generator import generate_contact_pdf


# --- LA VUE PRINCIPALE ---
class ContactListView(QWidget):
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.current_user = current_user
        print(self.controller, self.current_user)
        self.setup_ui()

    def setup_ui(self):
        # --- 1. Style Global et Layout Principal ---
        self.setStyleSheet("background-color: #f8fafc;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # --- 2. Header (Simplifié) ---
        header = QHBoxLayout()
        title_section = QVBoxLayout()
        title_page = QLabel("Gestion des Clients")
        title_page.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        title_section.addWidget(title_page)
        
        self.btn_audit = self._create_styled_button("📜 Audit", "#1e293b", "#ffffff", has_border=True)
        self.btn_add = self._create_styled_button("➕ Nouveau Contact", "#10b981", "#ffffff")
        self.btn_pdf = self._create_styled_button("PDF", "#ef4444", "#ffffff") # Bouton rouge
        

        header.addLayout(title_section)
        header.addStretch()
        header.addWidget(self.btn_audit)
        header.addSpacing(10)
        header.addWidget(self.btn_add)
        header.addWidget(self.btn_pdf) # Ajoute-le à côté du bouton Audit
        self.btn_pdf.clicked.connect(self.export_to_pdf)
        self.btn_audit.clicked.connect(self.show_audit_logs)
        self.btn_add.clicked.connect(self.on_add_click)
        self.main_layout.addLayout(header)

        # --- 3. Corps de la page avec QSplitter ---
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        # --- PARTIE GAUCHE : Large (75%) ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 10, 0)

        # Barre de recherche plein écran
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Rechercher par nom, téléphone, entreprise...")
        self.search_bar.setFixedHeight(45)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 1px solid #cbd5e1; border-radius: 10px;
                padding-left: 15px; font-size: 14px;
            }
        """)
        self.search_bar.textChanged.connect(self.on_search_changed)
        left_layout.addWidget(self.search_bar)

        # Zone de défilement pour la grille à 3 colonnes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15) # Espace entre les cartes
        self.grid_layout.setContentsMargins(0, 10, 0, 0)
        self.grid_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.grid_widget)
        left_layout.addWidget(self.scroll_area)

        # --- PARTIE DROITE : Dashboard Compact (25%) ---
        right_container = QWidget()
        right_container.setMinimumWidth(300) # Sécurité pour que le graphe reste lisible
        right_container.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        right_layout = QVBoxLayout(right_container)
        
        stats_label = QLabel("📊 STATISTIQUES")
        stats_label.setStyleSheet("font-weight: 800; color: #94a3b8; font-size: 10px; letter-spacing: 1px;")
        right_layout.addWidget(stats_label)

        # Zone des cartes de stats
        self.stats_cards_container = QVBoxLayout()
        right_layout.addLayout(self.stats_cards_container)

        # Zone du Graphe
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        right_layout.addWidget(self.chart_view)

        # --- Configuration finale des proportions ---
        self.splitter.addWidget(left_container)
        self.splitter.addWidget(right_container)
        
        # On définit les tailles initiales pour forcer le 3-colonnes à gauche
        # Si la fenêtre fait 1200px, gauche=900px, droite=300px
        self.splitter.setSizes([600, 400]) 
        
        self.main_layout.addWidget(self.splitter)

    def _create_styled_button(self, text, bg_color, text_color, has_border=False):
        """Fonction utilitaire pour créer des boutons cohérents"""
        btn = QPushButton(text)
        border = f"border: 1px solid #e2e8f0;" if has_border else "border: none;"
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: {text_color};
                {border} border-radius: 10px; padding: 10px 20px;
                font-weight: 700; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {bg_color}; opacity: 0.8; }}
        """)
        return btn

    def display_contacts(self, contacts):
        # 1. Nettoyage sécurisé pour éviter le freeze
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 2. Remplissage responsive simplifié
        stats_data = self.controller.contacts.get_contact_stats()
        self.refresh_dashboard(stats_data)
        # On calcule le nombre de colonnes selon la largeur actuelle
        cols = max(1, self.width() // 300) 
        
        for i, contact in enumerate(contacts):
            card = ContactCard(
                contact=contact,
                on_edit=self.on_edit_click,
                on_delete=self.on_delete_click,
                on_open_folder=self.open_contact_folder,
                user_role=self.current_user.role
            )
            self.grid_layout.addWidget(card, i // 3, i % 3)

    def resizeEvent(self, event):
        """Déclenché quand on redimensionne la fenêtre pour ajuster la grille"""
        super().resizeEvent(event)
        if hasattr(self, 'current_user'):
            # On rafraîchit la disposition sans recharger la BDD
            self.display_contacts(self.controller.contacts.get_all_contacts())
        super().resizeEvent(event)

    def on_add_click(self):
        """Déclenche l'ouverture du formulaire d'ajout de contact."""
        dialog = ContactForm(self)
        
        if dialog.exec_():
            new_data = dialog.get_data()
            
            # Appel au contrôleur
            result = self.controller.contacts.create_contact(new_data)
            
            # --- GESTION DU RETOUR DU CONTRÔLEUR ---
            new_contact = None
            success = False
            
            # Cas 1 : Le contrôleur renvoie un tuple (objet, succes) ou (objet, succes, message)
            if isinstance(result, tuple):
                new_contact = result[0]
                success = result[1]
            # Cas 2 : Le contrôleur renvoie directement l'objet ou None
            else:
                new_contact = result
                success = True if result else False

            if success and hasattr(new_contact, 'nom'):
                # --- AUDIT ---
                # On sécurise l'accès aux attributs
                nom = getattr(new_contact, 'nom', 'Inconnu')
                prenom = getattr(new_contact, 'prenom', '')
                details = f"Création du contact : {nom} {prenom}"
                
                # Log de l'action
                self.controller.contacts.log_contact_action("CRÉATION", new_contact.id, details)
                
                # Rafraîchir l'interface
                self.display_contacts(self.controller.get_all_contacts())
            else:
                AlertManager.show_error(self, "Erreur", "Le contact n'a pas pu être créé ou les données sont corrompues.")

    def on_edit_click(self, contact_obj):
        # 1. Vérification de sécurité immédiate
        if contact_obj is None:
            print("ERREUR : L'objet contact reçu est None !")
            return

        # 2. Utilise les données de l'objet reçu pour le nom (avant tout appel DB)
        # On utilise .get ou une vérification pour éviter le crash
        nom = getattr(contact_obj, 'nom', 'Inconnu')
        prenom = getattr(contact_obj, 'prenom', '')
        old_name = f"{nom} {prenom}"
        
        print(f"DEBUG : Début édition pour {old_name}")

        # 3. Si tu as besoin de rafraîchir les données depuis la DB
        # Assure-toi de NE PAS écraser la variable contact_obj si le résultat est None
        fresh_contact = self.controller.contacts.get_contact_by_id(contact_obj.id)
        if fresh_contact:
        # On passe fresh_contact directement sans le nom de l'argument
        # ou avec le nom exact défini dans ContactForm.__init__
            dialog = ContactForm(self, fresh_contact) 
            if dialog.exec():
                # 1. On récupère les stats mises à jour
                new_stats = self.controller.contacts.get_contact_stats() 
                # 2. On les passe à la fonction
                self.refresh_dashboard(new_stats)

    def on_delete_click(self, contact):
        # Sécurité : Si l'objet est None suite à un plantage précédent
        if contact is None:
            print("Erreur : L'objet contact est inexistant (None).")
            return

        # On extrait les infos AVANT de risquer une opération DB qui pourrait expirer l'objet
        nom_affiche = f"{contact.nom} {contact.prenom or ''}"
        
        confirm = QMessageBox.question(
            self, "Confirmation", 
            f"Êtes-vous sûr de vouloir supprimer {nom_affiche} ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # ✅ UTILISER .id et non l'objet entier
            success = self.controller.delete_contact(contact.id) 
            
            if success:
                self.refresh_dashboard(self.controller.get_contact_stats()) # Recharger la liste
            else:
                QMessageBox.critical(self, "Erreur", "La suppression a échoué en base de données.")

    def open_contact_folder(self, contact):
        folder_path = self.controller.contacts.dossier_client       
        # Maintenant on peut tester si le chemin existe
        if folder_path and os.path.exists(folder_path):
            # Logique pour ouvrir le dossier (os.startfile ou subprocess)
            import subprocess, platform
            if platform.system() == "Windows":
                os.startfile(folder_path)
            else:
                subprocess.run(["xdg-open", folder_path])
        else:
            print(f"Dossier introuvable pour {contact.nom}")

    def show_audit_logs(self):
        logs = self.controller.contacts.get_audit_logs() 
        
        if not logs:
            QMessageBox.information(self, "Audit", "Aucun historique disponible pour le moment.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Journal d'Audit des Contacts")
        dialog.resize(900, 600)
        dialog.setStyleSheet("background-color: #ffffff;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- Titre et Sous-titre ---
        title = QLabel("Historique des Actions")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e293b; border: none;")
        layout.addWidget(title)

        # --- Le Tableau Stylisé ---
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["DATE", "ACTION", "AUTEUR", "IP", "DÉTAILS"])
        
        # Configuration visuelle
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setVisible(False)
        
        # Stylesheet CSS pour le tableau
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: transparent;
                background-color: white;
                alternate-background-color: #f8fafc;
                selection-background-color: #eff6ff;
                color: #475569;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #64748b;
                font-size: 11px;
                text-transform: uppercase;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f5f9;
            }
        """)

        table.setRowCount(len(logs))
        
        for i, log in enumerate(logs):
            # 1. Date (Formatée proprement)
            date_item = QTableWidgetItem(log.created_at.strftime("%d/%m/%Y\n%H:%M"))
            date_item.setForeground(QColor("#94a3b8"))
            table.setItem(i, 0, date_item)

            # 2. Action (Badge Dynamique)
            action_val = log.action.upper()
            action_widget = QWidget()
            action_lyt = QHBoxLayout(action_widget)
            action_lyt.setContentsMargins(5, 5, 5, 5)
            
            badge = QLabel(action_val)
            # Couleurs selon l'action
            color = "#3b82f6" # Bleu par défaut
            bg = "#eff6ff"
            if "SUPPR" in action_val:
                color, bg = "#ef4444", "#fef2f2"
            elif "CRÉAT" in action_val or "AJOUT" in action_val:
                color, bg = "#10b981", "#ecfdf5"
                
            badge.setStyleSheet(f"""
                color: {color}; background-color: {bg}; 
                border-radius: 6px; padding: 4px 8px; 
                font-size: 10px; font-weight: bold;
            """)
            action_lyt.addWidget(badge)
            action_lyt.addStretch()
            table.setCellWidget(i, 1, action_widget)

            # 3. Auteur
            author_item = QTableWidgetItem(f"👤 Admin (ID: {log.user_id})")
            author_item.setFont(QFont("Arial", 9, QFont.Bold))
            table.setItem(i, 2, author_item)

            # 4. Détails
            detail_item = QTableWidgetItem(log.details)
            detail_item.setToolTip(log.details) # Tooltip si le texte est long
            table.setItem(i, 3, detail_item)

            ip_val = log.ip_address if log.ip_address else "Inconnue"
            ip_item = QTableWidgetItem(ip_val)
            ip_item.setTextAlignment(Qt.AlignCenter)
            ip_item.setForeground(QColor("#64748b")) # Gris ardoise
            table.setItem(i, 4, ip_item)

        # Ajustement des colonnes
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.verticalHeader().setDefaultSectionSize(55) # Hauteur de ligne
        
        layout.addWidget(table)

        # --- Pied de page avec bouton ---
        footer = QHBoxLayout()
        btn_close = QPushButton("Fermer la session d'audit")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: white; border-radius: 6px;
                padding: 10px 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        btn_close.clicked.connect(dialog.accept)
        footer.addStretch()
        footer.addWidget(btn_close)
        layout.addLayout(footer)

        dialog.exec_()

    def update_statistics(self, contacts):
            """Calcule les types et met à jour les indicateurs et le graphique"""
            # 1. Calcul des données
            stats = {}
            for c in contacts:
                t = c.type_contact or "Inconnu"
                stats[t] = stats.get(t, 0) + 1

            # 2. Mise à jour des cartes numériques (Haut-Droite)
            self._clear_layout(self.stats_cards_layout)
            for type_name, count in stats.items():
                card = self._create_stat_card(type_name, count)
                self.stats_cards_layout.addWidget(card)

            # 3. Mise à jour du Pie Chart (Bas-Droite)
            series = QPieSeries()
            for type_name, count in stats.items():
                slice = series.append(f"{type_name}: {count}", count)
                slice.setLabelVisible(True)
                
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Répartition des Contacts")
            chart.legend().setAlignment(Qt.AlignBottom)
            chart.setAnimationOptions(QChart.SeriesAnimations)
            self.chart_view.setChart(chart)
    
    def _create_stat_card(self, label, value):
        """Crée une carte d'information stylisée pour un type de contact."""
        card = QFrame()
        
        # Détermination de la couleur selon le type
        color = "#64748b" # Gris par défaut
        if "ASSURÉ" in label.upper(): color = "#10b981" # Vert
        elif "PROSPECT" in label.upper(): color = "#f59e0b" # Orange

        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 7px;
                border: 1px solid #e2e8f0;
                border-left: 2px solid {color}; /* Barre de couleur distinctive */
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        
        # Texte du Type
        label_widget = QLabel(label.upper())
        label_widget.setStyleSheet(f"color: #475569; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        
        # Valeur numérique
        value_widget = QLabel(str(value))
        value_widget.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 800;")
        
        layout.addWidget(label_widget)
        layout.addStretch()
        layout.addWidget(value_widget)
        
        return card
    
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def refresh_dashboard(self, stats):
        """Met à jour les cartes et le diagramme avec des couleurs personnalisées."""

        while self.stats_cards_container.count():
            item = self.stats_cards_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # On crée une carte distincte pour chaque type trouvé dans la BD
        for type_name, count in stats.items():
            label = type_name if type_name else "Non défini"
            card = self._create_stat_card(label, count)
            self.stats_cards_container.addWidget(card)
        
        # --- 1. Préparation des données du Graphique ---
        series = QPieSeries()
        
        # Palette de couleurs modernes (Flat UI)
        colors = {
            "ASSURÉ": "#10b981",    # Vert Émeraude
            "PROSPECT": "#f59e0b",  # Orange Ambre
            "AUTRE": "#64748b",     # Gris Ardoise
            "INCONNU": "#94a3b8"    # Gris Clair
        }

        for t_name, count in stats.items():
            label = t_name if t_name else "Inconnu"
            slice = series.append(f"{label} ({count})", count)
            
            # Application de la couleur selon le texte
            upper_label = label.upper()
            slice_color = colors.get("AUTRE") # Couleur par défaut
            
            if "ASSURÉ" in upper_label:
                slice_color = colors["ASSURÉ"]
            elif "PROSPECT" in upper_label:
                slice_color = colors["PROSPECT"]
            elif "INCONNU" in upper_label:
                slice_color = colors["INCONNU"]
                
            slice.setBrush(QColor(slice_color))
            slice.setLabelVisible(True)
            slice.setLabelFont(QFont("Arial", 10, QFont.Bold))
            slice.setExploded(False)
            slice.setLabelVisible(True) # Affiche une petite ligne vers le texte si besoin
            

        # --- 2. Configuration esthétique du Chart ---
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Répartition Stratégique")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Configuration de la légende
        legend = chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        
        # CORRECTION ICI : Utilisation de QLegend.MarkerShapeCircle
        legend.setMarkerShape(QLegend.MarkerShapeCircle) 

        self.chart_view.setChart(chart)

    def on_search_changed(self, text):
        """Filtre les contacts affichés en fonction de la saisie."""
        search_text = text.lower()
        
        # 1. Récupérer tous les contacts depuis le contrôleur (ou un cache local)
        all_contacts = self.controller.contacts.get_all_contacts()
        
        # 2. Filtrer la liste
        filtered_contacts = []
        for c in all_contacts:
            # On cherche dans le nom, le prénom, le téléphone ou le type
            match_found = (
                search_text in (c.nom or "").lower() or 
                search_text in (c.prenom or "").lower() or
                search_text in (c.telephone or "").lower() or
                search_text in (c.type_contact or "").lower()
            )
            if match_found:
                filtered_contacts.append(c)
        
        # 3. Rafraîchir l'affichage des cartes et des stats
        self.display_contacts(filtered_contacts)

    def export_to_pdf(self):
        # 1. Demander où enregistrer
        path, _ = QFileDialog.getSaveFileName(self, "Exporter en PDF", "", "PDF Files (*.pdf)")
        
        if path:
            try:
                # 2. Récupérer les données
                contacts, stats = self.controller.get_report_data()
                
                # 3. Générer
                generate_contact_pdf(path, contacts, stats)
                
                QMessageBox.information(self, "Succès", f"Rapport exporté avec succès : {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Échec de l'exportation : {str(e)}")

    def apply_security_policy(self, current_user):
        role = current_user.role  # Supposons que votre objet user a un attribut role
        
        # 1. Gestion du bouton d'ajout
        self.btn_add.setVisible(SecurityManager.has_permission(role, Permissions.CONTACT_ADD))
        
        # 2. Gestion du bouton d'audit
        self.btn_audit.setVisible(SecurityManager.has_permission(role, Permissions.AUDIT_VIEW))
        
        # 3. Gestion du bouton PDF
        self.btn_pdf.setVisible(SecurityManager.has_permission(role, Permissions.EXPORT_PDF))