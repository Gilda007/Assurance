# devis_printer.py - Version avec logo AMS
import os
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
import math

try:
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderPDF
    HAS_GRAPHICS = True
except ImportError:
    HAS_GRAPHICS = False


class DevisPrinter:
    """Générateur et imprimeur de devis d'assurance - Version Premium"""
    
    def __init__(self, vehicle_data, export_dir=None):
        self.vehicle_data = vehicle_data
        self.export_dir = export_dir or os.path.expanduser("~/Documents/Devis_Assurance")
        
        # Créer le dossier d'export s'il n'existe pas
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Chemin du logo
        self.logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "logo.png")
        if not os.path.exists(self.logo_path):
            # Chemin alternatif
            self.logo_path = os.path.join(os.getcwd(), "addons", "Automobiles", "static", "logo.png")
        
        # Couleurs personnalisées
        self.colors = {
            'primary': colors.HexColor("#1e293b"),      # Bleu foncé
            'secondary': colors.HexColor("#3b82f6"),    # Bleu clair
            'accent': colors.HexColor("#f59e0b"),       # Orange
            'success': colors.HexColor("#10b981"),      # Vert
            'danger': colors.HexColor("#ef4444"),       # Rouge
            'text': colors.HexColor("#334155"),         # Gris foncé
            'text_light': colors.HexColor("#64748b"),   # Gris clair
            'border': colors.HexColor("#e2e8f0"),       # Bordure
            'background': colors.HexColor("#f8fafc"),   # Fond
            'white': colors.white,
        }
    
    def draw_header(self, c, width, height):
        """Dessine l'en-tête du devis"""
        # Rectangle de fond d'en-tête
        c.setFillColor(self.colors['background'])
        c.rect(0, height - 100, width, 100, fill=1, stroke=0)
        
        # Logo
        try:
            if os.path.exists(self.logo_path):
                logo = ImageReader(self.logo_path)
                # Redimensionner le logo
                c.drawImage(logo, 40, height - 85, width=50, height=50, mask='auto')
            else:
                # Fallback si le logo n'existe pas
                c.setFillColor(self.colors['secondary'])
                c.roundRect(40, height - 85, 50, 50, 10, fill=1, stroke=0)
                c.setFillColor(self.colors['white'])
                c.setFont("Helvetica-Bold", 20)
                c.drawString(55, height - 60, "A")
        except Exception as e:
            print(f"Erreur chargement logo: {e}")
            # Fallback
            c.setFillColor(self.colors['secondary'])
            c.roundRect(40, height - 85, 50, 50, 10, fill=1, stroke=0)
            c.setFillColor(self.colors['white'])
            c.setFont("Helvetica-Bold", 20)
            c.drawString(55, height - 60, "A")
        
        # Titre de l'entreprise
        c.setFillColor(self.colors['primary'])
        c.setFont("Helvetica-Bold", 22)
        c.drawString(105, height - 65, "AMS")
        c.setFont("Helvetica", 10)
        c.setFillColor(self.colors['text_light'])
        c.drawString(105, height - 80, "Assurances & Services")
        
        # Ligne décorative
        c.setStrokeColor(self.colors['secondary'])
        c.setLineWidth(3)
        c.line(40, height - 90, width - 40, height - 90)
        
        # Numéro de devis
        devis_num = f"DEV-{datetime.now().strftime('%Y%m%d')}-{self.vehicle_data.get('id', '001')}"
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.colors['text_light'])
        c.drawRightString(width - 40, height - 55, f"N° {devis_num}")
        
        # Date
        date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        c.setFont("Helvetica", 9)
        c.drawRightString(width - 40, height - 70, f"Date : {date_str}")
        c.drawCentredString(width - 40, height - 85, "DEVIS")
    
    def draw_info_card(self, c, x, y, width, height, title, items, icon="📄"):
        """Dessine une carte d'information stylisée"""
        # Fond de la carte
        c.setFillColor(self.colors['white'])
        c.roundRect(x, y, width, height, 12, fill=1, stroke=0)
        
        # Bordure
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(1)
        c.roundRect(x, y, width, height, 12, fill=0, stroke=1)
        
        # En-tête de la carte
        c.setFillColor(self.colors['secondary'])
        c.roundRect(x, y + height - 35, width, 35, 12, fill=1, stroke=0)
        c.roundRect(x, y + height - 35, width, 20, 12, fill=1, stroke=0)  # Cacher le bas
        
        # Titre
        c.setFillColor(self.colors['white'])
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 15, y + height - 22, f"{icon} {title}")
        
        # Lignes d'information
        c.setFillColor(self.colors['text'])
        c.setFont("Helvetica", 9)
        y_pos = y + height - 50
        
        for i, (label, value) in enumerate(items):
            if i >= 6:  # Limiter le nombre de lignes
                break
            c.setFillColor(self.colors['text_light'])
            c.drawString(x + 15, y_pos - i * 20, label)
            c.setFillColor(self.colors['text'])
            c.drawString(x + 130, y_pos - i * 20, str(value))
    
    def draw_garanties_table(self, c, x, y, width, garanties):
        """Dessine le tableau des garanties"""
        # Titre
        c.setFillColor(self.colors['primary'])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "📋 GARANTIES SOUSCRITES")
        
        # Ligne sous le titre
        c.setStrokeColor(self.colors['secondary'])
        c.setLineWidth(2)
        c.line(x, y - 5, x + width, y - 5)
        
        # En-têtes du tableau
        c.setFillColor(self.colors['secondary'])
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 15, y - 25, "Garantie")
        c.drawRightString(x + width - 15, y - 25, "Prime (FCFA)")
        
        # Ligne de séparation
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(0.5)
        c.line(x, y - 30, x + width, y - 30)
        
        # Remplir le tableau
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['text'])
        y_pos = y - 50
        
        total_brut = 0
        for name, active, amount in garanties:
            if active:
                c.drawString(x + 15, y_pos, name)
                c.drawRightString(x + width - 15, y_pos, f"{int(amount):,}".replace(",", " "))
                y_pos -= 20
                total_brut += amount
        
        # Total
        y_pos -= 10
        c.setStrokeColor(self.colors['border'])
        c.line(x, y_pos + 10, x + width, y_pos + 10)
        
        reduction = self.vehicle_data.get('réduction', 0)
        total_net = self.vehicle_data.get('prime_nette', 0)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 15, y_pos, "Total Brut")
        c.drawRightString(x + width - 15, y_pos, f"{int(total_brut):,}".replace(",", " "))
        y_pos -= 18
        
        if reduction > 0:
            c.setFillColor(self.colors['success'])
            c.drawString(x + 15, y_pos, "Réduction")
            c.drawRightString(x + width - 15, y_pos, f"- {int(reduction):,}".replace(",", " "))
            y_pos -= 18
        
        c.setFillColor(self.colors['secondary'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 15, y_pos, "Total Net à Payer")
        c.drawRightString(x + width - 15, y_pos, f"{int(total_net):,}".replace(",", " "))
        
        return y_pos - 20
    
    def draw_footer(self, c, width, height):
        """Dessine le pied de page"""
        # Rectangle de fond
        c.setFillColor(self.colors['background'])
        c.rect(0, 0, width, 60, fill=1, stroke=0)
        
        # Ligne décorative
        c.setStrokeColor(self.colors['secondary'])
        c.setLineWidth(2)
        c.line(40, 55, width - 40, 55)
        
        # Texte du pied de page
        c.setFillColor(self.colors['text_light'])
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, 40, "AMS ASSURANCES - Siège social : Yaoundé, Cameroun")
        c.drawCentredString(width / 2, 28, "Tel: +237 6XX XX XX XX | Email: contact@amsassurance.com | www.amsassurance.com")
        c.drawCentredString(width / 2, 16, "Ce devis est valable 30 jours à compter de sa date d'émission")
        
        # Numéro de page
        c.drawRightString(width - 40, 8, "Page 1/1")
    
    def generate_pdf(self, output_path):
        """Génère le PDF du devis avec design amélioré"""
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # ========== EN-TÊTE ==========
        self.draw_header(c, width, height)
        
        # ========== INFORMATIONS VÉHICULE ==========
        vehicle_items = [
            ("Immatriculation", self.vehicle_data.get('immatriculation', 'N/A')),
            ("Marque / Modèle", f"{self.vehicle_data.get('marque', 'N/A')} {self.vehicle_data.get('modele', 'N/A')}"),
            ("Châssis (VIN)", self.vehicle_data.get('chassis', 'N/A')),
            ("Année", self.vehicle_data.get('annee', 'N/A')),
            ("Puissance fiscale", f"{self.vehicle_data.get('usage', 'N/A')} CV"),
            ("Énergie", self.vehicle_data.get('energy', 'N/A')),
            ("Places", self.vehicle_data.get('places', 'N/A')),
            ("Zone", self.vehicle_data.get('zone', 'N/A')),
        ]
        self.draw_info_card(c, 40, height - 270, 230, 150, "INFORMATIONS VÉHICULE", vehicle_items, "🚗")
        
        # ========== INFORMATIONS PROPRIÉTAIRE ==========
        owner_items = [
            ("Nom complet", self.vehicle_data.get('owner', 'N/A')),
            ("Téléphone", self.vehicle_data.get('phone', 'N/A')),
            ("Email", self.vehicle_data.get('email', 'N/A')),
            ("Adresse", self.vehicle_data.get('city', 'N/A')),
        ]
        self.draw_info_card(c, 290, height - 270, 280, 150, "PROPRIÉTAIRE", owner_items, "👤")
        
        # ========== TABLEAU DES GARANTIES ==========
        garanties = [
            ("Responsabilité Civile", self.vehicle_data.get('check_rc', False), self.vehicle_data.get('amt_rc', 0)),
            ("Défense et Recours", self.vehicle_data.get('check_dr', False), self.vehicle_data.get('amt_dr', 0)),
            ("Vol du véhicule", self.vehicle_data.get('check_vol', False), self.vehicle_data.get('amt_vol', 0)),
            ("Vol à Main Armée", self.vehicle_data.get('check_vb', False), self.vehicle_data.get('amt_vb', 0)),
            ("Incendie", self.vehicle_data.get('check_in', False), self.vehicle_data.get('amt_in', 0)),
            ("Bris de Glaces", self.vehicle_data.get('check_bris', False), self.vehicle_data.get('amt_bris', 0)),
            ("Assistance Panne", self.vehicle_data.get('check_ar', False), self.vehicle_data.get('amt_ar', 0)),
            ("Dommages Tous Accidents", self.vehicle_data.get('check_dta', False), self.vehicle_data.get('amt_dta', 0)),
            ("Individuelle Chauffeur", self.vehicle_data.get('check_ipt', False), self.vehicle_data.get('amt_ipt', 0)),
        ]
        
        y = self.draw_garanties_table(c, 40, height - 340, width - 80, garanties)
        
        # ========== DÉTAIL DES FRAIS ==========
        prime_totale = self.vehicle_data.get('prime_totale', 0)
        carte_rose = self.vehicle_data.get('carte_rose', 0)
        accessoires = self.vehicle_data.get('accessoires', 0)
        tva = self.vehicle_data.get('tva', 0)
        asac = self.vehicle_data.get('fichier_asac', 0)
        vignette = self.vehicle_data.get('vignette', 0)
        pttc = self.vehicle_data.get('PTTC', 0)
        
        frais_items = [
            ("Prime nette", prime_totale),
            ("Carte rose", carte_rose),
            ("Accessoires", accessoires),
            ("TVA (19.25%)", tva),
            ("Fichier ASAC", asac),
            ("Vignette", vignette),
        ]
        
        # Filtrer les frais > 0
        frais_actifs = [(label, value) for label, value in frais_items if value > 0]
        
        if frais_actifs:
            # Titre
            c.setFillColor(self.colors['primary'])
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y - 20, "💰 DÉTAIL DES FRAIS")
            
            # Tableau des frais
            c.setFont("Helvetica", 9)
            c.setFillColor(self.colors['text'])
            y_pos = y - 45
            
            for label, value in frais_actifs:
                c.drawString(60, y_pos, label)
                c.drawRightString(width - 60, y_pos, f"{int(value):,}".replace(",", " "))
                y_pos -= 18
            
            # Total
            y_pos -= 10
            c.setStrokeColor(self.colors['border'])
            c.line(40, y_pos + 8, width - 40, y_pos + 8)
            
            c.setFillColor(self.colors['secondary'])
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y_pos - 10, "TOTAL TTC")
            c.drawRightString(width - 40, y_pos - 10, f"{int(pttc):,}".replace(",", " ") + " FCFA")
        
        # ========== PIED DE PAGE ==========
        self.draw_footer(c, width, height)
        
        c.save()
    
    def print(self, parent_widget=None):
        """Génère le PDF et propose l'impression ou la sauvegarde"""
        try:
            # Générer un nom de fichier
            immat = self.vehicle_data.get('immatriculation', 'vehicule')
            filename = f"devis_{immat}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.export_dir, filename)
            
            # Générer le PDF
            self.generate_pdf(pdf_path)
            
            # Demander à l'utilisateur
            reply = QMessageBox.question(
                parent_widget,
                "Devis généré",
                f"✅ Le devis a été généré avec succès !\n\n"
                f"📄 Fichier : {filename}\n"
                f"📁 Dossier : {self.export_dir}\n\n"
                f"Souhaitez-vous l'imprimer ou le sauvegarder ?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Save
            )
            
            if reply == QMessageBox.Yes:
                # Imprimer
                import subprocess
                import sys
                if sys.platform == "win32":
                    os.startfile(pdf_path, "print")
                else:
                    subprocess.run(["lp", pdf_path])
                QMessageBox.information(parent_widget, "Impression", "🖨️ Le devis a été envoyé à l'imprimante.")
                
            elif reply == QMessageBox.Save:
                # Sauvegarder ailleurs
                save_path, _ = QFileDialog.getSaveFileName(
                    parent_widget,
                    "Sauvegarder le devis",
                    filename,
                    "PDF Files (*.pdf)"
                )
                if save_path:
                    import shutil
                    shutil.copy(pdf_path, save_path)
                    QMessageBox.information(parent_widget, "Succès", "💾 Devis sauvegardé avec succès!")
            else:
                QMessageBox.information(
                    parent_widget, 
                    "Devis généré", 
                    f"📄 Le devis a été sauvegardé dans :\n{self.export_dir}"
                )
            
        except Exception as e:
            print(f"Erreur lors de la génération du devis : {str(e)}")
            import traceback
            traceback.print_exc()
            
            if parent_widget:
                QMessageBox.critical(
                    parent_widget,
                    "Erreur",
                    f"❌ Une erreur est survenue lors de la génération du devis :\n\n{str(e)}"
                )