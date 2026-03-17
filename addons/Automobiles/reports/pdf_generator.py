import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_contact_pdf(filename, contacts, stats):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Titre
    elements.append(Paragraph("Rapport d'Activité - Gestion des Contacts", styles['Title']))
    elements.append(Spacer(1, 12))

    # Section Statistiques
    elements.append(Paragraph("Résumé du Portefeuille :", styles['Heading2']))
    stat_text = ", ".join([f"{k}: {v}" for k, v in stats.items()])
    elements.append(Paragraph(stat_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Tableau des Contacts
    data = [["Nom", "Prénom", "Téléphone", "Type"]] # En-tête
    for c in contacts:
        data.append([c.nom, c.prenom, c.telephone, c.type_contact])

    t = Table(data, colWidths=[150, 150, 100, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    
    elements.append(t)
    doc.build(elements)