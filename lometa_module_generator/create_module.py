# #!/usr/bin/env python3
# """
# Script interactif pour créer un module LOMETA à partir de données saisies.
# Version améliorée avec templates, gestion des dépendances et plus encore.
# """

# import json
# import os
# import shutil
# import sys
# from pathlib import Path
# from datetime import datetime
# import re

# ROOT = Path(__file__).resolve().parent
# TEMPLATE_DIR = ROOT

# # ============================================================================
# # COLORS
# # ============================================================================

# COLORS = {
#     'green': '\033[92m',
#     'yellow': '\033[93m',
#     'blue': '\033[94m',
#     'red': '\033[91m',
#     'cyan': '\033[96m',
#     'magenta': '\033[95m',
#     'bold': '\033[1m',
#     'reset': '\033[0m'
# }

# def color(text, color_name):
#     return f"{COLORS.get(color_name, '')}{text}{COLORS['reset']}"

# def print_header(text):
#     print(f"\n{color('='*60, 'cyan')}")
#     print(f"{color(text.center(60), 'bold')}")
#     print(f"{color('='*60, 'cyan')}\n")

# def print_success(text):
#     print(f"{color('✅', 'green')} {text}")

# def print_error(text):
#     print(f"{color('❌', 'red')} {text}")

# def print_info(text):
#     print(f"{color('ℹ️', 'blue')} {text}")

# def print_warning(text):
#     print(f"{color('⚠️', 'yellow')} {text}")

# # ============================================================================
# # UTILITIES
# # ============================================================================

# def ask(prompt, default="", required=False, choices=None):
#     """Demande une entrée à l'utilisateur avec validation."""
#     if choices:
#         prompt = f"{prompt} [{', '.join(choices)}]"
    
#     while True:
#         value = input(f"{prompt} [{default}]: ").strip() if default else input(f"{prompt}: ").strip()
#         value = value if value else default
        
#         if required and not value:
#             print_error("Ce champ est requis.")
#             continue
        
#         if choices and value not in choices:
#             print_error(f"Valeur invalide. Choisissez parmi: {', '.join(choices)}")
#             continue
        
#         return value

# def ask_bool(prompt, default=True):
#     """Demande une réponse oui/non."""
#     default_text = "y/n" if default else "n/y"
#     value = ask(f"{prompt} ({default_text})", "y" if default else "n")
#     return value.lower() in {"1", "true", "yes", "y", "oui", "o"}

# def snake_case(text):
#     """Convertit un texte en snake_case."""
#     text = re.sub(r'([A-Z])', r'_\1', text).lower()
#     text = re.sub(r'[^a-z0-9_]', '_', text)
#     text = re.sub(r'_+', '_', text)
#     return text.strip('_')

# def pascal_case(text):
#     """Convertit un texte en PascalCase."""
#     text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
#     words = text.split()
#     return ''.join(word.capitalize() for word in words if word)

# def kebab_case(text):
#     """Convertit un texte en kebab-case."""
#     text = re.sub(r'([A-Z])', r'-\1', text).lower()
#     text = re.sub(r'[^a-z0-9-]', '-', text)
#     text = re.sub(r'-+', '-', text)
#     return text.strip('-')

# def ensure_dir(path):
#     """Crée un répertoire s'il n'existe pas."""
#     path.mkdir(parents=True, exist_ok=True)

# # ============================================================================
# # TEMPLATES
# # ============================================================================

# TEMPLATES = {
#     'crud': {
#         'name': 'CRUD',
#         'description': 'Contrôleur, vues et modèles pour une entité simple',
#         'files': ['controller.py', 'model.py', 'views.py']
#     },
#     'api': {
#         'name': 'API REST',
#         'description': 'API REST avec endpoints CRUD',
#         'files': ['api.py', 'serializers.py']
#     },
#     'simple': {
#         'name': 'Simple',
#         'description': 'Module minimal avec point d\'entrée',
#         'files': ['main.py']
#     },
#     'full': {
#         'name': 'Complet',
#         'description': 'Structure complète avec tout ce qu\'il faut',
#         'files': ['controller.py', 'model.py', 'views.py', 'api.py', 'services.py']
#     }
# }

# # ============================================================================
# # TEMPLATES POUR main_ui.py ET view.py
# # ============================================================================

# def get_main_ui_template(module_name, class_name):
#     """Génère le template pour main_ui.py"""
#     return f'''from core.base_module import BaseModule
# from PySide6.QtWidgets import QPushButton, QVBoxLayout
# from PySide6.QtCore import Qt, QSize
# from PySide6.QtGui import QIcon
# from core.alerts import AlertManager

# from addons.{module_name}.views.view import {class_name}


# # Style moderne pour le bouton de la barre latérale
# MODERN_BTN_STYLE = """
# QPushButton {{
#     background-color: transparent;
#     color: #546e7a;
#     border: none;
#     border-radius: 8px;
#     text-align: left;
#     padding-left: 15px;
#     font-size: 14px;
#     font-weight: 500;
# }}
# QPushButton:hover {{
#     background-color: #f1f3f4;
#     color: #1a73e8;
# }}
# QPushButton:checked {{
#     background-color: #e8f0fe;
#     color: #1a73e8;
#     border-right: 3px solid #1a73e8;
# }}
# """


# class {class_name}Module(BaseModule):
#     def __init__(self, main_window=None, controller=None):
#         """Initialisation du module avec controller"""
#         super().__init__(main_window)
#         self.controller = controller
#         self.db_session = None
#         self.current_user = None
#         self.view = None
#         self.btn = None
        
#     def setup(self):
#         """Initialisation silencieuse du module"""
#         # 1. Récupération sécurisée de la session
#         self.db_session = getattr(self.main_window, 'db_session', None)
#         self.current_user = getattr(self.main_window, 'current_user', None)
        
#         # 2. Création du bouton avec un style Premium
#         self.btn = QPushButton("  👤 {module_name}")
#         self.btn.setCheckable(True)
#         self.btn.setFixedHeight(50)
#         self.btn.setCursor(Qt.PointingHandCursor)
#         self.btn.setStyleSheet(MODERN_BTN_STYLE)
        
#         # 3. Connexion de l'événement
#         self.btn.clicked.connect(self.activate_module)
        
#         # 4. Ajout au menu latéral
#         if hasattr(self.main_window, 'sidebar_layout'):
#             self.main_window.sidebar_layout.addWidget(self.btn)

#     def activate_module(self):
#         """Logique d'activation avec récupération dynamique de l'utilisateur"""
#         try:
#             # RECHERCHE DYNAMIQUE : On va chercher l'info fraîche dans la fenêtre principale
#             user = getattr(self.main_window, 'current_user', None)
#             db_session = getattr(self.main_window, 'db_session', None)

#             if not user:
#                 AlertManager.show_error(self.main_window, "Sécurité", "Aucun utilisateur connecté détecté.")
#                 return

#             # Mise à jour de la référence locale
#             self.current_user = user
#             self.db_session = db_session

#             # Création de la vue avec le controller
#             self.view = {class_name}(controller=self.controller, user=self.current_user)
            
#             # Affichage dans la fenêtre principale
#             self.main_window.set_content_widget(self.view)
            
#             # Mettre à jour l'état du bouton
#             self.btn.setChecked(True)

#         except Exception as e:
#             AlertManager.show_error(self.main_window, "Erreur", str(e))
# '''

# def get_view_template(module_name, class_name):
#     """Génère le template pour view.py"""
#     return f'''from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
#                              QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
#                              QListWidgetItem, QStackedWidget, QListWidget, QFrame, 
#                              QMessageBox, QDialog, QGraphicsDropShadowEffect)
# from PySide6.QtCore import Qt, QSize
# from PySide6.QtGui import QColor, QIcon, QFont


# class {class_name}(QWidget):
#     def __init__(self, controller=None, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.pages_cache = {{}}

#         # Style Global du Widget Principal
#         self.setObjectName("MainSettingsWindow")
#         self.setStyleSheet("background-color: #f8fafc;")

#         self.layout = QHBoxLayout(self)
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.layout.setSpacing(0)
        
#         # Configurer la sidebar et le contenu
#         self.setup_sidebar()
#         self.setup_content_area()
        
#         # Sélectionner la première page par défaut
#         if hasattr(self, 'sidebar') and self.sidebar.count() > 0:
#             self.sidebar.setCurrentRow(0)

#     def setup_sidebar(self):
#         """Création de la barre latérale avec les pages"""
#         # Conteneur de la sidebar
#         self.sidebar_container = QFrame()
#         self.sidebar_container.setFixedWidth(250)
#         self.sidebar_container.setStyleSheet("""
#             QFrame {{
#                 background-color: white;
#                 border-radius: 0px;
#                 border-right: 1px solid #e2e8f0;
#             }}
#         """)
        
#         sidebar_layout = QVBoxLayout(self.sidebar_container)
#         sidebar_layout.setContentsMargins(15, 20, 15, 20)
#         sidebar_layout.setSpacing(10)
        
#         # Titre de la sidebar
#         title_label = QLabel("📋 Menu")
#         title_label.setStyleSheet("""
#             QLabel {{
#                 font-size: 16px;
#                 font-weight: bold;
#                 color: #1e293b;
#                 padding-bottom: 15px;
#                 border-bottom: 2px solid #e2e8f0;
#             }}
#         """)
#         sidebar_layout.addWidget(title_label)
        
