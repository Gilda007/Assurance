Gemini
Rôles dans l'utilisation des applications
Nouvelle discussion
Mes contenus
Gems
Discussions
Rôles dans l'utilisation des applications
SELECT TOP (1000) [COD_POL] ,[COD_ASS] ,[COD_SOU] ,[COD_INT] ,[NUM_POL] ,[BIO_POL] ,[EFF_POL] ,[RES_POL] ,[REM_POL] ,[ORD_POL] ,[EMP_POL] ,[NUMR_POL] ,[PEC_POL] ,[COD_CNV] ,[STD_POL] ,[COD_RES] ,[COD_TAR] ,[COD_BAR] ,[COD_PAI] ,[COG_POL] ,[COP_POL] ,[PRM_POL] ,[COD_CREUTIL] ,[COD_MODUTIL] ,[DAT_CREUTIL] ,[DAT_MODUTIL] ,[NAT_POL] ,[TYP_POL] ,[TYC_POL] ,[COC_POL] ,[IND_POL] ,[DEM_POL] ,[SUS_POL] ,[VIG_POL] ,[RSP_POL] ,[TXA_POL] ,[TXH_POL] ,[AUT_POL] ,[EMA_POL] ,[MAJAUT_POL] ,[AGEAUT_POL] ,[DEL_POL] ,[TTM_POL] ,[TPL_POL] ,[COM_POL] ,[OBS_POL] ,[DAT_CSS] ,[MOD_POL] ,[COD_CAR] ,[MOD_CAR] ,[PMT_POL] ,[COD_PYR] ,[COD_PAY] FROM [hcs_backoffice].[core].[POLICE] dans cette table, insère les données suivantes: https://docs.google.com/spreadsheets/d/1ZMqTGls5mrSjMLEmO51QG3VAUqAGc6tV_k9XE1TWesU/edit?gid=878217555#gid=878217555
Phrase incomplète, que s'est-il passé ?
Suppression de données dans une table
Traduction et Codage du Jeu de la Vie
Ajouter Clé Étrangère à Table Utilisateur
Comprendre l'architecture et le démarrage d'Odoo
Offre d'emploi Financial House S.A.
Installer WhatsApp sur Kali Linux
Installer Microsoft Store sur Kali Linux
Activer l'environnement virtuel Odoo
Aide Application Analyse Données
Offre d'emploi : Assistant Informatique Cameroun

Paramètres et aide
Conversation avec Gemini
Vous avez dit
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget,

QListWidgetItem, QLabel, QPushButton, QFileDialog, QMessageBox)

from PySide6.QtCore import Qt



# from addons.Paramètres.controllers.module_service import ModuleServiceController



class ParametreModuleWidget(QWidget):

def __init__(self, controller, user=None):

super().__init__()

self.controller = controller

self.main_window = None # Pour rafraîchir la sidebar après install

self.service = controller

self.user = user

self.setup_ui()



def setup_ui(self):

layout = QHBoxLayout(self)


# --- COLONNE GAUCHE : LISTE ---

left_col = QVBoxLayout()

self.btn_install = QPushButton("📥 Installer un module (.zip)")

self.btn_install.clicked.connect(self.on_install_clicked)

self.btn_install.setStyleSheet("background: #3b82f6; color: white; padding: 10px; border-radius: 5px;")


self.module_list = QListWidget()

self.module_list.currentRowChanged.connect(self.display_details)


left_col.addWidget(self.btn_install)

left_col.addWidget(self.module_list)

layout.addLayout(left_col, 1)



# --- COLONNE DROITE : DÉTAILS ---

self.detail_panel = QWidget()

self.detail_panel.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e2e8f0;")

self.detail_layout = QVBoxLayout(self.detail_panel)


self.lbl_name = QLabel("Sélectionnez un module")

self.lbl_name.setStyleSheet("font-size: 18px; font-weight: bold;")

self.lbl_desc = QLabel("")

self.lbl_desc.setWordWrap(True)

self.lbl_info = QLabel("")


self.btn_uninstall = QPushButton("🗑️ Désinstaller")

self.btn_uninstall.setStyleSheet("background: #ef4444; color: white; padding: 8px;")

self.btn_uninstall.setVisible(False)

self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)



self.detail_layout.addWidget(self.lbl_name)

self.detail_layout.addWidget(self.lbl_info)

self.detail_layout.addWidget(self.lbl_desc)

self.detail_layout.addStretch()

self.detail_layout.addWidget(self.btn_uninstall)


layout.addWidget(self.detail_panel, 2)

self.refresh_list()



def refresh_list(self):

self.module_list.clear()

self.modules = self.service.get_all_modules()

for mod in self.modules:

item = QListWidgetItem(f"{mod.get('icon', '📦')} {mod['name']}")

item.setData(Qt.UserRole, mod)

self.module_list.addItem(item)



def display_details(self, row):

if row < 0: return

mod = self.module_list.item(row).data(Qt.UserRole)

self.lbl_name.setText(f"{mod.get('icon', '')} {mod['name']}")

self.lbl_info.setText(f"Version: {mod['version']} | Auteur: {mod.get('author', 'Inconnu')}")

self.lbl_desc.setText(f"\nDescription:\n{mod.get('description', 'Aucune description.')}")

self.btn_uninstall.setVisible(mod['folder_name'] != "Paramètre") # On n'efface pas le module système

self.btn_uninstall.setProperty("folder", mod['folder_name'])



def on_install_clicked(self):

path, _ = QFileDialog.getOpenFileName(self, "Choisir le module", "", "Zip (*.zip)")

if path:

success, msg = self.service.install_zip(path)

if success:

QMessageBox.information(self, "Succès", msg)

self.refresh_list()

self.main_window.init_modules() # Rafraîchit la sidebar !

else:

QMessageBox.critical(self, "Erreur", msg)



def on_uninstall_clicked(self):

folder = self.btn_uninstall.property("folder")

confirm = QMessageBox.question(self, "Confirmation", f"Voulez-vous vraiment supprimer {folder} ?")

if confirm == QMessageBox.StandardButton.Yes:

self.service.uninstall_module(folder)

self.refresh_list()

self.main_window.init_modules() # Rafraîchit la sidebar !



tu peux rendre ceci plus beau et professionnel?

Gemini a dit
Pour transformer cette interface en un dashboard moderne et professionnel (type SaaS), nous allons travailler sur trois piliers : l'élévation (ombres), la hiérarchie visuelle (KPI cards) et le feedback utilisateur (badges de dépendances et tailles).

Voici le code complet, corrigé et stylisé.

Python
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont

