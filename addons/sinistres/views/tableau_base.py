"""
Classe de base pour les tableaux avec colonne Actions et sélection par clic
"""
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout,
    QPushButton, QHeaderView, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor, QAction

from typing import List, Dict, Any, Callable, Optional


class TableauActions(QTableWidget):
    """
    Tableau avec colonne Actions intégrée et gestion de la sélection
    """
    
    row_double_clicked = Signal(int, dict)  # index, données
    row_selected = Signal(int, dict)        # index, données
    row_right_clicked = Signal(int, dict)   # index, données
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.actions_config = []
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        # Connexion des signaux
        self.cellClicked.connect(self._on_cell_clicked)
        self.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
    
    def _on_cell_clicked(self, row: int, col: int):
        """Gère le clic sur une cellule"""
        if row < len(self.data):
            self.selectRow(row)
            self.row_selected.emit(row, self.data[row])
    
    def _on_cell_double_clicked(self, row: int, col: int):
        """Gère le double-clic sur une cellule"""
        if row < len(self.data):
            self.row_double_clicked.emit(row, self.data[row])
    
    def _on_context_menu(self, position: QPoint):
        """Gère le clic droit pour afficher un menu contextuel"""
        row = self.rowAt(position.y())
        if row < 0 or row >= len(self.data):
            return
        
        self.selectRow(row)
        menu = QMenu(self)
        
        # Ajouter les actions du menu
        for action in self.actions_config:
            if action.get('context_menu', True):
                menu_action = QAction(action.get('label', 'Action'), self)
                menu_action.triggered.connect(lambda checked, d=self.data[row]: action.get('callback', lambda x: None)(d))
                menu.addAction(menu_action)
        
        menu.exec(self.viewport().mapToGlobal(position))
    
    def set_data(self, data: List[dict], columns: List[dict], actions: List[dict] = None):
        """
        Remplit le tableau avec des données
        columns: [{'key': 'id', 'label': 'ID', 'width': 50, 'format': lambda x: str(x)}, ...]
        actions: [{'label': 'Voir', 'icon': '👁️', 'callback': fonction, 'context_menu': True}, ...]
        """
        self.data = data
        self.actions_config = actions or []
        self.setRowCount(len(data))
        
        # Configurer les colonnes
        total_cols = len(columns) + (1 if actions else 0)
        self.setColumnCount(total_cols)
        
        # Définir les en-têtes
        headers = [c.get('label', c.get('key', '')) for c in columns]
        if actions:
            headers.append("Actions")
        self.setHorizontalHeaderLabels(headers)
        
        # Ajuster les largeurs
        for i, col in enumerate(columns):
            if col.get('width'):
                self.setColumnWidth(i, col['width'])
        
        # Remplir les données
        for row_idx, item in enumerate(data):
            for col_idx, col in enumerate(columns):
                key = col.get('key', '')
                value = item.get(key, '')
                
                # Appliquer le format
                format_func = col.get('format', lambda x: str(x) if x is not None else '')
                display = format_func(value)
                
                table_item = QTableWidgetItem(display)
                
                # Stocker les données dans l'item
                table_item.setData(Qt.UserRole, item)
                
                # Appliquer les couleurs si spécifiées
                if col.get('color_map'):
                    color = col['color_map'](value)
                    if color:
                        table_item.setBackground(QColor(color))
                        table_item.setForeground(QColor('white'))
                
                # Alignement
                if col.get('align'):
                    align_map = {
                        'left': Qt.AlignLeft | Qt.AlignVCenter,
                        'center': Qt.AlignCenter,
                        'right': Qt.AlignRight | Qt.AlignVCenter
                    }
                    table_item.setTextAlignment(align_map.get(col['align'], Qt.AlignLeft | Qt.AlignVCenter))
                
                self.setItem(row_idx, col_idx, table_item)
            
            # Ajouter les actions
            if actions:
                btn_widget = self._create_action_buttons(actions, item)
                self.setCellWidget(row_idx, len(columns), btn_widget)
        
        # Ajuster les colonnes
        self.resizeColumnsToContents()
    
    def _create_action_buttons(self, actions: List[dict], data_item: dict) -> QWidget:
        """Crée les boutons d'action pour une ligne"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        
        for action in actions:
            btn = QPushButton(action.get('icon', '🔹'))
            btn.setFixedSize(28, 28)
            btn.setToolTip(action.get('label', ''))
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 14px;
                    font-size: 12px;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
                QPushButton:pressed {
                    background-color: #cbd5e1;
                }
            """)
            
            # Passer les données à la callback
            callback = action.get('callback')
            if callback:
                btn.clicked.connect(lambda checked, d=data_item: callback(d))
            
            layout.addWidget(btn)
        
        layout.addStretch()
        return widget
    
    def get_selected_data(self) -> Optional[dict]:
        """Retourne les données de la ligne sélectionnée"""
        row = self.currentRow()
        if row >= 0 and row < len(self.data):
            return self.data[row]
        return None
    
    def get_selected_id(self, id_key: str = 'id') -> Optional[Any]:
        """Retourne l'ID de la ligne sélectionnée"""
        data = self.get_selected_data()
        if data:
            return data.get(id_key)
        return None
    
    def refresh_data(self):
        """Rafraîchit les données (à surcharger)"""
        pass