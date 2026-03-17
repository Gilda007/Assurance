# from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
#                              QListWidgetItem, QLabel, QPushButton, QFileDialog, 
#                              QMessageBox, QFrame, QGraphicsDropShadowEffect)
# from PySide6.QtCore import Qt, QSize
# from PySide6.QtGui import QColor, QFont
# import os

# class ParametreModuleWidget(QWidget):
#     def __init__(self, controller=None, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.setup_ui()
#         self.refresh_data()

#     def setup_ui(self):
#         self.setStyleSheet("background-color: #f8fafc; border: none;")
#         self.main_layout = QVBoxLayout(self)
#         self.main_layout.setContentsMargins(30, 30, 30, 30)
#         self.main_layout.setSpacing(25)

#         # --- 1. ZONE DES CARTES (STATISTIQUES) ---
#         self.stats_layout = QHBoxLayout()
#         self.stats_layout.setSpacing(20)

#         self.card_total = self._create_stat_card("Modules Totaux", "0", "#3b82f6")
#         self.card_installed = self._create_stat_card("Modules Installés", "0", "#10b981")
#         self.card_storage = self._create_stat_card("Espace Utilisé", "0 MB", "#f59e0b")

#         self.stats_layout.addWidget(self.card_total)
#         self.stats_layout.addWidget(self.card_installed)
#         self.stats_layout.addWidget(self.card_storage)
#         self.main_layout.addLayout(self.stats_layout)

#         # --- 2. ZONE DE CONTENU (LISTE + DÉTAILS) ---
#         content_layout = QHBoxLayout()
#         content_layout.setSpacing(25)

#         # Panneau Gauche
#         left_panel = QVBoxLayout()
#         self.btn_install = QPushButton("📥  Déployer une extension")
#         self.btn_install.setFixedHeight(45)
#         self.btn_install.setCursor(Qt.PointingHandCursor)
#         self.btn_install.setStyleSheet("""
#             QPushButton {
#                 background-color: #0f172a; color: white; border-radius: 10px;
#                 font-weight: 600; font-size: 13px; border: none;
#             }
#             QPushButton:hover { background-color: #1e293b; }
#         """)
#         self.btn_install.clicked.connect(self.on_install_clicked)

#         self.module_list = QListWidget()
#         self.module_list.setObjectName("ModernList")
#         self.module_list.setSpacing(5)
#         self.module_list.setStyleSheet("""
#             QListWidget#ModernList { background-color: transparent; border: none; outline: none; }
#             QListWidget#ModernList::item {
#                 background-color: white; border-radius: 10px; padding: 15px;
#                 color: #334155; border: 1px solid #e2e8f0; margin-bottom: 5px;
#             }
#             QListWidget#ModernList::item:selected {
#                 background-color: #ffffff; color: #2563eb; 
#                 border: 2px solid #3b82f6; font-weight: bold;
#             }
#         """)
#         self.module_list.currentRowChanged.connect(self.display_details)

#         left_panel.addWidget(self.btn_install)
#         left_panel.addWidget(self.module_list)
#         content_layout.addLayout(left_panel, 1)

#         # Panneau Droit (Carte Détails)
#         self.detail_card = QFrame()
#         self.detail_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        
#         detail_inner = QVBoxLayout(self.detail_card)
#         detail_inner.setContentsMargins(40, 40, 40, 40)
        
#         self.lbl_name = QLabel("Sélectionnez un module")
#         self.lbl_name.setStyleSheet("font-size: 26px; font-weight: 800; color: #0f172a; border: none;")
        
#         self.lbl_size_tag = QLabel("") # Affichera la taille
#         self.lbl_size_tag.setStyleSheet("color: #64748b; font-weight: bold; font-size: 12px; border: none;")
        
#         self.lbl_desc = QLabel("")
#         self.lbl_desc.setWordWrap(True)
#         self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 160%; margin-top: 15px; border: none;")

#         self.btn_uninstall = QPushButton("🗑️ Désinstaller")
#         self.btn_uninstall.setFixedSize(140, 40)
#         self.btn_uninstall.setStyleSheet("""
#             QPushButton {
#                 background-color: #fff1f2; color: #e11d48; 
#                 border-radius: 8px; font-weight: 700; border: 1px solid #fecdd3;
#             }
#             QPushButton:hover { background-color: #ffe4e6; }
#         """)
#         self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)
#         self.btn_uninstall.hide()

