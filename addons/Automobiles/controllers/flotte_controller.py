from socket import socket

import requests
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from addons.Automobiles.controllers.automobile_controller import VehicleController
from addons.Automobiles.models.automobile_models import AuditVehicleLog, Vehicle
from addons.Automobiles.models.contact_models import Contact
from addons.Automobiles.models.flottes_models import Fleet
from datetime import date, datetime, timezone
import json
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

class FleetController:
    def __init__(self, session: Session, current_user_id):
        self.session = session
        self.current_user_id = current_user_id

        self.vehicle_service = VehicleController(session)

    def create_fleet(self, data, user_id):
        """
        Crée une nouvelle flotte en incluant les totaux financiers 
        issus de la dernière ligne du tableau et gère l'audit.
        """
        try:
            # 1. Récupération des informations réseau pour l'audit
            local_ip, public_ip = self.get_network_info()

            # Fonction utilitaire pour sécuriser les montants (force le float)
            def to_f(key):
                val = data.get(key)
                try:
                    return float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    return 0.0

            # 2. Création de l'instance Fleet avec les nouveaux champs de totaux
            new_fleet = Fleet(
                nom_flotte=data.get('nom_flotte'),
                code_flotte=str(data.get('code_flotte', '')).strip().upper(),
                owner_id=data.get('owner_id'),
                assureur=data.get('assureur'),
                type_gestion=data.get('type_gestion'),
                remise_flotte=to_f('remise_flotte'),
                
                # --- NOUVEAUX CHAMPS : TOTAUX DES GARANTIES ---
                total_rc=to_f('total_rc'),
                total_dr=to_f('total_dr'),
                total_vol=to_f('total_vol'),
                total_vb=to_f('total_vb'),
                total_in=to_f('total_in'),
                total_bris=to_f('total_bris'),
                total_ar=to_f('total_ar'),
                total_dta=to_f('total_dta'),
                total_prime_nette=to_f('total_prime_nette'), # Cumul Col 11
                
                # Statut et Dates
                statut=data.get('statut', 'Actif'),
                is_active=data.get('is_active', True),
                date_debut=data.get('date_debut'),
                date_fin=data.get('date_fin'),
                observations=data.get('observations'),

                # Audit direct sur la ligne Fleet
                created_by=user_id,
                created_ip=public_ip,
                last_ip=local_ip
            )

            # 3. Pré-sauvegarde pour obtenir l'ID
            self.session.add(new_fleet)
            self.session.flush()

            # 4. Préparation des données pour le JSON d'Audit (Gestion des dates)
            serializable_data = data.copy()
            for key, value in serializable_data.items():
                if isinstance(value, (date, datetime)):
                    serializable_data[key] = value.isoformat()

            # 5. Création du Log d'Audit détaillé
            log = AuditVehicleLog(
                user_id=user_id,
                action="CREATION_FLOTTE_COMPLETE",
                module="FLEET_MANAGEMENT",
                item_id=new_fleet.id,
                old_values=None,
                new_values=json.dumps(serializable_data),
                ip_local=local_ip,
                ip_public=public_ip
            )
            self.session.add(log)
            
            # 6. Validation finale
            self.session.commit()
            return True, new_fleet.id

        except Exception as e:
            self.session.rollback()
            print(f"❌ Erreur SQL create_fleet: {e}")
            # Gestion d'erreur spécifique pour le code unique
            if "unique constraint" in str(e).lower():
                return False, f"Le code flotte '{data.get('code_flotte')}' est déjà utilisé."
            return False, str(e)

    def get_fleet_stats(self, fleet_id):
        """Récupère les indicateurs clés (KPI) pour le tableau de bord d'une flotte."""
        # Nombre de véhicules, somme des primes, etc.
        stats = self.session.query(
            func.count(Vehicle.id).label("total"),
            func.sum(Vehicle.prime_emise).label("prime_totale")
        ).filter(Vehicle.fleet_id == fleet_id).first()
        
        return {
            "total_vehicules": stats.total or 0,
            "prime_globale": stats.prime_totale or 0,
            # Vous pourrez ajouter ici le calcul des véhicules expirés
        }

    # --- GESTION DES VÉHICULES ---

    def add_vehicle_to_fleet(self, data):
        """Enregistre un véhicule avec ses données techniques et garanties."""
        try:
            # Conversion des données de garanties (dict) en colonnes si nécessaire
            new_vehicle = Vehicle(
                immatriculation=data['immatriculation'],
                fleet_id=data['fleet_id'],
                owner_id=data['owner_id'],
                marque=data['marque'],
                genre=data['genre'],
                poids=data['poids'],
                puissance=data['puissance'],
                val_neuf=data['val_neuf'],
                val_venale=data['val_venale'],
                prime_emise=data['prime_emise'],
                # Stockage des garanties (en colonnes booléennes ou JSON selon votre choix de modèle)
                rc=data['garanties']['rc'],
                tc=data['garanties']['tc'],
                vol=data['garanties']['vol'],
                bris=data['garanties']['bris'],
                dommages=data['garanties']['dommages'],
                individuelle=data['garanties']['individuelle'],
                dr=data['garanties']['dr']
            )
            self.session.add(new_vehicle)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False, str(e)

    # --- RÉCUPÉRATION DES DONNÉES POUR LES COMBOS ---

    def get_all_fleets_for_combo(self):
        try:
            return self.session.query(Fleet).order_by(Fleet.nom_flotte).all()
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return []

    def get_all_contacts_for_combo(self):
        """Retourne les contacts de nature physique depuis la table Contact."""
        try:
            # On récupère spécifiquement les colonnes ID et NOM
            compagnies = self.session.query(Contact.id, Contact.nom)\
                .filter(Contact.nature == "Physique")\
                .all()
            
            # Debug : affiche la liste brute pour vérification
            print(f"DEBUG Contacts : {compagnies}")
            
            # Correction de la compréhension de liste :
            # Puisque ce sont des tuples (id, nom), on les dépaquette directement
            return [(contact_id, contact_nom) for contact_id, contact_nom in compagnies]

        except Exception as e:
            print(f"Erreur lors de la récupération des contacts : {e}")
            return []

    def get_all_compagnies_for_combo(self):
        """
        Retourne la liste des compagnies d'assurance pour les combobox.
        Returns: Liste de tuples (id, nom)
        """
        try:
            # Récupérer toutes les compagnies depuis la table Compagnie
            from addons.Automobiles.models import Compagnie
            
            compagnies = self.session.query(Compagnie.id, Compagnie.nom).filter(
                Compagnie.is_active == True  # Optionnel: ne prendre que les compagnies actives
            ).all()
            
            # Debug : affiche la liste brute pour vérification
            print(f"DEBUG Compagnies : {compagnies}")
            
            # Retourner la liste des tuples (id, nom)
            return [(comp_id, comp_nom) for comp_id, comp_nom in compagnies]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des compagnies : {e}")
            import traceback
            traceback.print_exc()
            return []
    
    # --- DANS controllers/fleet_controller.py ---
    def get_all_fleets(self):
        try:
            # On utilise joinedload pour récupérer le nom du propriétaire en une seule fois
            from sqlalchemy.orm import joinedload
            return self.session.query(Fleet).options(joinedload(Fleet.owner)).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des flottes : {e}")
            return []
    
    def get_fleets_by_owner(self, owner_id):
        """Récupère les flottes avec le nom de la compagnie"""
        try:
            from addons.Automobiles.models import Fleet, Compagnie
            from sqlalchemy.orm import joinedload
            
            results = self.session.query(Fleet).filter(
                Fleet.owner_id == owner_id
            ).options(
                joinedload(Fleet.compagnie)  # Si la relation s'appelle 'compagnie'
            ).all()
            
            return results
        except Exception as e:
            print(f"Erreur: {e}")
            return []

    def get_fleet_with_details(self, fleet_id):
        """
        Récupère une flotte avec toutes ses relations chargées
        
        Args:
            fleet_id: ID de la flotte
        
        Returns:
            Objet Fleet ou None
        """
        try:
            from sqlalchemy.orm import joinedload
            
            fleet = self.session.query(Fleet).options(
                joinedload(Fleet.owner),
                joinedload(Fleet.vehicles)  # Si la relation existe
            ).filter(Fleet.id == fleet_id).first()
            
            return fleet
        except Exception as e:
            print(f"Erreur lors de la récupération de la flotte {fleet_id}: {e}")
        return None
        
    def update_status(self, fleet_id, is_active):
        try:
            fleet = self.session.query(Fleet).get(fleet_id)
            if fleet:
                fleet.is_active = is_active
                # On met aussi à jour le updated_by
                fleet.updated_by = self.current_user_id
                self.session.commit()
                return True
        except Exception as e:
            print(f"Erreur status: {e}")
            self.session.rollback()
            return False

    def get_all_vehicles(self):
        # On délègue le travail au service véhicule
        return self.vehicle_service.get_all_vehicles()

    def update_fleet_relation(self, fleet_id, selected_vehicle_ids, user_id, ip_local=None, ip_public=None):
        """Met à jour les véhicules appartenant à cette flotte."""
        try:
            # SÉCURITÉ : On s'assure que selected_vehicle_ids est une liste d'entiers
            # Si c'est un dictionnaire, on ne traite rien pour éviter le crash SQL
            if isinstance(selected_vehicle_ids, dict):
                print("ERREUR : Le contrôleur a reçu un dictionnaire au lieu d'une liste d'IDs")
                return False, "Données de véhicules invalides"

            # On convertit en liste d'entiers propre
            clean_ids = [i for i in selected_vehicle_ids if str(i).isdigit()]

            # 1. Détacher les véhicules qui étaient dans cette flotte mais ne sont plus sélectionnés
            self.session.query(Vehicle).filter(
                Vehicle.fleet_id == fleet_id,
                ~Vehicle.id.in_(clean_ids)
            ).update({"fleet_id": None}, synchronize_session=False)

            # 2. Attacher les nouveaux véhicules sélectionnés
            if clean_ids:
                self.session.query(Vehicle).filter(
                    Vehicle.id.in_(clean_ids)
                ).update({"fleet_id": fleet_id}, synchronize_session=False)

            audit = AuditVehicleLog(
                user_id=user_id,
                action="UPDATE_RELATION",
                module="FLEETS",
                item_id=fleet_id,
                new_values=json.dumps({"vehicle_ids": selected_vehicle_ids}), # Liste des IDs sélectionnés
                ip_local=ip_local,
                ip_public=ip_public,
                timestamp=datetime.now(timezone.utc)
            )
            self.session.add(audit)

            self.session.commit()
            return True, "Véhicules mis à jour"
        except Exception as e:
            self.session.rollback()
            print(f"Erreur SQL Relation : {e}")
            return False, str(e)
    
    def update_fleet_data(self, fleet_id, data, user_id):
        """
        Met à jour une flotte existante avec les totaux financiers et l'audit.
        """
        try:
            # 1. Récupération des informations réseau pour l'audit
            local_ip, public_ip = self.get_network_info()

            # Fonction utilitaire pour sécuriser les montants (force le float)
            def to_f(key):
                val = data.get(key)
                try:
                    return float(val) if val is not None and val != '' else 0.0
                except (ValueError, TypeError):
                    return 0.0

            # 2. Nettoyage du code flotte et de l'owner_id
            code_flotte = data.get('code_flotte')
            if isinstance(code_flotte, str):
                code_flotte = code_flotte.strip().upper()
                if not code_flotte:
                    code_flotte = None

            owner_id = data.get('owner_id')
            if isinstance(owner_id, str) and not owner_id.isdigit():
                owner_id = None

            # 3. Exécution de la mise à jour
            # On récupère d'abord l'ancienne version pour le log d'audit (optionnel mais recommandé)
            old_fleet = self.session.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not old_fleet:
                return False, "Flotte introuvable."

            # Mise à jour des champs
            self.session.query(Fleet).filter(Fleet.id == fleet_id).update({
                "nom_flotte": data.get('nom_flotte'),
                "code_flotte": code_flotte,
                "owner_id": owner_id,
                "assureur": data.get('assureur'),
                "type_gestion": data.get('type_gestion'),
                "remise_flotte": to_f('remise_flotte'),
                
                # --- NOUVEAUX CHAMPS FINANCIERS (MIS À JOUR) ---
                "total_rc": to_f('total_rc'),
                "total_dr": to_f('total_dr'),
                "total_vol": to_f('total_vol'),
                "total_vb": to_f('total_vb'),
                "total_in": to_f('total_in'),
                "total_bris": to_f('total_bris'),
                "total_ar": to_f('total_ar'),
                "total_dta": to_f('total_dta'),
                "total_prime_nette": to_f('total_prime_nette'),
                
                "statut": data.get('statut'),
                "is_active": data.get('is_active'),
                "date_debut": data.get('date_debut'),
                "date_fin": data.get('date_fin'),
                "observations": data.get('observations'),
                
                # Audit direct sur la table Fleet
                "updated_at": datetime.now(timezone.utc),
                "updated_by": user_id,
                "last_ip": local_ip
            }, synchronize_session=False)

            # 4. Création du Log d'Audit détaillé
            serializable_data = data.copy()
            for key, value in serializable_data.items():
                if isinstance(value, (date, datetime)):
                    serializable_data[key] = value.isoformat()

            audit_log = AuditVehicleLog(
                user_id=user_id,
                action="UPDATE_FLOTTE_COMPLETE",
                module="FLEET_MANAGEMENT",
                item_id=fleet_id,
                old_values=None, # On pourrait stocker old_fleet ici en JSON si besoin
                new_values=json.dumps(serializable_data),
                ip_local=local_ip,
                ip_public=public_ip
            )
            self.session.add(audit_log)

            self.session.commit()
            return True, "Flotte mise à jour avec succès."

        except Exception as e:
            self.session.rollback()
            print(f"❌ Erreur SQL update_fleet_data: {e}")
            if "unique constraint" in str(e).lower():
                return False, f"Le code flotte '{data.get('code_flotte')}' est déjà utilisé."
            return False, str(e)
        
    def get_network_info(self):
        """Récupère simultanément l'IP Locale et l'IP Publique."""
        # 1. IP Locale (Rapide)
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "127.0.0.1"

        # 2. IP Publique (Requête HTTP avec timeout court)
        try:
            # On utilise ipify avec un timeout de 1.5s pour ne pas bloquer l'UI
            response = requests.get('https://api.ipify.org?format=json', timeout=1.5)
            public_ip = response.json().get('ip')
        except:
            public_ip = "Offline"

        return local_ip, public_ip
    
    # ... (le reste de votre code actuel est correct pour gérer les IDs) ...
    def update_fleet_vehicles(self, fleet_id, selected_vehicle_ids, user_id):
        """
        Met à jour la relation entre une flotte et ses véhicules.
        """
        try:
            # --- SÉCURITÉ CRUCIALE ---
            # Si selected_vehicle_ids est un dictionnaire (erreur de vue), 
            # on ne fait rien pour éviter le crash SQL "InvalidTextRepresentation"
            if isinstance(selected_vehicle_ids, dict):
                print("ERREUR : Le contrôleur a reçu un dictionnaire au lieu d'une liste d'IDs.")
                return False, "Format de données invalide (attendu: liste d'IDs)."

            # Nettoyage de la liste pour s'assurer qu'on n'a que des entiers
            clean_ids = [int(i) for i in selected_vehicle_ids if str(i).isdigit() or isinstance(i, int)]

            # Récupération des infos réseau pour l'audit
            local_ip, public_ip = self.get_network_info()

            # --- 1. DÉTACHEMENT ---
            # On met à None le fleet_id de tous les véhicules qui pointaient sur cette flotte 
            # mais qui ne sont plus dans la nouvelle sélection.
            self.session.query(Vehicle).filter(
                Vehicle.fleet_id == fleet_id,
                ~Vehicle.id.in_(clean_ids)
            ).update({"fleet_id": None}, synchronize_session=False)

            # --- 2. ATTACHEMENT ---
            # On lie les véhicules de la nouvelle sélection à cette flotte
            if clean_ids:
                self.session.query(Vehicle).filter(
                    Vehicle.id.in_(clean_ids)
                ).update({"fleet_id": fleet_id}, synchronize_session=False)

            # --- 3. LOG D'AUDIT ---
            audit = AuditVehicleLog(
                user_id=user_id,
                action="UPDATE_RELATION_FLEET",
                module="FLEETS",
                item_id=fleet_id,
                # On stocke la liste des IDs sélectionnés pour l'historique
                new_values=json.dumps({"vehicle_ids": clean_ids}), 
                ip_local=local_ip,
                ip_public=public_ip,
                timestamp=datetime.now(timezone.utc)
            )
            self.session.add(audit)

            # --- 4. VALIDATION ---
            self.session.commit()
            return True, "Relation Flotte-Véhicules mise à jour avec succès."

        except Exception as e:
            self.session.rollback()
            print(f"Erreur Update Fleet Relation: {str(e)}")
            return False, f"Erreur base de données : {str(e)}"

    # RAPPORTS EN PDF DE CHAQUE FLOTTE

    def generate_fleet_pdf(self, fleet_id, output_path):
        """
        Génère un état de couverture PDF professionnel pour une flotte donnée.
        Inclut l'en-tête de l'agence, les infos flotte, la liste des véhicules
        et les totaux financiers cumulés.
        """
        try:
            # 1. Récupération des données (joinedload pour optimiser la requête)
            from sqlalchemy.orm import joinedload
            fleet = self.session.query(Fleet).options(
                joinedload(Fleet.owner),
                joinedload(Fleet.vehicles)
            ).filter(Fleet.id == fleet_id).first()

            if not fleet:
                return False, "Flotte introuvable en base de données."

            # 2. Configuration du document (Mode Paysage pour faire tenir toutes les colonnes)
            doc = SimpleDocTemplate(output_path, pagesize=landscape(A4), 
                                    rightMargin=1*cm, leftMargin=1*cm, 
                                    topMargin=1*cm, bottomMargin=1*cm)
            elements = []
            styles = getSampleStyleSheet()

            # --- 3. EN-TÊTE PROFESSIONNEL (Logo + Infos Agence) ---
            # Si vous avez un logo, décommentez les lignes suivantes :
            # logo_path = os.path.join(os.getcwd(), "assets", "logo_agence.png")
            # if os.path.exists(logo_path):
            #     im = Image(logo_path, width=4*cm, height=2*cm)
            #     im.hAlign = 'LEFT'
            #     elements.append(im)
            
            agency_style = ParagraphStyle('AgencyStyle', parent=styles['Normal'], fontSize=9, color=colors.grey)
            agency_info = Paragraph("VOTRE AGENCE D'ASSURANCES<br/>BP 1234, Douala - Cameroun<br/>Tél: (+237) 6xx xx xx xx", agency_style)
            elements.append(agency_info)
            elements.append(Spacer(1, 0.5*cm))

            # --- 4. TITRE DU DOCUMENT ET INFOS FLOTTE ---
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, fontSize=18, spaceAfter=20)
            elements.append(Paragraph(f"ÉTAT DE COUVERTURE FLOTTE : {fleet.nom_flotte.upper()}", title_style))
            
            # Grille d'informations Fleet (2 colonnes)
            info_data = [
                [Paragraph(f"<b>Code Flotte :</b> {fleet.code_flotte}", styles['Normal']),
                 Paragraph(f"<b>Période :</b> Du {fleet.date_debut.strftime('%d/%m/%Y')} au {fleet.date_fin.strftime('%d/%m/%Y')}", styles['Normal'])],
                [Paragraph(f"<b>Assureur :</b> {fleet.assureur or 'N/A'}", styles['Normal']),
                 Paragraph(f"<b>Souscripteur :</b> {fleet.owner.nom if fleet.owner else 'N/A'}", styles['Normal'])]
            ]
            info_table = Table(info_data, colWidths=[13*cm, 13*cm])
            info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
            elements.append(info_table)
            elements.append(Spacer(1, 1*cm))

            # --- 5. TABLEAU DES VÉHICULES (Corps du PDF) ---
            # En-têtes (Texte blanc sur fond gris foncé)
            headers = ["Immat.", "Marque", "R.Civile", "D.Recours", "TC", "Incendie", "Bris G.", "Dommages", "IPT", "PRIME NETTE"]
            data = [headers]

            # Audit interne des sommes (pour vérification)
            sum_prime = 0.0

            # Remplissage des lignes véhicules
            vehicle_row_style = ParagraphStyle('VehRow', parent=styles['Normal'], fontSize=8)
            num_v = 0
            
            # Tri des véhicules par immatriculation
            sorted_vehicles = sorted(fleet.vehicles, key=lambda x: x.immatriculation)

            for v in sorted_vehicles:
                num_v += 1
                # Formatage monétaire : 150 000 (sans virgule mais avec espace)
                def fmt(val):
                    f_val = float(val or 0.0)
                    return f"{f_val:,.0f}".replace(",", " ")

                line_total = float(v.prime_emise or 0.0)
                sum_prime += line_total

                data.append([
                    Paragraph(v.immatriculation, vehicle_row_style),
                    Paragraph(v.marque or "N/A", vehicle_row_style),
                    fmt(v.amt_rc),
                    fmt(v.amt_dr),
                    fmt(v.amt_vol), # Ou TC selon votre modèle
                    fmt(v.amt_vb),
                    fmt(v.amt_in),
                    fmt(v.amt_ar),
                    fmt(v.amt_dta),
                    fmt(v.amt_bris), # Dommages Tous Accidents
                    fmt(v.amt_ipt), # Individuelle Pilote
                    fmt(line_total) # Prime nette totale de la ligne
                ])

            # --- 6. LIGNE DE TOTALISATION (FOOTER DU TABLEAU) ---
            total_style = ParagraphStyle('TotalStyle', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
            
            def fmt_total(val):
                return f"{val:,.0f}".replace(",", " ")

            data.append([
                Paragraph(f"<b>TOTAL ({num_v} Véhs)</b>", total_style),
                "",
                fmt_total(fleet.total_rc),
                fmt_total(fleet.total_dr),
                fmt_total(fleet.total_vol),
                fmt_total(fleet.total_in),
                fmt_total(fleet.total_bris),
                fmt_total(fleet.total_dta),
                fmt_total(fleet.total_ar),
                fmt_total(fleet.total_prime_nette)
            ])

            # --- 7. STYLISATION DU TABLEAU (Le plus complexe) ---
            # Définition des largeurs de colonnes (total A4 Paysage utile approx 27.7cm)
            t = Table(data, colWidths=[2.5*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
            
            t_style = TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.2, 0.3)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                
                # Alignement du contenu
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),   # Immat/Marque gauche
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'), # Chiffres droite
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                
                # Ligne de totalisation (dernière ligne)
                ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
                ('ALIGN', (0, -1), (1, -1), 'LEFT'), # Label total gauche
                ('ALIGN', (2, -1), (-1, -1), 'RIGHT'), # Totaux droite
                ('SPAN', (0, -1), (1, -1)), # Fusion Immat + Marque pour le label total
                
                # Bordures
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ])
            t.setStyle(t_style)
            elements.append(t)
            
            # --- 8. BAS DE PAGE (Date d'impression et Audit) ---
            elements.append(Spacer(1, 1.5*cm))
            now = datetime.now()
            footer_data = [
                [Paragraph(f"Imprimé le : {now.strftime('%d/%m/%Y à %H:%M:%S')}", styles['Normal']),
                 Paragraph(f"Signature et Cachet de l'Agence : ______________________", styles['Normal'])]
            ]
            footer_table = Table(footer_data, colWidths=[10*cm, 16*cm])
            elements.append(footer_table)

            # --- 9. GÉNÉRATION FINALE DU PDF ---
            doc.build(elements)
            
            # Audit de cohérence (optionnel, écrit dans la console)
            # if abs(sum_prime - fleet.total_prime_nette) > 1:
            #     print(f"⚠️ Alerte Audit PDF Flotte {fleet_id}: La somme des véhicules ({sum_prime}) diffère du total enregistré ({fleet.total_prime_nette})")

            return True, f"PDF généré avec succès : {output_path}"

        except Exception as e:
            # Log détaillé de l'erreur pour la maintenance
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Erreur critique lors de la génération PDF : {e}\nDetails:\n{error_details}")
            return False, f"Erreur technique : {str(e)}"  