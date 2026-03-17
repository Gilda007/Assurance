# core/style_sheet.py
STYLE_SHEET = """
QMainWindow { background-color: #f8f9fa; }

/* Barre latérale à la Odoo (Bleu foncé/Gris) */
#Sidebar { 
    background-color: #2c3e50; 
    min-width: 200px;
}

#Sidebar QPushButton {
    color: white;
    border: none;
    padding: 12px;
    text-align: left;
    font-size: 14px;
}

#Sidebar QPushButton:hover {
    background-color: #34495e;
}

/* Tableaux modernes */
QTableWidget {
    gridline-color: #dcdde1;
    border: 1px solid #dcdde1;
}

QHeaderView::section {
    background-color: #f1f2f6;
    padding: 5px;
    border: 1px solid #dcdde1;
    font-weight: bold;
}
"""