#         detail_inner.addWidget(self.lbl_name)
#         detail_inner.addWidget(self.lbl_size_tag)
#         detail_inner.addWidget(self.lbl_desc)
#         detail_inner.addStretch()
#         detail_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

#         content_layout.addWidget(self.detail_card, 2)
#         self.main_layout.addLayout(content_layout)

#     # def _create_stat_card(self, title, value, color):
#     #     card = QFrame()
#     #     card.setFixedHeight(100)
#     #     card.setStyleSheet(f"""
#     #         QFrame {{
#     #             background-color: white; border-radius: 15px;
#     #             border-left: 5px solid {color}; border: 1px solid #e2e8f0;
#     #         }}
#     #     """)
        
#     #     # Ombre douce
#     #     shadow = QGraphicsDropShadowEffect()
#     #     shadow.setBlurRadius(15)
#     #     shadow.setColor(QColor(0, 0, 0, 10))
#     #     card.setGraphicsEffect(shadow)

#     #     layout = QVBoxLayout(card)
#     #     lbl_title = QLabel(title.upper())
#     #     lbl_title.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800; letter-spacing: 1px;")
        
#     #     lbl_value = QLabel(value)
#     #     lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 900;")
        
#     #     layout.addWidget(lbl_title)
#     #     layout.addWidget(lbl_value)
        
#     #     # On attache le label de valeur à la carte pour pouvoir le modifier plus tard
#     #     card.value_label = lbl_value 
#     #     return card

#     def _create_stat_card(self, title, value, color):
#         card = QFrame()
#         card.setObjectName("StatCard")
#         card.setStyleSheet(f"""
#             #StatCard {{
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 12px;
#                 padding: 15px;
#             }}
#         """)
        
#         # Ajout d'une ombre portée légère
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(15)
#         shadow.setColor(QColor(0, 0, 0, 20))
#         shadow.setOffset(0, 4)
#         card.setGraphicsEffect(shadow)

#         layout = QVBoxLayout(card)
        
#         title_lbl = QLabel(title.upper())
#         title_lbl.setStyleSheet(f"color: #64748b; font-size: 11px; font-weight: 800; letter-spacing: 1px;")
        
#         val_lbl = QLabel(value)
#         val_lbl.setObjectName("val_lbl") # Important pour refresh_data
#         val_lbl.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        
#         layout.addWidget(title_lbl)
#         layout.addWidget(val_lbl)
#         return card
    
#     def refresh_data(self):
#         self.module_list.clear()
#         modules = self.get_all_modules()
        
#         total_size = 0
#         for mod in modules:
#             size = mod.get('size', 0)
#             total_size += size
#             item = QListWidgetItem(f" 🧩 {mod['name']}")
#             item.setData(Qt.UserRole, mod)
#             self.module_list.addItem(item)

#         # Mise à jour des cartes KPI
#         # self.card_total.val_lbl.setText(str(len(modules)))
#         # self.card_installed.val_lbl.setText(str(len(modules))) # À adapter selon votre logique
#         # self.card_storage.val_lbl.setText(f"{total_size / 1024:.1f} MB")

#     def display_details(self, row):
#         if row < 0: return
#         mod = self.module_list.item(row).data(Qt.UserRole)
#         self.lbl_name.setText(mod['name'])
#         self.lbl_size_tag.setText(f"TAILLE SUR DISQUE : {mod.get('size', 0)} KB")
#         self.lbl_desc.setText(mod.get('description', 'Aucune description.'))
        
#         is_sys = mod['folder_name'].lower() in ["paramètre", "settings"]
#         self.btn_uninstall.setVisible(not is_sys)

#     def refresh_list(self):
#         self.module_list.clear()
#         modules = self.get_all_modules()
#         for mod in modules:
#             icon = mod.get('icon', '🧩')
#             item = QListWidgetItem(f"  {icon}   {mod['name']}")
#             item.setData(Qt.UserRole, mod)
#             self.module_list.addItem(item)

#     def display_details(self, row):
#         if row < 0: return
#         mod = self.module_list.item(row).data(Qt.UserRole)
        
#         # Mise à jour sécurisée des widgets
#         self.lbl_name.setText(mod['name'])
#         # self.badge_version.setText(f"V {mod['version']}")
#         self.lbl_desc.setText(mod.get('description', 'Aucune description.'))
        
