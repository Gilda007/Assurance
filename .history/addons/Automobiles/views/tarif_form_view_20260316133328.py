def on_add_tarif_click(self):
    # Appel du dialogue (Hérite de QDialog maintenant)
    dialog = CompanyTariffView(self, self.controller, self.user)
    
    # exec_() ne plantera plus
    if dialog.exec_():
        data = dialog.get_data()
        result = self.controller.tarifs.create_tarif(data)
        if result:
            AlertManager.show_success(self, "Succès", "Le barème a été enregistré.")
            # self.refresh_list()