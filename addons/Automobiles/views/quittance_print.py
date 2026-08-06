# addons/Automobiles/reports/quitance_generator.py
import os
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PySide6.QtCore import Qt, QThread, Signal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.fonts import addMapping
import tempfile


class QuitanceGenerator:
    """Générateur de quitance (conditions particulières)"""
    
    def __init__(self, contract_data, vehicle_data, owner_data, company_data):
        """
        Args:
            contract_data: Données du contrat
            vehicle_data: Données du véhicule
            owner_data: Données du propriétaire/souscripteur
            company_data: Données de la compagnie
        """
        self.contract = contract_data
        self.vehicle = vehicle_data
        self.owner = owner_data
        self.company = company_data
    
    def generate(self, output_path=None):
        """Génère le PDF de la quitance"""
        if output_path is None:
            output_path = os.path.join(
                tempfile.gettempdir(),
                f"quitance_{self.contract.get('numero_police', 'temp')}.pdf"
            )
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        styles = getSampleStyleSheet()
        
        # Styles personnalisés
        style_title = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        style_section = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
        
        style_normal = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=4
        )
        
        style_cell = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT
        )
        
        style_center = ParagraphStyle(
            'CenterStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        )
        
        style_right = ParagraphStyle(
            'RightStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT
        )
        
        elements = []
        
        # === 1. EN-TÊTE ===
        header_data = [
            [Paragraph("AGENCE YAOUNDÉ", style_title),
             Paragraph("405 AMS INSURANCES", style_title),
             Paragraph("Apporteur:", style_normal),
             Paragraph("TH", style_normal)],
            ["Adresse: BP 1011 DLA", "", "Fax:", "AMS"],
            ["Téléphone:", "", "Durée:", "365 Jours"]
        ]
        
        header_table = Table(header_data, colWidths=[4*cm, 4*cm, 3*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10*mm))
        
        # === 2. DATES DU CONTRAT ===
        date_debut = self.contract.get('date_debut', datetime.now())
        date_fin = self.contract.get('date_fin', datetime.now())
        
        date_data = [
            [Paragraph("Date d'effet", style_normal),
             Paragraph(date_debut.strftime("%d/%m/%Y 00:00") if date_debut else "", style_normal),
             Paragraph("Date d'expiration", style_normal),
             Paragraph(date_fin.strftime("%d/%m/%Y 00:00") if date_fin else "", style_normal),
             Paragraph("Contrat Sans Tacite Reconduction", style_normal)]
        ]
        
        date_table = Table(date_data, colWidths=[3*cm, 4*cm, 3*cm, 4*cm, 5*cm])
        date_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(date_table)
        elements.append(Spacer(1, 10*mm))
        
        # === 3. SOUSCRIPTEUR ET ASSURÉ ===
        owner_name = f"{self.owner.get('nom', '')} {self.owner.get('prenom', '')}".strip()
        owner_address = self.owner.get('adresse', 'BP YAOUNDÉ')
        client_code = self.owner.get('code_client', 'A00029')
        
        client_data = [
            ["Nom et Prénom", Paragraph(owner_name or "—", style_cell), "", ""],
            ["Adresse", Paragraph(owner_address or "—", style_cell), "", ""],
            ["Activité", Paragraph("-", style_cell), "", ""],
            ["N° Client", Paragraph(client_code or "—", style_cell), "", ""],
            ["Nom et Prénom", Paragraph(owner_name or "—", style_cell), "", ""],
            ["Adresse", Paragraph(owner_address or "—", style_cell), "", ""],
        ]
        
        client_table = Table(client_data, colWidths=[3*cm, 6*cm, 3*cm, 6*cm])
        client_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (2, 0), (3, 0)),  # Fusion des cellules pour le nom
            ('SPAN', (2, 1), (3, 1)),  # Fusion pour l'adresse
            ('SPAN', (2, 2), (3, 2)),  # Fusion pour l'activité
            ('SPAN', (2, 3), (3, 3)),  # Fusion pour N° Client
            ('SPAN', (0, 4), (1, 4)),  # Fusion pour le nom
            ('SPAN', (2, 4), (3, 4)),  # Fusion pour le nom
            ('SPAN', (0, 5), (1, 5)),  # Fusion pour l'adresse
            ('SPAN', (2, 5), (3, 5)),  # Fusion pour l'adresse
        ]))
        elements.append(client_table)
        elements.append(Spacer(1, 10*mm))
        
        # === 4. CARACTÉRISTIQUES DU VÉHICULE ===
        vehicle_data_table = [
            ["Caractéristiques", Paragraph("VEHICULE", style_cell), "", ""],
            ["Usage", Paragraph(self.vehicle.get('usage', 'CAT 01'), style_cell), 
             Paragraph(f"{self.vehicle.get('immatriculation', 'LT 840 FQ')}", style_cell),
             Paragraph(f"M.E.C. le: {self.vehicle.get('date_mise_circulation', '24/07/2015')}", style_cell)],
            ["Nbre Places", Paragraph(str(self.vehicle.get('places', 7)), style_cell), "", ""],
            ["Nbre de personnes", Paragraph("0", style_cell), "", ""],
            ["Nbre de places", Paragraph("0", style_cell), "", ""],
            ["Nbre de places", Paragraph("0", style_cell), "", ""],
        ]
        
        vehicle_table = Table(vehicle_data_table, colWidths=[3*cm, 4*cm, 3*cm, 4*cm])
        vehicle_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (1, 0)),  # Fusion pour "Caractéristiques"
            ('SPAN', (2, 0), (3, 0)),  # Fusion pour "VEHICULE"
        ]))
        elements.append(vehicle_table)
        elements.append(Spacer(1, 10*mm))
        
        # === 5. GARANTIES ===
        guarantees = self.contract.get('guarantees', [])
        if not guarantees:
            guarantees = [
                {"name": "RESPONSABILITE CIVILE", "franchise": "", "capital": "ILLIMITE", 
                 "taux": "117 764", "reduction": "0,10", "prime": "105 988"},
                {"name": "DEFENSE RECOURS", "franchise": "", "capital": "", 
                 "taux": "2 000", "reduction": "", "prime": "2 000"},
                {"name": "INDIVIDUELLE PERSONNES TRANSPORTEES", "franchise": "", "capital": "", 
                 "taux": "2 000", "reduction": "", "prime": "10 000"},
            ]
        
        guarantee_headers = ["Garanties", "Franchise", "Capital", "Taux", "Reduction", "Prime Période"]
        guarantee_data = [guarantee_headers]
        
        for g in guarantees:
            guarantee_data.append([
                Paragraph(g.get('name', ''), style_cell),
                Paragraph(g.get('franchise', ''), style_cell),
                Paragraph(str(g.get('capital', '')), style_cell),
                Paragraph(str(g.get('taux', '')), style_cell),
                Paragraph(str(g.get('reduction', '')), style_cell),
                Paragraph(str(g.get('prime', '')), style_cell)
            ])
        
        # Ajouter les garanties optionnelles (Décès, Invalidité, Frais)
        if self.contract.get('has_deces'):
            guarantee_data.append([
                "Deces Accidentel", "", "1 000 000", "", "", ""
            ])
        if self.contract.get('has_invalidite'):
            guarantee_data.append([
                "Invalide Permanente", "", "1 000 000", "", "", ""
            ])
        if self.contract.get('has_frais_traitement'):
            guarantee_data.append([
                "Frais de Traitement", "", "100 000", "", "", ""
            ])
        
        guarantee_table = Table(guarantee_data, colWidths=[4*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm, 2.5*cm])
        guarantee_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        elements.append(guarantee_table)
        elements.append(Spacer(1, 10*mm))
        
        # === 6. RÉCAPITULATIF FINANCIER ===
        prime_nette = self.contract.get('prime_nette', 117988)
        accessoires = self.contract.get('accessoires', 2500)
        asac = self.contract.get('asac', 1000)
        tva = self.contract.get('tva', 23386)
        carte_rose = self.contract.get('carte_rose', 1000)
        vignette = self.contract.get('vignette', 50000)
        prime_totale = prime_nette + accessoires + asac + tva + carte_rose + vignette
        
        financial_headers = ["Prime Nette", "Accessoires", "ASAC", "TVA", "Carte Rose", "Vignette", "Prime Totale"]
        financial_data = [
            financial_headers,
            [
                f"{prime_nette:,.0f}".replace(",", " "),
                f"{accessoires:,.0f}".replace(",", " "),
                f"{asac:,.0f}".replace(",", " "),
                f"{tva:,.0f}".replace(",", " "),
                f"{carte_rose:,.0f}".replace(",", " "),
                f"{vignette:,.0f}".replace(",", " "),
                f"{prime_totale:,.0f}".replace(",", " ")
            ]
        ]
        
        financial_table = Table(financial_data, colWidths=[2.5*cm]*7)
        financial_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        elements.append(financial_table)
        elements.append(Spacer(1, 10*mm))
        
        # === 7. PIED DE PAGE ===
        footer_data = [
            ["Contrat Produit par TH", "Charge de clientèle: TH", "", "", ""],
            ["", "", "", "", ""],
            ["Fait à Yaoundé en 03 Exemplaires le", "", "", datetime.now().strftime("%d/%m/%Y"), ""],
            ["Pour L'Assuré", "", "", "Pour La compagnie", ""]
        ]
        
        footer_table = Table(footer_data, colWidths=[4*cm, 2*cm, 2*cm, 4*cm, 4*cm])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (1, 0)),  # Fusion pour "Contrat Produit par TH"
            ('SPAN', (2, 0), (3, 0)),  # Fusion pour "Charge de clientèle: TH"
            ('SPAN', (0, 2), (2, 2)),  # Fusion pour "Fait à Yaoundé"
        ]))
        elements.append(footer_table)
        
        # Construire le document
        doc.build(elements)
        return output_path