#         # Gestion bouton désinstaller
#         is_system = mod['folder_name'].lower() in ["paramètre", "settings"]
#         self.btn_uninstall.setVisible(not is_system)
#         self.btn_uninstall.setProperty("folder", mod['folder_name'])
    
#     def on_install_clicked(self):
#         path, _ = QFileDialog.getOpenFileName(self, "Importer Extension", "", "Archives (*.zip)")
#         if path:
#             success, msg = self.service.install_zip(path)
#             if success:
#                 QMessageBox.information(self, "Système", "L'extension a été déployée avec succès.")
#                 self.refresh_list()
#             else:
#                 QMessageBox.critical(self, "Erreur", f"Échec du déploiement : {msg}")
  
#     def get_all_modules(self):
#         modules = []
#         # Chemin absolu vers le dossier addons (plus sécurisé)
#         base_path = os.path.dirname(os.path.abspath(__file__))
#         # On remonte d'un niveau si on est dans views, ou on cible la racine
#         addons_path = os.path.join(os.getcwd(), "addons")

#         if not os.path.exists(addons_path):
#             print(f"Erreur : Le dossier {addons_path} est introuvable.")
#             return []

#         try:
#             for folder in os.listdir(addons_path):
#                 folder_path = os.path.join(addons_path, folder)
                
#                 # On ne traite que les dossiers
#                 if os.path.isdir(folder_path) and not folder.startswith("__"):
#                     manifest_path = os.path.join(folder_path, "__manifest__.py")
                    
#                     if os.path.exists(manifest_path):
#                         try:
#                             with open(manifest_path, "r", encoding="utf-8") as f:
#                                 # Utilisation de eval pour lire le dictionnaire du manifeste
#                                 manifest_data = eval(f.read())
#                                 manifest_data['folder_name'] = folder
#                                 manifest_data['size'] = self._get_folder_size(folder_path)
#                                 modules.append(manifest_data)
#                         except Exception as e:
#                             print(f"Erreur lecture manifeste dans {folder}: {e}")
#                     else:
#                         # SI PAS DE MANIFESTE : On ajoute quand même le module avec des infos par défaut
#                         modules.append({
#                             "name": folder.replace("_", " ").title(),
#                             "version": "1.0.0",
#                             "author": "Développeur local",
#                             "description": f"Module situé dans le dossier {folder}",
#                             "folder_name": folder,
#                             "size": self._get_folder_size(folder_path)
#                         })
#         except Exception as e:
#             print(f"Erreur lors du scan des modules : {e}")
            
#         return modules
    
#     def on_uninstall_clicked(self):
#         folder = self.btn_uninstall.property("folder")
#         confirm = QMessageBox.question(self, "Sécurité", 
#                                      f"Voulez-vous vraiment supprimer le composant <b>{folder}</b> ?",
#                                      QMessageBox.Yes | QMessageBox.No)
#         if confirm == QMessageBox.Yes:
#             # Appel service suppression
#             pass

# from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
#                              QListWidgetItem, QLabel, QPushButton, QFileDialog, 
#                              QMessageBox, QFrame, QGraphicsDropShadowEffect)
# from PySide6.QtCore import Qt, QSize
# from PySide6.QtGui import QColor, QFont
# import os

# class ParametreModuleWidget(QWidget):
#     def __init__(self, controller=None, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.setup_ui()
#         self.refresh_data()

#     def setup_ui(self):
#         self.setStyleSheet("background-color: #f8fafc; border: none;")
#         self.main_layout = QVBoxLayout(self)
#         self.main_layout.setContentsMargins(30, 30, 30, 30)
#         self.main_layout.setSpacing(25)

#         # --- 1. ZONE DES CARTES (STATISTIQUES) ---
#         self.stats_layout = QHBoxLayout()
#         self.stats_layout.setSpacing(20)

#         self.card_total = self._create_stat_card("Modules Totaux", "0", "#3b82f6")
#         self.card_installed = self._create_stat_card("Modules Installés", "0", "#10b981")
#         self.card_storage = self._create_stat_card("Espace Utilisé", "0 MB", "#f59e0b")

#         self.stats_layout.addWidget(self.card_total)
#         self.stats_layout.addWidget(self.card_installed)
#         self.stats_layout.addWidget(self.card_storage)
#         self.main_layout.addLayout(self.stats_layout)

#         # --- 2. LISTE DES MODULES ---
#         self.list_container = QFrame()
#         self.list_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e2e8f0;")
#         list_vbox = QVBoxLayout(self.list_container)
        
