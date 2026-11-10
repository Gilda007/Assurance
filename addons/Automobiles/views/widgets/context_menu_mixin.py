# core/widgets/context_menu_mixin.py
from PySide6.QtWidgets import QMenu, QTableWidget
from PySide6.QtCore import Qt

class ContextMenuMixin:
    """Mixin pour ajouter un menu contextuel clic-droit à un QTableWidget."""
    
    def install_context_menu(self, table: QTableWidget, menu_builder, row_resolver):
        """
        :param table: le QTableWidget cible
        :param menu_builder: callable(rows: list[int]) -> QMenu
        :param row_resolver: callable(row) -> objet métier
        """
        table.setContextMenuPolicy(Qt.CustomContextMenu)

        def show_menu(pos):
            index = table.indexAt(pos)
            if not index.isValid():
                menu = menu_builder([])      # rows = [] → menu "vide"
            else:
                row = index.row()
                rows = {i.row() for i in table.selectedItems()} or {row}
                if row not in rows:
                    table.clearSelection()
                    table.selectRow(row)
                    rows = {row}
                menu = menu_builder(sorted(rows))
            menu.exec_(table.viewport().mapToGlobal(pos))

        table.customContextMenuRequested.connect(show_menu)