#         # Liste des pages
#         self.sidebar = QListWidget()
#         self.sidebar.setStyleSheet("""
#             QListWidget {{
#                 background-color: transparent;
#                 border: none;
#                 outline: none;
#             }}
#             QListWidget::item {{
#                 padding: 12px 15px;
#                 border-radius: 8px;
#                 color: #64748b;
#                 font-size: 14px;
#                 font-weight: 500;
#             }}
#             QListWidget::item:hover {{
#                 background-color: #f1f5f9;
#                 color: #1e293b;
#             }}
#             QListWidget::item:selected {{
#                 background-color: #e2e8f0;
#                 color: #1a73e8;
#             }}
#         """)
#         self.sidebar.setFixedWidth(220)
        
#         # Ajout des pages
#         pages = [
#             ("Accueil", "🏠"),
#             ("Véhicules", "🚗"),
#             ("Contrats", "📄"),
#             ("Clients", "👤"),
#             ("Rapports", "📊"),
#             ("Paramètres", "⚙️")
#         ]
        
#         for text, icon in pages:
#             item = QListWidgetItem(f"{{icon}} {{text}}")
#             self.sidebar.addItem(item)
        
#         self.sidebar.currentRowChanged.connect(self.switch_page)
#         sidebar_layout.addWidget(self.sidebar)
        
#         # Informations utilisateur en bas
#         user_info = QFrame()
#         user_info.setStyleSheet("""
#             QFrame {{
#                 background-color: #f8fafc;
#                 border-radius: 10px;
#                 padding: 10px;
#                 margin-top: 20px;
#             }}
#             QLabel {{
#                 color: #1e293b;
#                 font-size: 12px;
#             }}
#         """)
#         user_layout = QVBoxLayout(user_info)
        
#         user_name = QLabel(f"👤 {{self.user.username if self.user else 'Utilisateur'}}")
#         user_name.setStyleSheet("font-weight: bold; font-size: 13px;")
#         user_layout.addWidget(user_name)
        
#         user_role = QLabel(f"Rôle: {{self.user.role if self.user else 'Non défini'}}")
#         user_role.setStyleSheet("color: #64748b; font-size: 11px;")
#         user_layout.addWidget(user_role)
        
#         sidebar_layout.addWidget(user_info)
        
#         # Ajout de la sidebar au layout principal
#         self.layout.addWidget(self.sidebar_container)

#     def setup_content_area(self):
#         """Zone de contenu avec effet d'ombre interne"""
#         self.content_container = QFrame()
#         self.content_layout = QVBoxLayout(self.content_container)
#         self.content_layout.setContentsMargins(30, 30, 30, 30)

#         # Stack d'affichage (Pages)
#         self.container = QStackedWidget()
#         self.container.setStyleSheet("""
#             QStackedWidget {{
#                 background-color: white; 
#                 border-radius: 20px; 
#                 border: 1px solid #e2e8f0;
#             }}
#         """)
        
#         # Ajout d'une ombre portée douce au conteneur de contenu
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(25)
#         shadow.setXOffset(0)
#         shadow.setYOffset(4)
#         shadow.setColor(QColor(0, 0, 0, 20))
#         self.container.setGraphicsEffect(shadow)

#         # --- PAGE 1 : ACCUEIL (Hello World) ---
#         hello_page = QWidget()
#         hello_layout = QVBoxLayout(hello_page)
#         hello_layout.setAlignment(Qt.AlignCenter)
        
#         hello_label = QLabel("Hello World")
#         hello_label.setStyleSheet("""
#             QLabel {{
#                 font-size: 48px;
#                 font-weight: bold;
#                 color: #1e293b;
#                 background-color: transparent;
#                 padding: 20px;
#             }}
#         """)
#         hello_label.setAlignment(Qt.AlignCenter)
        
#         subtitle_label = QLabel("Bienvenue dans LOMETA")
#         subtitle_label.setStyleSheet("""
#             QLabel {{
#                 font-size: 18px;
#                 color: #64748b;
#                 background-color: transparent;
#             }}
#         """)
#         subtitle_label.setAlignment(Qt.AlignCenter)
        
#         hello_layout.addWidget(hello_label)
#         hello_layout.addWidget(subtitle_label)
#         self.container.addWidget(hello_page)

#         # --- PAGE 2 : VÉHICULES ---
#         vehicles_page = QWidget()
#         vehicles_layout = QVBoxLayout(vehicles_page)
#         vehicles_layout.setAlignment(Qt.AlignCenter)
        
#         vehicles_label = QLabel("🚗 Gestion des Véhicules")
#         vehicles_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
#         vehicles_label.setAlignment(Qt.AlignCenter)
#         vehicles_layout.addWidget(vehicles_label)
        
#         vehicles_sub = QLabel("Module en cours de développement")
#         vehicles_sub.setStyleSheet("font-size: 14px; color: #64748b;")
#         vehicles_sub.setAlignment(Qt.AlignCenter)
#         vehicles_layout.addWidget(vehicles_sub)
#         self.container.addWidget(vehicles_page)

#         # --- PAGE 3 : CONTRATS ---
#         contracts_page = QWidget()
#         contracts_layout = QVBoxLayout(contracts_page)
#         contracts_layout.setAlignment(Qt.AlignCenter)
        
#         contracts_label = QLabel("📄 Gestion des Contrats")
#         contracts_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
#         contracts_label.setAlignment(Qt.AlignCenter)
#         contracts_layout.addWidget(contracts_label)
        
#         contracts_sub = QLabel("Module en cours de développement")
#         contracts_sub.setStyleSheet("font-size: 14px; color: #64748b;")
#         contracts_sub.setAlignment(Qt.AlignCenter)
#         contracts_layout.addWidget(contracts_sub)
#         self.container.addWidget(contracts_page)

#         # --- PAGE 4 : CLIENTS ---
#         clients_page = QWidget()
#         clients_layout = QVBoxLayout(clients_page)
#         clients_layout.setAlignment(Qt.AlignCenter)
        
#         clients_label = QLabel("👤 Gestion des Clients")
#         clients_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
#         clients_label.setAlignment(Qt.AlignCenter)
#         clients_layout.addWidget(clients_label)
        
#         clients_sub = QLabel("Module en cours de développement")
#         clients_sub.setStyleSheet("font-size: 14px; color: #64748b;")
#         clients_sub.setAlignment(Qt.AlignCenter)
#         clients_layout.addWidget(clients_sub)
#         self.container.addWidget(clients_page)

#         # --- PAGE 5 : RAPPORTS ---
#         reports_page = QWidget()
#         reports_layout = QVBoxLayout(reports_page)
#         reports_layout.setAlignment(Qt.AlignCenter)
        
#         reports_label = QLabel("📊 Rapports et Statistiques")
#         reports_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
#         reports_label.setAlignment(Qt.AlignCenter)
#         reports_layout.addWidget(reports_label)
        
#         reports_sub = QLabel("Module en cours de développement")
#         reports_sub.setStyleSheet("font-size: 14px; color: #64748b;")
#         reports_sub.setAlignment(Qt.AlignCenter)
#         reports_layout.addWidget(reports_sub)
#         self.container.addWidget(reports_page)

#         # --- PAGE 6 : PARAMÈTRES ---
#         settings_page = QWidget()
#         settings_layout = QVBoxLayout(settings_page)
#         settings_layout.setAlignment(Qt.AlignCenter)
        
#         settings_label = QLabel("⚙️ Paramètres")
#         settings_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
#         settings_label.setAlignment(Qt.AlignCenter)
#         settings_layout.addWidget(settings_label)
        
#         settings_sub = QLabel("Configuration de l'application")
#         settings_sub.setStyleSheet("font-size: 14px; color: #64748b;")
#         settings_sub.setAlignment(Qt.AlignCenter)
#         settings_layout.addWidget(settings_sub)
#         self.container.addWidget(settings_page)

#         # Ajout du conteneur principal
#         self.content_layout.addWidget(self.container)
#         self.layout.addWidget(self.content_container)

#     def switch_page(self, index):
#         """Changer la page affichée"""
#         if index >= 0 and index < self.container.count():
#             self.container.setCurrentIndex(index)
# '''

# # ============================================================================
# # MODULE CREATION
# # ============================================================================

# def create_module_structure(config):
#     """Crée la structure du module selon la configuration."""
#     module_name = config['name']
#     output_dir = config['output_dir']
#     class_name = pascal_case(module_name) + "MainView"
    
#     print_header(f"📦 Création du module {module_name}")
    
#     # Structure de base
#     ensure_dir(output_dir)
#     ensure_dir(output_dir / "controllers")
#     ensure_dir(output_dir / "views")
#     ensure_dir(output_dir / "models")
#     ensure_dir(output_dir / "static")
#     ensure_dir(output_dir / "templates")
#     ensure_dir(output_dir / "tests")
#     ensure_dir(output_dir / "migrations")
    
#     # Fichiers init
#     init_files = [
#         (output_dir / "__init__.py", f'"""Package du module {module_name}."""\n'),
#         (output_dir / "controllers" / "__init__.py", '"""Contrôleurs du module."""\n'),
#         (output_dir / "views" / "__init__.py", '"""Vues du module."""\n'),
#         (output_dir / "models" / "__init__.py", '"""Modèles du module."""\n'),
#         (output_dir / "tests" / "__init__.py", '"""Tests du module."""\n'),
#         (output_dir / "migrations" / "__init__.py", '"""Migrations du module."""\n'),
#     ]
    
#     for file_path, content in init_files:
#         if not file_path.exists():
#             file_path.write_text(content, encoding="utf-8")
    
#     # Création de main_ui.py à la racine
#     main_ui_content = get_main_ui_template(module_name, class_name)
#     (output_dir / "main_ui.py").write_text(main_ui_content, encoding="utf-8")
#     print_success(f"Fichier main_ui.py créé")
    
#     # Création de view.py dans le dossier views
#     view_content = get_view_template(module_name, class_name)
#     (output_dir / "views" / "view.py").write_text(view_content, encoding="utf-8")
#     print_success(f"Fichier views/view.py créé")
    
