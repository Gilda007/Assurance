# update_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QLabel, QProgressBar)
from PySide6.QtCore import Qt

class UpdateDialog(QDialog):
    """Dialogue de sélection des mises à jour"""
    
    def __init__(self, parent, updates):
        super().__init__(parent)
        self.updates = updates  # ← Sauvegarder updates dans self.updates
        self.selected_updates = []
        self.setWindowTitle("Mises à jour disponibles")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QLabel(f"{len(self.updates)} mise(s) à jour disponible(s)")
        header.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Tableau des mises à jour
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["", "Module", "Version actuelle", "Nouvelle version", "Taille"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        
        # Remplir le tableau
        for i, (key, update) in enumerate(self.updates.items()):
            # Checkbox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Checked)
            self.table.setItem(i, 0, check_item)
            
            # Nom
            self.table.setItem(i, 1, QTableWidgetItem(update['name']))
            
            # Version actuelle
            self.table.setItem(i, 2, QTableWidgetItem(update['current_version']))
            
            # Nouvelle version
            self.table.setItem(i, 3, QTableWidgetItem(update['new_version']))
            
            # Taille
            size_mb = update.get('size', 0) / (1024 * 1024)
            size_text = f"{size_mb:.1f} MB" if size_mb > 0 else "Inconnue"
            self.table.setItem(i, 4, QTableWidgetItem(size_text))
        
        self.table.setFixedHeight(300)
        layout.addWidget(self.table)
        
        # Changelog
        changelog_label = QLabel("Détails des changements:")
        changelog_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(changelog_label)
        
        self.changelog_text = QLabel()
        self.changelog_text.setWordWrap(True)
        self.changelog_text.setStyleSheet("background: #f5f5f5; padding: 10px; border-radius: 5px;")
        
        # Correction ici : utiliser self.updates au lieu de updates
        changelog_lines = []
        for update in self.updates.values():
            if update.get('changelog'):
                changelog_lines.append(f"• {update['changelog']}")
        
        changelog_content = "\n".join(changelog_lines) if changelog_lines else "Aucune information"
        self.changelog_text.setText(changelog_content)
        layout.addWidget(self.changelog_text)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Boutons
        buttons = QHBoxLayout()
        
        self.install_btn = QPushButton("Installer les sélectionnés")
        self.install_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(self.install_btn)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
    
    def get_selected_updates(self):
        """Retourne la liste des mises à jour sélectionnées"""
        selected = []
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).checkState() == Qt.Checked:
                key = list(self.updates.keys())[i]
                selected.append(key)
        return selected