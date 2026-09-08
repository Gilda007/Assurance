"""
Données initiales des référentiels LOMETA
À insérer en base de données via ReferentielService
"""
from datetime import datetime

REFERENTIELS_INITIAUX = {
    # ============================================================
    # FAM-01: Référentiels Sinistres
    # ============================================================
    
    "sinistres_types": [
        {"code": "AUTO", "libelle": "Automobile", "description": "Sinistres automobiles"},
        {"code": "RC", "libelle": "Responsabilité Civile", "description": "Sinistres RC"},
        {"code": "INCENDIE", "libelle": "Incendie", "description": "Sinistres incendie"},
        {"code": "TRANSPORT", "libelle": "Transport", "description": "Sinistres transport"},
        {"code": "SANTE", "libelle": "Santé", "description": "Sinistres santé"},
        {"code": "MULTIRISQUE", "libelle": "Multirisque", "description": "Sinistres multirisque"},
    ],
    
    "circonstances": [
        {"code": "COLLISION", "libelle": "Collision", "description": "Collision avec un autre véhicule"},
        {"code": "RENVERSEMENT", "libelle": "Renversement", "description": "Renversement du véhicule"},
        {"code": "STATIONNEMENT", "libelle": "Stationnement", "description": "Dommage en stationnement"},
        {"code": "FOUDRE", "libelle": "Foudre", "description": "Dommage causé par la foudre"},
        {"code": "COURT_CIRCUIT", "libelle": "Court-circuit", "description": "Incendie par court-circuit"},
        {"code": "AVARIE", "libelle": "Avarie", "description": "Avarie de marchandise"},
        {"code": "VOL", "libelle": "Vol", "description": "Vol du véhicule ou des marchandises"},
        {"code": "INCENDIE", "libelle": "Incendie", "description": "Incendie"},
        {"code": "DEGATS_EAU", "libelle": "Dégâts des eaux", "description": "Dégâts causés par l'eau"},
        {"code": "EXPLOSION", "libelle": "Explosion", "description": "Explosion"},
        {"code": "CATASTROPHE", "libelle": "Catastrophe naturelle", "description": "Catastrophe naturelle"},
    ],
    
    "responsabilites": [
        {"code": "RESP_100", "libelle": "Responsable 100%", "valeur": 1.0},
        {"code": "RESP_50", "libelle": "Partagé 50%", "valeur": 0.5},
        {"code": "RESP_0", "libelle": "Non responsable 0%", "valeur": 0.0},
        {"code": "RESP_25", "libelle": "Partagé 25%", "valeur": 0.25},
        {"code": "RESP_75", "libelle": "Partagé 75%", "valeur": 0.75},
        {"code": "RESP_33", "libelle": "Partagé 33%", "valeur": 0.33},
        {"code": "RESP_66", "libelle": "Partagé 66%", "valeur": 0.66},
    ],
    
    "dommages": [
        {"code": "MATERIEL", "libelle": "Dommage matériel", "description": "Dommage aux biens"},
        {"code": "CORPOREL", "libelle": "Dommage corporel", "description": "Dommage aux personnes"},
        {"code": "IMMATERIEL", "libelle": "Préjudice immatériel", "description": "Préjudice immatériel"},
        {"code": "MIXTE", "libelle": "Dommage mixte", "description": "Dommage matériel et corporel"},
    ],
    
    "qualite_chauffeur": [
        {"code": "SALARIE", "libelle": "Salarié", "description": "Conducteur salarié de l'entreprise"},
        {"code": "INDEPENDANT", "libelle": "Indépendant", "description": "Conducteur indépendant"},
        {"code": "PROFESSIONNEL", "libelle": "Chauffeur professionnel", "description": "Chauffeur professionnel"},
        {"code": "OCCASIONNEL", "libelle": "Conducteur occasionnel", "description": "Conducteur occasionnel"},
        {"code": "JEUNE_CONDUCTEUR", "libelle": "Jeune conducteur", "description": "Conducteur de moins de 25 ans"},
    ],
    
    "types_sinistre_auto": [
        {"code": "AUTO_MATERIEL", "libelle": "Auto matériel", "description": "Dommage matériel automobile"},
        {"code": "AUTO_CORPOREL", "libelle": "Auto corporel", "description": "Dommage corporel automobile"},
        {"code": "AUTO_BRIS_GLACE", "libelle": "Bris de glace", "description": "Bris de glace automobile"},
        {"code": "AUTO_VOL", "libelle": "Vol", "description": "Vol du véhicule"},
    ],
    
    "types_evaluation": [
        {"code": "AUTO_MATERIEL", "libelle": "Auto matériel", "description": "Évaluation auto matériel"},
        {"code": "AUTO_CORPOREL", "libelle": "Auto corporel", "description": "Évaluation auto corporel"},
        {"code": "INCENDIE", "libelle": "Incendie", "description": "Évaluation incendie"},
        {"code": "VOL", "libelle": "Vol", "description": "Évaluation vol"},
        {"code": "DEGATS_EAU", "libelle": "Dégâts des eaux", "description": "Évaluation dégâts des eaux"},
        {"code": "RC_GENERALE", "libelle": "RC Générale", "description": "Évaluation RC générale"},
        {"code": "DEFENSE_RECOURS", "libelle": "Défense Recours", "description": "Évaluation défense recours"},
        {"code": "TRANSPORT_MARCHANDISES", "libelle": "Marchandises", "description": "Évaluation transport marchandises"},
        {"code": "TRANSPORT_CONTENEURS", "libelle": "Conteneurs", "description": "Évaluation transport conteneurs"},
    ],
    
    # ============================================================
    # FAM-02: Référentiels Contractuels
    # ============================================================
    
    "branches": [
        {"code": "AUTO", "libelle": "Automobile", "description": "Branche automobile"},
        {"code": "RC", "libelle": "Responsabilité Civile", "description": "Branche RC"},
        {"code": "INCENDIE", "libelle": "Incendie", "description": "Branche incendie"},
        {"code": "TRANSPORT", "libelle": "Transport", "description": "Branche transport"},
        {"code": "SANTE", "libelle": "Santé", "description": "Branche santé"},
        {"code": "MULTIRISQUE", "libelle": "Multirisque", "description": "Branche multirisque"},
    ],
    
    "garanties": [
        {"code": "GAR_AUTO_RC", "libelle": "Auto - Responsabilité Civile", "description": "Garantie RC auto"},
        {"code": "GAR_AUTO_CD", "libelle": "Auto - Collision/Dommage", "description": "Garantie collision/dommage"},
        {"code": "GAR_AUTO_VOL", "libelle": "Auto - Vol", "description": "Garantie vol"},
        {"code": "GAR_AUTO_BRIS", "libelle": "Auto - Bris de glace", "description": "Garantie bris de glace"},
        {"code": "GAR_RC_GEN", "libelle": "RC - Générale", "description": "Garantie RC générale"},
        {"code": "GAR_RC_PRO", "libelle": "RC - Professionnelle", "description": "Garantie RC professionnelle"},
        {"code": "GAR_INCENDIE", "libelle": "Incendie", "description": "Garantie incendie"},
        {"code": "GAR_TRANSPORT", "libelle": "Transport", "description": "Garantie transport"},
    ],
    
    # ============================================================
    # FAM-03: Référentiels Intervenants
    # ============================================================
    
    "types_experts": [
        {"code": "AUTO", "libelle": "Expert automobile", "description": "Expertise automobile"},
        {"code": "BATIMENT", "libelle": "Expert bâtiment", "description": "Expertise bâtiment"},
        {"code": "TRANSPORT", "libelle": "Expert transport", "description": "Expertise transport"},
        {"code": "MEDICAL", "libelle": "Expert médical", "description": "Expertise médicale"},
        {"code": "JUDICIAIRE", "libelle": "Expert judiciaire", "description": "Expertise judiciaire"},
        {"code": "CONTENANT", "libelle": "Expert contenant", "description": "Expertise contenant"},
        {"code": "MARCHANDISE", "libelle": "Expert marchandise", "description": "Expertise marchandise"},
    ],
    
    "types_avocats": [
        {"code": "CONTENTIEUX", "libelle": "Avocat contentieux", "description": "Avocat spécialisé en contentieux"},
        {"code": "RECOURS", "libelle": "Avocat recours", "description": "Avocat spécialisé en recours"},
        {"code": "CONSULTATION", "libelle": "Avocat conseil", "description": "Avocat conseil"},
        {"code": "MEDIATEUR", "libelle": "Médiateur", "description": "Médiateur"},
    ],
    
    "types_prestataires": [
        {"code": "GARAGE", "libelle": "Garage", "description": "Garage automobile"},
        {"code": "HOPITAL", "libelle": "Hôpital", "description": "Établissement hospitalier"},
        {"code": "CLINIQUE", "libelle": "Clinique", "description": "Clinique médicale"},
        {"code": "REPARATEUR", "libelle": "Réparateur", "description": "Réparateur"},
        {"code": "HUISSIER", "libelle": "Huissier", "description": "Huissier de justice"},
    ],
    
    # ============================================================
    # FAM-04: Référentiels Administratifs
    # ============================================================
    
    "pays": [
        {"code": "CM", "libelle": "Cameroun", "description": "République du Cameroun"},
        {"code": "FR", "libelle": "France", "description": "République Française"},
        {"code": "BE", "libelle": "Belgique", "description": "Royaume de Belgique"},
        {"code": "CH", "libelle": "Suisse", "description": "Confédération Suisse"},
        {"code": "SN", "libelle": "Sénégal", "description": "République du Sénégal"},
        {"code": "CI", "libelle": "Côte d'Ivoire", "description": "République de Côte d'Ivoire"},
    ],
    
    "devises": [
        {"code": "XAF", "libelle": "Franc CFA (CEMAC)", "valeur": 1.0},
        {"code": "EUR", "libelle": "Euro", "valeur": 655.96},
        {"code": "USD", "libelle": "Dollar US", "valeur": 600.00},
        {"code": "GBP", "libelle": "Livre Sterling", "valeur": 750.00},
    ],
    
    "types_documents": [
        {"code": "DECLARATION", "libelle": "Déclaration", "description": "Déclaration de sinistre"},
        {"code": "CONSTAT", "libelle": "Constat", "description": "Constat amiable"},
        {"code": "PV", "libelle": "Procès-verbal", "description": "Procès-verbal"},
        {"code": "PHOTO", "libelle": "Photo", "description": "Photo du sinistre"},
        {"code": "RAPPORT", "libelle": "Rapport", "description": "Rapport d'expertise"},
        {"code": "DEVIS", "libelle": "Devis", "description": "Devis de réparation"},
        {"code": "FACTURE", "libelle": "Facture", "description": "Facture"},
        {"code": "CHEQUE", "libelle": "Chèque", "description": "Chèque"},
        {"code": "BORDEREAU", "libelle": "Bordereau", "description": "Bordereau de paiement"},
        {"code": "COURRIER", "libelle": "Courrier", "description": "Courrier"},
        {"code": "JUGEMENT", "libelle": "Jugement", "description": "Jugement"},
        {"code": "ASSIGNATION", "libelle": "Assignation", "description": "Assignation"},
    ],
    
    # ============================================================
    # FAM-05: Référentiels Financiers
    # ============================================================
    
    "modes_paiement": [
        {"code": "CHEQUE", "libelle": "Chèque", "description": "Paiement par chèque"},
        {"code": "VIREMENT", "libelle": "Virement bancaire", "description": "Paiement par virement"},
        {"code": "MOBILE_MONEY", "libelle": "Mobile Money", "description": "Paiement par Mobile Money"},
        {"code": "COMPENSATION", "libelle": "Compensation", "description": "Paiement par compensation"},
    ],
    
    "modes_encaissement": [
        {"code": "VIREMENT", "libelle": "Virement", "description": "Encaissement par virement"},
        {"code": "CHEQUE", "libelle": "Chèque", "description": "Encaissement par chèque"},
        {"code": "MOBILE_MONEY", "libelle": "Mobile Money", "description": "Encaissement par Mobile Money"},
        {"code": "COMPENSATION", "libelle": "Compensation", "description": "Encaissement par compensation"},
    ],
    
    "operateurs_mobile": [
        {"code": "ORANGE", "libelle": "Orange Money", "description": "Opérateur Orange"},
        {"code": "MTN", "libelle": "MTN Mobile Money", "description": "Opérateur MTN"},
        {"code": "NEXTTEL", "libelle": "Nexttel Money", "description": "Opérateur Nexttel"},
        {"code": "CAMTEL", "libelle": "CAMTEL", "description": "Opérateur CAMTEL"},
    ],
    
    "types_beneficiaires": [
        {"code": "ASSURE", "libelle": "Assuré", "description": "Bénéficiaire assuré"},
        {"code": "TIERS", "libelle": "Tiers", "description": "Bénéficiaire tiers"},
        {"code": "EXPERT", "libelle": "Expert", "description": "Bénéficiaire expert"},
        {"code": "GARAGE", "libelle": "Garage", "description": "Bénéficiaire garage"},
        {"code": "AVOCAT", "libelle": "Avocat", "description": "Bénéficiaire avocat"},
        {"code": "HUISSIER", "libelle": "Huissier", "description": "Bénéficiaire huissier"},
        {"code": "HOPITAL", "libelle": "Hôpital", "description": "Bénéficiaire hôpital"},
        {"code": "COASSUREUR", "libelle": "Coassureur", "description": "Bénéficiaire coassureur"},
        {"code": "REASSUREUR", "libelle": "Réassureur", "description": "Bénéficiaire réassureur"},
    ],
    
    "journaux_comptables": [
        {"code": "BANQUE", "libelle": "Journal Banque", "description": "Mouvements bancaires"},
        {"code": "SINISTRES", "libelle": "Journal Sinistres", "description": "Opérations sinistres"},
        {"code": "RECOURS", "libelle": "Journal Recours", "description": "Opérations recours"},
        {"code": "REGULARISATION", "libelle": "Journal Régularisations", "description": "Opérations de régularisation"},
        {"code": "TRESORERIE", "libelle": "Journal Trésorerie", "description": "Opérations de trésorerie"},
    ],
    
    # ============================================================
    # FAM-06: Référentiels Workflow
    # ============================================================
    
    "statuts_sinistre": [
        {"code": "OUVERT", "libelle": "Ouvert", "description": "Dossier créé"},
        {"code": "EN_INSTRUCTION", "libelle": "En instruction", "description": "En cours d'analyse"},
        {"code": "EN_EXPERTISE", "libelle": "En expertise", "description": "Mission expert en cours"},
        {"code": "EN_EVALUATION", "libelle": "En évaluation", "description": "Calcul des montants"},
        {"code": "VALIDE", "libelle": "Validé", "description": "Évaluation validée"},
        {"code": "EN_REGLEMENT", "libelle": "En règlement", "description": "Paiement en cours"},
        {"code": "EN_RECOURS", "libelle": "En recours", "description": "Recours en cours"},
        {"code": "CLOTURE", "libelle": "Clôturé", "description": "Dossier clôturé"},
        {"code": "REOUVERT", "libelle": "Réouvert", "description": "Dossier réouvert"},
    ],
    
    "transitions_workflow": [
        {"code": "OUVERT->EN_INSTRUCTION", "libelle": "Passer en instruction", "description": "Début de l'instruction"},
        {"code": "EN_INSTRUCTION->EN_EXPERTISE", "libelle": "Lancer expertise", "description": "Lancer une mission d'expertise"},
        {"code": "EN_INSTRUCTION->EN_EVALUATION", "libelle": "Passer en évaluation", "description": "Début de l'évaluation"},
        {"code": "EN_EXPERTISE->EN_EVALUATION", "libelle": "Expertise terminée", "description": "Fin de l'expertise"},
        {"code": "EN_EVALUATION->VALIDE", "libelle": "Valider évaluation", "description": "Validation de l'évaluation"},
        {"code": "VALIDE->EN_REGLEMENT", "libelle": "Lancer règlement", "description": "Début du règlement"},
        {"code": "EN_REGLEMENT->EN_RECOURS", "libelle": "Ouvrir recours", "description": "Ouverture d'un recours"},
        {"code": "EN_RECOURS->EN_REGLEMENT", "libelle": "Retour au règlement", "description": "Fin du recours"},
        {"code": "CLOTURE->REOUVERT", "libelle": "Réouvrir dossier", "description": "Réouverture du dossier"},
    ],
    
    "statuts_expertise": [
        {"code": "CREEE", "libelle": "Créée", "description": "Mission créée"},
        {"code": "AFFECTEE", "libelle": "Affectée", "description": "Expert affecté"},
        {"code": "EN_COURS", "libelle": "En cours", "description": "Expertise en cours"},
        {"code": "RAPPORT_REÇU", "libelle": "Rapport reçu", "description": "Rapport reçu"},
        {"code": "VALIDE", "libelle": "Validé", "description": "Expertise validée"},
        {"code": "ANNULE", "libelle": "Annulé", "description": "Mission annulée"},
    ],
    
    "statuts_reglement": [
        {"code": "CREE", "libelle": "Créé", "description": "Règlement créé"},
        {"code": "VALIDE", "libelle": "Validé", "description": "Règlement validé"},
        {"code": "EN_ATTENTE", "libelle": "En attente", "description": "Règlement en attente"},
        {"code": "TRAITE", "libelle": "Traité", "description": "Règlement traité"},
        {"code": "PAYE", "libelle": "Payé", "description": "Règlement payé"},
        {"code": "ANNULE", "libelle": "Annulé", "description": "Règlement annulé"},
        {"code": "REJETE", "libelle": "Rejeté", "description": "Règlement rejeté"},
    ],
    
    "statuts_recours": [
        {"code": "OUVERT", "libelle": "Ouvert", "description": "Recours ouvert"},
        {"code": "EN_INSTRUCTION", "libelle": "En instruction", "description": "Recours en instruction"},
        {"code": "RELANCE", "libelle": "Relancé", "description": "Recours relancé"},
        {"code": "CONTESTE", "libelle": "Contesté", "description": "Recours contesté"},
        {"code": "REFUSE", "libelle": "Refusé", "description": "Recours refusé"},
        {"code": "ABOUTI", "libelle": "Abouti", "description": "Recours abouti"},
        {"code": "EN_ATTENTE_ENCAISSEMENT", "libelle": "En attente encaissement", "description": "En attente d'encaissement"},
        {"code": "PARTIELLEMENT_ENCAISSE", "libelle": "Partiellement encaissé", "description": "Partiellement encaissé"},
        {"code": "ENCAISSE", "libelle": "Encaissé", "description": "Recours encaissé"},
        {"code": "REVERSEMENT_EN_COURS", "libelle": "Reversement en cours", "description": "Reversement en cours"},
        {"code": "PAYE", "libelle": "Payé", "description": "Reversement payé"},
        {"code": "COMPTABILISE", "libelle": "Comptabilisé", "description": "Comptabilisé"},
        {"code": "CLOTURE", "libelle": "Clôturé", "description": "Recours clôturé"},
    ],
    
    "suites_a_donner": [
        {"code": "ATTENTE_CLIENT", "libelle": "Attente client", "description": "En attente d'information client", "valeur": 7},
        {"code": "ATTENTE_EXPERT", "libelle": "Attente expert", "description": "En attente du rapport expert", "valeur": 14},
        {"code": "ATTENTE_REGLEMENT", "libelle": "Attente règlement", "description": "En attente de validation paiement", "valeur": 3},
        {"code": "ETUDE_TECHNIQUE", "libelle": "Étude technique", "description": "Étude technique en cours", "valeur": 5},
        {"code": "RELANCE_CLIENT", "libelle": "Relance client", "description": "À relancer le client", "valeur": 3},
        {"code": "RELANCE_EXPERT", "libelle": "Relance expert", "description": "À relancer l'expert", "valeur": 5},
        {"code": "RELANCE_AVOCAT", "libelle": "Relance avocat", "description": "À relancer l'avocat", "valeur": 5},
        {"code": "RELANCE_COMPTABLE", "libelle": "Relance comptable", "description": "À relancer la comptabilité", "valeur": 2},
        {"code": "RELANCE_BANQUE", "libelle": "Relance banque", "description": "À relancer la banque", "valeur": 3},
        {"code": "ATTENTE_PIECES", "libelle": "Attente pièces", "description": "En attente de pièces justificatives", "valeur": 7},
        {"code": "ATTENTE_REPONSE", "libelle": "Attente réponse", "description": "En attente d'une réponse", "valeur": 5},
    ],
    
    "actions_commerciales": [
        {"code": "VISITE", "libelle": "Visite client", "description": "Visite à domicile"},
        {"code": "APPEL", "libelle": "Appel téléphonique", "description": "Appel client"},
        {"code": "PROPOSITION", "libelle": "Proposition", "description": "Proposition commerciale"},
        {"code": "REVISION_CONTRAT", "libelle": "Révision contrat", "description": "Proposition de révision de contrat"},
        {"code": "ACCOMPAGNEMENT", "libelle": "Accompagnement", "description": "Accompagnement après sinistre"},
    ],
    
    # ============================================================
    # FAM-07: Référentiels CRM
    # ============================================================
    
    "origines_rappels": [
        {"code": "PRODUCTION", "libelle": "Production", "description": "Rappel lié à la production"},
        {"code": "SINISTRES", "libelle": "Sinistres", "description": "Rappel lié aux sinistres"},
        {"code": "COMPTABILITE", "libelle": "Comptabilité", "description": "Rappel lié à la comptabilité"},
        {"code": "GENERAL", "libelle": "Général", "description": "Rappel général"},
        {"code": "EXPERTISE", "libelle": "Expertise", "description": "Rappel lié à l'expertise"},
        {"code": "RECOURS", "libelle": "Recours", "description": "Rappel lié aux recours"},
        {"code": "CONTENTIEUX", "libelle": "Contentieux", "description": "Rappel lié au contentieux"},
        {"code": "VALIDATION", "libelle": "Validation", "description": "Rappel lié aux validations"},
    ],
    
    "types_relances": [
        {"code": "COURRIER", "libelle": "Courrier", "description": "Relance par courrier"},
        {"code": "EMAIL", "libelle": "Email", "description": "Relance par email"},
        {"code": "TELEPHONE", "libelle": "Téléphone", "description": "Relance par téléphone"},
        {"code": "SMS", "libelle": "SMS", "description": "Relance par SMS"},
        {"code": "WHATSAPP", "libelle": "WhatsApp", "description": "Relance par WhatsApp"},
    ],
    
    "priorites": [
        {"code": "BASSE", "libelle": "Basse", "valeur": 0},
        {"code": "NORMALE", "libelle": "Normale", "valeur": 1},
        {"code": "HAUTE", "libelle": "Haute", "valeur": 2},
        {"code": "URGENTE", "libelle": "Urgente", "valeur": 3},
        {"code": "CRITIQUE", "libelle": "Critique", "valeur": 4},
    ],
}