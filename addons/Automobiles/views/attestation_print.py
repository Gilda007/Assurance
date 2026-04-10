from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont, QPageLayout
from PySide6.QtCore import Qt

class AttestationPrinter:
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
        draw_line(10, 30, self.data.get('owner'))
        
        # 2. BP YDé (Adresse)
        draw_line(10, 40, f"ID: {self.data.get('id', 'N/A')}")

        periode = f"{self.data.get('date_debut', '')} AU {self.data.get('date_fin', '')}"
        draw_line(10, 50, periode)
        
        # 4. Marque et Modèle
        marque_mod = f"{self.data.get('marque', '')} {self.data.get('modele', '')}"
        draw_line(10, 65, marque_mod)

        draw_line(10, 75, self.data.get('immatriculation', ''))
        
        # 6. AMS Assurance (Texte fixe ou ID Agence)
        draw_line(10, 85, "VT")
        
        # 7. ID (Châssis ou Identifiant interne)
        draw_line(10, 95, f"CAT {self.data.get('categorie', '01')}")
        
        # 8. Période : date_debut AU date_fin
        
        
        # 9. Catégorie
        usage_categorie = f"{self.data.get('libele_tarif', '')}, CATEGORIE: {self.data.get('categorie', '')}"
        draw_line(10, 100, usage_categorie)
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
        draw_text_mm(80, 30, self.data.get('id', ''))

        # Ligne 2 : Adresse / Ville
        draw_text_mm(80, 40, periode)

        # Ligne 3 : Numéro de police ou Code
        draw_text_mm(80, 50, marque_mod)

        # Ligne 4 : Période de validité
        draw_text_mm(80, 60, f"{self.data.get('immatriculation', 'N/A')}")

        # Ligne 5 : Marque et Modèle
        draw_text_mm(80, 70, 'VT')

        # Ligne 7 : Catégorie
        draw_text_mm(80, 100, f"CAT {self.data.get('categorie', '01')}")


         # Ligne 1 : Date de création et Propriétaire
        info_ower = f"{self.data.get('owner', '')} {self.data.get('phone', '')}"
        draw_text_mm(120, 30, info_ower)

        # Ligne 3 : Numéro de police ou Code
        draw_text_mm(120, 40, f"{self.data.get('id', 'N/A')}")

        # Ligne 2 : Adresse / Ville
        draw_text_mm(120, 50, periode)

        # Ligne 5 : Marque et Modèle
        draw_text_mm(120, 60, marque_mod)

        # Ligne 7 : Catégorie
        draw_text_mm(120, 70, f"{self.data.get('immatriculation', 'N/A')}")

        draw_text_mm(120, 80, 'VT')