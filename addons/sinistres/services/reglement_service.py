"""
Service de gestion des règlements (Tome 5 du CDC)
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService, func
from addons.sinistres.models.reglement import (
    LometaBeneficiaire, LometaCompteBancaire, LometaReglement, LometaLotPaiement, LometaNoteCredit
)
from addons.sinistres.models.sinistre import LometaSinistre, LometaTiers
from addons.sinistres.models.expertise import LometaEvaluation


class ReglementService(BaseService):
    """Service de gestion des règlements"""
    SEUIL_RESPONSABLE = 1_000_000      # 1M FCFA
    SEUIL_DIRECTION = 5_000_000        # 5M FCFA
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # GESTION DES BÉNÉFICIAIRES
    # ============================================================
    
    def creer_beneficiaire(self, data: Dict[str, Any]) -> LometaBeneficiaire:
        """Crée un nouveau bénéficiaire"""
        try:
            beneficiaire = LometaBeneficiaire(**data)
            self.session.add(beneficiaire)
            self.session.commit()
            return beneficiaire
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_beneficiaire(self, beneficiaire_id: int) -> Optional[LometaBeneficiaire]:
        """Récupère un bénéficiaire par son ID"""
        try:
            return self.session.query(LometaBeneficiaire).filter(
                LometaBeneficiaire.id == beneficiaire_id,
                LometaBeneficiaire.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e

    # def get_beneficiaires(
    #     self,
    #     type_beneficiaire: str = None,
    #     inclure_experts: bool = True,
    # ) -> List[Dict[str, Any]]:
    #     """
    #     Récupère tous les bénéficiaires possibles pour un règlement.
        
    #     Fusionne deux sources dans un format normalisé :
    #     - LometaTiers    (assurés, conducteurs, victimes, témoins…)
    #     - LometaExpert   (experts)
        
    #     Args:
    #         type_beneficiaire : Filtre
    #             - None             → tout
    #             - 'TIERS'          → tous les tiers
    #             - 'EXPERT'         → tous les experts
    #             - 'ASSURE', 'GARAGE', 'AVOCAT', ...  → filtre sur type_tiers
        
    #     Returns:
    #         Liste de dicts normalisés, triés par nom_complet.
    #     """
    #     try:
    #         resultats: List[Dict[str, Any]] = []
            
    #         # ============================================================
    #         # 1. TIERS (sauf si on demande uniquement EXPERT)
    #         # ============================================================
    #         if type_beneficiaire != 'EXPERT':
    #             query_tiers = self.session.query(LometaTiers).filter(
    #                 LometaTiers.is_active == True
    #             )
                
    #             # Filtrer par type_tiers si demandé
    #             if type_beneficiaire and type_beneficiaire not in ('TIERS', 'EXPERT'):
    #                 query_tiers = query_tiers.filter(
    #                     LometaTiers.type_tiers == type_beneficiaire
    #                 )
                
    #             tiers = query_tiers.order_by(LometaTiers.nom).all()
                
    #             for t in tiers:
    #                 resultats.append(self._serialize_tiers(t))
            
    #         # ============================================================
    #         # 2. EXPERTS (sauf si on demande uniquement TIERS)
    #         # ============================================================
    #         if inclure_experts and type_beneficiaire in (None, 'EXPERT', 'TIERS'):
    #             try:
    #                 from addons.sinistres.models.expertise import LometaExpert
                    
    #                 query_experts = self.session.query(LometaExpert).filter(
    #                     LometaExpert.is_active == True,
    #                     LometaExpert.est_actif == True,
    #                 )
                    
    #                 experts = query_experts.order_by(LometaExpert.nom).all()
                    
    #                 for e in experts:
    #                     resultats.append(self._serialize_expert(e))
                
    #             except ImportError:
    #                 print("⚠️ LometaExpert non importable")
    #             except Exception as e:
    #                 print(f"⚠️ Erreur chargement experts : {e}")
            
    #         # ============================================================
    #         # 3. Trier par nom complet
    #         # ============================================================
    #         resultats.sort(key=lambda x: x['nom_complet'].lower())
            
    #         return resultats
        
    #     except Exception as e:
    #         self.session.rollback()
    #         raise e

    def get_beneficiaires(
        self,
        type_beneficiaire: str = None,
        inclure_tiers: bool = True,
        inclure_experts: bool = True,
        inclure_beneficiaires: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Récupère TOUS les bénéficiaires possibles pour un règlement.
        
        Fusionne TROIS sources dans un format normalisé :
        - LometaBeneficiaire (déjà enregistrés)
        - LometaTiers        (assurés, conducteurs, victimes…)
        - LometaExpert      (experts)
        
        Args:
            type_beneficiaire : Filtre optionnel
                - None      → tout
                - 'BENEFICIAIRE' → uniquement LometaBeneficiaire
                - 'TIERS'        → uniquement les tiers
                - 'EXPERT'       → uniquement les experts
                - 'ASSURE', 'GARAGE', ... → filtre sur type_beneficiaire
        
        Returns:
            Liste de dicts normalisés avec 'source' et 'is_beneficiaire'.
        """
        try:
            resultats: List[Dict[str, Any]] = []
            
            # ============================================================
            # 1. LometaBeneficiaire (déjà enregistrés)
            # ============================================================
            if inclure_beneficiaires and type_beneficiaire in (None, 'BENEFICIAIRE'):
                query_benefs = self.session.query(LometaBeneficiaire).filter(
                    LometaBeneficiaire.is_active == True
                )
                
                if type_beneficiaire and type_beneficiaire not in (
                    'BENEFICIAIRE', 'TIERS', 'EXPERT'
                ):
                    query_benefs = query_benefs.filter(
                        LometaBeneficiaire.type_beneficiaire == type_beneficiaire
                    )
                
                benefs = query_benefs.order_by(LometaBeneficiaire.nom).all()
                
                for b in benefs:
                    resultats.append(self._serialize_beneficiaire(b))
            
            # ============================================================
            # 2. LometaTiers
            # ============================================================
            if inclure_tiers and type_beneficiaire != 'BENEFICIAIRE':
                query_tiers = self.session.query(LometaTiers).filter(
                    LometaTiers.is_active == True
                )
                
                if type_beneficiaire and type_beneficiaire not in (
                    'BENEFICIAIRE', 'TIERS', 'EXPERT'
                ):
                    query_tiers = query_tiers.filter(
                        LometaTiers.type_tiers == type_beneficiaire
                    )
                
                tiers = query_tiers.order_by(LometaTiers.nom).all()
                
                for t in tiers:
                    resultats.append(self._serialize_tiers(t))
            
            # ============================================================
            # 3. LometaExpert
            # ============================================================
            if inclure_experts and type_beneficiaire != 'BENEFICIAIRE':
                try:
                    from addons.sinistres.models.expertise import LometaExpert
                    
                    query_experts = self.session.query(LometaExpert).filter(
                        LometaExpert.is_active == True,
                        LometaExpert.est_actif == True,
                    )
                    
                    experts = query_experts.order_by(LometaExpert.nom).all()
                    
                    for e in experts:
                        resultats.append(self._serialize_expert(e))
                
                except ImportError:
                    print("⚠️ LometaExpert non importable")
                except Exception as e:
                    print(f"⚠️ Erreur chargement experts : {e}")
            
            # ============================================================
            # 4. Trier par nom complet
            # ============================================================
            resultats.sort(key=lambda x: x['nom_complet'].lower())
            
            return resultats
        
        except Exception as e:
            self.session.rollback()
            raise e

    def _serialize_tiers(self, t) -> Dict[str, Any]:
        """Normalise un LometaTiers en dict bénéficiaire."""
        nom = (getattr(t, 'nom', '') or '').strip()
        prenom = (getattr(t, 'prenom', '') or '').strip()
        
        return {
            'id': t.id,
            'source': 'TIERS',
            'type_beneficiaire': getattr(t, 'type_tiers', None) or 'AUTRE',
            'is_beneficiaire': False,
            'code': getattr(t, 'code_tiers', None),
            'nom': nom,
            'prenom': prenom or None,
            'nom_complet': f"{nom} {prenom}".strip() or "Sans nom",
            'civilite': getattr(t, 'civilite', None),
            'telephone': getattr(t, 'telephone', None),
            'email': getattr(t, 'email', None),
            'adresse': getattr(t, 'adresse', None),
            'ville': getattr(t, 'ville', None),
            'code_postal': getattr(t, 'code_postal', None),
            'pays': getattr(t, 'pays', None),
            # Champs spécifiques tiers
            'assurance': getattr(t, 'assurance', None),
            'police_assurance': getattr(t, 'police_assurance', None),
            # Pas d'IBAN pour les tiers
            'iban': None,
            # Activation : LometaTiers utilise is_active (mixin)
            'est_actif': getattr(t, 'is_active', True),
        }

    def _serialize_beneficiaire(self, b) -> Dict[str, Any]:
        """Normalise un LometaBeneficiaire."""
        nom = (getattr(b, 'nom', '') or '').strip()
        prenom = (getattr(b, 'prenom', '') or '').strip()
        
        return {
            'id': b.id,
            'source': 'BENEFICIAIRE',
            'is_beneficiaire': True,   # ✅ déjà un bénéficiaire
            'type_beneficiaire': getattr(b, 'type_beneficiaire', None) or 'AUTRE',
            'code': getattr(b, 'code', None),
            'nom': nom,
            'prenom': prenom or None,
            'nom_complet': f"{nom} {prenom}".strip() or "Sans nom",
            'civilite': getattr(b, 'civilite', None),
            'telephone': getattr(b, 'telephone', None),
            'email': getattr(b, 'email', None),
            'adresse': getattr(b, 'adresse', None),
            'ville': getattr(b, 'ville', None),
            'code_postal': getattr(b, 'code_postal', None),
            'pays': getattr(b, 'pays', None),
            'iban': getattr(b, 'iban', None),
            'banque': getattr(b, 'banque', None),
            'rib': getattr(b, 'rib', None),
            'est_actif': getattr(b, 'est_actif', True),
        }

    def _serialize_expert(self, e) -> Dict[str, Any]:
        """Normalise un LometaExpert en dict bénéficiaire."""
        nom = (getattr(e, 'nom', '') or '').strip()
        prenom = (getattr(e, 'prenom', '') or '').strip()
        
        return {
            'id': e.id,
            'source': 'EXPERT',
            'type_beneficiaire': 'EXPERT',
            'is_beneficiaire': False,
            'code': getattr(e, 'code', None),
            'nom': nom,
            'prenom': prenom or None,
            'nom_complet': f"{nom} {prenom}".strip() or "Sans nom",
            'civilite': getattr(e, 'civilite', None),
            'telephone': getattr(e, 'telephone', None),
            'portable': getattr(e, 'portable', None),
            'email': getattr(e, 'email', None),
            'adresse': getattr(e, 'adresse', None),
            'ville': getattr(e, 'ville', None),
            'code_postal': getattr(e, 'code_postal', None),
            'pays': getattr(e, 'pays', None),
            # Champs spécifiques expert
            'agrement': getattr(e, 'agrement', None),
            'domaines': getattr(e, 'domaines', None) or [],
            'zones': getattr(e, 'zones', None) or [],
            # Pas d'IBAN
            'iban': None,
            # Activation : LometaExpert utilise est_actif
            'est_actif': getattr(e, 'est_actif', True),
        }
    
    # ============================================================
    # GESTION DES RÈGLEMENTS
    # ============================================================

    def resolve_beneficiaire_id(
        self,
        source: str,
        source_id: int,
        source_data: Dict[str, Any],
        utilisateur_id: int = None,
    ) -> int:
        """
        Résout l'ID du LometaBeneficiaire à utiliser pour un règlement.
        
        ⚠️ IMPORTANT : la résolution se fait par IDENTITÉ MÉTIER (nom + prénom + téléphone),
        JAMAIS par comparaison d'ID entre tables différentes.
        
        Logique :
        - source == 'BENEFICIAIRE' :
            L'ID vient de lometa_beneficiaires → on le retourne tel quel
        
        - source == 'TIERS' ou 'EXPERT' :
            1. On ignore source_id (il vient d'une autre table)
            2. On cherche dans lometa_beneficiaires un enregistrement
            correspondant à (nom + prénom + téléphone)
            3. Si trouvé → on retourne son ID
            4. Si non trouvé → on crée un nouveau LometaBeneficiaire
        
        Args:
            source       : 'BENEFICIAIRE' | 'TIERS' | 'EXPERT'
            source_id    : ID dans la table source (info seulement)
            source_data  : dict normalisé (nom, prenom, telephone, email, adresse…)
            utilisateur_id : ID utilisateur pour created_by
        
        Returns:
            ID du LometaBeneficiaire à utiliser.
        
        Raises:
            ValueError: si la source est inconnue ou si les données sont invalides.
        """
        source = (source or 'BENEFICIAIRE').upper()
        
        # ============================================================
        # CAS 1 : BENEFICIAIRE → ID direct
        # ============================================================
        if source == 'BENEFICIAIRE':
            beneficiaire = self.session.query(LometaBeneficiaire).filter(
                LometaBeneficiaire.id == source_id,
                LometaBeneficiaire.is_active == True
            ).first()
            
            if not beneficiaire:
                raise ValueError(
                    f"Bénéficiaire (ID={source_id}) non trouvé dans lometa_beneficiaires"
                )
            
            print(f"✅ Bénéficiaire direct utilisé : ID={source_id}")
            return beneficiaire.id
        
        # ============================================================
        # CAS 2 : TIERS ou EXPERT → résolution par identité
        # ============================================================
        if source not in ('TIERS', 'EXPERT'):
            raise ValueError(
                f"Source inconnue : '{source}'. "
                f"Valeurs attendues : BENEFICIAIRE, TIERS, EXPERT"
            )
        
        # ─── Extraire les données d'identité ───
        nom = (source_data.get('nom') or '').strip()
        prenom = (source_data.get('prenom') or '').strip()
        telephone = (
            source_data.get('telephone')
            or source_data.get('portable')
            or ''
        ).strip()
        email = (source_data.get('email') or '').strip()
        
        if not nom:
            raise ValueError(
                f"Impossible de résoudre un bénéficiaire sans nom "
                f"(source={source}, source_id={source_id})"
            )
        
        # ─── 2.1 Chercher par identité métier ───
        existing = self._find_beneficiaire_by_identity(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
        )
        
        if existing:
            print(f"✅ Bénéficiaire existant trouvé par identité : "
                f"ID={existing.id} ({nom} {prenom} - {telephone})")
            return existing.id
        
        # ─── 2.2 Créer un nouveau bénéficiaire ───
        print(f"➕ Création d'un bénéficiaire pour {source} : "
            f"{nom} {prenom} - {telephone}")
        
        # Déterminer le type_beneficiaire
        type_beneficiaire = (
            source_data.get('type_beneficiaire')
            or ('EXPERT' if source == 'EXPERT' else 'AUTRE')
        )
        
        nouveau = LometaBeneficiaire(
            type_beneficiaire=type_beneficiaire,
            nom=nom,
            prenom=prenom or None,
            telephone=telephone or None,
            email=email or None,
            adresse=source_data.get('adresse'),
            ville=source_data.get('ville'),
            code_postal=source_data.get('code_postal'),
            pays=source_data.get('pays'),
            is_active=True,
            est_actif=True,
            created_by=utilisateur_id,
        )
        
        self.session.add(nouveau)
        self.session.flush()
        
        print(f"✅ Bénéficiaire créé : ID={nouveau.id}")
        
        # ─── Audit ───
        self.log_audit(
            utilisateur_id=utilisateur_id,
            action="CREATION",
            entite="Beneficiaire",
            entite_id=nouveau.id,
            entite_nom=f"{nom} {prenom}".strip(),
            commentaire=(
                f"Bénéficiaire créé automatiquement depuis {source} "
                f"(source_id={source_id}, type={type_beneficiaire})"
            )
        )
        
        return nouveau.id
    
    def _find_beneficiaire_by_identity(
        self,
        nom: str,
        prenom: str = '',
        telephone: str = '',
        email: str = '',
    ) -> Optional[LometaBeneficiaire]:
        """
        Cherche un LometaBeneficiaire par identité métier.
        
        Priorité des critères :
        1. nom + prenom + telephone (si téléphone fourni) → critère fort
        2. nom + prenom + email (si email fourni) → critère moyen
        3. nom + prenom (fallback) → critère faible
        
        La comparaison est insensible à la casse, aux espaces et à la ponctuation.
        
        Args:
            nom       : Nom (obligatoire)
            prenom    : Prénom (optionnel)
            telephone : Téléphone (optionnel, fortement recommandé)
            email     : Email (optionnel)
        
        Returns:
            LometaBeneficiaire trouvé ou None.
        """
        try:
            # ─── Normaliser ───
            nom_clean = (nom or '').strip().lower()
            prenom_clean = (prenom or '').strip().lower()
            tel_clean = (telephone or '').strip()
            email_clean = (email or '').strip().lower()
            
            if not nom_clean:
                return None
            
            # ─── Base de la requête ───
            base_query = self.session.query(LometaBeneficiaire).filter(
                LometaBeneficiaire.is_active == True,
                func.lower(func.trim(LometaBeneficiaire.nom)) == nom_clean,
            )
            
            # Prénom
            if prenom_clean:
                base_query = base_query.filter(
                    func.lower(func.trim(LometaBeneficiaire.prenom)) == prenom_clean
                )
            else:
                base_query = base_query.filter(
                    (LometaBeneficiaire.prenom == None)
                    | (func.trim(LometaBeneficiaire.prenom) == '')
                )
            
            # ─── Priorité 1 : téléphone ───
            if tel_clean:
                tel_norm = (
                    tel_clean
                    .replace(' ', '')
                    .replace('-', '')
                    .replace('.', '')
                    .replace('+', '')
                    .replace('(', '')
                    .replace(')', '')
                )
                
                if len(tel_norm) >= 9:
                    # Comparer sur les 9 derniers chiffres (tolérance formats)
                    tel_suffix = tel_norm[-9:]
                    
                    result = base_query.filter(
                        func.replace(
                            func.replace(
                                func.replace(
                                    func.replace(
                                        func.coalesce(
                                            LometaBeneficiaire.telephone, ''
                                        ),
                                        ' ', ''
                                    ),
                                    '-', ''
                                ),
                                '+', ''
                            ),
                            '.', ''
                        ).like(f'%{tel_suffix}')
                    ).first()
                    
                    if result:
                        return result
            
            # ─── Priorité 2 : email ───
            if email_clean:
                result = base_query.filter(
                    func.lower(func.trim(
                        func.coalesce(LometaBeneficiaire.email, '')
                    )) == email_clean
                ).first()
                
                if result:
                    return result
            
            # ─── Priorité 3 : fallback nom + prenom (uniquement si aucun autre critère) ───
            if not tel_clean and not email_clean:
                return base_query.first()
            
            return None
        
        except Exception as e:
            print(f"⚠️ Erreur recherche bénéficiaire par identité : {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # def creer_reglement(self, data: Dict[str, Any]) -> LometaReglement:
    #     """
    #     Crée une demande de règlement avec contrôles CDC.
        
    #     Accepte :
    #     - beneficiaire_id       : ID dans la table source
    #     - beneficiaire_source   : 'BENEFICIAIRE' | 'TIERS' | 'EXPERT'
    #     - beneficiaire_nom      : nom d'affichage (optionnel)
        
    #     La méthode résout automatiquement l'ID du LometaBeneficiaire à utiliser :
    #     - Si déjà bénéficiaire → utilise l'ID direct
    #     - Si tiers/expert → cherche ou crée un LometaBeneficiaire
    #     """
    #     try:
    #         # ============================================================
    #         # 1. Vérifier le sinistre
    #         # ============================================================
    #         sinistre = self.session.query(LometaSinistre).filter(
    #             LometaSinistre.id == data.get('sinistre_id'),
    #             LometaSinistre.is_active == True
    #         ).first()
    #         if not sinistre:
    #             raise ValueError("Sinistre non trouvé")
            
    #         # ============================================================
    #         # 2. Vérifier l'évaluation (REG-002 / FIN-100)
    #         # ============================================================
    #         evaluation = None
    #         if data.get('evaluation_id'):
    #             evaluation = self.session.query(LometaEvaluation).filter(
    #                 LometaEvaluation.id == data.get('evaluation_id'),
    #                 LometaEvaluation.is_active == True
    #             ).first()
                
    #             if not evaluation:
    #                 raise ValueError("Évaluation non trouvée")
                
    #             if not evaluation.est_validee:
    #                 raise ValueError(
    #                     "L'évaluation doit être validée avant tout règlement "
    #                     "(REG-002 / FIN-100)"
    #                 )
            
    #         # ============================================================
    #         # 3. ✅ RÉSOUDRE LE BÉNÉFICIAIRE
    #         # ============================================================
    #         beneficiaire_source = data.get('beneficiaire_source', 'BENEFICIAIRE')
    #         beneficiaire_source_id = data.get('beneficiaire_id')
            
    #         if not beneficiaire_source_id:
    #             raise ValueError("Aucun bénéficiaire identifié (REG-004)")
            
    #         # Récupérer les infos de la source pour la résolution
    #         source_data = self._get_source_data(
    #             source=beneficiaire_source,
    #             source_id=beneficiaire_source_id,
    #         )
            
    #         if not source_data:
    #             raise ValueError(
    #                 f"Bénéficiaire (source={beneficiaire_source}, "
    #                 f"ID={beneficiaire_source_id}) non trouvé (REG-004)"
    #             )
            
    #         # Résoudre l'ID du LometaBeneficiaire
    #         beneficiaire_id = self.resolve_beneficiaire_id(
    #             source=beneficiaire_source,
    #             source_id=beneficiaire_source_id,
    #             source_data=source_data,
    #             utilisateur_id=data.get('created_by'),
    #         )
            
    #         beneficiaire_nom = source_data.get('nom_complet', 'N/A')
            
    #         # ============================================================
    #         # 4. Contrôles de montant (FIN-001 / FIN-002 / REG-003)
    #         # ============================================================
    #         montant_demande = float(data.get('montant', 0))
            
    #         if montant_demande <= 0:
    #             raise ValueError("Le montant doit être strictement positif")
            
    #         if evaluation:
    #             if montant_demande > evaluation.montant_net:
    #                 raise ValueError(
    #                     f"Le montant ({montant_demande:,.0f}) dépasse "
    #                     f"l'évaluation ({evaluation.montant_net:,.0f}) - FIN-001"
    #                 )
                
    #             reglements_existants = self.session.query(LometaReglement).filter(
    #                 LometaReglement.evaluation_id == evaluation.id,
    #                 LometaReglement.statut.in_(
    #                     ['CREE', 'VALIDE', 'EN_ATTENTE', 'TRAITE', 'PAYE']
    #                 ),
    #                 LometaReglement.is_active == True
    #             ).all()
                
    #             total_deja_engage = sum(r.montant for r in reglements_existants)
    #             disponible = evaluation.montant_net - total_deja_engage
                
    #             if disponible <= 0:
    #                 raise ValueError(
    #                     f"Évaluation entièrement engagée "
    #                     f"({total_deja_engage:,.0f}/{evaluation.montant_net:,.0f}) - FIN-002"
    #                 )
                
    #             if montant_demande > disponible:
    #                 raise ValueError(
    #                     f"Montant ({montant_demande:,.0f}) > disponible "
    #                     f"({disponible:,.0f}) - FIN-002"
    #                 )
            
    #         # ============================================================
    #         # 5. Créer le règlement
    #         # ============================================================
    #         numero = self.generate_numero("REG", LometaReglement, 'numero_reglement')
            
    #         # Nettoyer data
    #         data.pop('beneficiaire_source', None)
    #         data.pop('beneficiaire_id', None)
    #         data.pop('beneficiaire_nom', None)
            
    #         reglement = LometaReglement(
    #             numero_reglement=numero,
    #             statut="CREE",
    #             date_demande=datetime.utcnow(),
    #             # ✅ Toujours pointer vers lometa_beneficiaires
    #             beneficiaire_id=beneficiaire_id,
    #             beneficiaire_nom=beneficiaire_nom,
    #             **data
    #         )
            
    #         self.session.add(reglement)
    #         self.session.flush()
            
    #         # ============================================================
    #         # 6. Statut sinistre
    #         # ============================================================
    #         if sinistre.statut not in ["EN_REGLEMENT", "CLOTURE"]:
    #             sinistre.statut = "EN_REGLEMENT"
    #             sinistre.updated_at = datetime.utcnow()
    #             sinistre.updated_by = data.get('created_by')
            
    #         # ============================================================
    #         # 7. Audit
    #         # ============================================================
    #         self.log_audit(
    #             utilisateur_id=data.get('created_by'),
    #             action="CREATION",
    #             entite="Reglement",
    #             entite_id=reglement.id,
    #             entite_nom=reglement.numero_reglement,
    #             commentaire=(
    #                 f"Règlement {reglement.numero_reglement} créé "
    #                 f"- Montant: {montant_demande:,.0f} FCFA "
    #                 f"- Bénéficiaire: {beneficiaire_nom} (résolu depuis {beneficiaire_source}) "
    #                 f"- Évaluation: {evaluation.numero_evaluation if evaluation else 'N/A'}"
    #             )
    #         )
            
    #         self.session.commit()
    #         return reglement
        
    #     except Exception as e:
    #         self.session.rollback()
    #         raise e

    def creer_reglement(self, data: Dict[str, Any]) -> LometaReglement:
        """
        Crée une demande de règlement avec contrôles CDC et résolution du bénéficiaire.
        
        Règles CDC appliquées :
        - REG-002 : L'évaluation doit être validée
        - REG-003 : Le montant doit être disponible
        - REG-004 : Le bénéficiaire doit être identifié (résolution par identité métier)
        - FIN-001 : Règlement ≤ Évaluation Validée
        - FIN-002 : Σ Règlements ≤ Évaluation Validée
        - FIN-003 : Le bénéficiaire doit être actif
        - FIN-100 : Aucun paiement sans évaluation validée
        
        Args:
            data: dict contenant :
                - sinistre_id (int, obligatoire)
                - evaluation_id (int, optionnel mais recommandé)
                - beneficiaire_source (str) : 'BENEFICIAIRE' | 'TIERS' | 'EXPERT'
                - beneficiaire_id (int) : ID dans la table source (info seulement)
                - beneficiaire_data (dict) : données complètes du bénéficiaire sélectionné
                                            (nom, prenom, telephone, email, etc.)
                - beneficiaire_nom (str, optionnel) : nom d'affichage
                - montant (float, obligatoire)
                - type_paiement (str) : CHEQUE | VIREMENT | MOBILE_MONEY
                - numero_cheque, banque_emetteur (si CHEQUE)
                - reference_virement (si VIREMENT)
                - reference_mobile, operateur_mobile (si MOBILE_MONEY)
                - observations (str, optionnel)
                - created_by (int) : ID utilisateur
        
        Returns:
            LometaReglement créé.
        
        Raises:
            ValueError: si une règle CDC n'est pas respectée.
        """
        try:
            # ============================================================
            # 1. VÉRIFICATION DU SINISTRE
            # ============================================================
            sinistre_id = data.get('sinistre_id')
            if not sinistre_id:
                raise ValueError("Aucun sinistre associé au règlement")
            
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == sinistre_id,
                LometaSinistre.is_active == True
            ).first()
            
            if not sinistre:
                raise ValueError(f"Sinistre (ID={sinistre_id}) non trouvé")
            
            # ============================================================
            # 2. VÉRIFICATION DE L'ÉVALUATION (REG-002 / FIN-100)
            # ============================================================
            evaluation = None
            evaluation_id = data.get('evaluation_id')
            
            if evaluation_id:
                evaluation = self.session.query(LometaEvaluation).filter(
                    LometaEvaluation.id == evaluation_id,
                    LometaEvaluation.is_active == True
                ).first()
                
                if not evaluation:
                    raise ValueError(f"Évaluation (ID={evaluation_id}) non trouvée")
                
                if not evaluation.est_validee:
                    raise ValueError(
                        "L'évaluation associée doit être validée avant tout règlement "
                        "(règle REG-002 / FIN-100)"
                    )
                
                # Vérifier que l'évaluation appartient bien au sinistre
                if evaluation.sinistre_id != sinistre_id:
                    raise ValueError(
                        f"L'évaluation (ID={evaluation_id}) n'appartient pas "
                        f"au sinistre {sinistre.numero_sinistre}"
                    )
            
            # ============================================================
            # 3. RÉSOLUTION DU BÉNÉFICIAIRE (REG-004 / FIN-003)
            # ============================================================
            beneficiaire_source = data.get('beneficiaire_source', 'BENEFICIAIRE')
            beneficiaire_source_id = data.get('beneficiaire_id')
            beneficiaire_data = data.get('beneficiaire_data')
            
            # Vérifications
            if not beneficiaire_source_id:
                raise ValueError(
                    "Aucun bénéficiaire identifié (règle REG-004)"
                )
            
            if not beneficiaire_data:
                raise ValueError(
                    "Données du bénéficiaire manquantes (beneficiaire_data requis)"
                )
            
            # ✅ Résolution par identité métier
            # (cherche dans lometa_beneficiaires par nom+prénom+téléphone)
            try:
                beneficiaire_id = self.resolve_beneficiaire_id(
                    source=beneficiaire_source,
                    source_id=beneficiaire_source_id,
                    source_data=beneficiaire_data,
                    utilisateur_id=data.get('created_by'),
                )
            except ValueError as e:
                raise ValueError(f"Erreur résolution bénéficiaire : {e}")
            
            # Vérifier que le bénéficiaire résolu est actif (FIN-003)
            beneficiaire = self.session.query(LometaBeneficiaire).filter(
                LometaBeneficiaire.id == beneficiaire_id,
                LometaBeneficiaire.is_active == True
            ).first()
            
            if not beneficiaire:
                raise ValueError(
                    f"Bénéficiaire (ID={beneficiaire_id}) non trouvé après résolution"
                )
            
            if hasattr(beneficiaire, 'est_actif') and not beneficiaire.est_actif:
                raise ValueError(
                    f"Le bénéficiaire {beneficiaire.nom} est inactif (règle FIN-003)"
                )
            
            # Nom d'affichage
            beneficiaire_nom = (
                beneficiaire_data.get('nom_complet')
                or f"{beneficiaire.nom} {beneficiaire.prenom or ''}".strip()
                or 'N/A'
            )
            
            # ============================================================
            # 4. CONTRÔLES DE MONTANT (FIN-001 / FIN-002 / REG-003)
            # ============================================================
            montant_demande = float(data.get('montant', 0))
            
            if montant_demande <= 0:
                raise ValueError("Le montant doit être strictement positif (REG-003)")
            
            if evaluation:
                # FIN-001 : Le montant ne peut pas dépasser l'évaluation
                montant_net = float(evaluation.montant_net)
                if montant_demande > montant_net:
                    raise ValueError(
                        f"Le montant demandé ({montant_demande:,.0f} FCFA) dépasse "
                        f"le montant net de l'évaluation ({montant_net:,.0f} FCFA) "
                        f"(règle FIN-001)"
                    )
                
                # FIN-002 : Σ règlements ≤ Évaluation Validée
                reglements_existants = self.session.query(LometaReglement).filter(
                    LometaReglement.evaluation_id == evaluation.id,
                    LometaReglement.statut.in_(
                        ['CREE', 'VALIDE', 'EN_ATTENTE', 'TRAITE', 'PAYE']
                    ),
                    LometaReglement.is_active == True
                ).all()
                
                total_deja_engage = sum(
                    float(r.montant or 0) for r in reglements_existants
                )
                disponible = montant_net - total_deja_engage
                
                if disponible <= 0:
                    raise ValueError(
                        f"Le montant net de l'évaluation est déjà entièrement engagé "
                        f"({total_deja_engage:,.0f} FCFA sur {montant_net:,.0f} FCFA) "
                        f"(règle FIN-002)"
                    )
                
                if montant_demande > disponible:
                    raise ValueError(
                        f"Le montant demandé ({montant_demande:,.0f} FCFA) dépasse "
                        f"le montant disponible ({disponible:,.0f} FCFA) après "
                        f"déduction des règlements existants ({total_deja_engage:,.0f} FCFA) "
                        f"(règle FIN-002 / REG-003)"
                    )
            
            # ============================================================
            # 5. VALIDATION DU TYPE DE PAIEMENT
            # ============================================================
            type_paiement = data.get('type_paiement', '').upper()
            if type_paiement not in ('CHEQUE', 'VIREMENT', 'MOBILE_MONEY'):
                raise ValueError(
                    f"Type de paiement invalide : '{type_paiement}'. "
                    f"Attendu : CHEQUE, VIREMENT, MOBILE_MONEY"
                )
            
            # ============================================================
            # 6. GÉNÉRATION DU NUMÉRO
            # ============================================================
            numero = self.generate_numero(
                "REG", LometaReglement, 'numero_reglement'
            )
            
            # ============================================================
            # 7. NETTOYAGE DES DONNÉES (retirer les champs non liés au modèle)
            # ============================================================
            data.pop('beneficiaire_source', None)
            data.pop('beneficiaire_data', None)
            data.pop('beneficiaire_nom', None)
            data.pop('beneficiaire_id', None)
            
            # ============================================================
            # 8. CRÉATION DU RÈGLEMENT
            # ============================================================
            reglement = LometaReglement(
                numero_reglement=numero,
                statut="CREE",
                date_demande=datetime.utcnow(),
                # ✅ Toujours pointer vers lometa_beneficiaires
                beneficiaire_id=beneficiaire_id,
                beneficiaire_nom=beneficiaire_nom,
                **data
            )
            
            self.session.add(reglement)
            self.session.flush()
            
            # ============================================================
            # 9. MISE À JOUR DU STATUT DU SINISTRE
            # ============================================================
            if sinistre.statut not in ["EN_REGLEMENT", "CLOTURE"]:
                sinistre.statut = "EN_REGLEMENT"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = data.get('created_by')
            
            # ============================================================
            # 10. AUDIT
            # ============================================================
            self.log_audit(
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Reglement",
                entite_id=reglement.id,
                entite_nom=reglement.numero_reglement,
                commentaire=(
                    f"Création du règlement {reglement.numero_reglement} "
                    f"- Montant: {montant_demande:,.0f} FCFA "
                    f"- Bénéficiaire: {beneficiaire_nom} "
                    f"(source={beneficiaire_source}, "
                    f"source_id={beneficiaire_source_id}, "
                    f"beneficiaire_id={beneficiaire_id}) "
                    f"- Évaluation: {evaluation.numero_evaluation if evaluation else 'N/A'}"
                )
            )
            
            self.session.commit()
            
            print(f"✅ Règlement créé : {reglement.numero_reglement} "
                f"(montant={montant_demande:,.0f} FCFA, "
                f"beneficiaire_id={beneficiaire_id})")
            
            return reglement
        
        except Exception as e:
            self.session.rollback()
            print(f"❌ Erreur création règlement : {e}")
            import traceback
            traceback.print_exc()
            raise e

    def _get_source_data(
        self,
        source: str,
        source_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère les données normalisées d'une source (tiers, expert ou bénéficiaire).
        """
        source = (source or 'BENEFICIAIRE').upper()
        
        if source == 'BENEFICIAIRE':
            b = self.session.query(LometaBeneficiaire).filter(
                LometaBeneficiaire.id == source_id,
                LometaBeneficiaire.is_active == True
            ).first()
            return self._serialize_beneficiaire(b) if b else None
        
        elif source == 'TIERS':
            t = self.session.query(LometaTiers).filter(
                LometaTiers.id == source_id,
                LometaTiers.is_active == True
            ).first()
            return self._serialize_tiers(t) if t else None
        
        elif source == 'EXPERT':
            try:
                from addons.sinistres.models.expertise import LometaExpert
                e = self.session.query(LometaExpert).filter(
                    LometaExpert.id == source_id,
                    LometaExpert.is_active == True
                ).first()
                return self._serialize_expert(e) if e else None
            except ImportError:
                return None
        
        return None

    def get_reglement(self, reglement_id: int) -> Optional[LometaReglement]:
        """Récupère un règlement par son ID"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.id == reglement_id,
                LometaReglement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reglement_by_numero(self, numero: str) -> Optional[LometaReglement]:
        """Récupère un règlement par son numéro"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.numero_reglement == numero,
                LometaReglement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reglements_by_sinistre(self, sinistre_id: int) -> List[LometaReglement]:
        """Récupère tous les règlements d'un sinistre"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.sinistre_id == sinistre_id,
                LometaReglement.is_active == True
            ).order_by(LometaReglement.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_reglements_en_attente(self) -> List[LometaReglement]:
        """Récupère tous les règlements en attente de validation"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.statut.in_(['CREE', 'VALIDE', 'EN_ATTENTE']),
                LometaReglement.is_active == True
            ).order_by(LometaReglement.date_demande.asc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def valider_reglement(self, reglement_id: int, utilisateur_id: int) -> Optional[LometaReglement]:
        """
        Valide un règlement (avec contrôle du seuil Tome 5 §6).
        """
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            if reglement.statut != "CREE":
                raise ValueError("Seul un règlement créé peut être validé")
            
            # ✅ Contrôle du seuil
            if not self._valider_seuil_reglement(reglement.montant, utilisateur_id):
                raise ValueError(
                    f"Vous n'avez pas les droits pour valider un règlement de "
                    f"{reglement.montant:,.0f} FCFA (seuil dépassé - Tome 5 §6)"
                )
            
            reglement.statut = "VALIDE"
            reglement.date_validation = datetime.utcnow()
            reglement.valide_par = utilisateur_id
            reglement.updated_at = datetime.utcnow()
            reglement.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="VALIDATION",
                entite="Reglement",
                entite_id=reglement.id,
                entite_nom=reglement.numero_reglement,
                commentaire=f"Validation du règlement {reglement.numero_reglement} "
                        f"(montant: {reglement.montant:,.0f} FCFA)"
            )
            
            self.session.commit()
            return reglement
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def payer_reglement(self, reglement_id: int, utilisateur_id: int, data: Dict[str, Any]) -> Optional[LometaReglement]:
        """Exécute le paiement d'un règlement"""
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            if reglement.statut not in ["VALIDE", "EN_ATTENTE"]:
                raise ValueError("Seul un règlement validé peut être payé")
            
            # Mettre à jour selon le type de paiement
            if reglement.type_paiement == "CHEQUE" and data.get('numero_cheque'):
                reglement.numero_cheque = data['numero_cheque']
                reglement.banque_emetteur = data.get('banque_emetteur')
                reglement.date_emission_cheque = datetime.utcnow()
            elif reglement.type_paiement == "VIREMENT" and data.get('reference_virement'):
                reglement.reference_virement = data['reference_virement']
                reglement.date_virement = datetime.utcnow()
            elif reglement.type_paiement == "MOBILE_MONEY" and data.get('reference_mobile'):
                reglement.reference_mobile = data['reference_mobile']
                reglement.operateur_mobile = data.get('operateur_mobile')
            
            reglement.statut = "PAYE"
            reglement.date_paiement = datetime.utcnow()
            reglement.paiement_effectue_par = utilisateur_id
            reglement.updated_at = datetime.utcnow()
            reglement.updated_by = utilisateur_id
            
            try:
                from addons.sinistres.services.comptabilite_service import ComptabiliteService
                comptabilite_service = ComptabiliteService(self.session)
                
                # Récupérer la branche du sinistre pour le schéma comptable
                from addons.sinistres.models.sinistre import LometaSinistre
                sinistre = self.session.query(LometaSinistre).filter(
                    LometaSinistre.id == reglement.sinistre_id
                ).first()
                branche = sinistre.branche if sinistre else None
                
                comptabilite_service.ecriture_paiement_sinistre(
                    reglement_id=reglement.id,
                    numero_reglement=reglement.numero_reglement,
                    montant=reglement.montant,
                    sinistre_id=reglement.sinistre_id,
                    utilisateur_id=utilisateur_id,
                    branche=branche,
                )
            except Exception as e:
                print(f"⚠️ Écriture comptable non générée : {e}")

            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="PAIEMENT",
                entite="Reglement",
                entite_id=reglement.id,
                entite_nom=reglement.numero_reglement,
                commentaire=f"Paiement du règlement {reglement.numero_reglement} - {reglement.type_paiement}"
            )
            
            self.session.commit()
            return reglement
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def annuler_reglement(self, reglement_id: int, utilisateur_id: int, motif: str) -> Optional[LometaReglement]:
        """
        Annule un règlement.
        
        Règles CDC :
        - REG-103 : Aucune suppression physique (utilise le statut ANNULE)
        - NC-001 : Une note de crédit doit être justifiée
        - NC-002 : Toute note de crédit doit être auditée
        
        Si le règlement est PAYE, crée une note de crédit au lieu d'annuler.
        """
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            if reglement.statut == "ANNULE":
                raise ValueError("Ce règlement est déjà annulé")
            
            # ============================================================
            # Cas 1 : Règlement PAYE → créer une note de crédit
            # ============================================================
            if reglement.statut == "PAYE":
                from addons.sinistres.models.reglement import LometaNoteCredit
                
                if not motif:
                    raise ValueError(
                        "Un motif est obligatoire pour créer une note de crédit (NC-001)"
                    )
                
                # Créer la note de crédit
                numero_nc = self.generate_numero("NC", LometaNoteCredit, 'numero_note')
                
                note = LometaNoteCredit(
                    numero_note=numero_nc,
                    sinistre_id=reglement.sinistre_id,
                    reglement_origine_id=reglement.id,
                    type_note="ANNULATION",
                    montant=reglement.montant,
                    motif=motif,
                    date_creation=datetime.utcnow(),
                    est_comptabilise=False,
                    created_by=utilisateur_id,
                )
                
                self.session.add(note)
                self.session.flush()
                
                # Lier la note au règlement
                reglement.note_credit_id = note.id
                reglement.est_note_credit = True
                
                self.log_audit(
                    utilisateur_id=utilisateur_id,
                    action="NOTE_CREDIT",
                    entite="Reglement",
                    entite_id=reglement.id,
                    entite_nom=reglement.numero_reglement,
                    commentaire=(
                        f"Note de crédit {numero_nc} créée "
                        f"(montant: {reglement.montant:,.0f} FCFA) "
                        f"- Motif: {motif}"
                    )
                )
            
            # ============================================================
            # Cas 2 : Règlement non payé → annulation simple
            # ============================================================
            else:
                reglement.statut = "ANNULE"
                reglement.motif_annulation = motif
                reglement.updated_at = datetime.utcnow()
                reglement.updated_by = utilisateur_id
                
                self.log_audit(
                    utilisateur_id=utilisateur_id,
                    action="ANNULATION",
                    entite="Reglement",
                    entite_id=reglement.id,
                    entite_nom=reglement.numero_reglement,
                    commentaire=(
                        f"Annulation du règlement {reglement.numero_reglement} "
                        f"- Motif: {motif}"
                    )
                )
            
            self.session.commit()
            return reglement
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_evaluations_by_sinistre(self, sinistre_id: int) -> List[LometaEvaluation]:
            """Récupère toutes les évaluations d'un sinistre"""
            try:
                return self.session.query(LometaEvaluation).filter(
                    LometaEvaluation.sinistre_id == sinistre_id,
                    LometaEvaluation.is_active == True
                ).order_by(LometaEvaluation.created_at.desc()).all()
            except Exception as e:
                self.session.rollback()
                raise e
    
    # ============================================================
    # GESTION DES LOTS DE PAIEMENT
    # ============================================================
   
    def creer_lot_paiement(self, data: Dict[str, Any]) -> LometaLotPaiement:
        """
        Crée un lot de paiement.
        
        data doit contenir :
        - reglement_ids : List[int]      ← IDs des règlements à inclure
        - banque_id : int                ← ID de la banque
        - compte_bancaire_id : int       ← ID du compte bancaire
        - type_lot : str                 ← STANDARD / URGENT / RECOURS
        - date_traitement : date         ← Date prévue de traitement
        - observations : str (optionnel)
        - created_by : int               ← Utilisateur créateur
        """
        try:
            # ============================================================
            # 1. Extraire les IDs des règlements
            # ============================================================
            reglement_ids = data.pop('reglement_ids', [])
            
            if not reglement_ids:
                raise ValueError("Aucun règlement sélectionné")
            
            # ============================================================
            # 2. Extraire et valider les IDs banque/compte
            # ============================================================
            banque_id = data.get('banque_id')
            compte_id = data.get('compte_bancaire_id')
            
            # ✅ Vérifications explicites
            if banque_id is None:
                raise ValueError("Aucune banque sélectionnée")
            if compte_id is None:
                raise ValueError("Aucun compte bancaire sélectionné")
            
            # ✅ Cast en int pour éviter les problèmes de type
            try:
                banque_id = int(banque_id)
                compte_id = int(compte_id)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"IDs invalides : banque_id={banque_id!r}, compte_id={compte_id!r}"
                )
            
            # ============================================================
            # 3. Vérifier que le compte bancaire existe, est actif,
            #    et appartient bien à la banque sélectionnée
            # ============================================================
            compte = self.session.query(LometaCompteBancaire).filter(
                LometaCompteBancaire.id == compte_id,
                LometaCompteBancaire.banque == banque_id,
                LometaCompteBancaire.is_active == True,
                LometaCompteBancaire.est_actif == True,
            ).first()
            
            if not compte:
                # ✅ Message détaillé pour debug
                # Vérifier si le compte existe sans les filtres
                compte_check = self.session.query(LometaCompteBancaire).filter(
                    LometaCompteBancaire.id == compte_id
                ).first()
                
                if not compte_check:
                    raise ValueError(
                        f"Le compte bancaire (ID={compte_id}) n'existe pas en base"
                    )
                
                # Le compte existe mais ne passe pas les filtres
                raisons = []
                if compte_check.banque != banque_id:
                    raisons.append(
                        f"appartient à la banque {compte_check.banque} "
                        f"(≠ {banque_id})"
                    )
                if not compte_check.is_active:
                    raisons.append("est supprimé logiquement (is_active=False)")
                if not compte_check.est_actif:
                    raisons.append("est inactif (est_actif=False)")
                
                raise ValueError(
                    f"Le compte bancaire {compte_check.libelle!r} "
                    f"(ID={compte_id}) ne peut pas être utilisé : "
                    f"{', '.join(raisons)}"
                )
            
            # ============================================================
            # 4. Recharger les règlements depuis la base
            # ============================================================
            reglements = self.session.query(LometaReglement).filter(
                LometaReglement.id.in_(reglement_ids),
                LometaReglement.is_active == True
            ).all()
            
            if len(reglements) != len(reglement_ids):
                trouves = {r.id for r in reglements}
                manquants = set(reglement_ids) - trouves
                raise ValueError(
                    f"Certains règlements sont introuvables ou inactifs : {manquants}"
                )
            
            # ============================================================
            # 5. Vérifier que tous les règlements sont VALIDE
            # ============================================================
            invalides = [r.numero_reglement for r in reglements if r.statut != "VALIDE"]
            if invalides:
                raise ValueError(
                    f"Ces règlements ne sont pas au statut VALIDE : "
                    f"{', '.join(invalides)}"
                )
            
            # ============================================================
            # 6. Vérifier qu'aucun règlement n'est déjà dans un lot
            # ============================================================
            deja_dans_lot = [r.numero_reglement for r in reglements if r.lot_paiement_id]
            if deja_dans_lot:
                raise ValueError(
                    f"Ces règlements sont déjà dans un lot : "
                    f"{', '.join(deja_dans_lot)}"
                )
            
            # ============================================================
            # 7. Calculer le montant total
            # ============================================================
            montant_total = sum(r.montant for r in reglements)
            
            # ============================================================
            # 8. Extraire les autres champs du lot
            # ============================================================
            type_lot = data.get('type_lot', 'STANDARD')
            date_traitement = data.get('date_traitement')
            observations = data.get('observations')
            created_by = data.get('created_by')
            
            # ============================================================
            # 9. Créer le lot avec des paramètres NOMMÉS (pas **data)
            # ============================================================
            numero = self.generate_numero("LOT", LometaLotPaiement, 'numero_lot')
            
            lot = LometaLotPaiement(
                numero_lot=numero,
                statut="OUVERT",
                date_creation=datetime.utcnow(),
                date_traitement=date_traitement,
                banque_id=banque_id,                       # ✅ Explicitement
                compte_bancaire_id=compte_id,              # ✅ Explicitement
                nombre_paiements=len(reglements),
                montant_total=montant_total,
                type_lot=type_lot,
                observations=observations,
                created_by=created_by,
                is_active=True,
            )
            
            self.session.add(lot)
            self.session.flush()   # ← Pour obtenir lot.id
            
            # ============================================================
            # 10. Lier chaque règlement au lot
            # ============================================================
            for reg in reglements:
                reg.lot_paiement_id = lot.id
                reg.updated_at = datetime.utcnow()
                reg.updated_by = created_by
            
            # ============================================================
            # 11. Log d'audit
            # ============================================================
            self.log_audit(
                utilisateur_id=created_by,
                action="CREATION",
                entite="LometaLotPaiement",
                entite_id=lot.id,
                entite_nom=lot.numero_lot,
                commentaire=(
                    f"Création du lot {lot.numero_lot} "
                    f"({len(reglements)} règlements, {montant_total:,.0f} FCFA) "
                    f"- Banque: {compte.banque} - Compte: {compte.libelle}"
                )
            )
            
            self.session.commit()
            return lot
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_lot_paiement(self, lot_id: int) -> Optional[LometaLotPaiement]:
        """Récupère un lot de paiement"""
        try:
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.id == lot_id,
                LometaLotPaiement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def ajouter_reglement_au_lot(self, reglement_id: int, lot_id: int, utilisateur_id: int) -> bool:
        """Ajoute un règlement à un lot"""
        try:
            reglement = self.get_reglement(reglement_id)
            if not reglement:
                raise ValueError("Règlement non trouvé")
            
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            
            if lot.statut != "OUVERT":
                raise ValueError("Seul un lot ouvert peut recevoir des règlements")
            
            reglement.lot_paiement_id = lot_id
            reglement.updated_at = datetime.utcnow()
            reglement.updated_by = utilisateur_id
            
            # Mettre à jour les statistiques du lot
            lot.nombre_paiements += 1
            lot.montant_total += reglement.montant
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def valider_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional[LometaLotPaiement]:
        """Valide un lot de paiement"""
        try:
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            
            if lot.statut != "OUVERT":
                raise ValueError("Seul un lot ouvert peut être validé")
            
            if not self._valider_seuil_reglement(lot.montant_total, utilisateur_id):
                raise ValueError(
                    f"Vous n'avez pas les droits pour valider un lot de "
                    f"{lot.montant_total:,.0f} FCFA (seuil Tome 5 §6)"
                )
            lot.date_validation = datetime.utcnow()
            lot.valide_par = utilisateur_id
            lot.updated_at = datetime.utcnow()
            lot.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="VALIDATION",
                entite="LometaLotPaiement",
                entite_id=lot.id,
                entite_nom=lot.numero_lot,
                commentaire=f"Validation du lot {lot.numero_lot} - {lot.nombre_paiements} paiements"
            )
            
            self.session.commit()
            return lot
            
        except Exception as e:
            self.session.rollback()
            raise e

    def _valider_seuil_reglement(self, montant: float, utilisateur_id: int) -> bool:
        """
        Vérifie que l'utilisateur peut valider selon le seuil (Tome 5 §6).
        
        Seuils :
        - < 1M    : Gestionnaire
        - < 5M    : Responsable
        - ≥ 5M    : Direction (admin)
        """
        from addons.sinistres.services.permission_service import PermissionService
        
        perm_service = PermissionService(self.session)
        user_roles = [r.code for r in perm_service.get_user_roles(utilisateur_id)]
        
        if montant < self.SEUIL_RESPONSABLE:
            # Gestionnaire, responsable, admin
            return any(r in user_roles for r in ['gestionnaire', 'responsable', 'admin'])
        elif montant < self.SEUIL_DIRECTION:
            # Responsable ou admin
            return any(r in user_roles for r in ['responsable', 'admin'])
        else:
            # Admin uniquement
            return 'admin' in user_roles

    # ============================================================
    # MÉTHODES UTILITAIRES
    # ============================================================
    
    def get_evaluation(self, evaluation_id: int) -> Optional[LometaEvaluation]:
        """Récupère une évaluation par son ID"""
        try:
            return self.session.query(LometaEvaluation).filter(
                LometaEvaluation.id == evaluation_id,
                LometaEvaluation.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # STATISTIQUES
    # ============================================================
    
    def get_statistiques(self, sinistre_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des règlements"""
        try:
            query = self.session.query(LometaReglement).filter(LometaReglement.is_active == True)
            
            if sinistre_id:
                query = query.filter(LometaReglement.sinistre_id == sinistre_id)
            
            total = query.count()
            
            # Par statut
            par_statut = {}
            for statut in ['CREE', 'VALIDE', 'EN_ATTENTE', 'TRAITE', 'PAYE', 'ANNULE', 'REJETE']:
                count = query.filter(LometaReglement.statut == statut).count()
                if count > 0:
                    par_statut[statut] = count
            
            # Montant total
            montant_total = query.with_entities(
                func.sum(LometaReglement.montant)
            ).scalar() or 0
            
            # Par type de paiement
            par_type = {}
            for type_ in ['CHEQUE', 'VIREMENT', 'MOBILE_MONEY']:
                count = query.filter(LometaReglement.type_paiement == type_).count()
                if count > 0:
                    par_type[type_] = count
            
            return {
                'total': total,
                'par_statut': par_statut,
                'montant_total': montant_total,
                'par_type_paiement': par_type
            }
        except Exception as e:
            self.session.rollback()
            raise e

    # Ajouter ces méthodes à la fin de la classe ReglementService
    def get_lots_by_sinistre(self, sinistre_id: int) -> List[LometaLotPaiement]:
        """Récupère les lots de paiement d'un sinistre"""
        try:
            from addons.sinistres.models.reglement import LometaReglement
            
            # Un lot est lié à un sinistre via ses règlements
            lot_ids = self.session.query(LometaReglement.lot_paiement_id).filter(
                LometaReglement.sinistre_id == sinistre_id,
                LometaReglement.lot_paiement_id.isnot(None),
                LometaReglement.is_active == True
            ).distinct().all()
            
            ids = [row[0] for row in lot_ids if row[0]]
            
            if not ids:
                return []
            
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.id.in_(ids),
                LometaLotPaiement.is_active == True
            ).order_by(LometaLotPaiement.date_creation.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_lots_by_statut(self, statut: str) -> List['LometaLotPaiement']:
        """Récupère les lots par statut"""
        try:
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.statut == statut,
                LometaLotPaiement.is_active == True
            ).order_by(LometaLotPaiement.date_creation.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def traiter_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional['LometaLotPaiement']:
        """Traite un lot de paiement (passage en TRAITE)"""
        try:
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            
            if lot.statut != "VALIDE":
                raise ValueError("Seul un lot validé peut être traité")
            
            lot.statut = "TRAITE"
            lot.date_traitement = datetime.utcnow()
            lot.updated_at = datetime.utcnow()
            lot.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="TRAITEMENT",
                entite="LometaLotPaiement",
                entite_id=lot.id,
                entite_nom=lot.numero_lot,
                commentaire=f"Traitement du lot {lot.numero_lot}"
            )
            
            self.session.commit()
            return lot
            
        except Exception as e:
            self.session.rollback()
            raise e

    # def comptabiliser_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional['LometaLotPaiement']:
    #     """Comptabilise un lot de paiement"""
    #     try:
    #         lot = self.get_lot_paiement(lot_id)
    #         if not lot:
    #             raise ValueError("Lot non trouvé")
            
    #         if lot.statut != "TRAITE":
    #             raise ValueError("Seul un lot traité peut être comptabilisé")
            
    #         lot.statut = "COMPTABILISE"
    #         lot.date_comptabilisation = datetime.utcnow()
    #         lot.updated_at = datetime.utcnow()
    #         lot.updated_by = utilisateur_id
            
    #         # Marquer tous les règlements du lot comme comptabilisés
    #         for reg in lot.reglements:
    #             reg.est_comptabilise = True
    #             reg.date_comptabilisation = datetime.utcnow()
    #             reg.updated_at = datetime.utcnow()
    #             reg.updated_by = utilisateur_id
            
    #         self.log_audit(
    #             utilisateur_id=utilisateur_id,
    #             action="COMPTABILISATION",
    #             entite="LometaLotPaiement",
    #             entite_id=lot.id,
    #             entite_nom=lot.numero_lot,
    #             commentaire=f"Comptabilisation du lot {lot.numero_lot}"
    #         )
            
    #         self.session.commit()
    #         return lot
            
    #     except Exception as e:
    #         self.session.rollback()
    #         raise e

    # ============================================================
    # BANQUES (nouveau)
    # ============================================================

    def get_banques(self) -> List[dict]:
        """Récupère le référentiel des banques"""
        try:
            from addons.sinistres.models.reglement import LometaBanque
            banques = self.session.query(LometaBanque).filter(
                LometaBanque.is_active == True
            ).order_by(LometaBanque.id).all()
            return [
                {
                    'id': b.id,
                    'code_banque': b.code_banque,
                    'libelle': b.libelle,
                    'bic_swift': b.bic_swift,
                    'pays': b.pays,
                    'adresse': b.adresse,
                    'telephone': b.telephone,
                    'email': b.email,
                    'est_actif': b.est_actif,
                }
                for b in banques
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def creer_banque(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée une banque dans le référentiel"""
        try:
            from addons.sinistres.models.reglement import LometaBanque
            banque = LometaBanque(**data)
            self.session.add(banque)
            self.session.commit()
            return {'id': banque.id, 'code_banque': banque.code_banque, 'libelle': banque.libelle}
        except Exception as e:
            self.session.rollback()
            raise e

    # ============================================================
    # COMPTES BANCAIRES (nouveau)
    # ============================================================

    def get_comptes_bancaires(self, actifs_only: bool = True) -> List[dict]:
        """Récupère les comptes bancaires"""
        try:
            from addons.sinistres.models.reglement import LometaCompteBancaire
            query = self.session.query(LometaCompteBancaire).filter(
                LometaCompteBancaire.is_active == True
            )
            if actifs_only:
                query = query.filter(LometaCompteBancaire.est_actif == True)
            return [
                {
                    'id': c.id,
                    'code_banque': c.code_banque,
                    'libelle': c.libelle,
                    'iban': c.iban,
                    'bic_swift': c.bic_swift,
                    'devise': c.devise,
                    'banque': c.banque,
                    'agence': getattr(c, 'agence', None), 
                    'solde': c.solde,
                    'est_actif': c.est_actif,
                    'est_par_defaut': getattr(c, 'est_par_defaut', False),  # ✅ AJOUT
                    'statut': getattr(c, 'statut', None),              # ✅ AJOUT
                }
                for c in query.order_by(LometaCompteBancaire.libelle).all()
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_compte_bancaire_by_bank(self, banque_id: Dict[str, Any]) -> List[dict]:

        try:
            from addons.sinistres.models.reglement import LometaCompteBancaire
            c = self.session.query(LometaCompteBancaire).filter(LometaCompteBancaire.banque==banque_id)
            c.filter(LometaCompteBancaire.est_actif==True)
            if not c:
                return None
            return {
                'id': c.id,
                'code_banque': c.code_banque,
                'libelle': c.libelle,
                'iban': c.iban,
                'bic_swift': c.bic_swift,
                'devise': c.devise,
                'banque': c.banque,
                'agence': getattr(c, 'agence', None), 
                'solde': c.solde,
                'est_actif': c.est_actif,
                'est_par_defaut': getattr(c, 'est_par_defaut', False),  # ✅ AJOUT
                'statut': getattr(c, 'statut', None), 
            }
        except Exception as e:
            self.session.rollback()
            raise e

    def get_compte_bancaire(self, compte_id: int) -> Optional[dict]:
        """Récupère un compte bancaire par ID"""
        try:
            from addons.sinistres.models.reglement import LometaCompteBancaire
            c = self.session.query(LometaCompteBancaire).filter(
                LometaCompteBancaire.id == compte_id
            ).first()
            if not c:
                return None
            return {
                'id': c.id,
                'code_banque': c.code_banque,
                'libelle': c.libelle,
                'iban': c.iban,
                'bic_swift': c.bic_swift,
                'devise': c.devise,
                'banque': c.banque,
                'banque_id': c.banque_id,
                'solde': c.solde,
            }
        except Exception as e:
            self.session.rollback()
            raise e

    def creer_compte_bancaire(self, data: Dict[str, Any]) -> Optional[dict]:
        """Crée un compte bancaire"""
        try:
            from addons.sinistres.models.reglement import LometaCompteBancaire
            compte = LometaCompteBancaire(**data)
            self.session.add(compte)
            self.session.commit()
            return {'id': compte.id, 'iban': compte.iban, 'libelle': compte.libelle}
        except Exception as e:
            self.session.rollback()
            raise e

    # ============================================================
    # NOTES DE CRÉDIT (nouveau)
    # ============================================================

    def get_notes_credit_by_reglement(self, reglement_id: int) -> List[dict]:
        """Récupère les notes de crédit liées à un règlement"""
        try:
            from addons.sinistres.models.reglement import LometaNoteCredit
            notes = self.session.query(LometaNoteCredit).filter(
                LometaNoteCredit.reglement_origine_id == reglement_id,
                LometaNoteCredit.is_active == True
            ).all()
            return [
                {
                    'id': n.id,
                    'numero_note': n.numero_note,
                    'type_note': n.type_note,
                    'montant': n.montant,
                    'motif': n.motif,
                    'date_creation': n.date_creation.isoformat() if n.date_creation else None,
                    'est_comptabilise': n.est_comptabilise,
                }
                for n in notes
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_notes_credit_by_sinistre(self, sinistre_id: int) -> List[dict]:
        """Récupère les notes de crédit d'un sinistre"""
        try:
            from addons.sinistres.models.reglement import LometaNoteCredit
            notes = self.session.query(LometaNoteCredit).filter(
                LometaNoteCredit.sinistre_id == sinistre_id,
                LometaNoteCredit.is_active == True
            ).order_by(LometaNoteCredit.date_creation.desc()).all()
            return [
                {
                    'id': n.id,
                    'numero_note': n.numero_note,
                    'type_note': n.type_note,
                    'montant': n.montant,
                    'motif': n.motif,
                    'date_creation': n.date_creation.isoformat() if n.date_creation else None,
                }
                for n in notes
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_notes_credit(self) -> List[dict]:
        """Récupère toutes les notes de crédit"""
        try:
            from addons.sinistres.models.reglement import LometaNoteCredit
            notes = self.session.query(LometaNoteCredit).filter(
                LometaNoteCredit.is_active == True
            ).order_by(LometaNoteCredit.date_creation.desc()).all()
            return [
                {
                    'id': n.id,
                    'numero_note': n.numero_note,
                    'type_note': n.type_note,
                    'montant': n.montant,
                    'sinistre_id': n.sinistre_id,
                    'date_creation': n.date_creation.isoformat() if n.date_creation else None,
                }
                for n in notes
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_note_credit(self, note_id: int) -> Optional[dict]:
        """Récupère une note de crédit par ID"""
        try:
            from addons.sinistres.models.reglement import LometaNoteCredit
            n = self.session.query(LometaNoteCredit).filter(
                LometaNoteCredit.id == note_id
            ).first()
            if not n:
                return None
            return {
                'id': n.id,
                'numero_note': n.numero_note,
                'type_note': n.type_note,
                'montant': n.montant,
                'motif': n.motif,
                'sinistre_id': n.sinistre_id,
                'reglement_origine_id': n.reglement_origine_id,
                'date_creation': n.date_creation.isoformat() if n.date_creation else None,
            }
        except Exception as e:
            self.session.rollback()
            raise e

    def creer_note_credit(self, data: Dict[str, Any]) -> Optional['LometaNoteCredit']:
        """Crée une note de crédit"""
        try:
            from addons.sinistres.models.reglement import LometaNoteCredit
            if not data.get('numero_note'):
                data['numero_note'] = self.generate_numero("NC", LometaNoteCredit, 'numero_note')
            
            note = LometaNoteCredit(**data)
            self.session.add(note)
            self.session.commit()
            return note
        except Exception as e:
            self.session.rollback()
            raise e

    # ============================================================
    # RÈGLEMENTS PAR ÉVALUATION (nouvelle FK)
    # ============================================================

    def get_reglements_by_evaluation(self, evaluation_id: int) -> List[LometaReglement]:
        """Récupère tous les règlements liés à une évaluation"""
        try:
            return self.session.query(LometaReglement).filter(
                LometaReglement.evaluation_id == evaluation_id,
                LometaReglement.is_active == True
            ).order_by(LometaReglement.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

    # ============================================================
    # LOT PAR NUMÉRO (nouveau)
    # ============================================================

    def get_comptes_bancaires_by_banque(self, banque_id: int) -> List[dict]:
        """
        Récupère les comptes bancaires actifs d'une banque donnée.
        
        Args:
            banque_id: ID de la banque
        
        Returns:
            Liste des comptes bancaires (dict sérialisés)
        """
        try:
            from addons.sinistres.models.reglement import LometaCompteBancaire
            
            comptes = self.session.query(LometaCompteBancaire).filter(
                LometaCompteBancaire.banque == banque_id,
                LometaCompteBancaire.est_actif == True,
                LometaCompteBancaire.is_active == True,
            ).order_by(LometaCompteBancaire.libelle).all()
            
            return [
                {
                    'id': c.id,
                    'code_banque': c.code_banque,
                    'libelle': c.libelle,
                    'iban': c.iban,
                    'bic_swift': c.bic_swift,
                    'devise': c.devise,
                    'banque': c.banque,
                    'agence': getattr(c, 'agence', None),
                    'solde': c.solde,
                    'est_actif': c.est_actif,
                    'est_par_defaut': getattr(c, 'est_par_defaut', False),
                    'statut': getattr(c, 'statut', None),
                }
                for c in comptes
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_lot_by_numero(self, numero: str) -> Optional['LometaLotPaiement']:
        """Récupère un lot par son numéro"""
        try:
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.numero_lot == numero,
                LometaLotPaiement.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_lots(self) -> List[LometaLotPaiement]:
        """Récupère tous les lots de paiement"""
        try:
            return self.session.query(LometaLotPaiement).filter(
                LometaLotPaiement.is_active == True
            ).order_by(LometaLotPaiement.date_creation.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    # ============================================================
    # TRAITEMENT ET COMPTABILISATION DES LOTS
    # ============================================================

    def traiter_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional['LometaLotPaiement']:
        """Traite un lot (passage en TRAITE)"""
        try:
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            if lot.statut != "VALIDE":
                raise ValueError("Seul un lot validé peut être traité")
            
            lot.statut = "TRAITE"
            lot.date_traitement = datetime.utcnow()
            lot.updated_at = datetime.utcnow()
            lot.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="TRAITEMENT_LOT",
                entite="LometaLotPaiement",
                entite_id=lot.id,
                entite_nom=lot.numero_lot,
                commentaire=f"Traitement du lot {lot.numero_lot}"
            )
            self.session.commit()
            return lot
        except Exception as e:
            self.session.rollback()
            raise e

    def comptabiliser_lot_paiement(self, lot_id: int, utilisateur_id: int) -> Optional['LometaLotPaiement']:
        """Comptabilise un lot"""
        try:
            lot = self.get_lot_paiement(lot_id)
            if not lot:
                raise ValueError("Lot non trouvé")
            if lot.statut != "TRAITE":
                raise ValueError("Seul un lot traité peut être comptabilisé")
            
            lot.statut = "COMPTABILISE"
            lot.date_comptabilisation = datetime.utcnow()
            lot.updated_at = datetime.utcnow()
            lot.updated_by = utilisateur_id
            
            for reg in lot.reglements:
                reg.est_comptabilise = True
                reg.date_comptabilisation = datetime.utcnow()
                reg.updated_at = datetime.utcnow()
                reg.updated_by = utilisateur_id
            
            self.session.commit()
            return lot
        except Exception as e:
            self.session.rollback()
            raise e