#     # Manifest
#     manifest = {
#         "name": module_name,
#         "version": config['version'],
#         "description": config['description'],
#         "author": config['author'],
#         "entry_point": "main_ui.py",
#         "enabled": config['enabled'],
#         "category": config['category'],
#         "min_app_version": config['min_app_version'],
#         "created_at": datetime.now().isoformat(),
#         "dependencies": config.get('dependencies', []),
#         "python_version": config.get('python_version', '>=3.8'),
#         "license": config.get('license', 'MIT'),
#         "repository": config.get('repository', ''),
#         "keywords": config.get('keywords', []),
#         "main_class": f"{class_name}Module",
#         "view_class": class_name
#     }
    
#     (output_dir / "manifest.json").write_text(
#         json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", 
#         encoding="utf-8"
#     )
    
#     # README
#     readme_content = (
#         f"# {module_name}\n\n"
#         f"## 📋 Description\n{config['description']}\n\n"
#         f"## 📦 Informations\n"
#         f"- **Version**: {config['version']}\n"
#         f"- **Auteur**: {config['author']}\n"
#         f"- **Catégorie**: {config['category']}\n"
#         f"- **Licence**: {config.get('license', 'MIT')}\n"
#         f"- **Date de création**: {datetime.now().strftime('%d/%m/%Y')}\n\n"
#         f"## 🚀 Installation\n```bash\n"
#         f"# Activer le module\n"
#         f"python manage.py enable_module {module_name}\n\n"
#         f"# Appliquer les migrations\n"
#         f"python manage.py migrate {module_name}\n```\n\n"
#         f"## 📁 Structure\n```\n"
#         f"{module_name}/\n"
#         f"├── controllers/     # Logique métier\n"
#         f"├── views/           # Interfaces utilisateur\n"
#         f"├── models/          # Modèles de données\n"
#         f"├── static/          # Fichiers statiques (CSS, JS, images)\n"
#         f"├── templates/       # Templates HTML\n"
#         f"├── tests/           # Tests unitaires\n"
#         f"├── migrations/      # Migrations de base de données\n"
#         f"├── main_ui.py       # Point d'entrée principal\n"
#         f"├── manifest.json    # Configuration du module\n"
#         f"└── README.md        # Documentation\n"
#         f"```\n\n"
#         f"## 🛠️ Développement\n```bash\n"
#         f"# Lancer les tests\n"
#         f"python -m pytest {module_name}/tests/\n\n"
#         f"# Formatage du code\n"
#         f"black {module_name}/\n```\n\n"
#         f"## 📄 Licence\n{config.get('license', 'MIT')}\n"
#     )
    
#     (output_dir / "README.md").write_text(readme_content, encoding="utf-8")
#     print_success(f"README.md créé")

# # ============================================================================
# # MAIN
# # ============================================================================

# def main():
#     """Point d'entrée principal."""
#     print_header("🚀 LOMETA - Module Creator v2.0")
    
#     # Informations de base
#     module_name = ask("Nom du module", "MonModule", required=True)
#     version = ask("Version", "1.0.0")
#     description = ask("Description", "Module créé automatiquement")
#     author = ask("Auteur", "Votre nom")
#     category = ask("Catégorie", "generic")
#     min_app_version = ask("Version minimale de l'application", "1.0.0")
#     enabled = ask_bool("Activer le module immédiatement ?", True)
    
#     # Template
#     print("\n📋 Types de templates disponibles:")
#     for key, template in TEMPLATES.items():
#         print(f"   [{key}] {template['name']}: {template['description']}")
    
#     template_type = ask("Type de template", "simple", choices=list(TEMPLATES.keys()))
    
#     # Dependencies
#     print("\n📦 Dépendances (séparées par des virgules, ex: requests, flask):")
#     deps_input = input("> ").strip()
#     dependencies = [d.strip() for d in deps_input.split(',') if d.strip()]
    
#     # Output directory
#     default_dir = str(Path.cwd() / snake_case(module_name))
#     output_dir = Path(ask("Dossier de destination", default_dir))
    
#     # Options supplémentaires
#     generate_routes = ask_bool("Générer les fichiers de routes ?", False)
#     generate_tests = ask_bool("Générer les tests unitaires ?", True)
    
#     # Configuration finale
#     config = {
#         'name': module_name,
#         'version': version,
#         'description': description,
#         'author': author,
#         'entry_point': 'main_ui.py',
#         'enabled': enabled,
#         'category': category,
#         'min_app_version': min_app_version,
#         'dependencies': dependencies,
#         'python_version': '>=3.8',
#         'license': 'MIT',
#         'template': template_type,
#         'output_dir': output_dir,
#         'generate_routes': generate_routes,
#         'generate_tests': generate_tests,
#     }
    
#     # Créer le module
#     try:
#         create_module_structure(config)
        
#         # Résumé final
#         print_header("📋 Résumé du module créé")
#         print(f"   Nom: {color(module_name, 'bold')}")
#         print(f"   Version: {version}")
#         print(f"   Auteur: {author}")
#         print(f"   Catégorie: {category}")
#         print(f"   Template: {template_type}")
#         if dependencies:
#             print(f"   Dépendances: {', '.join(dependencies)}")
#         print(f"   Activé: {color('Oui' if enabled else 'Non', 'green' if enabled else 'red')}")
#         print(f"\n📁 Emplacement: {output_dir}")
#         print(f"\n📄 Fichiers créés:")
#         print(f"   - {output_dir}/main_ui.py")
#         print(f"   - {output_dir}/views/view.py")
#         print(f"   - {output_dir}/manifest.json")
#         print(f"   - {output_dir}/README.md")
        
#         print("\n" + color("="*60, 'cyan'))
#         print(color("✅ Module créé avec succès !", 'bold'))
#         print(f"\n{color('💡', 'yellow')} Prochaines étapes:")
#         print("   1. Activez le module dans la configuration de l'application")
#         print("   2. Appliquez les migrations si nécessaire")
#         print("   3. Ajoutez votre logique métier")
#         print("   4. Testez votre module")
#         print("\n" + color("="*60, 'cyan'))
        
#     except Exception as e:
#         print_error(f"Erreur lors de la création du module: {e}")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)

# # ============================================================================
# # POINT D'ENTRÉE
# # ============================================================================

# if __name__ == "__main__":
#     main()



#!/usr/bin/env python3
"""
Script interactif pour créer un module LOMETA à partir de données saisies.
Version 3.0 : Lazy loading + LoadingPage + qtawesome.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT

# ============================================================================
# COLORS
# ============================================================================

COLORS = {
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'red': '\033[91m',
    'cyan': '\033[96m',
    'magenta': '\033[95m',
    'bold': '\033[1m',
    'reset': '\033[0m'
}

def color(text, color_name):
    return f"{COLORS.get(color_name, '')}{text}{COLORS['reset']}"

def print_header(text):
    print(f"\n{color('='*60, 'cyan')}")
    print(f"{color(text.center(60), 'bold')}")
    print(f"{color('='*60, 'cyan')}\n")

def print_success(text):
    print(f"{color('✅', 'green')} {text}")

def print_error(text):
    print(f"{color('❌', 'red')} {text}")

def print_info(text):
    print(f"{color('ℹ️', 'blue')} {text}")

def print_warning(text):
    print(f"{color('⚠️', 'yellow')} {text}")

# ============================================================================
# UTILITIES
# ============================================================================

def ask(prompt, default="", required=False, choices=None):
    if choices:
        prompt = f"{prompt} [{', '.join(choices)}]"
    while True:
        value = input(f"{prompt} [{default}]: ").strip() if default else input(f"{prompt}: ").strip()
        value = value if value else default
        if required and not value:
            print_error("Ce champ est requis.")
            continue
        if choices and value not in choices:
            print_error(f"Valeur invalide. Choisissez parmi: {', '.join(choices)}")
            continue
        return value

def ask_bool(prompt, default=True):
    default_text = "y/n" if default else "n/y"
    value = ask(f"{prompt} ({default_text})", "y" if default else "n")
    return value.lower() in {"1", "true", "yes", "y", "oui", "o"}

def snake_case(text):
    text = re.sub(r'([A-Z])', r'_\1', text).lower()
    text = re.sub(r'[^a-z0-9_]', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_')

def pascal_case(text):
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    words = text.split()
    return ''.join(word.capitalize() for word in words if word)

def kebab_case(text):
    text = re.sub(r'([A-Z])', r'-\1', text).lower()
    text = re.sub(r'[^a-z0-9-]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# TEMPLATES
# ============================================================================

TEMPLATES = {
    'crud': {'name': 'CRUD', 'description': 'Contrôleur, vues et modèles'},
    'api': {'name': 'API REST', 'description': 'API REST avec endpoints CRUD'},
    'simple': {'name': 'Simple', 'description': 'Module minimal'},
    'full': {'name': 'Complet', 'description': 'Structure complète'},
}


# ============================================================================
# LOADING PAGE (généré dans views/widgets/loading_page.py)
# ============================================================================

def get_loading_page_content():
    return '''"""
Widget de chargement avec progression en temps réel.
Pattern LOMETA standard.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QProgressBar, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath


class SpinnerWidget(QWidget):
    def __init__(self, size=80, color="#2563eb", parent=None):
        super().__init__(parent)
        self._size = size
        self._color = QColor(color)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(16)
        self.setFixedSize(size, size)

    def _rotate(self):
        self._angle = (self._angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen_bg = QPen(QColor("#e2e8f0"), 6)
        pen_bg.setCapStyle(Qt.RoundCap)
        p.setPen(pen_bg)
        rect = QRectF(4, 4, self._size - 8, self._size - 8)
        p.drawArc(rect, 0, 360 * 16)
        pen = QPen(self._color, 6)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, -self._angle * 16, 90 * 16)

    def start(self):
        if not self._timer.isActive():
            self._timer.start(16)

    def stop(self):
        self._timer.stop()


