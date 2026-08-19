from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont, QPageLayout, QPageSize
from PySide6.QtCore import Qt, QRectF, QMarginsF, QSizeF
from PySide6.QtWidgets import QMessageBox

# ✅ Désactiver les avertissements Wayland
import os
os.environ["QT_LOGGING_RULES"] = "qt.qpa.wayland.*=false"
os.environ["QT_QPA_PLATFORM"] = "xcb"

class CarteRosePrinter:
    def __init__(self, vehicle_data):
        self.data = vehicle_data

    def print(self, parent_widget):
        """Imprime la Carte Rose en paysage sur tous les systèmes"""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        
        
        dialog = QPrintDialog(printer, parent_widget)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            if painter.isActive():
                # ✅ Passer printer en paramètre
                self.draw_content(painter, printer)
                painter.end()

    def draw_content(self, painter, printer):
        """Dessine le contenu de la Carte Rose"""
        # ✅ Obtenir les dimensions de la page en points
        page_layout = printer.pageLayout()
        paint_rect = page_layout.paintRect()
        
        # ✅ Facteur d'échelle (points par mm)
        dpi = printer.resolution()
        scale = dpi / 25.4
        
        # Police adaptée à la résolution
        font = QFont("Courier New", 10)
        font.setPointSizeF(10)
        painter.setFont(font)
        painter.setPen(Qt.black)

        def draw_line(xmm, ymm, text):
            """Dessine du texte à partir de coordonnées en millimètres"""
            if not text or text == "None":
                return
            x = int(xmm * scale)
            y = int(ymm * scale)
            painter.drawText(x, y, str(text).upper())

        def format_date(date_value):
            """Formate une date en JJ/MM/AAAA"""
            if not date_value:
                return ""
            try:
                from datetime import datetime
                if isinstance(date_value, datetime):
                    return date_value.strftime("%d/%m/%Y")
                elif isinstance(date_value, str):
                    # Si c'est déjà une chaîne, essayer de la parser
                    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(date_value, fmt)
                            return dt.strftime("%d/%m/%Y")
                        except ValueError:
                            continue
                    return date_value[:10]  # Fallback: prendre les 10 premiers caractères
            except:
                return str(date_value)[:10]
            return str(date_value)[:10]

        # --- POSITIONS EN MILLIMÈTRES ---
        # A4 paysage: 297mm x 210mm
        
        # 1. Nom du propriétaire
        draw_line(10, 85, self.data.get('owner'))
        
        # 2. Immatriculation
        draw_line(10, 92, f"{self.data.get('immatriculation', '')}")
        
        # 3. Marque et Modèle
        marque_mod = f"{self.data.get('marque', '')} {self.data.get('modele', '')}"
        draw_line(10, 99, marque_mod)
        
        # 4. Assureur
        draw_line(10, 106, self.data.get('compagny'))
        
        # 5. AMS Assurance
        draw_line(10, 113, "AMS ASSURANCE")
        
        # 6. ID (Châssis)
        draw_line(10, 120, f"ID: {self.data.get('id', 'N/A')}")
        
        # 7. Période
        # periode = f"{self.data.get('date_debut', '')} AU {self.data.get('date_fin', '')}"
        date_debut = format_date(self.data.get('date_debut', ''))
        date_fin = format_date(self.data.get('date_fin', ''))
        periode = f"{date_debut} AU {date_fin}"
        draw_line(10, 127, periode)
        
        # 8. Catégorie
        usage_categorie = f"{self.data.get('libele_tarif', '')}, {self.data.get('categorie', '')}"
        draw_line(10, 134, usage_categorie)
        
        # --- DEUXIÈME COLONNE ---
        draw_line(80, 85, self.data.get('owner', ''))
        draw_line(80, 92, periode)
        draw_line(80, 99, self.data.get('immatriculation', ''))
        draw_line(80, 106, marque_mod)
        draw_line(80, 113, self.data.get('compagny', ''))
        draw_line(80, 120, f"ID: {self.data.get('id', 'N/A')}")
        draw_line(80, 127, usage_categorie)
        
        # --- TROISIÈME COLONNE ---
        draw_line(160, 85, self.data.get('owner', ''))
        draw_line(160, 92, self.data.get('immatriculation', ''))
        draw_line(160, 99, "AMS ASSURANCE, YAOUNDE")
        draw_line(160, 106, usage_categorie)

        # --- QUATRIEME COLONNE ---
        draw_line(230, 85, f"ID: {self.data.get('id', 'N/A')}")
        draw_line(230, 92, periode)
        draw_line(230, 106, marque_mod)
        draw_line(230, 113, self.data.get('chassis', 'N/A'))
        draw_line(230, 120, "AMS ASSURANCE, YAOUNDE")
        
        # ✅ Ajouter un cadre de bordure
        painter.drawRect(
            int(5 * scale), 
            int(5 * scale), 
            int(287 * scale), 
            int(200 * scale)
        )

 