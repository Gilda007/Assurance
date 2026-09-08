# check_icons.py
import qtawesome as qta
from icons import ICONS

def check_icons():
    """Vérifie toutes les icônes du dictionnaire"""
    invalid_icons = []
    valid_icons = []
    
    for name, icon_path in ICONS.items():
        try:
            icon = qta.icon(icon_path)
            valid_icons.append(name)
            print(f"✅ {name}: {icon_path}")
        except Exception as e:
            invalid_icons.append(name)
            print(f"❌ {name}: {icon_path} - {e}")
    
    print("\n" + "="*50)
    print(f"Total: {len(ICONS)} icônes")
    print(f"✅ Valides: {len(valid_icons)}")
    print(f"❌ Invalides: {len(invalid_icons)}")
    
    if invalid_icons:
        print("\n⚠️ Icônes invalides à corriger:")
        for name in invalid_icons:
            print(f"  - {name}: {ICONS[name]}")

if __name__ == "__main__":
    check_icons()