from addons.Automobiles.controllers.automobile_controller import VehicleController, AuditVehicleLog
from addons.Automobiles.controllers.contacts_controller import ContactController, ContactAuditLog
from addons.Automobiles.controllers.contract_controller import ContractController
from addons.Automobiles.controllers.flotte_controller import FleetController
from addons.Automobiles.controllers.automobile_tarif_controller import CompagnieController
from addons.


class AutomobileMainController:
    def __init__(self, session, current_user_id):
        # On centralise tous les sous-contrôleurs ici
        self.vehicles = VehicleController(session)
        self.contacts = ContactController(session, current_user_id)
        self.fleets = FleetController(session, current_user_id)
        self.tarifs = CompagnieController(session, current_user_id)
        self.contracts = ContractController()
        
        # On garde la session accessible au cas où
        self.session = session