class StepIcon(QWidget):
    def __init__(self, size=22, parent=None):
        super().__init__(parent)
        self._size = size
        self._state = "pending"
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self.setFixedSize(size, size)

    def set_state(self, state):
        self._state = state
        if state == "loading":
            self._timer.start(50)
        else:
            self._timer.stop()
        self.update()

    def _rotate(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._size
        c = s / 2
        r = s / 2 - 2
        if self._state == "pending":
            p.setPen(QPen(QColor("#cbd5e1"), 2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(c, c), r, r)
        elif self._state == "loading":
            p.setPen(QPen(QColor("#e2e8f0"), 2))
            p.drawEllipse(QPointF(c, c), r, r)
            pen = QPen(QColor("#2563eb"), 2)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawArc(QRectF(2, 2, s - 4, s - 4), -self._angle * 16, 90 * 16)
        elif self._state == "done":
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#10b981")))
            p.drawEllipse(QPointF(c, c), r, r)
            pen = QPen(QColor("white"), 2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(pen)
            path = QPainterPath()
            path.moveTo(s * 0.3, s * 0.5)
            path.lineTo(s * 0.45, s * 0.65)
            path.lineTo(s * 0.72, s * 0.35)
            p.drawPath(path)
        elif self._state == "error":
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#ef4444")))
            p.drawEllipse(QPointF(c, c), r, r)
            pen = QPen(QColor("white"), 2)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(s * 0.32, s * 0.32), QPointF(s * 0.68, s * 0.68))
            p.drawLine(QPointF(s * 0.68, s * 0.32), QPointF(s * 0.32, s * 0.68))


class StepRow(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.icon = StepIcon(size=20)
        layout.addWidget(self.icon)
        self.label = QLabel(label)
        self.label.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
        layout.addWidget(self.label)
        layout.addStretch()
        self.status = QLabel("")
        self.status.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600; background: transparent;")
        layout.addWidget(self.status)

    def set_state(self, state, status_text=""):
        self.icon.set_state(state)
        if state == "pending":
            self.label.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
            self.status.setText("")
        elif state == "loading":
            self.label.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 600; background: transparent;")
            self.status.setStyleSheet("color: #2563eb; font-size: 11px; font-weight: 600; background: transparent;")
            self.status.setText(status_text or "…")
        elif state == "done":
            self.label.setStyleSheet("color: #1e293b; font-size: 12px; background: transparent;")
            self.status.setStyleSheet("color: #10b981; font-size: 11px; font-weight: 700; background: transparent;")
            self.status.setText(status_text or "✓")
        elif state == "error":
            self.label.setStyleSheet("color: #ef4444; font-size: 12px; background: transparent;")
            self.status.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: 700; background: transparent;")
            self.status.setText(status_text or "✕")


class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(False)
        self.setFixedHeight(8)
        self.setStyleSheet("""
            QProgressBar { background: #f1f5f9; border: none; border-radius: 4px; }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:0.5 #3b82f6, stop:1 #60a5fa);
                border-radius: 4px;
            }
        """)


class LoadingPage(QWidget):
    def __init__(self, title="Chargement...", message=None, parent=None):
        super().__init__(parent)
        self._title = message or title
        self.setStyleSheet("background: white;")
        self._steps = {}
        self._step_weights = {}
        self._weights_done = 0
        self._total_weight = 0
        self._current_progress = 0
        self._target_progress = 0
        self._smooth_timer = QTimer(self)
        self._smooth_timer.timeout.connect(self._smooth_progress)
        self._smooth_timer.start(16)
        self._setup_ui()
        self._animate_in()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("LoadingCard")
        self.card.setFixedSize(500, 480)
        self.card.setStyleSheet("""
            QFrame#LoadingCard {
                background: white; border-radius: 24px; border: 1px solid #e2e8f0;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(37, 99, 235, 25))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 32, 40, 32)
        card_layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(16)
        self.spinner = SpinnerWidget(size=56, color="#2563eb")
        header.addWidget(self.spinner)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a; background: transparent;")
        title_box.addWidget(self.title_label)
        self.subtitle_label = QLabel("Préparation en cours...")
        self.subtitle_label.setStyleSheet("font-size: 12px; color: #64748b; background: transparent;")
        title_box.addWidget(self.subtitle_label)
        header.addLayout(title_box, 1)
        card_layout.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #f1f5f9;")
        card_layout.addWidget(sep)

        self.steps_container = QVBoxLayout()
        self.steps_container.setSpacing(4)
        card_layout.addLayout(self.steps_container)
        card_layout.addStretch()

        progress_header = QHBoxLayout()
        lbl = QLabel("Progression")
        lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; background: transparent;")
        progress_header.addWidget(lbl)
        progress_header.addStretch()
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet("color: #2563eb; font-size: 16px; font-weight: 800; background: transparent;")
        progress_header.addWidget(self.percent_label)
        card_layout.addLayout(progress_header)

        self.progress_bar = ModernProgressBar()
        card_layout.addWidget(self.progress_bar)

        self.current_step_label = QLabel("Initialisation...")
        self.current_step_label.setStyleSheet("color: #94a3b8; font-size: 11px; font-style: italic; background: transparent;")
        self.current_step_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.current_step_label)

        main_layout.addWidget(self.card, 0, Qt.AlignCenter)

    def _animate_in(self):
        self._opacity = QGraphicsOpacityEffect()
        self.card.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity")
        self._fade.setDuration(300)
        self._fade.setStartValue(0)
        self._fade.setEndValue(1)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade.finished.connect(self._restore_shadow)
        self._fade.start()

    def _restore_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(37, 99, 235, 25))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

    def reset(self, title=None):
        if title:
            self._title = title
            self.title_label.setText(title)
        while self.steps_container.count():
            item = self.steps_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._steps.clear()
        self._step_weights.clear()
        self._weights_done = 0
        self._total_weight = 0
        self._current_progress = 0
        self._target_progress = 0
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")
        self.current_step_label.setText("Initialisation...")
        self.subtitle_label.setText("Préparation en cours...")

    def add_step(self, step_id, label, weight=1):
        row = StepRow(label)
        self.steps_container.addWidget(row)
        self._steps[step_id] = row
        self._step_weights[step_id] = weight
        self._total_weight += weight

    def step_started(self, step_id, subtitle=None):
        if step_id in self._steps:
            self._steps[step_id].set_state("loading")
            self.current_step_label.setText(f"→ {step_id}")
        if subtitle:
            self.subtitle_label.setText(subtitle)

    def step_done(self, step_id, status_text="✓"):
        if step_id in self._steps:
            self._steps[step_id].set_state("done", status_text)
        if step_id in self._step_weights:
            self._weights_done += self._step_weights[step_id]
            self._target_progress = int((self._weights_done / self._total_weight) * 100)

    def step_error(self, step_id, error_message=None):
        if step_id in self._steps:
            self._steps[step_id].set_state("error", "✕")
        if error_message:
            self.current_step_label.setText(f"❌ {error_message}")

    def set_subtitle(self, text):
        self.subtitle_label.setText(text)

    def set_message(self, text):
        self._title = text
        self.title_label.setText(text)

    def set_title(self, text):
        self._title = text
        self.title_label.setText(text)

    def set_percent(self, percent):
        self._target_progress = max(0, min(100, percent))

    def _smooth_progress(self):
        if self._current_progress < self._target_progress:
            diff = self._target_progress - self._current_progress
            step = max(1, diff // 6)
            self._current_progress = min(self._target_progress, self._current_progress + step)
            self.progress_bar.setValue(self._current_progress)
            self.percent_label.setText(f"{self._current_progress}%")
            if self._current_progress >= 100:
                self.current_step_label.setText("✅ Chargement terminé")
                self.subtitle_label.setText("Prêt")

    def stop(self):
        self.spinner.stop()
        self._smooth_timer.stop()
'''


# ============================================================================
# MAIN_UI TEMPLATE (avec sidebar.add_menu_button + qtawesome)
# ============================================================================

def get_main_ui_template(module_name, class_name, icon_name, icon_label):
    """Génère main_ui.py avec intégration sidebar + qtawesome."""
    return f'''from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from core.alerts import AlertManager
import qtawesome as qta

from addons.{module_name}.views.view import {class_name}


class {class_name}Module(BaseModule):
    """Module {module_name} — Pattern LOMETA standard."""

    def __init__(self, main_window=None, controller=None):
        super().__init__(main_window)
        self.controller = controller
        self.db_session = None
        self.current_user = None
        self.view = None
        self.btn = None
        self._is_loaded = False

    def setup(self):
        """Ajout du bouton dans la sidebar principale."""
        self.db_session = getattr(self.main_window, 'db_session', None)
        self.current_user = getattr(self.main_window, 'current_user', None)

        sidebar = getattr(self.main_window, 'sidebar', None)

        if sidebar and hasattr(sidebar, 'add_menu_button'):
            # ✅ Utiliser la méthode de la sidebar principale
            self.btn = sidebar.add_menu_button(
                "{icon_label}",
                "{icon_name}",
                self,
            )
            # Icône qtawesome cohérente avec la sidebar
            self.btn.setIcon(qta.icon('{icon_name}', color='#cbd5f5'))
            self.btn.setIconSize(QSize(20, 20))

            # Connecter à activate_module
            try:
                self.btn.clicked.disconnect()
            except Exception:
                pass
            self.btn.clicked.connect(self.activate_module)
        else:
            # Fallback : bouton simple
            self.btn = QPushButton("  {icon_label}")
            self.btn.setIcon(qta.icon('{icon_name}', color='#546e7a'))
            self.btn.setIconSize(QSize(20, 20))
            self.btn.setCheckable(True)
            self.btn.setFixedHeight(50)
            self.btn.setCursor(Qt.PointingHandCursor)
            self.btn.setStyleSheet("""
                QPushButton {{
                    background: transparent;
                    color: #546e7a;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 15px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: #f1f3f4;
                    color: #1a73e8;
                }}
                QPushButton:checked {{
                    background: #e8f0fe;
                    color: #1a73e8;
                    border-right: 3px solid #1a73e8;
                }}
            """)
            self.btn.clicked.connect(self.activate_module)

            if hasattr(self.main_window, 'sidebar_layout'):
                self.main_window.sidebar_layout.addWidget(self.btn)

    def activate_module(self):
        """Active le module — la vue gère son propre LoadingPage."""
        # ✅ Si déjà chargé, afficher directement
        if self._is_loaded and self.view:
            self.main_window.set_content_widget(self.view, "{icon_label}")
            if self.btn:
                self.btn.setChecked(True)
            return

        try:
            user = getattr(self.main_window, 'current_user', None)
            db_session = getattr(self.main_window, 'db_session', None)

            if not user:
                AlertManager.show_error(
                    self.main_window,
                    "Sécurité",
                    "Aucun utilisateur connecté détecté."
                )
                return

            self.current_user = user
            self.db_session = db_session

            # ✅ Créer la vue (rapide — les pages sont créées à la demande)
            self.view = {class_name}(controller=self.controller, user=self.current_user)
            self._is_loaded = True

            self.main_window.set_content_widget(self.view, "{icon_label}")
            if self.btn:
                self.btn.setChecked(True)

        except Exception as e:
            import traceback
            traceback.print_exc()
            AlertManager.show_error(self.main_window, "Erreur", str(e))
'''


# ============================================================================
# VIEW TEMPLATE (Lazy loading + LoadingPage + qtawesome)
# ============================================================================

# def get_view_template(module_name, class_name, pages_config):
#     """
#     Génère view.py avec lazy loading.
    
#     pages_config: list de tuples (page_id, label, icon_name)
#     """
#     # Construction des entrées sidebar
#     sidebar_entries = "\n".join([
#         f'            ("{label}", "{pid}", "{icon}"),'
#         for pid, label, icon in pages_config
#     ])

#     # Construction des messages de chargement
#     loading_msgs = "\n".join([
#         f'            "{pid}": "Chargement de {label.lower()}...",'
#         for pid, label, icon in pages_config
#     ])

#     # Factories par défaut (juste un QLabel pour démarrer)
#     factories = []
#     for pid, label, icon in pages_config:
#         factories.append(f'''
# def _make_{pid}(self):
#     """Page : {label}"""
#     # TODO: remplacer par la vraie vue
#     page = QWidget()
#     layout = QVBoxLayout(page)
#     layout.setAlignment(Qt.AlignCenter)

#     icon_lbl = QLabel()
#     icon_lbl.setPixmap(qta.icon("{icon}", color="#1a73e8").pixmap(64, 64))
#     icon_lbl.setAlignment(Qt.AlignCenter)
#     layout.addWidget(icon_lbl)

#     title = QLabel("{label}")
#     title.setStyleSheet("font-size: 28px; font-weight: 700; color: #1e293b;")
#     title.setAlignment(Qt.AlignCenter)
#     layout.addWidget(title)

#     sub = QLabel("Page prête à être développée")
#     sub.setStyleSheet("font-size: 14px; color: #64748b;")
#     sub.setAlignment(Qt.AlignCenter)
#     layout.addWidget(sub)

#     return page
# ''')

#     factories_code = "\n".join(factories)

#     # Dictionnaire des factories
#     factory_dict = "\n".join([
#         f'            "{pid}": lambda: self._make_{pid}(),'
#         for pid, label, icon in pages_config
#     ])

#     return f'''from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QListWidgetItem, QStackedWidget, QListWidget, QFrame,
#     QMessageBox, QGraphicsDropShadowEffect
# )
# from PySide6.QtCore import Qt, QSize, QTimer
# from PySide6.QtGui import QColor
# import qtawesome as qta

# from addons.{module_name}.views.widgets.loading_page import LoadingPage


# # ═══════════════════════════════════════════════════════════════════
# # BOUTON SIDEBAR MODERNE (avec qtawesome)
# # ═══════════════════════════════════════════════════════════════════

# class ModernSidebarButton(QPushButton):
#     """Bouton de navigation avec icône qtawesome."""

#     def __init__(self, text: str, icon_name: str, is_active: bool = False):
#         super().__init__()
#         self.icon_name = icon_name
#         self.button_text = text
#         self.is_active = is_active
#         self.setup_ui()

#     def setup_ui(self):
#         self.setFixedHeight(44)
#         self.setCursor(Qt.PointingHandCursor)
#         self.setStyleSheet(self._get_style())

#         self.setLayout(QHBoxLayout())
#         self.layout().setContentsMargins(12, 0, 16, 0)
#         self.layout().setSpacing(10)

#         self.icon_label = QLabel()
#         self.update_icon()

#         self.text_label = QLabel(self.button_text)
#         self.text_label.setStyleSheet("font-size: 13px; background: transparent; border: none;")
#         self.layout().addWidget(self.icon_label)
#         self.layout().addWidget(self.text_label)
#         self.layout().addStretch()
#         self.update_style()

#     def update_icon(self):
#         color = "#1a73e8" if self.is_active else "#64748b"
#         pix = qta.icon(self.icon_name, color=color).pixmap(18, 18)
#         self.icon_label.setPixmap(pix)
#         self.icon_label.setStyleSheet("background: transparent; border: none;")

#     def _get_style(self):
#         if self.is_active:
#             return """
#                 QPushButton {
#                     background-color: #eff6ff;
#                     color: #1a73e8;
#                     border: none;
#                     border-left: 4px solid #1a73e8;
#                     border-radius: 0 8px 8px 0;
#                     text-align: left;
#                     padding: 0;
#                     font-weight: 600;
#                 }
#                 QPushButton:hover { background-color: #dbeafe; }
#             """
#         return """
#             QPushButton {
#                 background-color: transparent;
#                 color: #475569;
#                 border: none;
#                 border-radius: 8px;
#                 text-align: left;
#                 padding: 0;
#             }
#             QPushButton:hover { background-color: #f1f5f9; color: #1a73e8; }
#         """

#     def update_style(self):
#         self.setStyleSheet(self._get_style())
#         self.update_icon()
#         color = "#1a73e8" if self.is_active else "#475569"
#         weight = "600" if self.is_active else "500"
#         self.text_label.setStyleSheet(
#             f"font-size: 13px; color: {{color}}; background: transparent; border: none; font-weight: {{weight}};"
#         )

#     def set_active(self, active: bool):
#         self.is_active = active
#         self.update_style()


# # ═══════════════════════════════════════════════════════════════════
# # VUE PRINCIPALE — Lazy Loading + LoadingPage
# # ═══════════════════════════════════════════════════════════════════

# class {class_name}(QWidget):
#     """Vue principale du module {module_name}."""

#     SIDEBAR_ITEMS = [
# {sidebar_entries}
#     ]

#     def __init__(self, controller=None, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user

#         # ✅ Lazy loading
#         self._page_factories = {{}}
#         self.page_widgets = {{}}
#         self.pages = []
#         self._page_rows = {{}}
#         self._page_history = []
#         self._loading_page_id = None  # verrou anti double-clic

#         self.setObjectName("MainModuleWindow")
#         self.setStyleSheet("background-color: #f8fafc;")

#         self.layout = QHBoxLayout(self)
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.layout.setSpacing(0)

#         self.setup_sidebar()
#         self.setup_content_area()

#         # ✅ Enregistrer les factories puis afficher la 1ère page
#         self._register_page_factories()
#         if self.pages:
#             self.sidebar.setCurrentRow(0)

#     # ═══════════════════════════════════════════════════════════════
#     # SIDEBAR
#     # ═══════════════════════════════════════════════════════════════

#     def setup_sidebar(self):
#         self.sidebar_container = QFrame()
#         self.sidebar_container.setFixedWidth(260)
#         self.sidebar_container.setStyleSheet(
#             "QFrame { background: white; border-right: 1px solid #e2e8f0; }"
#         )

#         sidebar_layout = QVBoxLayout(self.sidebar_container)
#         sidebar_layout.setContentsMargins(0, 0, 0, 0)
#         sidebar_layout.setSpacing(0)

#         # Header
#         header = QFrame()
#         header.setFixedHeight(70)
#         header.setStyleSheet(
#             "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
#             "stop:0 #1a73e8, stop:1 #1557b0); }"
#         )
#         header_layout = QHBoxLayout(header)
#         header_layout.setContentsMargins(20, 0, 20, 0)
#         header_layout.setSpacing(12)

#         logo_icon = QLabel()
#         logo_icon.setPixmap(
#             qta.icon('fa5s.cube', color='white').pixmap(QSize(24, 24))
#         )
#         header_layout.addWidget(logo_icon)

#         title = QLabel("{module_name}")
#         title.setStyleSheet(
#             "color: white; font-size: 16px; font-weight: 700; "
#             "letter-spacing: 1px; background: transparent;"
#         )
#         header_layout.addWidget(title)
#         header_layout.addStretch()
#         sidebar_layout.addWidget(header)

#         # Liste des pages
#         self.sidebar = QListWidget()
#         self.sidebar.setFocusPolicy(Qt.NoFocus)
#         self.sidebar.setStyleSheet("""
#             QListWidget {
#                 background: transparent;
#                 border: none;
#                 padding-top: 12px;
#                 outline: none;
#             }
#             QListWidget::item {
#                 background: transparent;
#                 border: none;
#                 padding: 0;
#                 margin: 2px 8px;
#                 height: 44px;
#             }
#             QListWidget::item:selected { background: transparent; }
#             QListWidget::item:hover { background: transparent; }
#         """)

#         for label, page_id, icon_name in self.SIDEBAR_ITEMS:
#             item = QListWidgetItem()
#             item.setData(Qt.UserRole, page_id)
#             item.setSizeHint(QSize(0, 44))

#             # Widget personnalisé
#             btn = ModernSidebarButton(label, icon_name, is_active=False)
#             self.sidebar.addItem(item)
#             self.sidebar.setItemWidget(item, btn)

#         self.sidebar.currentRowChanged.connect(self.display_page)
#         sidebar_layout.addWidget(self.sidebar, 1)

#         # User info en bas
#         footer = QFrame()
#         footer.setFixedHeight(80)
#         footer.setStyleSheet(
#             "QFrame { background: #f8fafc; border-top: 1px solid #e2e8f0; }"
#         )
#         footer_layout = QHBoxLayout(footer)
#         footer_layout.setContentsMargins(16, 10, 16, 10)
#         footer_layout.setSpacing(10)

#         avatar = QLabel()
#         avatar.setFixedSize(38, 38)
#         initials = "U"
#         if self.user and hasattr(self.user, 'username'):
#             initials = self.user.username[0].upper()
#         avatar.setText(initials)
#         avatar.setAlignment(Qt.AlignCenter)
#         avatar.setStyleSheet("""
#             QLabel {
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
#                     stop:0 #1a73e8, stop:1 #6366f1);
#                 color: white; border-radius: 19px;
#                 font-weight: 700; font-size: 14px;
#             }
#         """)
#         footer_layout.addWidget(avatar)

#         info = QVBoxLayout()
#         info.setSpacing(2)
#         name_lbl = QLabel(
#             getattr(self.user, 'username', 'Utilisateur') if self.user else 'Utilisateur'
#         )
#         name_lbl.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 600;")
#         info.addWidget(name_lbl)
#         role_lbl = QLabel(
#             f"● {{getattr(self.user, 'role', 'Membre') if self.user else 'Membre'}}"
#         )
#         role_lbl.setStyleSheet("color: #10b981; font-size: 10px; font-weight: 600;")
#         info.addWidget(role_lbl)
#         footer_layout.addLayout(info)
#         footer_layout.addStretch()
#         sidebar_layout.addWidget(footer)

#         self.layout.addWidget(self.sidebar_container)

#     # ═══════════════════════════════════════════════════════════════
#     # CONTENT AREA
#     # ═══════════════════════════════════════════════════════════════

#     def setup_content_area(self):
#         self.content_container = QFrame()
#         self.content_layout = QVBoxLayout(self.content_container)
#         self.content_layout.setContentsMargins(24, 24, 24, 24)
#         self.content_layout.setSpacing(12)

#         # ✅ LoadingPage
#         self.loading_page = LoadingPage(message="Chargement...")

#         # ✅ Stack
#         self.container = QStackedWidget()
#         self.container.setStyleSheet(
#             "QStackedWidget { background: white; border-radius: 16px; "
#             "border: 1px solid #e2e8f0; }"
#         )
#         self.container.addWidget(self.loading_page)

#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(25)
#         shadow.setColor(QColor(0, 0, 0, 15))
#         shadow.setOffset(0, 4)
#         self.container.setGraphicsEffect(shadow)

#         self.content_layout.addWidget(self.container)
#         self.layout.addWidget(self.content_container, 1)

#     # ═══════════════════════════════════════════════════════════════
#     # LAZY LOADING — Factories
#     # ═══════════════════════════════════════════════════════════════

#     def _register_page_factories(self):
#         self._page_factories = {{
# {factory_dict}
#         }}

#         self.pages = []
#         self._page_rows = {{}}
#         for label, page_id, icon_name in self.SIDEBAR_ITEMS:
#             if page_id in self._page_factories:
#                 self._page_rows[page_id] = len(self.pages)
#                 self.pages.append(page_id)

# {factories_code}

#     # ═══════════════════════════════════════════════════════════════
#     # SWITCH PAGE — Lazy Loading + LoadingPage
#     # ═══════════════════════════════════════════════════════════════

#     def display_page(self, row):
#         """Change de page avec lazy loading."""
#         if not (0 <= row < len(self.pages)):
#             return

#         # ✅ Verrou anti double-clic
#         if self._loading_page_id is not None:
#             return

#         page_id = self.pages[row]

#         # Mettre à jour les boutons
#         for i in range(self.sidebar.count()):
#             widget = self.sidebar.itemWidget(self.sidebar.item(i))
#             if isinstance(widget, ModernSidebarButton):
#                 widget.set_active(i == row)

#         # Historique
#         if not self._page_history or self._page_history[-1] != page_id:
#             self._page_history.append(page_id)
#             if len(self._page_history) > 20:
#                 self._page_history.pop(0)

#         widget = self.page_widgets.get(page_id)

#         # ─── CAS 1 : Première visite → LoadingPage + création ───
#         if widget is None:
#             loading_msgs = {{
# {loading_msgs}
#             }}

#             self.loading_page.set_message(loading_msgs.get(page_id, "Chargement..."))
#             self.loading_page.set_subtitle("Veuillez patienter quelques instants...")
#             self.container.setCurrentWidget(self.loading_page)

#             from PySide6.QtWidgets import QApplication
#             QApplication.processEvents()

#             self._loading_page_id = page_id

#             # Créer la page
#             try:
#                 widget = self._page_factories[page_id]()
#             except Exception as e:
#                 import traceback
#                 traceback.print_exc()
#                 error_widget = self._build_error_widget(page_id, str(e))
#                 self.container.addWidget(error_widget)
#                 self.container.setCurrentWidget(error_widget)
#                 self._loading_page_id = None
#                 return

#             if widget is None:
#                 error_widget = self._build_error_widget(
#                     page_id, "Widget non créé (import manquant ?)"
#                 )
#                 self.container.addWidget(error_widget)
#                 self.container.setCurrentWidget(error_widget)
#                 self._loading_page_id = None
#                 return

#             # Charger les données
#             self.loading_page.set_message("Chargement des données...")
#             QApplication.processEvents()

#             try:
#                 if hasattr(widget, 'refresh'):
#                     widget.refresh()
#                 elif hasattr(widget, 'load_data'):
#                     widget.load_data()
#             except Exception as refresh_err:
#                 print(f"⚠️ Erreur refresh {{page_id}}: {{refresh_err}}")

#             # Mise en cache + affichage
#             self.page_widgets[page_id] = widget
#             self.container.addWidget(widget)

#             def do_switch(w=widget):
#                 self.container.setCurrentWidget(w)
#                 self._loading_page_id = None

#             QTimer.singleShot(300, do_switch)

#         # ─── CAS 2 : Déjà visitée → affichage direct + refresh ───
#         else:
#             self.container.setCurrentWidget(widget)
#             if hasattr(widget, 'refresh'):
#                 try:
#                     QTimer.singleShot(10, widget.refresh)
#                 except Exception:
#                     pass

#     def _build_error_widget(self, page_id, error):
#         """Widget d'erreur stylisé."""
#         w = QWidget()
#         w.setStyleSheet("background: white;")
#         layout = QVBoxLayout(w)
#         layout.setAlignment(Qt.AlignCenter)
#         layout.setSpacing(20)

#         icon = QLabel()
#         icon.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#f59e0b').pixmap(64, 64))
#         icon.setAlignment(Qt.AlignCenter)
#         layout.addWidget(icon)

#         title = QLabel(f"Impossible de charger '{{page_id}}'")
#         title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b;")
#         title.setAlignment(Qt.AlignCenter)
#         layout.addWidget(title)

#         msg = QLabel(error)
#         msg.setStyleSheet("color: #64748b; font-size: 13px;")
#         msg.setAlignment(Qt.AlignCenter)
#         msg.setWordWrap(True)
#         layout.addWidget(msg)

#         return w
# '''

def get_view_template(module_name, class_name, pages_config):
    """
    Génère view.py avec lazy loading.
    APPROCHE PAR PLACEHOLDERS : aucun f-string imbriqué, aucune accolade à doubler.
    
    pages_config: list de tuples (page_id, label, icon_name)
    """
    # ─── Construction des fragments ───
    sidebar_entries = "\n".join([
        f'            ("{label}", "{pid}", "{icon}"),'
        for pid, label, icon in pages_config
    ])

    loading_msgs = "\n".join([
        f'            "{pid}": "Chargement de {label.lower()}...",'
        for pid, label, icon in pages_config
    ])

    factory_dict = "\n".join([
        f'            "{pid}": lambda: self._make_{pid}(),'
        for pid, label, icon in pages_config
    ])

    factories = []
    for pid, label, icon in pages_config:
        factories.append(f'''
    def _make_{pid}(self):
        """Page : {label}"""
        # TODO: remplacer par la vraie vue
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("{icon}", color="#1a73e8").pixmap(64, 64))
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)

        title = QLabel("{label}")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Page prête à être développée")
        sub.setStyleSheet("font-size: 14px; color: #64748b;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        return page
''')
    factories_code = "\n".join(factories)

    # ═══════════════════════════════════════════════════════════════════
    # TEMPLATE EN RAW STRING (pas de f-string → aucune accolade à doubler)
    # ═══════════════════════════════════════════════════════════════════
    template = r'''from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidgetItem, QStackedWidget, QListWidget, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor
import qtawesome as qta

from addons.__MODULE__.views.widgets.loading_page import LoadingPage


# ═══════════════════════════════════════════════════════════════════
# BOUTON SIDEBAR MODERNE (avec qtawesome)
# ═══════════════════════════════════════════════════════════════════

class ModernSidebarButton(QPushButton):
    """Bouton de navigation avec icône qtawesome."""

    def __init__(self, text: str, icon_name: str, is_active: bool = False):
        super().__init__()
        self.icon_name = icon_name
        self.button_text = text
        self.is_active = is_active
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self._get_style())

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(12, 0, 16, 0)
        self.layout().setSpacing(10)

        self.icon_label = QLabel()
        self.update_icon()

        self.text_label = QLabel(self.button_text)
        self.text_label.setStyleSheet(
            "font-size: 13px; background: transparent; border: none;"
        )
        self.layout().addWidget(self.icon_label)
        self.layout().addWidget(self.text_label)
        self.layout().addStretch()
        self.update_style()

    def update_icon(self):
        color = "#1a73e8" if self.is_active else "#64748b"
        pix = qta.icon(self.icon_name, color=color).pixmap(18, 18)
        self.icon_label.setPixmap(pix)
        self.icon_label.setStyleSheet("background: transparent; border: none;")

    def _get_style(self):
        if self.is_active:
            return """
                QPushButton {
                    background-color: #eff6ff;
                    color: #1a73e8;
                    border: none;
                    border-left: 4px solid #1a73e8;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                    text-align: left;
                    padding: 0;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #dbeafe;
                }
            """
        return """
            QPushButton {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #1a73e8;
            }
        """

    def update_style(self):
        self.setStyleSheet(self._get_style())
        self.update_icon()
        color = "#1a73e8" if self.is_active else "#475569"
        weight = "600" if self.is_active else "500"
        self.text_label.setStyleSheet(
            "font-size: 13px; color: " + color + "; background: transparent; "
            "border: none; font-weight: " + weight + ";"
        )

    def set_active(self, active: bool):
        self.is_active = active
        self.update_style()


# ═══════════════════════════════════════════════════════════════════
# VUE PRINCIPALE — Lazy Loading + LoadingPage
# ═══════════════════════════════════════════════════════════════════

class __CLASS__(QWidget):
    """Vue principale du module __MODULE__."""

    SIDEBAR_ITEMS = [
__SIDEBAR_ENTRIES__
    ]

    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user

        # Lazy loading
        self._page_factories = {}
        self.page_widgets = {}
        self.pages = []
        self._page_rows = {}
        self._page_history = []
        self._loading_page_id = None

        self.setObjectName("MainModuleWindow")
        self.setStyleSheet("background-color: #f8fafc;")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_content_area()

        # Enregistrer les factories puis afficher la 1re page
        self._register_page_factories()
        if self.pages:
            self.sidebar.setCurrentRow(0)

    # ═══════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════

    def setup_sidebar(self):
        self.sidebar_container = QFrame()
        self.sidebar_container.setFixedWidth(260)
        self.sidebar_container.setStyleSheet(
            "QFrame { background: white; border-right: 1px solid #e2e8f0; }"
        )

        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #1a73e8, stop:1 #1557b0); }"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(12)

        logo_icon = QLabel()
        logo_icon.setPixmap(
            qta.icon('fa5s.cube', color='white').pixmap(QSize(24, 24))
        )
        header_layout.addWidget(logo_icon)

        title = QLabel("__MODULE__")
        title.setStyleSheet(
            "color: white; font-size: 16px; font-weight: 700; "
            "letter-spacing: 1px; background: transparent;"
        )
        header_layout.addWidget(title)
        header_layout.addStretch()
        sidebar_layout.addWidget(header)

        # Liste des pages
        self.sidebar = QListWidget()
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                padding-top: 12px;
                outline: none;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 0;
                margin: 2px 8px;
                height: 44px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QListWidget::item:hover {
                background: transparent;
            }
        """)

        for label, page_id, icon_name in self.SIDEBAR_ITEMS:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, page_id)
            item.setSizeHint(QSize(0, 44))

            btn = ModernSidebarButton(label, icon_name, is_active=False)
            self.sidebar.addItem(item)
            self.sidebar.setItemWidget(item, btn)

        self.sidebar.currentRowChanged.connect(self.display_page)
        sidebar_layout.addWidget(self.sidebar, 1)

        # User info en bas
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet(
            "QFrame { background: #f8fafc; border-top: 1px solid #e2e8f0; }"
        )
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 10, 16, 10)
        footer_layout.setSpacing(10)

        avatar = QLabel()
        avatar.setFixedSize(38, 38)
        initials = "U"
        if self.user and hasattr(self.user, 'username'):
            initials = self.user.username[0].upper()
        avatar.setText(initials)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a73e8, stop:1 #6366f1);
                color: white;
                border-top-left-radius: 19px;
                border-top-right-radius: 19px;
                border-bottom-left-radius: 19px;
                border-bottom-right-radius: 19px;
                font-weight: 700;
                font-size: 14px;
            }
        """)
        footer_layout.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(
            getattr(self.user, 'username', 'Utilisateur') if self.user else 'Utilisateur'
        )
        name_lbl.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 600;")
        info.addWidget(name_lbl)

        role_text = str(getattr(self.user, 'role', 'Membre')) if self.user else 'Membre'
        role_lbl = QLabel("● " + role_text)
        role_lbl.setStyleSheet("color: #10b981; font-size: 10px; font-weight: 600;")
        info.addWidget(role_lbl)
        footer_layout.addLayout(info)
        footer_layout.addStretch()
        sidebar_layout.addWidget(footer)

        self.layout.addWidget(self.sidebar_container)

    # ═══════════════════════════════════════════════════════════════
    # CONTENT AREA
    # ═══════════════════════════════════════════════════════════════

    def setup_content_area(self):
        self.content_container = QFrame()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(12)

        # LoadingPage
        self.loading_page = LoadingPage(message="Chargement...")

        # Stack
        self.container = QStackedWidget()
        self.container.setStyleSheet(
            "QStackedWidget { background: white; border-radius: 16px; "
            "border: 1px solid #e2e8f0; }"
        )
        self.container.addWidget(self.loading_page)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        self.content_layout.addWidget(self.container)
        self.layout.addWidget(self.content_container, 1)

    # ═══════════════════════════════════════════════════════════════
    # LAZY LOADING — Factories
    # ═══════════════════════════════════════════════════════════════

    def _register_page_factories(self):
        self._page_factories = {
__FACTORY_DICT__
        }

        self.pages = []
        self._page_rows = {}
        for label, page_id, icon_name in self.SIDEBAR_ITEMS:
            if page_id in self._page_factories:
                self._page_rows[page_id] = len(self.pages)
                self.pages.append(page_id)

__FACTORIES_CODE__

    # ═══════════════════════════════════════════════════════════════
    # SWITCH PAGE — Lazy Loading + LoadingPage
    # ═══════════════════════════════════════════════════════════════

    def display_page(self, row):
        """Change de page avec lazy loading."""
        if not (0 <= row < len(self.pages)):
            return

        # Verrou anti double-clic
        if self._loading_page_id is not None:
            return

        page_id = self.pages[row]

        # Mettre à jour les boutons
        for i in range(self.sidebar.count()):
            widget = self.sidebar.itemWidget(self.sidebar.item(i))
            if isinstance(widget, ModernSidebarButton):
                widget.set_active(i == row)

        # Historique
        if not self._page_history or self._page_history[-1] != page_id:
            self._page_history.append(page_id)
            if len(self._page_history) > 20:
                self._page_history.pop(0)

        widget = self.page_widgets.get(page_id)

        # ─── CAS 1 : Première visite → LoadingPage + création ───
        if widget is None:
            loading_msgs = {
__LOADING_MSGS__
            }

            self.loading_page.set_message(loading_msgs.get(page_id, "Chargement..."))
            self.loading_page.set_subtitle("Veuillez patienter quelques instants...")
            self.container.setCurrentWidget(self.loading_page)

            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()

            self._loading_page_id = page_id

            # Créer la page
            try:
                widget = self._page_factories[page_id]()
            except Exception as e:
                import traceback
                traceback.print_exc()
                error_widget = self._build_error_widget(page_id, str(e))
                self.container.addWidget(error_widget)
                self.container.setCurrentWidget(error_widget)
                self._loading_page_id = None
                return

            if widget is None:
                error_widget = self._build_error_widget(
                    page_id, "Widget non créé (import manquant ?)"
                )
                self.container.addWidget(error_widget)
                self.container.setCurrentWidget(error_widget)
                self._loading_page_id = None
                return

            # Charger les données
            self.loading_page.set_message("Chargement des données...")
            QApplication.processEvents()

            try:
                if hasattr(widget, 'refresh'):
                    widget.refresh()
                elif hasattr(widget, 'load_data'):
                    widget.load_data()
            except Exception as refresh_err:
                print("Erreur refresh " + str(page_id) + ": " + str(refresh_err))

            # Mise en cache + affichage
            self.page_widgets[page_id] = widget
            self.container.addWidget(widget)

            def do_switch(w=widget):
                self.container.setCurrentWidget(w)
                self._loading_page_id = None

            QTimer.singleShot(300, do_switch)

        # ─── CAS 2 : Déjà visitée → affichage direct + refresh ───
        else:
            self.container.setCurrentWidget(widget)
            if hasattr(widget, 'refresh'):
                try:
                    QTimer.singleShot(10, widget.refresh)
                except Exception:
                    pass

    def _build_error_widget(self, page_id, error):
        """Widget d'erreur stylisé."""
        w = QWidget()
        w.setStyleSheet("background: white;")
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        icon = QLabel()
        icon.setPixmap(
            qta.icon('fa5s.exclamation-triangle', color='#f59e0b').pixmap(64, 64)
        )
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Impossible de charger '" + str(page_id) + "'")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        msg = QLabel(str(error))
        msg.setStyleSheet("color: #64748b; font-size: 13px;")
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        return w
'''

    # ─── Substitutions finales ───
    return (template
        .replace("__MODULE__", module_name)
        .replace("__CLASS__", class_name)
        .replace("__SIDEBAR_ENTRIES__", sidebar_entries)
        .replace("__LOADING_MSGS__", loading_msgs)
        .replace("__FACTORY_DICT__", factory_dict)
        .replace("__FACTORIES_CODE__", factories_code)
    )
# ============================================================================
# MODULE CREATION
# ============================================================================

def create_module_structure(config):
    module_name = config['name']
    output_dir = config['output_dir']
    class_name = pascal_case(module_name) + "MainView"

    print_header(f"📦 Création du module {module_name}")

    # Structure de base
    ensure_dir(output_dir)
    ensure_dir(output_dir / "controllers")
    ensure_dir(output_dir / "views")
    ensure_dir(output_dir / "views" / "widgets")   # ✅ Nouveau
    ensure_dir(output_dir / "models")
    ensure_dir(output_dir / "static")
    ensure_dir(output_dir / "templates")
    ensure_dir(output_dir / "tests")
    ensure_dir(output_dir / "migrations")

    # __init__.py
    init_files = [
        (output_dir / "__init__.py", f'"""Package du module {module_name}."""\n'),
        (output_dir / "controllers" / "__init__.py", '"""Contrôleurs."""\n'),
        (output_dir / "views" / "__init__.py", '"""Vues."""\n'),
        (output_dir / "views" / "widgets" / "__init__.py",
         'from .loading_page import LoadingPage\n__all__ = ["LoadingPage"]\n'),
        (output_dir / "models" / "__init__.py", '"""Modèles."""\n'),
        (output_dir / "tests" / "__init__.py", '"""Tests."""\n'),
        (output_dir / "migrations" / "__init__.py", '"""Migrations."""\n'),
    ]
    for file_path, content in init_files:
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")

    # ✅ loading_page.py
    (output_dir / "views" / "widgets" / "loading_page.py").write_text(
        get_loading_page_content(), encoding="utf-8"
    )
    print_success("Fichier views/widgets/loading_page.py créé")

    # Configuration des pages par défaut
    pages_config = config.get('pages', [
        ("home",     "Accueil",     "fa5s.home"),
        ("items",    "Éléments",    "fa5s.cube"),
        ("reports",  "Rapports",    "fa5s.chart-bar"),
        ("settings", "Paramètres",  "fa5s.cog"),
    ])

    # Icon + label pour le menu principal
    icon_name = config.get('icon_name', 'fa5s.cube')
    icon_label = config.get('icon_label', module_name)

    # ✅ main_ui.py
    main_ui_content = get_main_ui_template(
        module_name, class_name, icon_name, icon_label
    )
    (output_dir / "main_ui.py").write_text(main_ui_content, encoding="utf-8")
    print_success("Fichier main_ui.py créé")

    # ✅ views/view.py
    view_content = get_view_template(module_name, class_name, pages_config)
    (output_dir / "views" / "view.py").write_text(view_content, encoding="utf-8")
    print_success("Fichier views/view.py créé")

    # Manifest
    manifest = {
        "name": module_name,
        "version": config['version'],
        "description": config['description'],
        "author": config['author'],
        "entry_point": "main_ui.py",
        "enabled": config['enabled'],
        "category": config['category'],
        "min_app_version": config['min_app_version'],
        "created_at": datetime.now().isoformat(),
        "dependencies": config.get('dependencies', []),
        "python_version": config.get('python_version', '>=3.12'),
        "license": config.get('license', 'MIT'),
        "repository": config.get('repository', ''),
        "keywords": config.get('keywords', []),
        "main_class": f"{class_name}Module",
        "view_class": class_name,
        "icon_name": icon_name,
        "icon_label": icon_label,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    # README
    readme_content = (
        f"# {module_name}\n\n"
        f"## 📋 Description\n{config['description']}\n\n"
        f"## 📦 Informations\n"
        f"- **Version**: {config['version']}\n"
        f"- **Auteur**: {config['author']}\n"
        f"- **Catégorie**: {config['category']}\n"
        f"- **Icône sidebar**: `{icon_name}`\n"
        f"- **Label sidebar**: {icon_label}\n"
        f"- **Date**: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        f"## 🏗️ Architecture\n"
        f"Ce module utilise le **pattern LOMETA Lazy Loading** :\n"
        f"- Chaque page est créée **à la demande**\n"
        f"- Un `LoadingPage` s'affiche pendant la création\n"
        f"- L'UI ne gèle **jamais**\n\n"
        f"## 📁 Structure\n```\n"
        f"{module_name}/\n"
        f"├── controllers/          # Logique métier\n"
        f"├── views/                # Interfaces utilisateur\n"
        f"│   ├── widgets/\n"
        f"│   │   └── loading_page.py  # Loader réutilisable\n"
        f"│   └── view.py           # Vue principale (lazy loading)\n"
        f"├── models/               # Modèles de données\n"
        f"├── main_ui.py            # Point d'entrée principal\n"
        f"├── manifest.json         # Configuration du module\n"
        f"└── README.md             # Documentation\n"
        f"```\n\n"
        f"## ✨ Développement\n\n"
        f"### Remplacer une page par défaut\n"
        f"Dans `views/view.py`, remplace le corps de `_make_<page_id>()` :\n"
        f"```python\n"
        f"def _make_items(self):\n"
        f"    from .items_view import ItemsView\n"
        f"    return ItemsView(controller=self.controller, user=self.user)\n"
        f"```\n\n"
        f"### Ajouter une page\n"
        f"1. Ajoute une entrée dans `SIDEBAR_ITEMS`\n"
        f"2. Ajoute une factory dans `_register_page_factories`\n\n"
        f"## 📄 Licence\n{config.get('license', 'MIT')}\n"
    )
    (output_dir / "README.md").write_text(readme_content, encoding="utf-8")
    print_success("README.md créé")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print_header("🚀 LOMETA - Module Creator v3.0")

    module_name = ask("Nom du module", "MonModule", required=True)
    version = ask("Version", "1.0.0")
    description = ask("Description", "Module créé automatiquement")
    author = ask("Auteur", "Votre nom")
    category = ask("Catégorie", "generic")
    min_app_version = ask("Version minimale de l'application", "1.0.0")
    enabled = ask_bool("Activer le module immédiatement ?", True)

    # ✅ Icon + label sidebar
    print()
    print_info("Icône sidebar (format qtawesome, ex: fa5s.car, fa5s.cube, fa5s.chart-line)")
    icon_name = ask("Icône", "fa5s.cube")
    icon_label = ask("Label du bouton sidebar", module_name)

    # Template
    print("\n📋 Templates disponibles:")
    for key, template in TEMPLATES.items():
        print(f"   [{key}] {template['name']}: {template['description']}")
    template_type = ask("Type de template", "simple", choices=list(TEMPLATES.keys()))

    # Dépendances
    print("\n📦 Dépendances (séparées par virgules):")
    deps_input = input("> ").strip()
    dependencies = [d.strip() for d in deps_input.split(',') if d.strip()]

    # Pages personnalisées
    print("\n📄 Pages du module (format: page_id|Label|icône, une par ligne, vide pour terminer)")
    print("   Exemple: vehicles|Véhicules|fa5s.car")
    custom_pages = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        parts = line.split('|')
        if len(parts) == 3:
            custom_pages.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
        else:
            print_warning("Format invalide. Utilisez: page_id|Label|icône")

    if not custom_pages:
        custom_pages = [
            ("home",     "Accueil",     "fa5s.home"),
            ("items",    "Éléments",    "fa5s.cube"),
            ("reports",  "Rapports",    "fa5s.chart-bar"),
            ("settings", "Paramètres",  "fa5s.cog"),
        ]

    # Destination
    default_dir = str(Path.cwd() / snake_case(module_name))
    output_dir = Path(ask("Dossier de destination", default_dir))

    config = {
        'name': module_name,
        'version': version,
        'description': description,
        'author': author,
        'entry_point': 'main_ui.py',
        'enabled': enabled,
        'category': category,
        'min_app_version': min_app_version,
        'dependencies': dependencies,
        'python_version': '>=3.12',
        'license': 'MIT',
        'template': template_type,
        'output_dir': output_dir,
        'icon_name': icon_name,
        'icon_label': icon_label,
        'pages': custom_pages,
    }

    try:
        create_module_structure(config)

        print_header("📋 Résumé")
        print(f"   Nom: {color(module_name, 'bold')}")
        print(f"   Version: {version}")
        print(f"   Icône: {icon_name}")
        print(f"   Label sidebar: {icon_label}")
        print(f"   Pages: {len(custom_pages)}")
        for pid, lbl, icn in custom_pages:
            print(f"      • {lbl:20s} ({icn})")
        print(f"\n📁 Emplacement: {output_dir}")

        print("\n" + color("="*60, 'cyan'))
        print(color("✅ Module créé avec succès !", 'bold'))
        print(f"\n{color('💡', 'yellow')} Caractéristiques :")
        print("   ✅ Lazy loading (pages créées à la demande)")
        print("   ✅ LoadingPage intégrée (l'UI ne gèle jamais)")
        print("   ✅ Icônes qtawesome")
        print("   ✅ Intégration sidebar principale")
        print("\n" + color("="*60, 'cyan'))

    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()