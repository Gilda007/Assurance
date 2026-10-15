"""
Page GED - Tous les documents centralisés
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class DocumentsPage(QWidget):
    """Page GED - Consultation de tous les documents"""
    
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.controller = controller  # SinistreController
        self.user = user
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel("📚 GED - Documents")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # Filtres
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔍 Rechercher un document...")
        self.input_search.setStyleSheet("padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px;")
        self.input_search.textChanged.connect(self._filtrer)
        filter_row.addWidget(self.input_search, 1)
        
        filter_row.addWidget(QLabel("Type:"))
        self.filter_type = QComboBox()
        self.filter_type.addItem("Tous", None)
        for t in ['DECLARATION', 'CONSTAT', 'PHOTO', 'RAPPORT', 'DEVIS', 
                  'FACTURE', 'JUGEMENT', 'ASSIGNATION']:
            self.filter_type.addItem(t, t)
        self.filter_type.currentIndexChanged.connect(self._filtrer)
        filter_row.addWidget(self.filter_type)
        
        filter_row.addWidget(QLabel("Entité:"))
        self.filter_entite = QComboBox()
        self.filter_entite.addItem("Tous", None)
        for e in ['SINISTRE', 'EXPERTISE', 'REGLEMENT', 'RECOURS']:
            self.filter_entite.addItem(e, e)
        self.filter_entite.currentIndexChanged.connect(self._filtrer)
        filter_row.addWidget(self.filter_entite)
        
        layout.addLayout(filter_row)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N° Document", "Nom fichier", "Type", "Entité", "Version", "Taille", "Date"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(self.table)
        
        # Boutons
        btn_row = QHBoxLayout()
        
        self.btn_ouvrir = QPushButton("📂 Ouvrir")
        self.btn_ouvrir.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8; color: white;
                padding: 8px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1557b0; }
        """)
        self.btn_ouvrir.clicked.connect(self._ouvrir_document)
        btn_row.addWidget(self.btn_ouvrir)
        
        self.btn_telecharger = QPushButton("📥 Télécharger")
        self.btn_telecharger.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_telecharger.clicked.connect(self._telecharger_document)
        btn_row.addWidget(self.btn_telecharger)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
    
    def load_data(self):
        """Charge tous les documents"""
        try:
            # TODO: appeler le controller pour récupérer les documents
            self._documents = []  # à remplir
            self._afficher(self._documents)
        except Exception as e:
            print(f"Erreur chargement documents: {e}")
    
    def refresh(self):
        """Rafraîchit la page"""
        self.load_data()
    
    def _afficher(self, documents):
        """Affiche les documents"""
        self.table.setRowCount(len(documents))
        for i, doc in enumerate(documents):
            self.table.setItem(i, 0, QTableWidgetItem(str(doc.get('id', ''))))
            self.table.setItem(i, 1, QTableWidgetItem(doc.get('nom_fichier', '')))
            self.table.setItem(i, 2, QTableWidgetItem(doc.get('type_document', '')))
            self.table.setItem(i, 3, QTableWidgetItem(doc.get('entite_type', '')))
            self.table.setItem(i, 4, QTableWidgetItem(f"v{doc.get('version', 1)}"))
            
            taille = doc.get('taille', 0)
            taille_str = f"{taille / 1024:.1f} Ko" if taille else "-"
            self.table.setItem(i, 5, QTableWidgetItem(taille_str))
            
            date = doc.get('created_at', '')[:10] if doc.get('created_at') else ''
            self.table.setItem(i, 6, QTableWidgetItem(date))
    
    def _filtrer(self):
        """Filtre les documents"""
        text = self.input_search.text().lower()
        type_f = self.filter_type.currentData()
        entite_f = self.filter_entite.currentData()
        
        filtered = [
            d for d in self._documents
            if (not text or text in (d.get('nom_fichier') or '').lower())
            and (not type_f or d.get('type_document') == type_f)
            and (not entite_f or d.get('entite_type') == entite_f)
        ]
        self._afficher(filtered)
    
    def _ouvrir_document(self):
        QMessageBox.information(self, "Info", "Ouverture du document (à implémenter)")
    
    def _telecharger_document(self):
        QMessageBox.information(self, "Info", "Téléchargement (à implémenter)")