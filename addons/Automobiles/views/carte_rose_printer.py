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
        draw_line(50, 30, self.data.get('owner'))
        
        # 2. BP YDé (Adresse)
        draw_line(50, 40, f"BP {self.data.get('city', 'Ydé')}")
        
        # 3. Plaque d'immatriculation
        draw_line(50, 50, self.data.get('immatriculation'))
        
        # 4. Marque et Modèle
        marque_mod = f"{self.data.get('marque', '')} {self.data.get('modele', '')}"
        draw_line(50, 60, marque_mod)
        
        # 5. Assureur
        draw_line(50, 70, self.data.get('compagny'))
        
        # 6. AMS Assurance (Texte fixe ou ID Agence)
        draw_line(50, 80, "AMS ASSURANCE")
        
        # 7. ID (Châssis ou Identifiant interne)
        draw_line(50, 90, f"ID: {self.data.get('id', 'N/A')}")
        
        # 8. Période : date_debut AU date_fin
        periode = f"{self.data.get('date_debut', '')} AU {self.data.get('date_fin', '')}"
        draw_line(50, 100, periode)
        
        # 9. Catégorie
        draw_line(50, 110, f"CATEGORIE: {self.data.get('categorie')}")
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
        draw_text_mm(60, 25, self.data.get('date_debut', '')) 
        draw_text_mm(160, 25, self.data.get('owner', ''))

        # Ligne 2 : Adresse / Ville
        draw_text_mm(30, 35, self.data.get('city', 'YAOUNDE'))

        # Ligne 3 : Numéro de police ou Code
        draw_text_mm(30, 45, self.data.get('code_tarif', ''))

        # Ligne 4 : Période de validité
        validite = f"DU {self.data.get('date_debut')} AU {self.data.get('date_fin')}"
        draw_text_mm(30, 55, validite)

        # Ligne 5 : Marque et Modèle
        marque_mod = f"{self.data.get('marque')} {self.data.get('modele')}"
        draw_text_mm(40, 65, marque_mod)

        # Ligne 6 : Immatriculation
        draw_text_mm(40, 75, self.data.get('immatriculation', ''))

        # Ligne 7 : Catégorie
        draw_text_mm(40, 85, f"CAT {self.data.get('categorie', '01')}")

        # Ligne 8 : Montants spécifiques (Ex: DTA comme sur votre image)
        if self.data.get('amt_dta', 0) > 0:
            dta_text = f"DTA: {float(self.data.get('amt_dta')):,.0f}".replace(",", " ")
            draw_text_mm(120, 85, dta_text)