#         title_list = QLabel("Composants du Système")
#         title_list.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b; border: none; padding: 10px;")
#         list_vbox.addWidget(title_list)

#         self.module_list = QListWidget()
#         self.module_list.setStyleSheet("border: none; background: transparent;")
#         self.module_list.setSpacing(8)
#         list_vbox.addWidget(self.module_list)

#         self.main_layout.addWidget(self.list_container)

#     def _create_stat_card(self, title, value, color):
#         card = QFrame()
#         card.setFixedHeight(120)
#         card.setStyleSheet(f"""
#             background-color: white; 
#             border-radius: 15px; 
#             border-left: 5px solid {color};
#             border: 1px solid #e2e8f0;
#         """)
        
#         layout = QVBoxLayout(card)
#         lbl_title = QLabel(title)
#         lbl_title.setStyleSheet("color: #64748b; font-size: 13px; font-weight: bold; border: none;")
        
#         lbl_value = QLabel(value)
#         lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 800; border: none;")
        
#         layout.addWidget(lbl_title)
#         layout.addWidget(lbl_value)
        
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(15)
#         shadow.setColor(QColor(0, 0, 0, 20))
#         shadow.setOffset(0, 4)
#         card.setGraphicsEffect(shadow)
        
#         return card

#     def get_all_module(self):
#         """
#         Scanne dynamiquement le dossier 'addons' pour détecter les modules.
#         """
#         modules = []
#         # On utilise le répertoire de travail actuel (racine du projet)
#         addons_path = os.path.join(os.getcwd(), "addons")

#         if not os.path.exists(addons_path):
#             return [{"name": "Erreur", "description": "Dossier addons introuvable", "version": "0"}]

#         try:
#             for folder in os.listdir(addons_path):
#                 folder_path = os.path.join(addons_path, folder)
                
#                 # On ignore les fichiers et les dossiers techniques
#                 if os.path.isdir(folder_path) and not folder.startswith("__") and not folder.startswith("."):
#                     manifest_path = os.path.join(folder_path, "__manifest__.py")
                    
#                     module_info = {
#                         "name": folder.replace("_", " ").title(),
#                         "version": "1.0.0",
#                         "author": "Interne",
#                         "description": f"Module local situé dans {folder}",
#                         "folder_name": folder,
#                         "size": self._get_folder_size(folder_path)
#                     }

#                     # Si un manifeste existe, on écrase les infos par défaut
#                     if os.path.exists(manifest_path):
#                         try:
#                             with open(manifest_path, "r", encoding="utf-8") as f:
#                                 manifest_data = eval(f.read())
#                                 module_info.update(manifest_data)
#                         except:
#                             pass
                    
#                     modules.append(module_info)
#         except Exception as e:
#             print(f"Erreur scan modules: {e}")
            
#         return modules

#     def refresh_data(self):
#         self.module_list.clear()
#         modules = self.get_all_module()
        
#         total_size = 0
#         for mod in modules:
#             total_size += mod.get('size', 0)
#             item = QListWidgetItem(self.module_list)
#             item.setSizeHint(QSize(0, 80))
            
#             widget = self._create_module_item_widget(mod)
#             self.module_list.setItemWidget(item, widget)

#         # Mise à jour des stats
#         self.card_total.findChildren(QLabel)[1].setText(str(len(modules)))
#         self.card_installed.findChildren(QLabel)[1].setText(str(len(modules))) # Ici, on considère tout installé
#         self.card_storage.findChildren(QLabel)[1].setText(f"{total_size / (1024*1024):.2f} MB")

#     def _create_module_item_widget(self, mod):
#         container = QWidget()
#         layout = QHBoxLayout(container)
        
#         icon_label = QLabel("📦")
#         icon_label.setStyleSheet("font-size: 24px; padding: 10px;")
        
#         info_layout = QVBoxLayout()
#         name_label = QLabel(f"{mod.get('name')} <span style='color: #94a3b8; font-size: 11px;'>v{mod.get('version')}</span>")
#         name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e293b;")
        
#         desc_label = QLabel(mod.get('description'))
#         desc_label.setStyleSheet("color: #64748b; font-size: 12px;")
        
#         info_layout.addWidget(name_label)
#         info_layout.addWidget(desc_label)
        
#         layout.addWidget(icon_label)
#         layout.addLayout(info_layout, 1)
        
