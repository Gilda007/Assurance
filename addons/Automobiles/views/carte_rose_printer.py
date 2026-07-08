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
        
        # Configuration robuste pour forcer le paysage sur tous les OS
        self._configure_printer(printer)
        
        dialog = QPrintDialog(printer, parent_widget)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            if painter.isActive():
                # ✅ Passer printer en paramètre
                self.draw_content(painter, printer)
                painter.end()

    def _configure_printer(self, printer):
        """Configure le format A4 en paysage de manière fiable"""
        # ✅ Définir explicitement la taille A4 en millimètres
        a4_size = QSizeF(297, 210)  # A4 paysage: 297mm x 210mm
        
        # ✅ Créer un QPageSize avec des dimensions exactes
        page_size = QPageSize(a4_size, QPageSize.Millimeter, "A4 Landscape")
        
        # ✅ Créer un layout avec le format A4 en paysage
        page_layout = QPageLayout()
        page_layout.setPageSize(page_size)
        page_layout.setOrientation(QPageLayout.Landscape)
        page_layout.setMargins(QMarginsF(10, 10, 10, 10))  # Marges en mm
        
        # Appliquer le layout
        printer.setPageLayout(page_layout)
        
        # ✅ Forcer avec les propriétés directes
        printer.setPageOrientation(QPageLayout.Landscape)
        printer.setResolution(300)
        printer.setFullPage(False)

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

        # --- POSITIONS EN MILLIMÈTRES ---
        # A4 paysage: 297mm x 210mm
        
        # 1. Nom du propriétaire
        draw_line(10, 85, self.data.get('owner'))
        
        # 2. Immatriculation
        draw_line(10, 95, f"{self.data.get('immatriculation', '')}")
        
        # 3. Marque et Modèle
        marque_mod = f"{self.data.get('marque', '')} {self.data.get('modele', '')}"
        draw_line(10, 105, marque_mod)
        
        # 4. Assureur
        draw_line(10, 115, self.data.get('compagny'))
        
        # 5. AMS Assurance
        draw_line(10, 125, "AMS ASSURANCE")
        
        # 6. ID (Châssis)
        draw_line(10, 135, f"ID: {self.data.get('id', 'N/A')}")
        
        # 7. Période
        periode = f"{self.data.get('date_debut', '')} AU {self.data.get('date_fin', '')}"
        draw_line(10, 145, periode)
        
        # 8. Catégorie
        usage_categorie = f"{self.data.get('libele_tarif', '')}, {self.data.get('categorie', '')}"
        draw_line(10, 155, usage_categorie)
        
        # --- DEUXIÈME COLONNE ---
        draw_line(100, 85, periode)
        draw_line(100, 95, self.data.get('owner', ''))
        draw_line(100, 105, self.data.get('immatriculation', ''))
        draw_line(100, 115, self.data.get('compagny', ''))
        draw_line(100, 125, usage_categorie)
        
        # --- TROISIÈME COLONNE ---
        draw_line(200, 85, f"ID: {self.data.get('id', 'N/A')}")
        draw_line(200, 95, periode)
        draw_line(200, 105, marque_mod)
        draw_line(200, 115, self.data.get('chassis', 'N/A'))
        draw_line(200, 125, "AMS ASSURANCE, YAOUNDE")
        
        # ✅ Ajouter un cadre de bordure
        painter.drawRect(
            int(5 * scale), 
            int(5 * scale), 
            int(287 * scale), 
            int(200 * scale)
        )

    def export_to_pdf(self, file_path):
        """Exporte la Carte Rose en PDF (format A4 paysage garanti)"""
        printer = QPrinter(QPrinter.HighResolution)
        
        # Configuration pour PDF en paysage
        self._configure_printer(printer)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        
        painter = QPainter(printer)
        if painter.isActive():
            self.draw_content(painter, printer)
            painter.end()
            return True
        return False

    def preview(self, parent_widget):
        """Affiche un aperçu avant impression"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        
        # Créer une image de prévisualisation
        preview_dialog = QDialog(parent_widget)
        preview_dialog.setWindowTitle("Aperçu Carte Rose")
        preview_dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(preview_dialog)
        
        # Créer un QPrinter virtuel pour l'aperçu
        printer = QPrinter(QPrinter.HighResolution)
        self._configure_printer(printer)
        printer.setOutputFormat(QPrinter.PdfFormat)
        
        # Dessiner sur le printer
        painter = QPainter(printer)
        if painter.isActive():
            self.draw_content(painter, printer)
            painter.end()
        
        # Afficher un message d'aperçu
        label = QLabel("📄 Aperçu de la Carte Rose (format A4 paysage)\n\n")
        label.setStyleSheet("font-size: 14px; padding: 20px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Bouton d'impression
        btn_imprimer = QPushButton("🖨️ Imprimer")
        btn_imprimer.clicked.connect(lambda: self.print(preview_dialog))
        layout.addWidget(btn_imprimer)
        
        # Bouton d'export PDF
        from PySide6.QtWidgets import QFileDialog
        btn_pdf = QPushButton("📄 Exporter en PDF")
        btn_pdf.clicked.connect(lambda: self._export_pdf_from_dialog(preview_dialog))
        layout.addWidget(btn_pdf)
        
        # Bouton fermer
        btn_fermer = QPushButton("Fermer")
        btn_fermer.clicked.connect(preview_dialog.accept)
        layout.addWidget(btn_fermer)
        
        preview_dialog.exec_()

    def _export_pdf_from_dialog(self, parent):
        """Exporte en PDF depuis le dialogue d'aperçu"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Enregistrer le PDF",
            f"carte_rose_{self.data.get('immatriculation', 'vehicle')}.pdf",
            "PDF (*.pdf)"
        )
        
        if file_path:
            if self.export_to_pdf(file_path):
                QMessageBox.information(parent, "Succès", f"PDF exporté avec succès : {file_path}")
            else:
                QMessageBox.warning(parent, "Erreur", "Erreur lors de l'export PDF")

    def get_pdf_bytes(self):
        """Génère le PDF en mémoire (bytes) pour utilisation sans fichier"""
        from PySide6.QtCore import QBuffer
        
        # Créer un buffer mémoire
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        
        # Créer le printer avec le buffer
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputDevice(buffer)
        
        # Configurer le format A4 paysage
        self._configure_printer(printer)
        
        # Dessiner le contenu
        painter = QPainter(printer)
        if painter.isActive():
            self.draw_content(painter, printer)
            painter.end()
        
        # Récupérer les données
        buffer.seek(0)
        data = buffer.data()
        buffer.close()
        
        return data