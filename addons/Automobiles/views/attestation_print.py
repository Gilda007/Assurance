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
        draw_line(10, 75, self.data.get('owner'))
        
        # 2. BP YDé (Adresse)
        draw_line(10, 85, f"ID: {self.data.get('id', 'N/A')}")

        periode = f"{self.data.get('date_debut', '')} AU {self.data.get('date_fin', '')}"
        draw_line(10, 95, periode)
        
        # 4. Marque et Modèle
        marque_mod = f"{self.data.get('marque', '')} {self.data.get('modele', '')}"
        draw_line(10, 105, marque_mod)

        draw_line(10, 115, self.data.get('immatriculation', ''))
        
        # 6. AMS Assurance (Texte fixe ou ID Agence)
        draw_line(10, 125, "VT")
        
        # 7. ID (Châssis ou Identifiant interne)
        draw_line(10, 135, f"CAT {self.data.get('categorie', '01')}")
        
        # 8. Période : date_debut AU date_fin
        
        
        # 9. Catégorie
        usage_categorie = f"{self.data.get('libele_tarif', '')}"
        draw_line(10, 145, usage_categorie)

        # Configuration de la police"
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


         # Ligne 1 : Date de création et Propriétaire
        info_ower = f"{self.data.get('owner', '')} {self.data.get('phone', '')}"
        draw_text_mm(100, 75, info_ower)

        # Ligne 3 : Numéro de police ou Code
        draw_text_mm(100, 85, f"{self.data.get('id', 'N/A')}")

        # Ligne 2 : Adresse / Ville
        draw_text_mm(100, 95, periode)

        # Ligne 5 : Marque et Modèle
        draw_text_mm(100, 105, marque_mod)

        # Ligne 7 : Catégorie
        draw_text_mm(100, 115, f"{self.data.get('immatriculation', 'N/A')}")

        draw_text_mm(100, 125, 'VT')


        # --- MAPPAGE SELON VOTRE CAPTURE D'ÉCRAN ---
        # Note : Vous devrez ajuster ces coordonnées au millimètre près avec une règle
        
        # Ligne 1 : Date de création et Propriétaire
        info_ower = f"{self.data.get('owner', '')} {self.data.get('phone', '')}"
        draw_text_mm(200, 75, info_ower)

        # Ligne 2 : Adresse / Ville
        draw_text_mm(200, 85, f"{self.data.get('id', 'N/A')}")

        # Ligne 3 : Numéro de police ou Code
        draw_text_mm(200, 95, periode)

        # Ligne 4 : Période de validité
        
        draw_text_mm(200, 105, marque_mod)

        # Ligne 5 : Marque et Modèle
        draw_text_mm(200, 115, f"{self.data.get('immatriculation', 'N/A')}")

        draw_text_mm(200, 125, f"{self.data.get('libele_tarif', '')}")

        # Ligne 7 : Catégorie
        draw_text_mm(200, 135, f"CAT {self.data.get('categorie', '')}")

        draw_text_mm(200, 145, marque_mod)

        draw_text_mm(200, 155, f"{self.data.get('immatriculation', 'N/A')}")