#         btn_action = QPushButton("Gérer")
#         btn_action.setFixedWidth(80)
#         btn_action.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9; color: #475569; border-radius: 6px; 
#                 padding: 5px; font-weight: bold;
#             }
#             QPushButton:hover { background-color: #e2e8f0; }
#         """)
#         layout.addWidget(btn_action)
        
#         return container

#     def _get_folder_size(self, path):
#         total = 0
#         try:
#             for entry in os.scandir(path):
#                 if entry.is_file(): total += entry.stat().st_size
#                 elif entry.is_dir(): total += self._get_folder_size(entry.path)
#         except: pass
# #         return total

# from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
#                              QListWidgetItem, QLabel, QPushButton, QFileDialog, 
#                              QMessageBox, QFrame, QGraphicsDropShadowEffect)
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QColor

# class ParametreModuleWidget(QWidget):
#     def __init__(self, controller, user=None):
#         super().__init__()
#         self.controller = controller
#         self.service = controller
#         self.user = user
#         self.setup_ui()
#         self.refresh_data()

#     def _create_stat_card(self, title, color):
#         """Crée une carte KPI. (Prend 3 arguments avec self)"""
#         card = QFrame()
#         card.setFixedHeight(90)
#         card.setStyleSheet(f"""
#             QFrame {{
#                 background-color: white; border-radius: 12px;
#                 border: 1px solid #e2e8f0; border-left: 5px solid {color};
#             }}
#         """)
        
#         layout = QVBoxLayout(card)
#         t_lbl = QLabel(title.upper())
#         t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800; letter-spacing: 1px;")
        
#         v_lbl = QLabel("--")
#         v_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        
#         layout.addWidget(t_lbl)
#         layout.addWidget(v_lbl)
        
#         # On attache le label pour pouvoir le mettre à jour
#         card.val_lbl = v_lbl 
#         return card

#     def setup_ui(self):
#         self.setStyleSheet("background-color: #f8fafc;")
#         self.main_layout = QVBoxLayout(self)
#         self.main_layout.setContentsMargins(25, 25, 25, 25)
#         self.main_layout.setSpacing(20)

#         # --- 1. DASHBOARD (KPI CARDS) ---
#         self.stats_layout = QHBoxLayout()
#         # CORRECTION : On ne passe que 3 arguments (self, titre, couleur)
#         self.card_total = self._create_stat_card("Modules Disponibles", "#3b82f6")
#         self.card_installed = self._create_stat_card("Modules Installés", "#10b981")
#         self.card_size = self._create_stat_card("Espace Disque", "#f59e0b")
        
#         self.stats_layout.addWidget(self.card_total)
#         self.stats_layout.addWidget(self.card_installed)
#         self.stats_layout.addWidget(self.card_size)
#         self.main_layout.addLayout(self.stats_layout)

#         # --- 2. ZONE DE CONTENU ---
#         content_layout = QHBoxLayout()
#         content_layout.setSpacing(20)

#         # Liste (Gauche)
#         left_panel = QVBoxLayout()
#         self.btn_install = QPushButton("📥 Importer un module (.zip)")
#         self.btn_install.setFixedHeight(40)
#         self.btn_install.setStyleSheet("background: #0f172a; color: white; border-radius: 8px; font-weight: bold;")
#         self.btn_install.clicked.connect(self.on_install_clicked)

#         self.module_list = QListWidget()
#         self.module_list.setObjectName("ModernList")
#         self.module_list.setStyleSheet("""
#             QListWidget#ModernList { background: transparent; border: none; outline: none; }
#             QListWidget#ModernList::item {
#                 background: white; border-radius: 10px; padding: 15px; margin-bottom: 5px; border: 1px solid #e2e8f0;
#             }
#             QListWidget#ModernList::item:selected { background: #eff6ff; color: #2563eb; border: 1px solid #3b82f6; }
#         """)
#         self.module_list.currentRowChanged.connect(self.display_details)
#         left_panel.addWidget(self.btn_install)
#         left_panel.addWidget(self.module_list)
#         content_layout.addLayout(left_panel, 1)

#         # Détails (Droite)
#         self.detail_card = QFrame()
#         self.detail_card.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
#         d_inner = QVBoxLayout(self.detail_card)
#         d_inner.setContentsMargins(30, 30, 30, 30)

#         self.lbl_name = QLabel("Sélectionnez un module")
#         self.lbl_name.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")

