from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont, QPageLayout
from PySide6.QtCore import Qt

class CarteRosePrinter:
    def __init__(self, vehicle_data):
        self.data = vehicle_data

    def print(self, parent_widget):
        printer = QPrinter(QPrinter.HighResolution)
        # Orientation Paysage pour la Carte Rose
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        
        dialog = QPrintDialog(printer, parent_widget)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            if painter.isActive():
                self.draw_content(painter)
                painter.end()

    def draw_content(self, painter):
        # Police type "Machine à écrire" pour l'administration
        font = QFont("Courier New", 11)
        painter.setFont(font)
        painter.setPen(Qt.black)

        # Facteur d'échelle (à ajuster selon la précision de votre imprimante)
        scale = 40 

        def draw_line(xmm, ymm, text):
            if text and text != "None":
                painter.drawText(int(xmm * scale), int(ymm * scale), str(text).upper())

        # --- CONFIGURATION DES LIGNES (Coordonnées à ajuster à la règle) ---
        # xmm : distance du bord gauche | ymm : distance du bord haut
        
        # 1. Nom du propriétaire
        draw_line(10, 85, self.data.get('owner'))
        
        # 2. BP YDé (Adresse)
        draw_line(10, 95, f"{self.data.get('immatriculation', '')}")
        
        # 4. Marque et Modèle
        marque_mod = f"{self.data.get('marque', '')} {self.data.get('modele', '')}"
        draw_line(10, 105, marque_mod)
        
        # 5. Assureur
        draw_line(10, 115, self.data.get('compagny'))
        
        # 6. AMS Assurance (Texte fixe ou ID Agence)
        draw_line(10, 125, "AMS ASSURANCE")
        
        # 7. ID (Châssis ou Identifiant interne)
        draw_line(10, 135, f"ID: {self.data.get('id', 'N/A')}")
        
        # 8. Période : date_debut AU date_fin
        periode = f"{self.data.get('date_debut', '')} AU {self.data.get('date_fin', '')}"
        draw_line(10, 145, periode)
        
        # 9. Catégorie
        usage_categorie = f"{self.data.get('libele_tarif', '')}, {self.data.get('categorie', '')}"
        draw_line(10, 155, usage_categorie)
        # Configuration de la police
        font = QFont("Courier", 10) # Police fixe souvent utilisée pour les formulaires
        painter.setFont(font)
        painter.setPen(Qt.black)

        # --- FONCTION DE PLACEMENT (x, y en mm) ---
        def draw_text_mm(x_mm, y_mm, text):
            if not text: return
            # Conversion mm vers unités logique de l'imprimante
            # On utilise environ 40 dots par mm pour une haute précision
            factor = 40 
            painter.drawText(x_mm * factor, y_mm * factor, str(text).upper())

        # --- MAPPAGE SELON VOTRE CAPTURE D'ÉCRAN ---
        # Note : Vous devrez ajuster ces coordonnées au millimètre près avec une règle
        
        # Ligne 1 : Date de création et Propriétaire
        draw_text_mm(100, 85, self.data.get('owner', ''))

        # Ligne 2 : Adresse / Ville
        draw_text_mm(100, 95, self.data.get('immatriculation', ''))

        # Ligne 3 : Numéro de police ou Code
        draw_text_mm(100, 105, self.data.get('compagny'))

        # Ligne 4 : Période de validité
        draw_text_mm(100, 115, "AMS ASSURANCE")

        # Ligne 5 : Marque et Modèle
        marque_mod = f"{self.data.get('marque')} {self.data.get('modele')}"
        draw_text_mm(100, 125, marque_mod)

        # Ligne 6 : Immatriculation
        draw_text_mm(100, 135, f"ID: {self.data.get('id', 'N/A')}")

        draw_line(100, 145, periode)

        # Ligne 7 : Catégorie
        draw_text_mm(100, 155, f"CAT {self.data.get('categorie', '01')}")

        # Ligne 8 : Montants spécifiques (Ex: DTA comme sur votre image)

        draw_line(200, 85, periode)

        draw_text_mm(190, 95, self.data.get('owner', ''))

        draw_text_mm(190, 105, self.data.get('immatriculation', ''))

        draw_text_mm(190, 115, self.data.get('compagny'))

        draw_text_mm(190, 125, usage_categorie)

        draw_text_mm(280, 85, f"ID: {self.data.get('id', 'N/A')}")

        draw_text_mm(280, 95, periode)

        draw_text_mm(280, 105, marque_mod)

        draw_text_mm(280, 115, self.data.get('chassis', 'N/A'))

        periode = f"AMS ASSURANCE, YAOUNDE"
        draw_line(280, 125, periode)