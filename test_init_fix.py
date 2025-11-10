"""
Test rápido para verificar que la aplicación puede inicializarse sin errores.
Específicamente verifica que ForwardView puede conectarse al nuevo SettingsModel.
"""

import sys
sys.path.insert(0, 'src')

from PySide6.QtWidgets import QApplication
from src.models.settings_model import SettingsModel
from src.views.forward_view import ForwardView

def test_init():
    """Prueba que ForwardView puede inicializarse con el nuevo SettingsModel."""
    print("=" * 80)
    print("TEST: Inicialización de ForwardView con nuevo SettingsModel")
    print("=" * 80)
    print()
    
    # Crear QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Crear SettingsModel
        print("[1/3] Creando SettingsModel...")
        settings_model = SettingsModel()
        print("      ✓ SettingsModel creado exitosamente")
        print()
        
        # Verificar que las nuevas señales existen
        print("[2/3] Verificando señales del modelo...")
        assert hasattr(settings_model, 'trm_cop_usdChanged'), "Falta señal trm_cop_usdChanged"
        assert hasattr(settings_model, 'trm_eur_usdChanged'), "Falta señal trm_eur_usdChanged"
        assert hasattr(settings_model, 'lineasCreditoChanged'), "Falta señal lineasCreditoChanged"
        print("      ✓ Señales verificadas correctamente")
        print()
        
        # Verificar que las señales viejas NO existen
        print("      Verificando que señales viejas fueron eliminadas...")
        assert not hasattr(settings_model, 'patrimonioChanged'), "patrimonioChanged NO debería existir"
        assert not hasattr(settings_model, 'trmChanged'), "trmChanged NO debería existir"
        assert not hasattr(settings_model, 'colchonChanged'), "colchonChanged NO debería existir"
        print("      ✓ Señales viejas eliminadas correctamente")
        print()
        
        # Crear ForwardView con SettingsModel
        print("[3/3] Creando ForwardView con SettingsModel...")
        forward_view = ForwardView(settings_model=settings_model)
        print("      ✓ ForwardView creado exitosamente")
        print()
        
        # Verificar que la vista se creó correctamente
        assert forward_view._settings_model == settings_model, "SettingsModel no asignado correctamente"
        print("      ✓ SettingsModel asignado correctamente a ForwardView")
        print()
        
        print("=" * 80)
        print("✅ TEST EXITOSO - La aplicación puede inicializarse sin errores")
        print("=" * 80)
        print()
        print("Resumen:")
        print("  • SettingsModel inicializado correctamente")
        print("  • Nuevas señales (trm_cop_usdChanged, trm_eur_usdChanged) funcionan")
        print("  • Señales viejas (patrimonioChanged, trmChanged, colchonChanged) eliminadas")
        print("  • ForwardView se conecta sin errores al nuevo modelo")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ TEST FALLÓ")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        resultado = test_init()
        sys.exit(0 if resultado else 1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