#         self.badge_version = QLabel("")
#         self.badge_version.setStyleSheet("background: #f1f5f9; color: #475569; padding: 4px; border-radius: 4px; font-weight: bold;")
        
#         self.lbl_size = QLabel("") # Affichage de la taille
#         self.lbl_size.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold;")

#         self.lbl_desc = QLabel("")
#         self.lbl_desc.setWordWrap(True)
#         self.lbl_desc.setStyleSheet("color: #334155; font-size: 14px; margin-top: 10px;")

#         # Zone Dépendances
#         self.lbl_dep_title = QLabel("DÉPENDANCES")
#         self.lbl_dep_title.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; margin-top: 20px;")
#         self.dep_container = QWidget()
#         self.dep_layout = QHBoxLayout(self.dep_container)
#         self.dep_layout.setContentsMargins(0, 5, 0, 5)
#         self.dep_layout.addStretch()

#         self.btn_uninstall = QPushButton("🗑️ Désinstaller")
#         self.btn_uninstall.setFixedSize(130, 35)
#         self.btn_uninstall.setStyleSheet("background: #fff1f2; color: #e11d48; border-radius: 6px; font-weight: bold;")
#         self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)

#         d_inner.addWidget(self.lbl_name)
#         d_inner.addWidget(self.badge_version)
#         d_inner.addWidget(self.lbl_size)
#         d_inner.addWidget(self.lbl_desc)
#         d_inner.addWidget(self.lbl_dep_title)
#         d_inner.addWidget(self.dep_container)
#         d_inner.addStretch()
#         d_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

#         content_layout.addWidget(self.detail_card, 2)
#         self.main_layout.addLayout(content_layout)

#     def refresh_data(self):
#         self.module_list.clear()
#         modules = self.controller.get_all_modules()
#         total_kb = 0
#         for mod in modules:
#             total_kb += mod.get('size', 0)
#             item = QListWidgetItem(f" 🧩 {mod['name']}")
#             item.setData(Qt.UserRole, mod)
#             self.module_list.addItem(item)

#         self.card_total.val_lbl.setText(str(len(modules)))
#         self.card_installed.val_lbl.setText(str(len(modules)))
#         self.card_size.val_lbl.setText(f"{total_kb / 1024:.1f} MB")

#     def display_details(self, row):
#         if row < 0: return
#         mod = self.module_list.item(row).data(Qt.UserRole)
        
#         self.lbl_name.setText(mod['name'])
#         self.badge_version.setText(f"VERSION {mod.get('version', '1.0')}")
#         self.lbl_size.setText(f"TAILLE : {mod.get('size', 0)} KB")
#         self.lbl_desc.setText(mod.get('description', 'Aucune description.'))

#         # Nettoyage et affichage des dépendances
#         for i in reversed(range(self.dep_layout.count())):
#             w = self.dep_layout.itemAt(i).widget()
#             if w: w.deleteLater()
        
#         deps = mod.get('dependencies', [])
#         if not deps:
#             self.dep_layout.insertWidget(0, QLabel("Aucune"))
#         else:
#             for d in deps:
#                 b = QLabel(d)
#                 b.setStyleSheet("background: #f0fdf4; color: #16a34a; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;")
#                 self.dep_layout.insertWidget(self.dep_layout.count()-1, b)

#         is_sys = mod['folder_name'].lower() in ["paramètre", "settings"]
#         self.btn_uninstall.setVisible(not is_sys)
#         self.btn_uninstall.setProperty("folder", mod['folder_name'])

#     def on_install_clicked(self):
#         path, _ = QFileDialog.getOpenFileName(self, "Choisir ZIP", "", "Zip (*.zip)")
#         if path:
#             res, msg = self.service.install_zip(path)
#             if res: 
#                 QMessageBox.information(self, "Succès", msg)
#                 self.refresh_data()
#             else: 
#                 QMessageBox.critical(self, "Erreur", msg)

#     def on_uninstall_clicked(self):
#         folder = self.btn_uninstall.property("folder")
#         if QMessageBox.question(self, "Supprimer", f"Supprimer {folder} ?") == QMessageBox.Yes:
#             pass # Ajoutez ici l'appel vers controller.delete_module(folder)

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont
import os
import json

