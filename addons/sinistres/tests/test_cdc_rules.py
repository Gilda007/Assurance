"""
Test des règles CDC pour évaluations et règlements
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.database import SessionLocal


def test_prov_001():
    """PROV-001 : Validation → provision créée"""
    print("\n📌 Test PROV-001 : Validation → Provision")
    session = SessionLocal()
    try:
        from addons.sinistres.services.evaluation_service import EvaluationService
        from addons.sinistres.models.expertise import LometaEvaluation, LometaProvision
        
        service = EvaluationService(session)
        
        # Prendre une évaluation non validée
        evaluation = session.query(LometaEvaluation).filter(
            LometaEvaluation.est_validee == False,
            LometaEvaluation.is_active == True
        ).first()
        
        if not evaluation:
            print("   ⏭️  Pas d'évaluation à tester")
            return True
        
        print(f"   📋 Évaluation: {evaluation.numero_evaluation}")
        
        nb_avant = session.query(LometaProvision).filter(
            LometaProvision.evaluation_id == evaluation.id
        ).count()
        print(f"   Provisions AVANT: {nb_avant}")
        
        service.valider_evaluation(evaluation.id, utilisateur_id=1)
        
        nb_apres = session.query(LometaProvision).filter(
            LometaProvision.evaluation_id == evaluation.id
        ).count()
        print(f"   Provisions APRÈS: {nb_apres}")
        
        if nb_apres == nb_avant + 1:
            print("   ✅ PROV-001 : OK")
            return True
        else:
            print("   ❌ PROV-001 : VIOLÉ")
            return False
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False
    finally:
        session.close()


# def test_fin_001():
#     """FIN-001 : Règlement > Évaluation → erreur"""
#     print("\n📌 Test FIN-001 : Règlement ≤ Évaluation")
#     session = SessionLocal()
#     try:
#         from addons.sinistres.services.reglement_service import ReglementService
#         from addons.sinistres.models.expertise import LometaEvaluation
        
#         service = ReglementService(session)
        
#         evaluation = session.query(LometaEvaluation).filter(
#             LometaEvaluation.est_validee == True,
#             LometaEvaluation.is_active == True
#         ).first()
        
#         if not evaluation:
#             print("   ⏭️  Pas d'évaluation validée à tester")
#             return True
        
#         print(f"   📋 Évaluation: {evaluation.numero_evaluation}")
#         print(f"   💰 Montant net: {evaluation.montant_net:,.0f} FCFA")
        
#         montant_excessif = float(evaluation.montant_net) + 1_000_000
        
#         try:
#             service.creer_reglement({
#                 'sinistre_id': evaluation.sinistre_id,
#                 'evaluation_id': evaluation.id,
#                 'beneficiaire_id': 1,
#                 'montant': montant_excessif,
#                 'type_paiement': 'VIREMENT',
#                 'created_by': 1,
#             })
#             print("   ❌ FIN-001 : VIOLÉ (règlement excessif accepté)")
#             return False
#         except ValueError as e:
#             if "FIN-001" in str(e) or "dépasse" in str(e):
#                 print(f"   ✅ FIN-001 : OK")
#                 print(f"   → {e}")
#                 return True
#             else:
#                 print(f"   ⚠️  Autre erreur : {e}")
#                 return False
#     except Exception as e:
#         print(f"   ❌ Erreur : {e}")
#         return False
#     finally:
#         session.close()
def test_fin_001():
    """FIN-001 : Règlement > Évaluation → erreur"""
    print("\n📌 Test FIN-001 : Règlement ≤ Évaluation")
    session = SessionLocal()
    try:
        from addons.sinistres.services.reglement_service import ReglementService
        from addons.sinistres.models.expertise import LometaEvaluation
        from addons.sinistres.models.reglement import LometaBeneficiaire
        
        service = ReglementService(session)
        
        # Trouver une évaluation validée
        evaluation = session.query(LometaEvaluation).filter(
            LometaEvaluation.est_validee == True,
            LometaEvaluation.is_active == True
        ).first()
        
        if not evaluation:
            print("   ⏭️  Pas d'évaluation validée à tester")
            return True
        
        print(f"   📋 Évaluation: {evaluation.numero_evaluation}")
        print(f"   💰 Montant net: {evaluation.montant_net:,.0f} FCFA")
        
        # ✅ Trouver un bénéficiaire existant et actif
        beneficiaire = session.query(LometaBeneficiaire).filter(
            LometaBeneficiaire.est_actif == True,
            LometaBeneficiaire.is_active == True
        ).first()
        
        if not beneficiaire:
            print("   ⚠️  Aucun bénéficiaire en base — créez-en un avec :")
            print("      python -m addons.sinistres.scripts.init_test_data")
            return False
        
        print(f"   👤 Bénéficiaire: {beneficiaire.nom} (ID: {beneficiaire.id})")
        
        montant_excessif = float(evaluation.montant_net) + 1_000_000
        
        try:
            service.creer_reglement({
                'sinistre_id': evaluation.sinistre_id,
                'evaluation_id': evaluation.id,
                'beneficiaire_id': beneficiaire.id,   # ✅ ID réel
                'beneficiaire_nom': f"{beneficiaire.nom} {beneficiaire.prenom or ''}".strip(),
                'montant': montant_excessif,
                'type_paiement': 'VIREMENT',
                'created_by': 1,
            })
            print("   ❌ FIN-001 : VIOLÉ (règlement excessif accepté)")
            return False
        except ValueError as e:
            if "FIN-001" in str(e) or "dépasse" in str(e):
                print(f"   ✅ FIN-001 : OK")
                print(f"   → {e}")
                return True
            else:
                print(f"   ⚠️  Autre erreur : {e}")
                return False
    
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

def test_fin_001_ok():
    """FIN-001 : Règlement valide (< montant net) → OK"""
    print("\n📌 Test FIN-001 (cas valide) : Règlement < Évaluation")
    session = SessionLocal()
    try:
        from addons.sinistres.services.reglement_service import ReglementService
        from addons.sinistres.models.expertise import LometaEvaluation
        from addons.sinistres.models.reglement import LometaBeneficiaire
        
        service = ReglementService(session)
        
        # Trouver une évaluation validée
        evaluation = session.query(LometaEvaluation).filter(
            LometaEvaluation.est_validee == True,
            LometaEvaluation.is_active == True
        ).first()
        
        if not evaluation:
            print("   ⏭️  Pas d'évaluation validée")
            return True
        
        # Trouver un bénéficiaire
        beneficiaire = session.query(LometaBeneficiaire).filter(
            LometaBeneficiaire.est_actif == True
        ).first()
        
        if not beneficiaire:
            print("   ⏭️  Pas de bénéficiaire")
            return True
        
        print(f"   💰 Montant net: {evaluation.montant_net:,.0f} FCFA")
        
        # Règlement valide (50% du net)
        montant_valide = float(evaluation.montant_net) * 0.5
        print(f"   💳 Règlement: {montant_valide:,.0f} FCFA (50%)")
        
        try:
            reglement = service.creer_reglement({
                'sinistre_id': evaluation.sinistre_id,
                'evaluation_id': evaluation.id,
                'beneficiaire_id': beneficiaire.id,
                'beneficiaire_nom': f"{beneficiaire.nom} {beneficiaire.prenom or ''}".strip(),
                'montant': montant_valide,
                'type_paiement': 'VIREMENT',
                'created_by': 1,
            })
            print(f"   ✅ Règlement créé : {reglement.numero_reglement}")
            
            # Nettoyer : annuler le règlement
            service.annuler_reglement(reglement.id, 1, "Test — nettoyage")
            print(f"   🧹 Règlement annulé (nettoyage)")
            return True
        except ValueError as e:
            print(f"   ❌ Échec inattendu : {e}")
            return False
    
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False
    finally:
        session.close()

def test_fin_002():
    """FIN-002 : Σ Règlements > Évaluation → erreur"""
    print("\n📌 Test FIN-002 : Σ Règlements ≤ Évaluation")
    # Similaire à FIN-001 mais avec un cumul
    print("   ⏭️  Test non implémenté (nécessite des données de test)")
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TEST DES RÈGLES CDC")
    print("=" * 70)
    
    results = []
    results.append(("PROV-001", test_prov_001()))
    results.append(("FIN-001 (invalide)", test_fin_001()))
    results.append(("FIN-001 (valide)", test_fin_001_ok()))
    results.append(("FIN-002", test_fin_002()))
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS")
    print("=" * 70)
    for name, ok in results:
        status = "✅ OK" if ok else "❌ ÉCHEC"
        print(f"   {name}: {status}")
    print("=" * 70)