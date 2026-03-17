# addons/contract_manager/controllers/contract_controller.py

class ContractController:
    def calculate_totals(self, prime_nette, has_vignette=True):
        """
        Calcule les taxes selon les règles fiscales en vigueur.
        """
        tva_rate = 0.1925 # Exemple : 19.25%
        dta_fixe = 2000   # Exemple de montant fixe pour la DTA
        
        tva = prime_nette * tva_rate
        vignette = 10000 if has_vignette else 0 # Selon la puissance fiscale (à lier au véhicule)
        
        total_ttc = prime_nette + tva + dta_fixe + vignette
        
        return {
            "tva": round(tva, 2),
            "dta": dta_fixe,
            "vignette": vignette,
            "total": round(total_ttc, 2)
        }