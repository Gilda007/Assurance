from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                             QLineEdit, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon

# class VehicleMainView(QWidget):
#     def __init__(self, controller=None, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.setup_ui()
#         self.load_data()

#     def setup_ui(self):
#         self.setStyleSheet("background-color: #f8fafc;")
#         self.layout = QVBoxLayout(self)
#         self.layout.setContentsMargins(30, 30, 30, 30)
#         self.layout.setSpacing(20)

#         # --- EN-TÊTE ---
#         header_layout = QHBoxLayout()
        
#         title_container = QVBoxLayout()
#         self.title_label = QLabel("Parc Automobile")
#         self.title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b;")
#         self.subtitle_label = QLabel("Gérez vos véhicules, contrats et expertises")
#         self.subtitle_label.setStyleSheet("color: #64748b; font-size: 14px;")
#         title_container.addWidget(self.title_label)
#         title_container.addWidget(self.subtitle_label)
        
#         header_layout.addLayout(title_container)
#         header_layout.addStretch()
        
#         # Bouton Ajouter (Visible selon rôle)
#         self.btn_add = QPushButton(" + Nouveau Véhicule")
#         self.btn_add.setCursor(Qt.PointingHandCursor)
#         self.btn_add.setStyleSheet("""
#             QPushButton {
#                 background-color: #3b82f6; color: white; padding: 10px 20px;
#                 border-radius: 8px; font-weight: bold; border: none;
#             }
#             QPushButton:hover { background-color: #2563eb; }
#         """)
#         header_layout.addWidget(self.btn_add)
#         self.layout.addLayout(header_layout)

#         # --- BARRE DE RECHERCHE & FILTRES ---
#         filter_frame = QFrame()
#         filter_frame.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e2e8f0;")
#         filter_layout = QHBoxLayout(filter_frame)
        
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("Rechercher par immatriculation, marque ou propriétaire...")
#         self.search_input.setStyleSheet("border: none; padding: 8px; font-size: 14px;")
        
#         filter_layout.addWidget(self.search_input)
#         self.layout.addWidget(filter_frame)

#         # --- TABLEAU DES VÉHICULES ---
#         self.table = QTableWidget()
#         self.table.setColumnCount(5)
#         self.table.setHorizontalHeaderLabels(["Immatriculation", "Marque/Modèle", "Propriétaire", "Statut", "Actions"])
#         self.table.setAlternatingRowColors(True)
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.verticalHeader().setVisible(False)
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
#         self.table.setStyleSheet("""
#             QTableWidget {
#                 background-color: white; border: 1px solid #e2e8f0;
#                 border-radius: 12px; gridline-color: #f1f5f9; outline: none;
#             }
#             QHeaderView::section {
#                 background-color: #f8fafc; padding: 15px; border: none;
#                 border-bottom: 2px solid #e2e8f0; color: #475569; font-weight: bold;
#             }
#             QTableWidget::item { padding: 12px; border-bottom: 1px solid #f1f5f9; }
#         """)
        
#         self.layout.addWidget(self.table)

#     def load_data(self):
#         """Remplit le tableau avec les données du contrôleur"""
#         if not self.controller:
#             return
            
#         vehicles = self.controller.get_all_vehicles()
#         self.table.setRowCount(len(vehicles))
        
#         for i, v in enumerate(vehicles):
#             # --- CORRECTION ICI ---
#             # getattr(objet, "nom_attribut", "valeur_par_défaut")
#             immat = getattr(v, 'immatriculation', '---')
#             marque = getattr(v, 'marque', '')
#             modele = getattr(v, 'modele', '')
#             proprietaire = getattr(v, 'client_name', 'Inconnu')
#             statut = getattr(v, 'status', 'Actif')

#             # On crée les items du tableau en s'assurant que ce sont des STR
#             self.table.setItem(i, 0, QTableWidgetItem(str(immat)))
            
#             # On peut combiner marque et modèle
#             self.table.setItem(i, 1, QTableWidgetItem(f"{marque} {modele}"))
            
#             self.table.setItem(i, 2, QTableWidgetItem(str(proprietaire)))
            
#             # Pour le statut, on peut garder le centrage
#             status_item = QTableWidgetItem(str(statut))
#             status_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(i, 3, status_item)
            
#             # Bouton détails (inchangé)
#             btn_view = QPushButton("Détails")
#             btn_view.setStyleSheet("color: #3b82f6; font-weight: bold; border: none; background: transparent;")
#             self.table.setCellWidget(i, 4, btn_view)