class ParametreModuleWidget(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc; border: none;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- 1. STATISTIQUES ---
        self.stats_layout = QHBoxLayout()
        self.card_total = self._create_stat_card("Détectés", "0", "#3b82f6")
        self.card_installed = self._create_stat_card("Actifs", "0", "#10b981")
        self.card_storage = self._create_stat_card("Stockage", "0 MB", "#f59e0b")
        self.stats_layout.addWidget(self.card_total)
        self.stats_layout.addWidget(self.card_installed)
        self.stats_layout.addWidget(self.card_storage)
        self.main_layout.addLayout(self.stats_layout)

        # --- 2. LISTE ---
        self.list_container = QFrame()
        self.list_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        list_vbox = QVBoxLayout(self.list_container)
        
        self.title_label = QLabel("Gestion des Modules (manifest.json)")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b; padding: 10px;")
        list_vbox.addWidget(self.title_label)

        self.module_list = QListWidget()
        self.module_list.setStyleSheet("border: none; background: transparent;")
        self.module_list.setSpacing(10)
        list_vbox.addWidget(self.module_list)

        self.main_layout.addWidget(self.list_container)

    def _create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"background: white; border-radius: 12px; border-left: 5px solid {color}; border: 1px solid #e2e8f0;")
        l = QVBoxLayout(card)
        t = QLabel(title); t.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
        v = QLabel(value); v.setObjectName("val"); v.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        l.addWidget(t); l.addWidget(v)
        return card

    def get_all_modules(self):
        """Scanne addons/ et lit manifest.json"""
        modules = []
        addons_path = os.path.join(os.getcwd(), "addons")
        
        if not os.path.exists(addons_path):
            return []

        for folder in os.listdir(addons_path):
            folder_path = os.path.join(addons_path, folder)
            if os.path.isdir(folder_path) and not folder.startswith("."):
                manifest_path = os.path.join(folder_path, "manifest.json")
                
                # Default data
                mod_data = {
                    "name": folder, "version": "1.0", "installable": True,
                    "folder_name": folder, "size": self._get_size(folder_path)
                }

                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            mod_data.update(json.load(f))
                    except Exception as e:
                        print(f"Erreur JSON {folder}: {e}")
                
                modules.append(mod_data)
        return modules

    def toggle_module_status(self, folder_name):
        """Bouton Désinstaller : passe installable à False dans le manifest.json"""
        addons_path = os.path.join(os.getcwd(), "addons", folder_name)
        manifest_path = os.path.join(addons_path, "manifest.json")
        
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Logique : on bascule le statut
                current_status = data.get("installable", True)
                data["installable"] = not current_status
                
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                
                self.refresh_data()
                QMessageBox.information(self, "Succès", f"Statut du module {folder_name} mis à jour.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier le fichier : {e}")

def refresh_data(self):
        self.list_installed.clear()
        self.list_available.clear()
        modules = self.get_all_modules()
        
        active_count = 0
        for mod in modules:
            is_active = mod.get("installable", False)
            target_list = self.list_installed if is_active else self.list_available
            if is_active: active_count += 1

            item = QListWidgetItem(target_list)
            item.setSizeHint(QSize(0, 80))
            
            w = QWidget()
            l = QHBoxLayout(w)
            
            info = QVBoxLayout()
            name = QLabel(f"{mod.get('name')} (v{mod.get('version', '1.0')})")
            name.setStyleSheet("font-weight: bold; color: #1e293b;")
            # Sécurité anti-crash finale
            desc_text = str(mod.get('description', ''))
            desc = QLabel(desc_text if desc_text != "None" else "Pas de description")
            desc.setStyleSheet("color: #64748b; font-size: 11px;")
            info.addWidget(name); info.addWidget(desc)
            
            l.addLayout(info, 1)

            btn = QPushButton("Désactiver" if is_active else "Activer")
            btn.setFixedWidth(100)
            btn.setStyleSheet(f"background: {'#ef4444' if is_active else '#10b981'}; color: white; font-weight: bold; border-radius: 5px; padding: 6px;")
            btn.clicked.connect(lambda checked=False, f=mod['folder_name'], s=is_active: self.toggle_module(f, s))
            
            l.addWidget(btn)
            target_list.setItemWidget(item, w)

        self.card_total.findChild(QLabel, "val").setText(str(len(modules)))
        self.card_active.findChild(QLabel, "val").setText(str(active_count))
    def _get_size(self, p):
        s = 0
        try:
            for entry in os.scandir(p):
                if entry.is_file(): s += entry.stat().st_size
                elif entry.is_dir(): s += self._get_size(entry.path)
        except: pass
        return s