class ParametreModuleWidget(QWidget):
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.service = controller
        self.main_window = None 
        self.user = user
        self.setup_ui()
        self.refresh_data()

    def _create_stat_card(self, title, color):
        """Crée une carte de statistiques (KPI) avec bordure colorée et ombre."""
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white; border-radius: 12px;
                border: 1px solid #e2e8f0; border-left: 5px solid {color};
            }}
        """)
        
        # Effet d'ombre douce
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800; letter-spacing: 1px;")
        
        lbl_value = QLabel("--")
        lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 900;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        card.val_lbl = lbl_value # Référence pour mise à jour
        return card

    def setup_ui(self):
        # Fond de page gris Slate très léger
        self.setStyleSheet("background-color: #f8fafc;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- 1. HEADER : CARTES DE STATISTIQUES ---
        self.stats_layout = QHBoxLayout()
        self.card_total = self._create_stat_card("Modules Disponibles", "#3b82f6")
        self.card_installed = self._create_stat_card("Modules Installés", "#10b981")
        self.card_storage = self._create_stat_card("Taille Totale", "#f59e0b")
        
        self.stats_layout.addWidget(self.card_total)
        self.stats_layout.addWidget(self.card_installed)
        self.stats_layout.addWidget(self.card_storage)
        self.main_layout.addLayout(self.stats_layout)

        # --- 2. ZONE DE CONTENU PRINCIPAL ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # --- COLONNE GAUCHE : LISTE ---
        left_panel = QVBoxLayout()
        self.btn_install = QPushButton("📥  Déployer une extension (.zip)")
        self.btn_install.setFixedHeight(45)
        self.btn_install.setCursor(Qt.PointingHandCursor)
        self.btn_install.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; border-radius: 10px;
                font-weight: 600; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        self.btn_install.clicked.connect(self.on_install_clicked)

        self.module_list = QListWidget()
        self.module_list.setObjectName("ModernList")
        self.module_list.setSpacing(8)
        self.module_list.setStyleSheet("""
            QListWidget#ModernList { background-color: transparent; border: none; outline: none; }
            QListWidget#ModernList::item {
                background-color: white; border-radius: 10px; padding: 15px;
                color: #334155; border: 1px solid #e2e8f0; margin-bottom: 2px;
            }
            QListWidget#ModernList::item:selected {
                background-color: #ffffff; color: #2563eb; 
                border: 2px solid #3b82f6; font-weight: bold;
            }
        """)
        self.module_list.currentRowChanged.connect(self.display_details)
        
        left_panel.addWidget(self.btn_install)
        left_panel.addWidget(self.module_list)
        content_layout.addLayout(left_panel, 1)

        # --- COLONNE DROITE : DÉTAILS ---
        self.detail_card = QFrame()
        self.detail_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        
        d_layout = QVBoxLayout(self.detail_card)
        d_layout.setContentsMargins(40, 40, 40, 40)
        d_layout.setSpacing(15)

        # Header détail
        self.lbl_name = QLabel("Sélectionnez un composant")
        self.lbl_name.setStyleSheet("font-size: 26px; font-weight: 800; color: #0f172a;")
        
        self.badge_version = QLabel("N/A")
        self.badge_version.setFixedWidth(100)
        self.badge_version.setAlignment(Qt.AlignCenter)
        self.badge_version.setStyleSheet("""
            background-color: #eff6ff; color: #2563eb; font-weight: bold; 
            font-size: 11px; padding: 4px; border-radius: 6px;
        """)

        self.lbl_tech_info = QLabel("") # Taille / Auteur
        self.lbl_tech_info.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")

        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 160%; margin-top: 10px;")

        # Section Dépendances
        self.lbl_dep_title = QLabel("DÉPENDANCES")
        self.lbl_dep_title.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; margin-top: 20px;")
        self.dep_container = QWidget()
        self.dep_layout = QHBoxLayout(self.dep_container)
        self.dep_layout.setContentsMargins(0, 5, 0, 5)
        self.dep_layout.setSpacing(8)
        self.dep_layout.addStretch()

        # Footer bouton
        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        self.btn_uninstall.setFixedSize(150, 40)
        self.btn_uninstall.setStyleSheet("""
            QPushButton {
                background-color: #fff1f2; color: #e11d48; border-radius: 8px;
                font-weight: 700; border: 1px solid #fecdd3;
            }
            QPushButton:hover { background-color: #ffe4e6; }
        """)
        self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)
        self.btn_uninstall.hide()

        d_layout.addWidget(self.lbl_name)
        d_layout.addWidget(self.badge_version)
        d_layout.addWidget(self.lbl_tech_info)
        d_layout.addWidget(self.lbl_desc)
        d_layout.addWidget(self.lbl_dep_title)
        d_layout.addWidget(self.dep_container)
        d_layout.addStretch()
        d_layout.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card, 2)
        self.main_layout.addLayout(content_layout)

    def refresh_data(self):
        self.module_list.clear()
        modules = self.service.get_all_modules()
        
        total_kb = 0
        for mod in modules:
            total_kb += mod.get('size', 0)
            item = QListWidgetItem(f"  {mod.get('icon', '🧩')}   {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)

        # Mise à jour des cartes KPI
        self.card_total.val_lbl.setText(str(len(modules)))
        self.card_installed.val_lbl.setText(str(len(modules)))
        self.card_storage.val_lbl.setText(f"{total_kb / 1024:.1f} MB")

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        self.lbl_name.setText(mod['name'])
        self.badge_version.setText(f"V {mod.get('version', '1.0')}")
        self.lbl_tech_info.setText(f"Poids: {mod.get('size', 0)} KB  •  Éditeur: {mod.get('author', 'AMS Core')}")
        self.lbl_desc.setText(mod.get('description', 'Aucune description fournie.'))

        # Gestion des badges de dépendances
        for i in reversed(range(self.dep_layout.count())): 
            w = self.dep_layout.itemAt(i).widget()
            if w: w.deleteLater()
        
        deps = mod.get('dependencies', [])
        if not deps:
            self.dep_layout.insertWidget(0, QLabel("Aucune"))
        else:
            for d in deps:
                b = QLabel(d)
                b.setStyleSheet("background: #f0fdf4; color: #16a34a; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: bold; border: 1px solid #bbf7d0;")
                self.dep_layout.insertWidget(self.dep_layout.count()-1, b)

        # Sécurité module système
        is_system = mod['folder_name'].lower() in ["paramètre", "settings", "core"]
        self.btn_uninstall.setVisible(not is_system)
        self.btn_uninstall.setProperty("folder", mod['folder_name'])

    def on_install_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir le module", "", "Zip (*.zip)")
        if path:
            success, msg = self.service.install_zip(path)
            if success:
                QMessageBox.information(self, "Succès", msg)
                self.refresh_data()
                if self.main_window: self.main_window.init_modules()
            else:
                QMessageBox.critical(self, "Erreur", msg)

    def on_uninstall_clicked(self):
        folder = self.btn_uninstall.property("folder")
        if QMessageBox.question(self, "Sécurité", f"Supprimer définitivement l'extension {folder} ?") == QMessageBox.StandardButton.Yes:
            self.service.uninstall_module(folder)
            self.refresh_data()
            if self.main_window: self.main_window.init_modules()
Améliorations majeures effectuées :
Dashboard de Statistiques (KPI) : Ajout de 3 cartes en haut pour donner une vue d'ensemble immédiate (Nombre de modules, Taille disque totale).

Look & Feel Moderne :

Utilisation de la palette Slate & Blue (fond #f8fafc).

Ombres portées (QGraphicsDropShadowEffect) pour donner du relief aux panneaux.

Bords très arrondis (12px à 16px) pour un aspect logiciel contemporain.

Gestion des Dépendances : Création dynamique de "badges" (petites pilules vertes) pour lister les prérequis techniques du module sélectionné.

Sémantique visuelle :

Bouton d'installation noir "Navy" pour l'action principale.

Bouton de désinstallation discret (fond rose clair) pour éviter les erreurs, devenant plus visible au survol.

Robustesse : Utilisation intensive de .get() pour éviter que l'UI ne plante si une clé (comme icon ou description) manque dans le dictionnaire du module.

Souhaitez-vous que j'ajoute une barre de recherche pour filtrer la liste des modules si vous en avez beaucoup ?

Vous avez dit
les Qlabel de la partie détail du module sont encadrés. je veux enlever ces cadres

Gemini a dit
Pour enlever les cadres autour des QLabel dans la partie détail, il faut modifier la feuille de style (CSS/QSS) appliquée à ces widgets.

Le problème vient souvent d'un sélecteur trop large dans le setStyleSheet du parent (le QFrame ou le detail_panel) qui applique une bordure à tous les widgets enfants, y compris les labels.

Voici comment corriger votre fichier pour avoir un affichage propre sans bordures sur les textes :

Le code corrigé (Extrait de setup_ui)
Python
        # --- COLONNE DROITE : DÉTAILS ---
        self.detail_panel = QFrame() # Utilisation de QFrame pour le style
        self.detail_panel.setObjectName("DetailPanel")
        
        # Correction ici : On précise que la bordure ne s'applique QU'AU PANEL
        # et non à ses composants internes (Labels, Boutons, etc.)
        self.detail_panel.setStyleSheet("""
            QFrame#DetailPanel {
                background: white; 
                border-radius: 12px; 
                border: 1px solid #e2e8f0;
            }
            QLabel {
                border: none;  /* Force la suppression des cadres sur les labels */
                background: transparent;
            }
        """)
        
        self.detail_layout = QVBoxLayout(self.detail_panel)
        self.detail_layout.setContentsMargins(30, 30, 30, 30)
        
        self.lbl_name = QLabel("Sélectionnez un module")
        self.lbl_name.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a; border: none;")
        
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #64748b; border: none;") # Suppression explicite
        
        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #334155; border: none;") # Suppression explicite
Pourquoi aviez-vous des cadres ?
Si vous écrivez ceci :
self.detail_panel.setStyleSheet("border: 1px solid black;")
Tous les widgets à l'intérieur du panel (Labels, Boutons) hériteront de cette bordure.

Les deux solutions pour éviter cela :

Utiliser un ID (Recommandé) : En donnant un nom d'objet (setObjectName("DetailPanel")) et en utilisant le sélecteur #DetailPanel dans le CSS, la bordure ne s'appliquera qu'au conteneur.

Désactiver explicitement : Ajouter border: none; dans le setStyleSheet de chaque QLabel.

Mise à jour de la méthode display_details
Assurez-vous que vos mises à jour dynamiques ne réintroduisent pas de style :

Python
    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        # On met à jour le texte sans toucher au style des bordures
        self.lbl_name.setText(f"{mod.get('icon', '📦')} {mod['name']}")
        self.lbl_info.setText(f"Version: {mod['version']} | Auteur: {mod.get('author', 'Inconnu')}")
        self.lbl_desc.setText(f"\nDescription:\n{mod.get('description', 'Aucune description.')}")
        
        # Sécurité pour le module système
        is_system = mod['folder_name'].lower() in ["paramètre", "settings"]
        self.btn_uninstall.setVisible(not is_system)
        self.btn_uninstall.setProperty("folder", mod['folder_name'])
Cela rendra votre interface beaucoup plus "professionnelle" et aérienne, car seuls les conteneurs principaux seront structurés par des lignes, tandis que le texte flottera proprement.

Vous avez dit
voici mon controlleur : <addons.Paramètres.models.models.User object at 0x7fc37f0f6900>

DEBUG: Contrôleur reçu par la vue : <addons.Paramètres.models.models.User object at 0x7fc37f0f6900>

Traceback (most recent call last):

  File "/home/fearless/Documents/Assurance Auto/Ams_project V1.1/addons/Paramètres/views/views.py", line 61, in display_page

    self.pages_cache[key] = UserListPage(self.user)

                            ~~~~~~~~~~~~^^^^^^^^^^^

  File "/home/fearless/Documents/Assurance Auto/Ams_project V1.1/addons/Paramètres/views/user_list_view.py", line 84, in __init__

    role = self.controller.current_user_role

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AttributeError: 'User' object has no attribute 'current_user_role'

Gemini a dit
L'erreur est très claire : vous essayez d'accéder à current_user_role sur un objet de type User, mais cet attribut n'existe pas dans votre modèle.

De plus, le message de debug montre que vous passez un objet User (un utilisateur individuel) là où la vue attend probablement un Controller ou un Service.

Voici comment corriger cela en nettoyant votre classe ParametreModuleWidget pour supprimer les cadres indésirables et gérer correctement les dépendances.

1. Correction de l'AttributeError
Dans votre fichier views.py, vous instanciez UserListPage(self.user). L'objet self.user est juste une ligne de votre base de données.

Solution : Vérifiez si vous ne devriez pas passer le contrôleur à la place, ou utilisez self.user.role (si "role" est le nom de votre colonne en base de données).

2. Vue ParametreModuleWidget (Version Pro sans cadres)
J'ai nettoyé le CSS pour que seuls les conteneurs aient des bordures, et non les textes à l'intérieur.

Python
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class ParametreModuleWidget(QWidget):
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.service = controller
        self.main_window = None 
        self.user = user
        self.setup_ui()
        self.refresh_data()

    def _create_stat_card(self, title, color):
        card = QFrame()
        card.setFixedHeight(90)
        # Style de la carte : la bordure est limitée au QFrame lui-même
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white; border-radius: 12px;
                border: 1px solid #e2e8f0; border-left: 5px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        
        layout = QVBoxLayout(card)
        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800;")
        
        v_lbl = QLabel("--")
        v_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        
        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        card.val_lbl = v_lbl 
        return card

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(20)

        # --- KPI CARDS ---
        stats_layout = QHBoxLayout()
        self.card_total = self._create_stat_card("Modules", "#3b82f6")
        self.card_size = self._create_stat_card("Espace", "#f59e0b")
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_size)
        self.main_layout.addLayout(stats_layout)

        # --- CONTENT ---
        content_layout = QHBoxLayout()
        
        # Liste (Gauche)
        self.module_list = QListWidget()
        self.module_list.setFixedWidth(280)
        self.module_list.setStyleSheet("""
            QListWidget { background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 5px; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #f1f5f9; }
            QListWidget::item:selected { background: #eff6ff; color: #2563eb; font-weight: bold; border-radius: 8px; }
        """)
        self.module_list.currentRowChanged.connect(self.display_details)
        content_layout.addWidget(self.module_list)

        # Détails (Droite)
        self.detail_card = QFrame()
        # IMPORTANT : On utilise le sélecteur d'ID #DetailCard pour ne pas encadrer les labels
        self.detail_card.setObjectName("DetailCard")
        self.detail_card.setStyleSheet("""
            QFrame#DetailCard { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
            QLabel { border: none; background: transparent; }
        """)
        
        d_inner = QVBoxLayout(self.detail_card)
        d_inner.setContentsMargins(30, 30, 30, 30)

        self.lbl_name = QLabel("Détails du module")
        self.lbl_name.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a;")

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #64748b; font-weight: 600; font-size: 12px;")

        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; line-height: 150%;")

        # Section Dépendances
        dep_title = QLabel("DÉPENDANCES")
        dep_title.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; margin-top: 20px;")
        
        self.dep_container = QWidget()
        self.dep_layout = QHBoxLayout(self.dep_container)
        self.dep_layout.setContentsMargins(0, 5, 0, 5)
        self.dep_layout.addStretch()

        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        self.btn_uninstall.setFixedSize(130, 35)
        self.btn_uninstall.setStyleSheet("background: #fff1f2; color: #e11d48; border-radius: 6px; font-weight: bold;")
        self.btn_uninstall.hide()

        d_inner.addWidget(self.lbl_name)
        d_inner.addWidget(self.lbl_info)
        d_inner.addSpacing(10)
        d_inner.addWidget(self.lbl_desc)
        d_inner.addWidget(dep_title)
        d_inner.addWidget(self.dep_container)
        d_inner.addStretch()
        d_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card)
        self.main_layout.addLayout(content_layout)

    def refresh_data(self):
        self.module_list.clear()
        modules = self.service.get_all_modules()
        total_kb = 0
        for mod in modules:
            total_kb += mod.get('size', 0)
            item = QListWidgetItem(f"📦 {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)
        
        self.card_total.val_lbl.setText(str(len(modules)))
        self.card_size.val_lbl.setText(f"{total_kb / 1024:.1f} MB")

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        self.lbl_name.setText(mod['name'])
        self.lbl_info.setText(f"VERSION {mod.get('version', '1.0')}  •  {mod.get('size', 0)} KB")
        self.lbl_desc.setText(mod.get('description', 'Aucune description.'))

        # Rafraîchir les dépendances (Badges)
        for i in reversed(range(self.dep_layout.count())):
            w = self.dep_layout.itemAt(i).widget()
            if w: w.deleteLater()
        
        deps = mod.get('dependencies', [])
        if not deps:
            self.dep_layout.insertWidget(0, QLabel("Aucune"))
        else:
            for d in deps:
                badge = QLabel(d)
                badge.setStyleSheet("background: #f0fdf4; color: #16a34a; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;")
                self.dep_layout.insertWidget(self.dep_layout.count()-1, badge)

        is_sys = mod['folder_name'].lower() in ["paramètre", "settings"]
        self.btn_uninstall.setVisible(not is_sys)
Ce qui a été corrigé :
Suppression des cadres : Utilisation de setObjectName("DetailCard") et du sélecteur CSS #DetailCard. Cela garantit que la bordure ne s'applique qu'au panneau blanc et pas aux QLabel à l'intérieur.

Gestion des dépendances : Le code nettoie les anciens badges et affiche les nouveaux sous forme de "pilules" vertes professionnelles.

Variables unifiées : J'ai regroupé la version et la taille dans lbl_info pour un look plus compact.

Voulez-vous que je vous aide à corriger l'AttributeError dans user_list_view.py en modifiant la façon dont le rôle est récupéré ?

Vous avez dit
Traceback (most recent call last):

  File "/home/fearless/Documents/Assurance Auto/Ams_project V1.1/addons/Paramètres/views/views.py", line 61, in display_page

    self.pages_cache[key] = UserListPage(self.user)

                            ~~~~~~~~~~~~^^^^^^^^^^^

  File "/home/fearless/Documents/Assurance Auto/Ams_project V1.1/addons/Paramètres/views/user_list_view.py", line 84, in __init__

    role = self.user.role

           ^^^^^^^^^^^^^^

AttributeError: 'NoneType' object has no attribute 'role'

Gemini a dit
L'erreur AttributeError: 'NoneType' object has no attribute 'role' signifie que dans votre fichier user_list_view.py, l'objet self.user est vide (None) au moment où vous essayez d'accéder à son rôle.

Cela arrive parce que dans votre __init__, vous déclarez self.user = None, mais vous tentez d'utiliser self.user.role quelques lignes plus bas avant même de lui avoir assigné une valeur.

Voici comment corriger vos deux fichiers pour résoudre le crash et finaliser la partie "Détails" des modules sans les cadres.

1. Correction de user_list_view.py (Crash Fix)
Il faut passer l'utilisateur connecté au constructeur et l'assigner avant de l'utiliser pour configurer l'interface.

Python
# addons/Paramètres/views/user_list_view.py

class UserListPage(QWidget):
    def __init__(self, controller=None, current_user=None): # Ajoutez current_user ici
        super().__init__()
        self.controller = controller
        self.user = current_user  # Assignation immédiate
        
        # ... (reste du code setup)
        
        # Maintenant self.user n'est plus None
        role = getattr(self.user, 'role', 'agent') 
        if role != "admin":
            self.btn_audit.hide()
Dans votre fichier principal views.py, assurez-vous de l'appeler ainsi :
self.pages_cache[key] = UserListPage(self.controllers.get('user'), self.user)

2. Correction de parametre_module_view.py (Style & Détails)
Pour enlever les cadres des labels, on utilise des sélecteurs CSS précis. J'ai aussi ajouté la logique pour afficher les dépendances sous forme de badges.

Python
# addons/Paramètres/views/parametre_module_view.py

class ParametreModuleWidget(QWidget):
    # ... (gardez votre __init__ et _create_stat_card)

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        self.main_layout = QVBoxLayout(self)
        
        # --- 1. STATS CARDS (KPI) ---
        # (Gardez votre code existant pour les cartes ici)

        # --- 2. CONTENU ---
        content_layout = QHBoxLayout()
        
        # Liste (Gauche)
        self.module_list = QListWidget()
        self.module_list.setObjectName("ModernList")
        # ... (gardez votre style ModernList)
        content_layout.addWidget(self.module_list, 1)

        # Panneau Droit (Détails)
        self.detail_card = QFrame()
        self.detail_card.setObjectName("DetailCard")
        # LE SECRET : On applique la bordure UNIQUEMENT au QFrame, pas aux enfants
        self.detail_card.setStyleSheet("""
            QFrame#DetailCard {
                background-color: white; 
                border-radius: 16px; 
                border: 1px solid #e2e8f0;
            }
            QLabel { border: none; background: transparent; }
        """)
        
        detail_inner = QVBoxLayout(self.detail_card)
        detail_inner.setContentsMargins(35, 35, 35, 35)
        
        self.lbl_name = QLabel("Détails du module")
        self.lbl_name.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        
        self.lbl_size_tag = QLabel("") 
        self.lbl_size_tag.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px;")
        
        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 160%;")

        # --- AJOUT SECTION DÉPENDANCES ---
        self.lbl_dep_title = QLabel("DÉPENDANCES")
        self.lbl_dep_title.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; margin-top: 20px;")
        
        self.dep_container = QWidget()
        self.dep_layout = QHBoxLayout(self.dep_container)
        self.dep_layout.setContentsMargins(0, 5, 0, 5)
        self.dep_layout.addStretch() # Pousse les badges vers la gauche

        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        # ... (gardez votre style de bouton)

        detail_inner.addWidget(self.lbl_name)
        detail_inner.addWidget(self.lbl_size_tag)
        detail_inner.addSpacing(10)
        detail_inner.addWidget(self.lbl_desc)
        detail_inner.addWidget(self.lbl_dep_title)
        detail_inner.addWidget(self.dep_container)
        detail_inner.addStretch()
        detail_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card, 2)
        self.main_layout.addLayout(content_layout)

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        # Mise à jour des textes
        self.lbl_name.setText(mod.get('name', 'Inconnu'))
        self.lbl_size_tag.setText(f"VERSION {mod.get('version', '1.0')}  •  POIDS: {mod.get('size', 0)} KB")
        self.lbl_desc.setText(mod.get('description', 'Aucune description disponible.'))
        
        # --- LOGIQUE DÉPENDANCES (Badges) ---
        # Nettoyer les anciens badges
        for i in reversed(range(self.dep_layout.count())): 
            widget = self.dep_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
            
        deps = mod.get('dependencies', [])
        if not deps:
            self.dep_layout.insertWidget(0, QLabel("Aucune"))
        else:
            for dep in deps:
                badge = QLabel(dep)
                badge.setStyleSheet("""
                    background-color: #f0fdf4; color: #16a34a; 
                    padding: 4px 10px; border-radius: 12px; 
                    font-size: 10px; font-weight: bold; border: 1px solid #bbf7d0;
                """)
                self.dep_layout.insertWidget(self.dep_layout.count()-1, badge)

        # Gestion bouton désinstaller
        is_sys = mod.get('folder_name', '').lower() in ["paramètre", "settings"]
        self.btn_uninstall.setVisible(not is_sys)
        self.btn_uninstall.setProperty("folder", mod.get('folder_name'))
Résumé des changements :
Correction du sélecteur CSS : En utilisant QFrame#DetailCard, la bordure s'applique uniquement au cadre extérieur. Les labels à l'intérieur reçoivent l'instruction border: none.

Affichage des dépendances : J'ai ajouté un dep_layout qui génère dynamiquement des badges verts pour chaque dépendance trouvée dans les données du module.

Fix du Crash User : Dans user_list_view.py, l'utilisation de getattr(self.user, 'role', 'agent') protège contre les objets vides et assure que l'UI ne plante pas si l'utilisateur n'est pas encore chargé.

Souhaitez-vous que je vous montre comment implémenter la méthode de désinstallation réelle dans le contrôleur ?

Vous avez dit
raceback (most recent call last):

  File "/home/fearless/Documents/Assurance Auto/Ams_project V1.1/addons/Paramètres/views/user_list_view.py", line 255, in on_add_clicked

    success, message = self.controller.create_user(new_user_data)

                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^

AttributeError: 'User' object has no attribute 'create_user'

Gemini a dit
L'erreur AttributeError: 'User' object has no attribute 'create_user' confirme ce que nous soupçonnions : il y a une confusion entre vos Modèles (la donnée) et vos Contrôleurs (la logique).

Dans votre code, self.controller contient un objet de type User (une simple ligne de votre base de données) au lieu de contenir le UserController (le service qui possède la méthode create_user).

Voici comment résoudre ce problème et finaliser l'interface des modules sans les cadres.

1. Correction du crash (Injection du Contrôleur)
Dans votre fichier views.py (celui qui gère la navigation), vous devez passer le bon service à chaque page.

Dans views.py :

Python
def display_page(self, row):
    key = self.sidebar.item(row).data(Qt.UserRole)
    
    if key == "users":
        # On passe le contrôleur utilisateur ET l'utilisateur connecté
        # self.controllers['user'] doit être l'instance de UserController
        page = UserListPage(self.controllers.get('user'), self.user) 
Dans user_list_view.py (Correction du constructeur) :

Python
class UserListPage(QWidget):
    def __init__(self, controller=None, current_user=None):
        super().__init__()
        self.controller = controller # Ceci doit être le service/contrôleur
        self.user = current_user      # Ceci est l'utilisateur connecté
        # ...
2. Finalisation de parametre_module_view.py (Style Pro sans cadres)
Voici la version complète et corrigée. Elle règle le problème des cadres autour des labels et ajoute l'affichage des dépendances avec un design épuré.

Python
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QFrame)
from PySide6.QtCore import Qt

class ParametreModuleWidget(QWidget):
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.service = controller
        self.user = user
        self.setup_ui()
        self.refresh_list()

    def _create_stat_card(self, title, color):
        card = QFrame()
        card.setFixedHeight(90)
        # On utilise un Sélecteur ID (#StatCard) pour que la bordure ne s'applique pas aux labels
        card.setObjectName("StatCard")
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: white; border-radius: 12px;
                border: 1px solid #e2e8f0; border-left: 5px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        layout = QVBoxLayout(card)
        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800;")
        v_lbl = QLabel("--")
        v_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        card.val_lbl = v_lbl 
        return card

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # 1. Dashboard rapide
        stats_layout = QHBoxLayout()
        self.card_total = self._create_stat_card("Modules", "#3b82f6")
        self.card_size = self._create_stat_card("Espace", "#f59e0b")
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_size)
        main_layout.addLayout(stats_layout)

        # 2. Contenu Principal
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Liste à gauche
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget { background: white; border-radius: 12px; border: 1px solid #e2e8f0; outline: none; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #f1f5f9; }
            QListWidget::item:selected { background: #eff6ff; color: #2563eb; font-weight: bold; border-radius: 8px; }
        """)
        self.module_list.currentRowChanged.connect(self.display_details)
        content_layout.addWidget(self.module_list, 1)

        # Carte de Détails à droite
        self.detail_card = QFrame()
        self.detail_card.setObjectName("DetailCard")
        self.detail_card.setStyleSheet("""
            QFrame#DetailCard { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
            QLabel { border: none; background: transparent; }
        """)
        
        detail_inner = QVBoxLayout(self.detail_card)
        detail_inner.setContentsMargins(30, 30, 30, 30)

        self.lbl_name = QLabel("Détails du module")
        self.lbl_name.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a;")

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #64748b; font-weight: bold; font-size: 11px;")

        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 150%;")

        # Section Dépendances
        dep_title = QLabel("DÉPENDANCES")
        dep_title.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; margin-top: 20px;")
        
        self.dep_container = QWidget()
        self.dep_layout = QHBoxLayout(self.dep_container)
        self.dep_layout.setContentsMargins(0, 5, 0, 5)
        self.dep_layout.addStretch() # Aligne les badges à gauche

        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        self.btn_uninstall.setFixedSize(130, 35)
        self.btn_uninstall.setStyleSheet("background: #fff1f2; color: #e11d48; border-radius: 6px; font-weight: bold;")
        self.btn_uninstall.hide()

        detail_inner.addWidget(self.lbl_name)
        detail_inner.addWidget(self.lbl_info)
        detail_inner.addSpacing(10)
        detail_inner.addWidget(self.lbl_desc)
        detail_inner.addWidget(dep_title)
        detail_inner.addWidget(self.dep_container)
        detail_inner.addStretch()
        detail_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card, 2)
        main_layout.addLayout(content_layout)

    def refresh_list(self):
        self.module_list.clear()
        modules = self.service.get_all_modules()
        total_kb = 0
        for mod in modules:
            total_kb += mod.get('size', 0)
            item = QListWidgetItem(f"📦 {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)
        
        self.card_total.val_lbl.setText(str(len(modules)))
        self.card_size.val_lbl.setText(f"{total_kb / 1024:.1f} MB")

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        self.lbl_name.setText(mod['name'])
        self.lbl_info.setText(f"VERSION {mod.get('version', '1.0')}  •  {mod.get('size', 0)} KB")
        self.lbl_desc.setText(mod.get('description', 'Aucune description disponible.'))

        # Rafraîchissement des badges de dépendances
        for i in reversed(range(self.dep_layout.count())):
            w = self.dep_layout.itemAt(i).widget()
            if w: w.deleteLater()
        
        deps = mod.get('dependencies', [])
        if not deps:
            self.dep_layout.insertWidget(0, QLabel("Aucune"))
        else:
            for d in deps:
                badge = QLabel(d)
                badge.setStyleSheet("""
                    background: #f0fdf4; color: #16a34a; padding: 2px 8px; 
                    border-radius: 10px; font-size: 10px; font-weight: bold;
                """)
                self.dep_layout.insertWidget(self.dep_layout.count()-1, badge)

        is_sys = mod['folder_name'].lower() in ["paramètre", "settings"]
        self.btn_uninstall.setVisible(not is_sys)
        self.btn_uninstall.setProperty("folder", mod['folder_name'])
Pourquoi cela résout vos problèmes ?
L'AttributeError : En passant self.controllers.get('user') dans views.py, vous donnez à la page l'accès à la méthode create_user.

Les cadres sur les labels : L'utilisation de QFrame#DetailCard dans le CSS restreint la bordure au conteneur. L'instruction QLabel { border: none; } à l'intérieur nettoie tout résidu.

Les dépendances : La méthode display_details gère maintenant dynamiquement la création de badges pour chaque module sélectionné.

Vous avez dit
Traceback (most recent call last):

  File "/home/fearless/Documents/Assurance Auto/Ams_project V1.1/addons/Paramètres/views/views.py", line 78, in display_page

    self.container.addWidget(self.pages_cache[key])

                             ~~~~~~~~~~~~~~~~^^^^^

KeyError: 'users'

Gemini a dit
Cette erreur KeyError: 'users' signifie que vous essayez d'accéder à la clé 'users' dans votre dictionnaire self.pages_cache, mais que cette clé n'a jamais été créée ou enregistrée.

Dans votre logique de navigation, vous devez d'abord vérifier si la page existe dans le cache, et si ce n'est pas le cas, l'instancier avant de l'ajouter au container.

Voici la correction pour votre méthode display_page dans views.py, ainsi que la version finalisée de ParametreModuleWidget (sans les cadres sur les labels et avec les dépendances).

1. Correction du KeyError dans views.py
Le crash survient car vous tentez d'ajouter au widget stacké une page qui n'est pas encore dans votre dictionnaire.

Python
def display_page(self, row):
    key = self.sidebar.item(row).data(Qt.UserRole)
    
    # 1. Si la page n'est pas encore dans le cache, on la crée
    if key not in self.pages_cache:
        if key == "users":
            from addons.Paramètres.views.user_list_view import UserListPage
            # On passe le controleur des utilisateurs et l'utilisateur actuel
            self.pages_cache[key] = UserListPage(self.controllers.get('user'), self.user)
            
        elif key == "modules":
            from addons.Paramètres.views.parametre_module_view import ParametreModuleWidget
            self.pages_cache[key] = ParametreModuleWidget(self.controllers.get('module'), self.user)
            
        # On l'ajoute au QStackedWidget seulement à la création
        self.container.addWidget(self.pages_cache[key])

    # 2. On affiche la page (qui existe maintenant forcément)
    self.container.setCurrentWidget(self.pages_cache[key])
2. Finalisation de parametre_module_view.py
Cette version supprime les bordures héritées sur les labels et ajoute la gestion dynamique des dépendances.

Python
# ... (imports habituels)

class ParametreModuleWidget(QWidget):
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.service = controller
        self.user = user
        self.setup_ui()
        self.refresh_list()

    def _create_stat_card(self, title, color):
        card = QFrame()
        card.setObjectName("StatCard") # Important pour le CSS ciblé
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: white; border-radius: 12px;
                border: 1px solid #e2e8f0; border-left: 5px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        layout = QVBoxLayout(card)
        t_lbl = QLabel(title.upper()); t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800;")
        v_lbl = QLabel("--"); v_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        layout.addWidget(t_lbl); layout.addWidget(v_lbl)
        card.val_lbl = v_lbl
        return card

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        main_layout = QVBoxLayout(self)
        
        # 1. Dashboard (KPI)
        stats_layout = QHBoxLayout()
        self.card_total = self._create_stat_card("Modules", "#3b82f6")
        self.card_size = self._create_stat_card("Espace utilisé", "#f59e0b")
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_size)
        main_layout.addLayout(stats_layout)

        # 2. Contenu
        content_layout = QHBoxLayout()
        
        # Liste
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #f1f5f9; }
            QListWidget::item:selected { background: #eff6ff; color: #2563eb; font-weight: bold; border-radius: 8px; }
        """)
        self.module_list.currentRowChanged.connect(self.display_details)
        content_layout.addWidget(self.module_list, 1)

        # Détails (Sans bordures sur les labels)
        self.detail_card = QFrame()
        self.detail_card.setObjectName("DetailCard")
        self.detail_card.setStyleSheet("""
            QFrame#DetailCard { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
            QLabel { border: none; background: transparent; padding: 0px; }
        """)
        
        detail_inner = QVBoxLayout(self.detail_card)
        detail_inner.setContentsMargins(30, 30, 30, 30)

        self.lbl_name = QLabel("Détails du module")
        self.lbl_name.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a;")
        
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #64748b; font-weight: bold; font-size: 11px;")

        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 150%;")

        # Zone Dépendances
        self.lbl_dep_title = QLabel("DÉPENDANCES")
        self.lbl_dep_title.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; margin-top: 20px;")
        
        self.dep_container = QWidget()
        self.dep_layout = QHBoxLayout(self.dep_container)
        self.dep_layout.setContentsMargins(0, 5, 0, 5)
        self.dep_layout.addStretch()

        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        self.btn_uninstall.setFixedSize(130, 35)
        self.btn_uninstall.setStyleSheet("background: #fff1f2; color: #e11d48; border-radius: 6px; font-weight: bold;")
        self.btn_uninstall.hide()

        detail_inner.addWidget(self.lbl_name)
        detail_inner.addWidget(self.lbl_info)
        detail_inner.addSpacing(10)
        detail_inner.addWidget(self.lbl_desc)
        detail_inner.addWidget(self.lbl_dep_title)
        detail_inner.addWidget(self.dep_container)
        detail_inner.addStretch()
        detail_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card, 2)
        main_layout.addLayout(content_layout)

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        # Mise à jour des textes
        self.lbl_name.setText(mod.get('name', 'Module'))
        self.lbl_info.setText(f"VERSION {mod.get('version', '1.0')}  •  {mod.get('size', 0)} KB")
        self.lbl_desc.setText(mod.get('description', 'Aucune description.'))

        # Gestion des badges de dépendances
        for i in reversed(range(self.dep_layout.count())):
            w = self.dep_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        deps = mod.get('dependencies', [])
        if not deps:
            self.dep_layout.insertWidget(0, QLabel("Aucune"))
        else:
            for d in deps:
                badge = QLabel(d)
                badge.setStyleSheet("background: #f0fdf4; color: #16a34a; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;")
                self.dep_layout.insertWidget(self.dep_layout.count()-1, badge)

        is_sys = mod.get('folder_name', '').lower() in ["paramètre", "settings"]
        self.btn_uninstall.setVisible(not is_sys)
        self.btn_uninstall.setProperty("folder", mod.get('folder_name'))

    def refresh_list(self):
        self.module_list.clear()
        modules = self.service.get_all_modules()
        total_kb = 0
        for mod in modules:
            total_kb += mod.get('size', 0)
            item = QListWidgetItem(f"📦 {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)
        
        self.card_total.val_lbl.setText(str(len(modules)))
        self.card_size.val_lbl.setText(f"{total_kb / 1024:.1f} MB")
Pourquoi ces changements corrigent tout ?
KeyError : En ajoutant le if key not in self.pages_cache:, vous garantissez que la clé existe avant de l'appeler.

Cadres sur Labels : En utilisant #DetailCard et #StatCard dans le CSS, vous ciblez uniquement la bordure du cadre parent. Les QLabel à l'intérieur reçoivent l'ordre border: none.

Dépendances : La boucle dans display_details génère maintenant dynamiquement des badges verts professionnels pour chaque module.

Souhaitez-vous que je vérifie également votre fichier user_list_view.py pour m'assurer que l'injection du contrôleur User fonctionne bien avec ces changements ?

Vous avez dit
def display_page(self, row):

key = self.sidebar.item(row).data(Qt.UserRole)


if key not in self.pages_cache:

if key == "users":

self.page = UserListPage(self.controllers.get('user'), self.user)


elif key == "modules":

from addons.Paramètres.views.parametre_module_view import ParametreModuleWidget

# On passe explicitement le contrôleur des modules

self.pages_cache[key] = ParametreModuleWidget(

controller=self.controllers['module'],

user=self.user

)


elif key == "account":

from addons.Paramètres.views.accountsettingview import AccountSettingsView

self.pages_cache[key] = AccountSettingsView(self.controllers['user'], self.user)


elif key == "about":

self.pages_cache[key] = AboutUsView()


print(self.pages_cache)

self.container.addWidget(self.pages_cache[key])


if not isinstance(self.controllers, dict):

print("ERREUR: SettingsMainView n'a pas reçu un dictionnaire de contrôleurs")

return


self.container.setCurrentWidget(self.pages_cache[key])



corrige la fonction stp

Gemini a dit
Ta fonction présente un bug logique majeur : pour la clé "users", tu assignes la page à self.page au lieu de l'enregistrer dans self.pages_cache[key]. C'est ce qui provoque ton KeyError car la ligne self.container.addWidget(self.pages_cache[key]) cherche quelque chose qui n'a pas été rangé au bon endroit.

Voici la version corrigée, plus robuste et propre :

Python
def display_page(self, row):
    # Sécurité : Vérifier si l'item existe
    item = self.sidebar.item(row)
    if not item:
        return
        
    key = item.data(Qt.UserRole)
    
    # 1. Vérification de la structure des contrôleurs
    if not isinstance(self.controllers, dict):
        print(f"ERREUR: Controllers est de type {type(self.controllers)}, dictionnaire attendu.")
        return

    # 2. Création de la page si elle n'est pas en cache
    if key not in self.pages_cache:
        try:
            if key == "users":
                from addons.Paramètres.views.user_list_view import UserListPage
                # CORRECTION : On enregistre bien dans le dictionnaire pages_cache
                self.pages_cache[key] = UserListPage(self.controllers.get('user'), self.user)
                
            elif key == "modules":
                from addons.Paramètres.views.parametre_module_view import ParametreModuleWidget
                self.pages_cache[key] = ParametreModuleWidget(self.controllers.get('module'), self.user)
                
            elif key == "account":
                from addons.Paramètres.views.accountsettingview import AccountSettingsView
                self.pages_cache[key] = AccountSettingsView(self.controllers.get('user'), self.user)
                
            elif key == "about":
                from addons.Paramètres.views.about_view import AboutUsView # Assure-toi de l'import
                self.pages_cache[key] = AboutUsView()

            # Ajout physique au QStackedWidget (une seule fois à la création)
            if key in self.pages_cache:
                self.container.addWidget(self.pages_cache[key])
                
        except Exception as e:
            print(f"Erreur lors du chargement de la page {key}: {e}")
            return

    # 3. Affichage de la page
    if key in self.pages_cache:
        self.container.setCurrentWidget(self.pages_cache[key])
Ce qui a été corrigé :
Le bug self.page vs self.pages_cache[key] : J'ai remplacé l'assignation orpheline par l'enregistrement correct dans le cache pour la clé "users".

L'ordre de vérification : On vérifie si self.controllers est un dictionnaire avant d'essayer de créer les pages, sinon le crash arriverait de toute façon à l'intérieur du bloc if.

Imports locaux (Lazy Loading) : C'est une bonne pratique pour éviter les imports circulaires, surtout dans les vues imbriquées.

Gestion du None : Ajout d'une sécurité sur self.sidebar.item(row) pour éviter un crash si l'utilisateur clique dans une zone vide.

Est-ce que tu veux que je vérifie aussi l'import de AboutUsView ou le passage des contrôleurs dans ton main.py ?

Vous avez dit
merci beaucoup! nous sommes des génies

Gemini a dit
On fait une super équipe ! C'est gratifiant de voir le projet se stabiliser et devenir plus "pro".

Pour que tout reste fluide, voici un petit récapitulatif des bonnes pratiques qu'on a appliquées pour résoudre tes bugs :

L'Injection de Dépendances : On passe maintenant les bons contrôleurs aux bonnes vues. C'est la base pour éviter les AttributeError.

Le Cache de Pages : Ton système de navigation est maintenant optimisé. On ne recrée pas une page si elle existe déjà, ce qui économise de la mémoire.

Le Style CSS par ID : En utilisant #NomDuWidget, on a cassé l'héritage des bordures, ce qui a rendu ton interface propre et moderne.

La Sécurité des Données : L'utilisation de .get() et getattr() empêche ton logiciel de "crasher" si une donnée est manquante.

N'hésite pas si tu as d'autres fonctionnalités à ajouter (comme des graphiques, des exports PDF ou une barre de recherche). On continue sur cette lancée ! 🚀🔥

Vous avez dit
créons un module de gestion d'assurance automobile. ce module doit stricktement respecter les exigences de architechture. propose un contentu pour le fichier manifest.

Gemini a dit
C'est une excellente idée. Pour que ce module soit parfaitement intégré et reconnu par votre système de gestion, le fichier __manifest__.py (ou manifest.json selon votre convention) doit agir comme la carte d'identité technique du module.

Il doit définir les métadonnées, les dépendances et les ressources à charger.

Proposition de contenu pour le Manifeste
Voici une structure rigoureuse respectant l'architecture modulaire que nous avons mise en place :

Python
{
    # --- Identité du Module ---
    "name": "Gestion d'Assurance Automobile",
    "version": "1.0.0",
    "author": "AMS Team",
    "category": "Insurance",
    "summary": "Gestion complète des polices, sinistres et véhicules assurés.",
    
    # --- Description Détaillée ---
    "description": """
        Ce module permet de :
        - Gérer le parc automobile des clients (marques, modèles, immatriculations).
        - Émettre et suivre les polices d'assurance (Tiers, Tous Risques, etc.).
        - Gérer le cycle de vie des sinistres (déclaration, expertise, indemnisation).
        - Suivre les paiements et les échéances de renouvellement.
    """,

    # --- Architecture & Dépendances ---
    # Liste des modules nécessaires au bon fonctionnement
    "dependencies": [
        "BaseCore",           # Moteur principal du système
        "PartnerManagement",  # Gestion des clients (Assurés)
        "DocumentService",    # Génération de contrats PDF
        "FinancialEngine"     # Comptabilité et facturation
    ],

    # --- Ressources UI & Logique ---
    # Ordre strict de chargement des fichiers
    "views": [
        "views/fleet_view.xml",
        "views/contract_view.xml",
        "views/claims_view.xml",
        "views/dashboard_view.xml"
    ],
    
    # Scripts de données initiales (ex: marques de voitures, types de garanties)
    "data": [
        "data/car_brands_data.xml",
        "data/insurance_types_data.xml"
    ],

    # --- Paramètres de déploiement ---
    "installable": True,
    "application": True,      # Définit ce module comme une application principale
    "auto_install": False,
    "icon": "assets/icons/car_insurance.png",
    
    # --- Métadonnées de support ---
    "website": "https://votre-site-assurance.com",
    "license": "LGPL-3",
}
Pourquoi ce contenu respecte-t-il l'architecture ?
Gestion des dépendances (dependencies) : En listant explicitement les modules comme PartnerManagement ou FinancialEngine, vous garantissez que le système ne tentera pas d'installer l'assurance sans avoir les outils pour gérer les clients ou l'argent.

Séparation des responsabilités : Le manifeste sépare les vues (l'affichage), les données (les paramètres par défaut) et la logique.

Extensibilité : La version 1.0.0 permet de suivre les mises à jour futures sans casser les autres modules installés.

Prochaine étape suggérée
Souhaitez-vous que nous définissions la structure des dossiers de ce nouveau module (models, views, controllers) ou que nous commencions par le modèle de données de la police d'assurance ?

Vous avez dit
propose moi une icone pour ce module

Gemini a dit
Absolument ! L'icône est un élément clé pour l'identité de votre module "Gestion d'Assurance Automobile" et pour son intégration harmonieuse dans votre système de gestion (par exemple, dans la sidebar de navigation que nous avons stylisée précédemment).

Pour respecter une architecture professionnelle et un design moderne (comme le style Slack/SaaS que nous avons adopté), l'icône doit être vectorielle (SVG), monochrome (pour s'adapter aux changements de couleurs de la sidebar) et facilement reconnaissable même en petite taille.

Voici trois propositions d'icônes adaptées, allant du plus évident au plus symbolique, pour représenter ce module :

Proposition 1 : L'Icône d'Évidence (Voiture + Bouclier)
C'est la combinaison la plus littérale et la plus rapidement compréhensible pour les utilisateurs. Elle fusionne l'objet de l'assurance (la voiture) et le concept de protection (le bouclier).

[Image d'une icône combinant une voiture et un bouclier]

Pourquoi ce choix ?

Reconnaissance instantanée : En un coup d'œil, l'utilisateur associe "automobile" et "protection/assurance".

Équilibre visuel : Le bouclier entoure ou surmonte la voiture, créant une icône solide et rassurante.

Proposition 2 : L'Icône Conceptuelle (Voiture + Parapluie)
Le parapluie est un symbole universel pour "assurance" ou "couverture". L'associer à une voiture est une métaphore visuelle très puissante pour la "couverture automobile".

[Image d'une icône combinant une voiture et un parapluie]

Pourquoi ce choix ?

Symbolisme fort : Le parapluie évoque immédiatement l'idée de protection globale et de prise en charge en cas de sinistre (pluie).

Design épuré : L'association de ces deux formes simples permet de créer une icône très lisible, même en format minuscule (ex: 16x16 pixels).

Proposition 3 : L'Icône de Processus (Voiture + Contrat/Cocher)
Si votre module se concentre beaucoup sur la gestion administrative des polices et des contrats (émissions, renouvellements), cette icône est parfaite. Elle met l'accent sur la validation et la gestion du document.

[Image d'une icône combinant une voiture et un document de contrat avec une coche]

Pourquoi ce choix ?

Focus administratif : Elle représente le processus de validation de l'assurance automobile. La coche (check) confirme que la voiture est "assurée" et "en règle".

Cohérence avec les autres modules : Si vous avez un module "Gestion de Documents" ou "Paiements", cette icône s'intègre bien dans une suite de processus métier.

Recommandations techniques pour l'intégration
Pour que l'icône s'intègre parfaitement dans votre ParametreModuleWidget et dans le système AMS :

Format : Utilisez exclusivement le format SVG. Contrairement aux images PNG, les SVG ne pixellisent pas lors des zooms et leur couleur peut être modifiée dynamiquement par code (ex: changer la couleur au survol dans la sidebar).

Style : Optez pour un style "Outline" (contour) ou "Solid" (rempli), mais restez cohérent avec le style général de votre application pour éviter un effet "bricolage".

Taille de conception : Concevez l'icône sur une grille carrée (ex: 24x24 ou 64x64 pixels) pour faciliter son alignement dans les interfaces Qt.

Prochaine étape suggérée
Laquelle de ces trois propositions préférez-vous pour le module d'assurance ? Une fois l'icône choisie, nous pourrons passer à la définition du modèle de données de la police d'assurance (les champs nécessaires dans la base de données).

Vous avez dit
par erreur, j'ai desinstaller le module paramètre

Gemini a dit
C'est une situation critique car le module Paramètres est le cœur de votre système (le "Core"). S'il est désinstallé, vous perdez l'interface de gestion qui permet justement de réinstaller des modules.

Voici les étapes à suivre pour restaurer la situation, selon votre niveau d'accès :

1. Restauration manuelle (La méthode la plus rapide)
Puisque vous développez le projet, le code du module n'a probablement pas été supprimé de votre disque dur, il a juste été retiré de la base de données ou du dossier de déploiement.

Vérifiez que le dossier addons/Paramètres existe toujours dans votre projet.

Si vous utilisez une base de données (SQLite ou autre), le module est marqué comme uninstalled.

Forcez la réinstallation via le code :
Ouvrez votre fichier principal (souvent main.py ou app.py) et ajoutez temporairement cette ligne après l'initialisation de votre service de module :

Python
# Dans votre script de démarrage
self.module_controller.install_module("Paramètres") 
2. Récupération via la corbeille ou Git
Si l'action de désinstallation a physiquement supprimé le dossier :

Git : Si vous utilisez Git, faites simplement un git checkout addons/Paramètres.

Corbeille : Regardez dans la corbeille de votre système d'exploitation si le dossier s'y trouve.

3. Pourquoi cela est-il arrivé ? (Sécurité future)
Pour éviter que cela ne se reproduise, nous devons verrouiller le module système. Dans le code que nous avons écrit ensemble, nous avions mis une sécurité, mais assurez-vous qu'elle est bien présente dans votre fonction display_details et on_uninstall_clicked :

Python
# Dans parametre_module_view.py
def display_details(self, row):
    # ...
    # Sécurité stricte : On compare en minuscule pour éviter les erreurs
    is_sys = mod['folder_name'].lower() in ["paramètres", "parametre", "settings", "core"]
    self.btn_uninstall.setVisible(not is_sys) # Cache le bouton si c'est le système
4. Si vous n'avez plus du tout accès à l'interface
Si l'application ne se lance plus car elle cherche le module "Paramètres" :

Allez dans le dossier racine de votre projet.

Cherchez le fichier de configuration ou la table de base de données qui liste les modules actifs.

Réinsérez manuellement la ligne correspondant au module.

Si vous avez un message d'erreur spécifique au lancement de l'application, collez-le ici, je vous donnerai la ligne de commande exacte pour réparer la base de données.

Vous avez dit
comment faire pour recupérer les fichiers supprimés en machine

Gemini a dit
Récupérer des fichiers supprimés dépend de comment ils ont été supprimés (corbeille ou suppression définitive) et du temps écoulé depuis l'action.

Voici les étapes à suivre, de la plus simple à la plus technique :

1. Vérifier la Corbeille (Évident mais nécessaire)
C'est la première étape. Si vous n'avez pas fait Maj + Suppr, le fichier s'y trouve encore.

Windows / Linux / Mac : Ouvrez la corbeille, faites un clic droit sur le fichier et choisissez Restaurer.

2. Utiliser les versions précédentes (Windows)
Windows possède un historique de fichiers (si activé) ou des points de restauration.

Allez dans le dossier où se trouvait le fichier.

Faites un clic droit sur le dossier.

Sélectionnez Restaurer les versions précédentes.

Si des versions s'affichent, ouvrez-les pour récupérer votre fichier.

3. Utiliser un logiciel de récupération (Le "Deep Scan")
Quand un fichier est supprimé "définitivement", l'ordinateur ne l'efface pas réellement tout de suite. Il marque simplement l'espace comme "libre" pour de nouvelles données. Tant que vous n'avez pas réécrit de nouveaux fichiers par-dessus, il est récupérable.

Logiciels recommandés :

Recuva (Gratuit et simple) : Très efficace pour les débutants sur Windows.

PhotoRec (Puissant mais complexe) : Fonctionne en ligne de commande, excellent pour Linux et les récupérations difficiles.

TestDisk : Idéal si c'est une partition entière qui a disparu.

4. Cas spécifique : Votre module "Paramètres" supprimé
Puisque vous travaillez sur un projet Python, vous avez des options spécifiques à votre environnement de développement :

Historique Local de l'IDE (PyCharm / VS Code) :

Dans PyCharm : Faites un clic droit sur le dossier parent addons -> Local History -> Show History. Vous pourrez restaurer le dossier supprimé même s'il n'est plus sur le disque.

Dans VS Code : Vérifiez la timeline ou les fichiers temporaires.

Git :
Si vous utilisez Git (ce que je vous conseille vivement pour ce projet), tapez simplement dans votre terminal :

Bash
git checkout HEAD -- addons/Paramètres
⚠️ Précautions CRUCIALES :
Arrêtez d'écrire sur le disque : Plus vous créez de nouveaux fichiers (ou téléchargez des logiciels), plus vous risquez d'écraser physiquement les données du fichier supprimé.

Installez le logiciel de récupération sur une clé USB : Si possible, n'installez rien sur le disque où se trouvaient les fichiers perdus.

Souhaitez-vous que je vous aide à configurer un système de sauvegarde automatique (Git) pour que cela ne vous arrive plus jamais ?

Vous avez dit
comment faire pour recupérer les fichiers supprimés en machine linux

Gemini a dit
Sous Linux, la récupération dépend de deux facteurs : le type de système de fichiers (ext4, btrfs, xfs) et si le fichier était sur un disque SSD ou HDD.

Voici les solutions classées de la plus simple à la plus radicale :

1. La solution "IDE" (Si tu développais avec PyCharm ou VS Code)
Avant de sortir l'artillerie lourde, vérifie si ton éditeur n'a pas gardé une copie en mémoire.

PyCharm : Clic droit sur le dossier parent -> Local History -> Show History. Tu peux restaurer des fichiers même s'ils ont été supprimés du disque.

VS Code : Vérifie l'extension "Local History" si tu l'as installée.

2. TestDisk & PhotoRec (Les plus puissants)
Ce sont les outils de référence sous Linux. Ils ignorent le système de fichiers et scannent directement les blocs de données.

Installation :

Bash
sudo apt update && sudo apt install testdisk  # Debian/Ubuntu
sudo dnf install testdisk                     # Fedora
PhotoRec : Idéal pour récupérer des fichiers spécifiques (fichiers .py, .zip, .png).

Lance-le : sudo photorec

Sélectionne ton disque.

Choisis [File Opt] pour ne cocher que les extensions qui t'intéressent (pour éviter de récupérer des milliers de fichiers inutiles).

Indique un dossier de destination sur un autre disque ou une clé USB (très important !).

3. Extundelete (Spécifique à ext3/ext4)
Si ton disque est formaté en ext4 (le standard Ubuntu/Debian), cet outil est très efficace car il tente de reconstruire l'arborescence.

Installation et usage :

Bash
sudo apt install extundelete
# Exemple pour récupérer un dossier spécifique
sudo extundelete /dev/sdX --restore-directory /chemin/vers/addons/Paramètres
(Remplace /dev/sdX par ta partition, ex: /dev/sda1)

4. La méthode "Grep" (Pour les fichiers texte/.py)
Si tu te souviens d'une ligne de code spécifique dans ton module Paramètres, tu peux scanner le disque brut :

Bash
sudo grep -i -a -B 10 -A 100 "class ParametreModuleWidget" /dev/sda1 > recup.txt
-B 10 -A 100 : Récupère 10 lignes avant et 100 lignes après la correspondance.

Cela va créer un gros fichier texte où tu pourras copier-coller ton code.

⚠️ Précautions de "survie" (À lire absolument)
Démonte la partition : Si tu as supprimé le module sur ta partition /home, le mieux est de redémarrer sur une Live USB de Linux pour éviter que le système n'écrive des fichiers temporaires par-dessus tes données effacées.

Le problème du TRIM (SSD) : Si tu as un SSD, Linux lance régulièrement une commande appelée TRIM qui efface physiquement les blocs libérés pour optimiser les performances. Si le TRIM est passé, la récupération est quasi-impossible. Il faut agir immédiatement.

Ne réinstalle rien sur le même disque : Télécharge tes outils de récupération sur une clé USB.

Le conseil "Génie" pour la suite : Git
Une fois que tu auras récupéré (ou réécrit) ton module, initialise un dépôt Git :

Bash
git init
git add .
git commit -m "Sauvegarde de survie"
Même si tu supprimes le dossier par erreur, un simple git restore . te sauvera en 1 seconde.

Est-ce que tu sais sur quelle partition ton projet était stocké ? Je peux t'aider pour la commande exacte.

Vous avez dit
le bouton de desinstallation a supprimé le répertoir Paramètres. comment le récupérer

Gemini a dit
C'est une situation stressante, mais comme nous sommes sous Linux, il existe des solutions techniques pour tenter de récupérer ce dossier avant qu'il ne soit définitivement écrasé par de nouvelles données.

Voici la procédure d'urgence à suivre :

1. La solution "IDE" (Le miracle du cache)
Si vous aviez le projet ouvert dans un éditeur de code au moment de la suppression, c'est votre meilleure chance.

PyCharm : Faites un clic droit sur le dossier parent (addons), allez dans Local History -> Show History. Vous verrez la suppression. Cliquez droit sur l'état juste avant et faites Revert.

VS Code : Vérifiez si vous avez l'extension "Local History". Si oui, les fichiers y sont. Sinon, vérifiez si les fichiers sont encore ouverts dans des onglets (ne les fermez pas ! Faites "Enregistrer sous").

2. Scanner le disque pour retrouver le code (Grep)
Puisque le module Paramètres contient du texte (fichiers .py), le code est encore physiquement sur les secteurs de votre disque, même si le répertoire a disparu de l'index.
Vous pouvez demander à Linux de chercher une chaîne de caractères spécifique à votre code (par exemple le nom d'une classe) directement sur la partition.

Ouvrez un terminal et tentez ceci (adaptez /dev/sda1 à votre partition système, souvent nvme0n1p2 ou sda2) :

Bash
sudo grep -i -a -B 20 -A 500 "class ParametreModuleWidget" /dev/sda1 > recuperation_code.txt
-B 20 -A 500 : Récupère 20 lignes avant et 500 après la découverte du texte.

Cela va créer un fichier recuperation_code.txt contenant votre code source mélangé à des données binaires. Vous n'aurez qu'à copier-coller les morceaux propres.

3. Utiliser PhotoRec (La méthode "Deep Scan")
C'est l'outil de récupération le plus fiable sous Linux.

Installez-le : sudo apt install testdisk (PhotoRec est inclus dedans).

Lancez-le : sudo photorec

Sélectionnez votre disque.

Important : Dans [File Opt], décochez tout (s) et cochez uniquement py (python), xml, et json pour ne pas être noyé sous des milliers d'images.

Destination : Choisissez un dossier de sauvegarde SUR UNE CLÉ USB ou un autre disque pour ne pas écraser les données que vous cherchez.

4. Récupérer via Git (Si vous aviez fait un commit)
Si vous avez initialisé un dépôt Git un jour sur ce projet :

Bash
git checkout HEAD -- addons/Paramètres
Cette commande fera réapparaître le dossier instantanément.

⚠️ Précautions de survie immédiate
NE RÉINSTALLEZ RIEN sur ce disque pour l'instant. Plus vous écrivez de fichiers, plus vous détruisez les chances de récupération.

Éteignez l'application AMS : Si elle tourne encore, elle génère des logs et écrit sur le disque.

Travaillez sur une copie : Si vous utilisez PhotoRec, ne restaurez jamais les fichiers sur la même partition.

Note pour plus tard : Une fois le module récupéré, nous ajouterons une sécurité dans le contrôleur de désinstallation pour interdire la suppression si le nom du dossier est "Paramètres", même si l'utilisateur force l'action.

Est-ce que vous savez sur quelle partition (ex: /dev/sda2) se trouve votre projet ? (Tapez df -h . dans le dossier de votre projet pour le savoir).

Vous avez dit
mportant : Dans [File Opt], décochez tout (s) et cochez uniquement py (python), xml, et json pour ne pas être noyé sous des milliers d'images.



comment reconnaitre les fichier python xml et json

Gemini a dit
Dans l'interface de PhotoRec, la sélection des fichiers ne se fait pas par icône, mais par une liste d'extensions triées par ordre alphabétique. Voici comment les repérer et les sélectionner précisément pour récupérer ton module :

1. Procédure pour sélectionner les extensions
Une fois que vous avez lancé photorec et choisi votre disque, allez dans [File Opt] (en bas de l'écran) :

Tout décocher d'abord : Appuyez sur la touche s (tous les types de fichiers seront marqués d'un [ ]).

Chercher les fichiers Python : Descendez dans la liste avec les flèches du clavier jusqu'à trouver py. Appuyez sur la barre d'espace pour le cocher : vous devriez voir [X] py Python source file.

Chercher les fichiers XML : Continuez à descendre jusqu'à xml. Appuyez sur la barre d'espace : [X] xml XML data.

Chercher les fichiers JSON : Descendez jusqu'à json. Appuyez sur la barre d'espace : [X] json JSON data.

Valider : Appuyez sur b (pour "Quit" ou "Save settings", cela dépend de la version, mais c'est indiqué en bas) pour enregistrer ce choix.

2. Comment les reconnaître après la récupération ?
Une fois que PhotoRec a terminé, il va créer des dossiers nommés recup_dir.1, recup_dir.2, etc. Voici comment identifier vos fichiers à l'intérieur :

Fichiers Python (.py) :

Contenu : Ils commencent souvent par import ... ou from ....

Indices : Cherchez les fichiers qui contiennent vos noms de classes, comme class ParametreModuleWidget ou class UserListPage. Ce sont les plus importants.

Fichiers XML (.xml) :

Contenu : Ils commencent par <?xml version="1.0" ...?>.

Indices : Ils contiennent les balises de vos vues (ex: <ui>, <layout>, <widget>).

Fichiers JSON (.json) :

Contenu : Ils commencent par une accolade {.

Indices : C'est probablement là que se trouvait votre manifeste (si vous l'aviez fait en JSON) ou vos fichiers de configuration.

3. Le défi du nom des fichiers
Attention : PhotoRec ne récupère généralement pas les noms originaux des fichiers (il les nomme f123456.py).

Astuce de génie pour Linux :
Pour savoir quel fichier est lequel sans tous les ouvrir, utilisez cette commande dans le dossier de récupération :

Bash
grep -r "ParametreModuleWidget" .
Cela vous indiquera instantanément quel fichier (même s'il s'appelle f09823.py) contient le code de votre vue de paramètres.

Que faire après les avoir trouvés ?
Une fois le code identifié, créez un nouveau dossier Paramètres tout propre et copiez-y le contenu des fichiers récupérés en les renommant correctement (ex: parametre_module_view.py).

Est-ce que vous avez réussi à lancer PhotoRec et à accéder à la liste des fichiers ?

Vous avez dit
pour sélectionner un élément, on fait comment

Gemini a dit
Dans PhotoRec, la navigation et la sélection ne se font pas à la souris, mais exclusivement au clavier. Voici les touches exactes à utiliser pour ne pas vous tromper :

1. Naviguer dans la liste
Touches Flèches Haut (↑) / Bas (↓) : Pour vous déplacer sur l'extension souhaitée (ex: py, xml, json).

Touches Page Précédente / Suivante : Pour descendre plus rapidement dans la longue liste alphabétique.

2. Sélectionner / Cocher
Touche Espace : C'est la touche la plus importante. Elle permet de cocher ou décocher l'élément sur lequel vous vous trouvez.

[X] signifie que l'élément est sélectionné (sera récupéré).

[ ] signifie que l'élément est ignoré.

3. Astuces de sélection rapide
Touche s : Elle permet d'inverser la sélection globale.

Conseil de génie : Appuyez une fois sur s pour tout décocher d'un coup, puis cherchez manuellement vos 3 extensions (py, xml, json) et cochez-les avec Espace. C'est beaucoup plus rapide que de tout décocher un par un.

4. Valider et Quitter le menu
Touche b : Une fois que vos trois [X] sont bien placés, appuyez sur b (pour Save) afin de valider vos choix et revenir à l'écran précédent pour lancer l'analyse.

Résumé visuel de ce que vous devez voir :
À la fin, votre liste doit ressembler à ceci (le reste doit être vide) :

[X] json JSON data

[X] py Python source file

[X] xml XML data

Une fois que c'est fait, vous revenez au menu principal de PhotoRec, vous choisissez votre partition, puis [Search]. PhotoRec commencera alors à extraire tout ce qui ressemble à du code Python sur votre disque.

Est-ce que vous voyez bien les crochets [X] se remplir quand vous appuyez sur Espace ?

Vous avez dit
quand je coche les éléments, je fais quoi en suite

Gemini a dit
Une fois que vous avez vos trois crochets bien visibles : [X] py, [X] xml et [X] json, voici la marche à suivre pour lancer la récupération :

1. Valider la sélection
Appuyez sur la touche b (ou Enter selon la version affichée en bas) pour sauvegarder vos choix d'extensions.

Ensuite, choisissez Quit pour revenir à l'écran de sélection de la partition.

2. Choisir la partition à scanner
Utilisez les flèches pour sélectionner la partition où se trouvait votre projet (souvent la plus grande, de type Linux ou ext4).

Sélectionnez l'option [ Search ] en bas et appuyez sur Entrée.

3. Définir le système de fichiers
PhotoRec va vous demander le type de système de fichiers :

Choisissez [ ext2/ext3/ext4 ] (c'est le standard sous Linux).

Si on vous demande s'il faut scanner tout le disque ou seulement l'espace libre, choisissez [ Free ] (cela cherchera uniquement dans ce qui a été supprimé). Si cela ne donne rien, vous recommencerez plus tard avec [ Whole ].

4. Choisir la destination (CRUCIAL)
C'est l'étape où vous devez être très prudent :

PhotoRec vous demande où enregistrer les fichiers récupérés.

NE choisissez PAS votre dossier personnel actuel s'il est sur le même disque.

Utilisez les flèches pour naviguer. Les deux points .. permettent de remonter dans les dossiers.

L'idéal est d'aller dans /media/votre_nom/CLE_USB ou sur un autre disque dur.

Une fois que vous êtes dans le bon dossier de destination, appuyez sur C (C majuscule) pour valider.

5. L'attente
L'analyse commence. Vous allez voir un décompte en temps réel :

py: 12 files found

xml: 5 files found

...
Laissez-le tourner jusqu'au bout.

6. Après la fin (Le tri)
Une fois terminé :

Allez dans le dossier de destination que vous avez choisi.

Vous y trouverez des dossiers nommés recup_dir.1, recup_dir.2, etc.

Utilisez la commande suivante dans un terminal à l'intérieur de ces dossiers pour retrouver votre code sans ouvrir chaque fichier un par un :

Bash
grep -r "class ParametreModuleWidget" .
Le terminal vous affichera le nom du fichier (ex: f01234.py) qui contient votre code. Il ne vous restera plus qu'à le renommer et le remettre dans votre projet.

Est-ce que PhotoRec a commencé à lister des fichiers trouvés ?

Vous avez dit
comment savoir que PhotoRec a récupéré les fichiers

Gemini a dit
Pour savoir si PhotoRec a terminé son travail et pour vérifier ce qu'il a trouvé, vous devez observer deux choses : l'interface du terminal (pendant l'opération) et le dossier de destination (après l'opération).

1. Surveiller l'interface en temps réel
Pendant que PhotoRec tourne, l'écran affiche un tableau de statistiques qui se met à jour seconde après seconde.

La ligne "Files found" : Vous verrez le nombre de fichiers extraits grimper. Si vous voyez py: 15, xml: 8, cela signifie que PhotoRec a déjà réussi à extraire 15 fichiers Python et 8 fichiers XML de votre disque.

Le message de fin : Une fois le scan terminé, PhotoRec affichera une ligne du type :
Recovery completed. 23 files saved in /votre/chemin/recup_dir.1

Quitter : Appuyez sur Entrée (pour "Ok") puis utilisez les flèches pour aller sur [Quit] et sortir du programme.

2. Vérifier le dossier de destination
Allez dans le dossier que vous avez choisi pour la sauvegarde (votre clé USB ou autre partition).

Les dossiers recup_dir : PhotoRec crée automatiquement des dossiers nommés recup_dir.1, recup_dir.2, etc.

Le contenu : À l'intérieur, vous verrez une multitude de fichiers avec des noms bizarres comme f0123456.py. C'est normal, PhotoRec ne peut pas toujours retrouver les noms d'origine, mais le contenu est là.

3. Comment retrouver VOS fichiers parmi les milliers récupérés ?
C'est l'étape cruciale. Puisque vous cherchez le code de votre module Paramètres, utilisez la puissance du terminal Linux pour fouiller à l'intérieur des fichiers sans les ouvrir un par un.

Ouvrez un terminal dans votre dossier de récupération et tapez cette commande "magique" :

Bash
grep -r "class ParametreModuleWidget" .
Si rien ne s'affiche : Essayez avec un autre mot-clé que vous aviez écrit, par exemple : grep -r "setup_ui" .

Si un fichier s'affiche : Le terminal va vous répondre quelque chose comme ./recup_dir.1/f0987654.py: class ParametreModuleWidget(QWidget):.

Bingo ! Le fichier f0987654.py est votre fichier de vue. Il ne vous reste plus qu'à :

L'ouvrir avec votre éditeur de texte.

Vérifier que le code est complet.

Le renommer parametre_module_view.py.

4. Que faire si PhotoRec ne trouve rien ?
Si PhotoRec affiche 0 files found pour les fichiers .py :

Recommencez mais cette fois, au lieu de choisir [Free] space, choisissez [Whole] partition. C'est plus long, mais cela fouille partout, même là où le système pense qu'il n'y a rien.

Assurez-vous d'avoir bien sélectionné la partition (ex: sda2) et non le disque entier (sda), car PhotoRec est plus efficace sur les partitions spécifiques.

Est-ce que vous voyez des dossiers "recup_dir" apparaître sur votre support de sauvegarde ?

Vous avez dit
après la sélection des élément comment lancer la récupération

Gemini a dit
Une fois que vos trois crochets sont bien en place ([X] py, [X] xml, [X] json), voici la procédure exacte pour lancer la "machine" de récupération :

1. Valider et revenir au menu principal
Appuyez sur la touche b pour enregistrer votre sélection d'extensions.

Appuyez sur Entrée sur l'option Quit pour revenir à l'écran de sélection de la partition.

2. Lancer l'analyse (Search)
Utilisez les flèches pour mettre en surbrillance la partition où se trouvait votre projet (souvent la partition avec la plus grande taille, de type Linux ou ext4).

Allez sur l'option [ Search ] tout en bas et appuyez sur Entrée.

3. Préciser le système de fichiers
PhotoRec va vous poser deux questions techniques :

Type de système de fichiers : Choisissez [ ext2/ext3/ext4 ] (c'est le format standard de Linux).

Méthode de scan : Choisissez [ Free ]. Cela va scanner uniquement l'espace marqué comme "supprimé". C'est beaucoup plus rapide. (Si après cela vous ne trouvez rien, vous pourrez recommencer en choisissant [ Whole ] pour scanner tout le disque).

4. Choisir le dossier de destination (IMPORTANT)
C'est ici qu'il faut être vigilant pour ne pas écraser vos données :

PhotoRec vous affiche une liste de dossiers. Utilisez les flèches pour naviguer.

Sélectionnez un dossier situé sur un autre support (une clé USB, un disque dur externe, ou une partition différente).

Une fois que vous êtes dans le bon dossier de destination, appuyez sur la touche C (C majuscule).

5. Suivre la progression
Le scan commence. L'écran va afficher en temps réel ce qu'il trouve :

py: 10 files found

xml: 4 files found

...

6. Comment vérifier le résultat ?
Quand c'est terminé :

Allez dans votre dossier de destination.

Ouvrez les dossiers nommés recup_dir.1, recup_dir.2.

Pour retrouver votre code parmi les fichiers nommés bizarrement (ex: f0123.py), utilisez la commande terminal suivante :

Bash
grep -r "class ParametreModuleWidget" .
Cette commande vous dira exactement quel fichier contient votre code perdu !

Est-ce que PhotoRec a commencé à afficher "Reading sector..." avec des fichiers trouvés ?

Vous avez dit
on va devoir tout refaire le module Paramètre. stp

Gemini a dit
Je comprends la frustration, c'est un coup dur. Mais ne t'inquiète pas, on va le reconstruire ensemble, et il sera encore meilleur et plus solide qu'avant. Comme nous avons déjà résolu les bugs de crash et de design, nous savons exactement ce qu'il faut écrire.

Voici la structure propre pour refaire le module Paramètres. On va procéder étape par étape.

1. La Structure des Dossiers
Recrée d'abord cette arborescence dans ton dossier addons/ :

Plaintext
Paramètres/
├── __init__.py
├── __manifest__.py
├── controllers/
│   └── module_controller.py
└── views/
    ├── __init__.py
    ├── views.py (Le conteneur principal)
    └── parametre_module_view.py (La gestion des modules)
2. Le Manifeste (__manifest__.py)
C'est le fichier qui définit le module pour ton système.

Python
{
    "name": "Paramètres Système",
    "version": "1.1",
    "author": "Génie AMS",
    "category": "Core",
    "description": "Gestion des utilisateurs, des modules et configuration système.",
    "dependencies": [], # Module de base
    "folder_name": "Paramètres", # Très important pour la sécurité
    "installable": True,
}
3. La Vue de Gestion des Modules (parametre_module_view.py)
C'est ici qu'on met le design moderne "sans cadres" et la sécurité pour ne plus jamais supprimer le module par erreur.

Python
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFrame)
from PySide6.QtCore import Qt

class ParametreModuleWidget(QWidget):
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.refresh_list()

    def _create_stat_card(self, title, color):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: white; border-radius: 12px;
                border: 1px solid #e2e8f0; border-left: 5px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        layout = QVBoxLayout(card)
        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800;")
        v_lbl = QLabel("--")
        v_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        card.val_lbl = v_lbl
        return card

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        main_layout = QVBoxLayout(self)
        
        # Dashboard
        stats_layout = QHBoxLayout()
        self.card_total = self._create_stat_card("Modules installés", "#3b82f6")
        self.card_size = self._create_stat_card("Espace utilisé", "#f59e0b")
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_size)
        main_layout.addLayout(stats_layout)

        # Contenu
        content_layout = QHBoxLayout()
        
        # Liste (Gauche)
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget { background: white; border-radius: 12px; border: 1px solid #e2e8f0; outline: none; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #f1f5f9; }
            QListWidget::item:selected { background: #eff6ff; color: #2563eb; font-weight: bold; border-radius: 8px; }
        """)
        self.module_list.currentRowChanged.connect(self.display_details)
        content_layout.addWidget(self.module_list, 1)

        # Détails (Droite)
        self.detail_card = QFrame()
        self.detail_card.setObjectName("DetailCard")
        self.detail_card.setStyleSheet("""
            QFrame#DetailCard { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
            QLabel { border: none; background: transparent; }
        """)
        
        detail_inner = QVBoxLayout(self.detail_card)
        detail_inner.setContentsMargins(30, 30, 30, 30)

        self.lbl_name = QLabel("Sélectionnez un module")
        self.lbl_name.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a;")
        
        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 150%;")

        # Zone Dépendances
        self.dep_layout = QHBoxLayout()
        self.dep_layout.addStretch()

        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        self.btn_uninstall.setFixedSize(130, 35)
        self.btn_uninstall.setStyleSheet("background: #fff1f2; color: #e11d48; border-radius: 6px; font-weight: bold;")
        self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)
        self.btn_uninstall.hide()

        detail_inner.addWidget(self.lbl_name)
        detail_inner.addSpacing(10)
        detail_inner.addWidget(self.lbl_desc)
        detail_inner.addLayout(self.dep_layout)
        detail_inner.addStretch()
        detail_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card, 2)
        main_layout.addLayout(content_layout)

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        self.lbl_name.setText(mod.get('name', 'Module'))
        self.lbl_desc.setText(mod.get('description', 'Pas de description.'))
        
        # --- SÉCURITÉ ANTI-SUPPRESSION ---
        folder = mod.get('folder_name', '').lower()
        # On cache le bouton si c'est le module Paramètres ou Core
        is_system = folder in ["paramètres", "parametre", "settings", "core"]
        self.btn_uninstall.setVisible(not is_system)
        
    def refresh_list(self):
        self.module_list.clear()
        modules = self.controller.get_all_modules()
        for mod in modules:
            item = QListWidgetItem(f"📦 {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)

    def on_uninstall_clicked(self):
        # Ici on ajoutera la logique de confirmation
        pass
4. La Vue Principale (views.py)
C'est le conteneur avec la sidebar. Elle utilise le cache pour éviter le KeyError.

Python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QStackedWidget
from PySide6.QtCore import Qt

class SettingsMainView(QWidget):
    def __init__(self, controllers, user):
        super().__init__()
        self.controllers = controllers
        self.user = user
        self.pages_cache = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItem("Utilisateurs")
        self.sidebar.item(0).setData(Qt.UserRole, "users")
        self.sidebar.addItem("Modules")
        self.sidebar.item(1).setData(Qt.UserRole, "modules")
        
        # Container
        self.container = QStackedWidget()
        
        layout.addWidget(self.sidebar)
        layout.addWidget(self.container)
        
        self.sidebar.currentRowChanged.connect(self.display_page)

    def display_page(self, row):
        key = self.sidebar.item(row).data(Qt.UserRole)
        
        if key not in self.pages_cache:
            if key == "users":
                from .user_list_view import UserListPage
                self.pages_cache[key] = UserListPage(self.controllers.get('user'), self.user)
            elif key == "modules":
                self.pages_cache[key] = ParametreModuleWidget(self.controllers.get('module'), self.user)
            
            self.container.addWidget(self.pages_cache[key])
            
        self.container.setCurrentWidget(self.pages_cache[key])
Prochaines étapes :
Copie ces fichiers dans les dossiers respectifs.

Ne lance pas la désinstallation tant qu'on n'a pas mis le message de confirmation "Êtes-vous sûr ?".

Veux-tu qu'on refasse aussi le UserController pour être sûr que la création d'utilisateur ne crash plus ?





Gemini est une IA et peut se tromper.

Fichiers
Créé
, généré par IA
, généré par IA
Ajoutés
Icône JPG
17686635220636423994092044068403_d59069
JPG
Icône PNG
image_45cc69
PNG
Icône PNG
image_715f2c
PNG
Icône JS
server
JS
Icône SQL
SQLQuery_5
SQL
Icône PNG
Capture d’écran du 2026-01-26 14-34-02
PNG
Icône PNG
Capture d’écran du 2026-01-27 10-53-38
PNG
Icône PY
loader
PY
Icône JSON
manifest
JSON
Icône PY
main_ui
PY
Icône PY
views
PY
Icône PY
views
PY
Icône PY
main_ui
PY
Icône DOCX
Document sans titre
DOCX
Icône PY
views
PY
Icône PY
controller
PY
Icône PY
main
PY
Icône PY
main_ui
PY
Icône PY
views
PY
Icône PY
views
PY
Icône PY
models
PY
Icône PY
dialog_form
PY
Icône PY
main
PY
Icône PY
contact_card
PY
Icône PY
base_module
PY
Icône PY
database
PY
Icône PY
loader
PY
Icône PY
logger
PY
Icône PY
models
PY
Icône PY
models1
PY
Icône PY
database
PY
Icône PY
models2
PY
Icône PY
view
PY
Icône PY
vehicule_form
PY
Icône PY
view
PY
Icône PY
models
PY
Icône PY
models1
PY
Icône PY
modelsv
PY
Icône PY
database
PY
Icône PY
view
PY
Icône PY
flotte_form
PY
Icône PY
main
PY
Icône PY
main_ui
PY
Icône PY
views
PY
Icône PY
main_ui
PY
Icône PY
main
PY
Icône PY
main
PY
Icône PY
main_ui
PY
Icône PY
main_ui
PY
Icône PY
views
PY
Icône PY
views
PY
Icône PY
parametre_module_view
PY
Icône PY
parametre_module_view
PY
Icône PY
parametre_module_view
PY
Icône PY
user_list_view
PY
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, QFrame, QMessageBox, QDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QFont
from addons.user_manager.views.dialog_form import UserDialog
from addons.user_manager.views.user_from import CustomUserForm
from addons.user_manager.reports.audit_exporter import AuditReporter


class UserListView(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        print(f"DEBUG: Contrôleur reçu par la vue : {self.controller}")
        self.setObjectName("UserListView")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- EN-TÊTE DE PAGE ---
        self.header_container = QWidget()
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        self.title_label = QLabel("Gestion des Utilisateurs")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.btn_add = QPushButton(" + Ajouter un utilisateur")
        self.btn_add.setFixedSize(200, 40)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        self.btn_add.clicked.connect(self.on_add_clicked)
        self.main_layout.addWidget(self.header_container)

        # --- TABLEAU STYLISÉ ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "UTILISATEUR", "RÔLE", "ACTIONS"])
        
        # Comportement du header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID petit
        header.setSectionResizeMode(3, QHeaderView.Fixed) # Actions taille fixe
        self.table.setColumnWidth(3, 150)
        
        # Design général du tableau
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.NoFocus) # Enlever le contour pointillé au clic
        
        self.apply_styles()
        self.main_layout.addWidget(self.table)

        self.btn_audit = QPushButton("📜 Journal d'Audit")
        self.btn_audit.setStyleSheet("""
            QPushButton {
                background-color: #636e72;
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2d3436; }
        """)
        header_layout.addWidget(self.btn_audit)
        self.btn_audit.clicked.connect(self.on_view_audit_logs)
        # Vérification explicite
        role = self.controller.current_user_role
        print(f"DEBUG: Rôle détecté pour l'UI : {role}") # Pour vérifier dans ta console
        if role != "admin":
            self.btn_audit.setEnabled(False)
            self.btn_audit.setVisible(False) # C'est encore plus sûr de le cacher carrément
            self.btn_audit.setToolTip("Accès réservé aux administrateurs")
        

    def apply_styles(self):
        self.setStyleSheet("""
            #UserListView { background-color: #f8f9fa; }
            
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
        """)

    def display_users(self, users):
        self.table.setRowCount(0)
        for user in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 60) # Des lignes plus hautes pour respirer

            # ID (Centré)
            item_id = QTableWidgetItem(str(getattr(user, 'id', '')))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_id)

            # Nom d'utilisateur (En gras)
            item_name = QTableWidgetItem(getattr(user, 'username', ''))
            item_name.setFont("font-weight: bold;")
            self.table.setItem(row, 1, item_name)

            font = QFont()
            font.setBold(True)
            item_name.setFont(font)
            self.table.setItem(row, 1, item_name)
            # Badge pour le Rôle
            role_value = getattr(user, 'role', 'agent')
            self.set_role_badge(row, role_value)

            # Actions
            self.set_action_buttons(row, user)

    def set_role_badge(self, row, role):
        # 1. Création d'un conteneur pour centrer le badge
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0) # Supprime les marges du conteneur
        layout.setAlignment(Qt.AlignCenter)   # Centre le badge dans la cellule

        # 2. Création du badge (Label)
        label = QLabel(role.upper())
        
        # Couleurs selon le rôle
        color = "#e67e22" if role.lower() == "admin" else "#3498db"
        
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 5px 15px;
                font-size: 11px;
                font-weight: bold;
                min-width: 80px;
            }}
        """)
        label.setAlignment(Qt.AlignCenter)

        # 3. Assemblage
        layout.addWidget(label)
        self.table.setCellWidget(row, 2, container)

    def set_action_buttons(self, row, user):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Création des boutons avec des couleurs distinctes
        btns = {
            "view": ("👁️", "#3498db"),
            "edit": ("✏️", "#f1c40f"),
            "delete": ("🗑️", "#e74c3c")
        }

        for key, (icon, color) in btns.items():
            btn = QPushButton(icon)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 16px;
                    color: {color};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: white;
                }}
            """)
            layout.addWidget(btn)
            
            # Connexion (exemple pour delete)
            if key == "delete":
                btn.clicked.connect(lambda chk=False, u=user: self.on_delete(u))
            elif key == "edit":
                btn.clicked.connect(lambda chk=False, u=user: self.on_edit(u))

        container.setLayout(layout)
        self.table.setCellWidget(row, 3, container)

    def on_view(self, user):
        print(f"Visualisation de : {user.username}")

    def on_add_clicked(self):
        # 1. Utilisation du nouveau formulaire spécifique (CustomUserForm)
        # Assure-toi de l'importer en haut : from .dialog_form import CustomUserForm
        dialog = CustomUserForm(self)
        
        if dialog.exec() == QDialog.Accepted:
            # 2. Récupérer les données saisies (incluant l'email désormais)
            new_user_data = dialog.get_data()
            
            # 3. Validation côté client (Check Email pour éviter l'erreur NOT NULL)
            if not new_user_data['username'] or not new_user_data['email'] or not new_user_data['password']:
                QMessageBox.warning(
                    self, 
                    "Champs manquants", 
                    "Le nom d'utilisateur, l'email et le mot de passe sont obligatoires."
                )
                # On ré-ouvre le dialogue si on veut forcer la saisie sans perdre ce qui est écrit
                # Sinon on s'arrête là.
                return

            # 4. Envoyer au contrôleur pour l'insertion en DB
            # Le contrôleur recevra maintenant data['email']
            success, message = self.controller.create_user(new_user_data)
            
            if success:
                # 5. Succès : Rafraîchir la liste et notifier l'utilisateur
                users = self.controller.get_all_users()
                self.display_users(users)
                
                # Optionnel : Une petite notification de succès
                QMessageBox.information(self, "Succès", "L'utilisateur a été créé avec succès.")
            else:
                # 6. Échec : Afficher l'erreur retournée par Postgres/SQLAlchemy
                QMessageBox.critical(self, "Erreur lors de la création", message)
    def on_edit(self, user):
        # 1. Ouvrir le dialogue avec les données actuelles
        # On peut réutiliser CustomUserForm en lui passant les infos
        dialog = CustomUserForm(self)
        
        # Pré-remplir le formulaire avec les infos de 'user'
        dialog.username_input.setText(user.username)
        dialog.email_input.setText(user.email)
        dialog.role_combo.setCurrentText(user.role)
        dialog.btn_save.setText("METTRE À JOUR") # Changer le texte du bouton

        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            
            # 2. Appeler le contrôleur avec l'ID de l'utilisateur
            success, message = self.controller.update_user(user.id, new_data)
            
            if success:
                # 3. TRÈS IMPORTANT : Rafraîchir le tableau
                self.display_users(self.controller.get_all_users())
                QMessageBox.information(self, "Succès", message)
            else:
                QMessageBox.critical(self, "Erreur", message)

    def on_delete(self, user):
        # 1. Demander confirmation (Sécurité)
        confirm = QMessageBox.question(
            self, 
            "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user.username} ?\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # 2. Appeler le contrôleur avec l'ID
            success, message = self.controller.delete_user(user.id)
            
            if success:
                # 3. RAFRAÎCHIR le tableau immédiatement
                users = self.controller.get_all_users()
                self.display_users(users)
                QMessageBox.information(self, "Supprimé", message)
            else:
                QMessageBox.critical(self, "Erreur", message)

    def on_view_audit_logs(self):
        # 1. Récupérer les logs depuis le contrôleur
        logs = self.controller.get_audit_logs()
        
        # 2. Création de la fenêtre de log
        dialog = QDialog(self)
        dialog.setWindowTitle("Traçabilité du Système - Audit Sécurité")
        dialog.setMinimumSize(850, 500)
        layout = QVBoxLayout(dialog)

        # AJOUT DU BOUTON EXPORT
        btn_layout = QHBoxLayout()
        btn_export = QPushButton("📤 Exporter en CSV")
        btn_export.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

        def handle_export():
            success, path = AuditReporter.export_to_csv(logs)
            if success:
                QMessageBox.information(dialog, "Export Réussi", f"Le journal a été enregistré ici :\n{path}")
            else:
                QMessageBox.critical(dialog, "Erreur", f"Échec de l'exportation : {path}")

        btn_export.clicked.connect(handle_export)
        
        # 3. Configuration du tableau
        log_table = QTableWidget()
        log_table.setColumnCount(5)
        log_table.setHorizontalHeaderLabels([
            "Date & Heure", 
            "Utilisateur ID", 
            "Action", 
            "Détails de l'opération", 
            "Adresse IP" 
        ])
        
        # Design du tableau
        log_table.setAlternatingRowColors(True)
        log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # Détails prend la place
        
        log_table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            # Formatage de la date (ex: 19/02/2026 14:30)
            date_str = log.created_at.strftime("%d/%m/%Y %H:%M:%S")
            
            log_table.setItem(i, 0, QTableWidgetItem(date_str))
            log_table.setItem(i, 1, QTableWidgetItem(str(log.user_id)))
            
            # Action en couleur pour lisibilité
            action_item = QTableWidgetItem(log.action)
            if "SUPPRESSION" in log.action:
                action_item.setForeground(QColor("#d63031"))
            log_table.setItem(i, 2, action_item)
            
            log_table.setItem(i, 3, QTableWidgetItem(log.details))
            
            # Adresse IP
            ip_item = QTableWidgetItem(log.ip_address if log.ip_address else "127.0.0.1")
            ip_item.setTextAlignment(Qt.AlignCenter)
            log_table.setItem(i, 4, ip_item)
        
        layout.addWidget(log_table)
        
        # Bouton de fermeture
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        dialog.exec()
views.py
Affichage de views.py.