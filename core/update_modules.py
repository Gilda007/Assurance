"""Gestionnaire simple de mise à jour de modules en production."""
import json
from core.module_manager import ModuleManager


def sync_modules_from_registry(registry_file="module_registry.json"):
    """Cette commande synchronise et met à jour les modules locaux via le registre."""
    manager = ModuleManager()
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)

    actions = manager.sync_from_repository(registry)
    if not actions:
        print("Tous les modules sont à jour.")
        return

    for action in actions:
        print(f"Module {action['name']} -> {action['action']} vers {action['version']}")

    for remote in registry:
        if manager.update_available(remote.get("name"), remote):
            print(f"Mise à jour de {remote['name']} -> {remote['version']}")
            try:
                result = manager.install_or_update_module(remote)
                print(f"  OK: {result}")
            except Exception as e:
                print(f"  ERREUR sur {remote['name']}: {e}")

if __name__ == '__main__':
    sync_modules_from_registry()
if __name__ == '__main__':
    sync_modules_from_registry()