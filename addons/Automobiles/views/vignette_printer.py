# vignette_printer.py

from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt, QCoreApplication
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from datetime import datetime

class VignettePrinter:
    def __init__(self, vehicle_data, export_dir=None):
        """
        Initialise l'imprimeur de vignette.
        
        Args:
            vehicle_data (dict): Données du véhicule
            export_dir (str, optional): Dossier d'export par défaut
        """
        self.data = vehicle_data
        self.width, self.height = A4
        self.export_dir = export_dir or os.path.join(os.path.expanduser("~"), "Documents", "Attestations_Assurance")
        
    def print(self, parent_widget=None):
        """
        Affiche la boîte de dialogue pour sauvegarder le PDF.
        
        Args:
            parent_widget (QWidget, optional): Widget parent pour les dialogues
        """
        # Créer le nom de fichier par défaut
        immat = self.data.get('immatriculation', 'vehicule').replace(' ', '_')
        default_filename = f"attestation_timbre_{immat}_{datetime.now().strftime('%Y%m%d')}.pdf"
        default_path = os.path.join(self.export_dir, default_filename)
        
        # Boîte de dialogue pour choisir l'emplacement
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Enregistrer l'attestation de timbre",
            default_path,
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return  # L'utilisateur a annulé
        
        try:
            # Afficher une progression
            progress = QProgressDialog("Génération du document...", "Annuler", 0, 100, parent_widget)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(500)
            progress.setValue(10)
            QCoreApplication.processEvents()
            
            # Générer le PDF
            self.generate_pdf(file_path, progress)
            
            progress.setValue(100)
            progress.close()
            
            # Confirmation
            QMessageBox.information(
                parent_widget,
                "Succès",
                f"L'attestation de timbre a été générée avec succès !\n\n"
                f"Fichier : {os.path.basename(file_path)}\n"
                f"Emplacement : {os.path.dirname(file_path)}"
            )
            
            # Option pour ouvrir le dossier
            reply = QMessageBox.question(
                parent_widget,
                "Ouvrir le dossier ?",
                "Voulez-vous ouvrir le dossier contenant le fichier ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                import subprocess
                import platform
                
                file_dir = os.path.dirname(file_path)
                if platform.system() == 'Windows':
                    os.startfile(file_dir)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.Popen(['open', file_dir])
                else:  # Linux
                    subprocess.Popen(['xdg-open', file_dir])
                    
        except Exception as e:
            if progress:
                progress.close()
            QMessageBox.critical(
                parent_widget,
                "Erreur de génération",
                f"Erreur lors de la génération du PDF :\n\n{str(e)}"
            )
            raise
    
    def generate_pdf(self, file_path, progress=None):
        """Génère le PDF avec ReportLab"""
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            topMargin=15*mm,
            bottomMargin=15*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )
        
        if progress:
            progress.setValue(20)
            QCoreApplication.processEvents()
        
        # Styles personnalisés
        styles = self.create_styles()
        
        # Construction du document
        story = []
        
        # 1. Titre "Automobile"
        story.append(Paragraph("Automobile", styles['AutoTitle']))
        
        # 2. Contrat n°
        story.append(Paragraph("Contrat n° 377A010009", styles['Contract']))
        
        # 3. Ligne de séparation
        story.append(Spacer(1, 2))
        
        if progress:
            progress.setValue(30)
            QCoreApplication.processEvents()
        
        # 4. Section Assureur
        story.append(Paragraph("AMS INSURANCES", styles['Assureur']))
        story.append(Paragraph("MINDZIE BALIABA P/C HAMBEN P/C", styles['AssureurInfo']))
        story.append(Paragraph("AMS INSURANCE", styles['AssureurInfo']))
        story.append(Paragraph("BP : 4962 Douala", styles['AssureurInfo']))
        story.append(Paragraph("BP YAOUNDE", styles['AssureurInfo']))
        story.append(Paragraph("Code: 356", styles['AssureurInfo']))
        
        story.append(Spacer(1, 8))
        
        # 5. Titre de l'attestation
        story.append(Paragraph("Attestation de paiement du Droit de Timbre Automobile", styles['Title']))
        
        story.append(Spacer(1, 6))
        
        if progress:
            progress.setValue(40)
            QCoreApplication.processEvents()
        
        # 6. Période de validité
        date_debut = self.format_date(self.data.get('date_debut', ''))
        date_fin = self.format_date(self.data.get('date_fin', ''))
        validity_text = f"La présente attestation est valable du {date_debut} AU {date_fin}"
        story.append(Paragraph(validity_text, styles['Validity']))
        
        story.append(Spacer(1, 6))
        
        # 7. Montant du timbre
        story.append(Paragraph("Le montant du droit de timbre automobile acquitté est de :", styles['MontantTitre']))
        
        montant = self.data.get('reduction', )
        if isinstance(montant, str):
            try:
                montant = float(montant)
            except:
                montant = 0
        
        montant_text = f"{montant} FCFA".replace(",", " ")
        story.append(Paragraph(montant_text, styles['Montant']))
        
        story.append(Spacer(1, 12))
        
        if progress:
            progress.setValue(50)
            QCoreApplication.processEvents()
        
        # 8. Titre section véhicule
        story.append(Paragraph("Véhicule assuré", styles['VehiculeTitle']))
        
        # 9. Tableau des informations véhicule
        data_table = self.create_vehicle_table()
        
        # Création du tableau
        table = Table(data_table, colWidths=[45*mm, 35*mm, 45*mm, 35*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        
        # Mettre en gras les valeurs
        for i in range(len(data_table)):
            table.setStyle(TableStyle([
                ('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'),
                ('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'),
            ]))
        
        story.append(table)
        
        story.append(Spacer(1, 16))
        
        if progress:
            progress.setValue(70)
            QCoreApplication.processEvents()
        
        # 10. Pied de page
        story.append(Spacer(1, 8))
        
        # Ligne de séparation
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        
        story.append(Spacer(1, 8))
        
        # Texte du pied
        story.append(Paragraph("AMS ASSURANCES - Agrément n° 2025/001/MINFI", styles['Footer']))
        story.append(Paragraph("Siège social : Douala - Cameroun | Tél : (+237) 233 42 42 42", styles['Footer']))
        story.append(Paragraph("Document authentifié par signature électronique", styles['Footer']))
        
        story.append(Spacer(1, 12))
        
        # Date et signature
        today = datetime.now().strftime("%d/%m/%Y")
        
        signature_data = [
            ["", ""],
            [f"Fait à Yaoundé, le {today}", "Pour AMS ASSURANCES"],
            ["", "Le Directeur Général"],
            ["", "_________________________"]
        ]
        
        signature_table = Table(signature_data, colWidths=[100*mm, 70*mm])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
            ('ALIGN', (1, 2), (1, 2), 'RIGHT'),
            ('ALIGN', (1, 3), (1, 3), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(signature_table)
        
        if progress:
            progress.setValue(90)
            QCoreApplication.processEvents()
        
        # Génération du PDF
        doc.build(story)
        
        if progress:
            progress.setValue(100)
            QCoreApplication.processEvents()
    
    def create_styles(self):
        """Crée les styles personnalisés pour le document"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'AutoTitle': ParagraphStyle(
                'AutoTitle',
                parent=styles['Heading1'],
                fontSize=24,
                fontName='Helvetica-Bold',
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=6
            ),
            'Contract': ParagraphStyle(
                'Contract',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica',
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=12
            ),
            'Assureur': ParagraphStyle(
                'Assureur',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=4
            ),
            'AssureurInfo': ParagraphStyle(
                'AssureurInfo',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                textColor=colors.black,
                alignment=TA_LEFT,
                leading=12
            ),
            'Title': ParagraphStyle(
                'Title',
                parent=styles['Normal'],
                fontSize=11,
                fontName='Helvetica-Bold',
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=12,
                spaceBefore=8
            ),
            'Validity': ParagraphStyle(
                'Validity',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold',
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=12
            ),
            'MontantTitre': ParagraphStyle(
                'MontantTitre',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold',
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=6
            ),
            'Montant': ParagraphStyle(
                'Montant',
                parent=styles['Normal'],
                fontSize=14,
                fontName='Helvetica-Bold',
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=16
            ),
            'VehiculeTitle': ParagraphStyle(
                'VehiculeTitle',
                parent=styles['Normal'],
                fontSize=11,
                fontName='Helvetica-Bold',
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=6,
                spaceBefore=12
            ),
            'Footer': ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=7,
                fontName='Helvetica',
                textColor=colors.grey,
                alignment=TA_CENTER,
                leading=10
            )
        }
        
        return custom_styles
    
    def create_vehicle_table(self):
        """Crée le tableau des informations du véhicule"""
        return [
            ["Marque :", self.data.get('marque', '').upper(), "Modele :", self.data.get('modele', '').upper()],
            ["Immatriculation :", self.data.get('immatriculation', '').upper(), 
             "Date de 1ère mise en circulation :", self.format_date(self.data.get('date_premiere_mise_circulation', self.data.get('date_debut', '')))],
            ["Énergie :", self.data.get('energy', self.data.get('energie', '')).upper(), 
             "Puissance :", f"{self.data.get('usage', '')}"],
            ["Nbre Places :", str(self.data.get('places', '')), 
             "Zone de circulation :", self.data.get('zone', '')],
            ["Usage :", self.data.get('categorie', '')], 
            ["Type :", self.data.get('type_vehicule', '')],
            ["Genre :", self.data.get('genre', '')], 
            ["Carrosserie :", self.data.get('carrosserie', '')]
        ]
    
    def format_date(self, date):
        """Formate une date au format JJ/MM/AAAA"""
        if date and date != 'N/A' and date != '':
            try:
                if hasattr(date, 'strftime'):
                    return date.strftime("%d/%m/%Y")
                return str(date)
            except:
                return str(date)
        return "01/01/2026"