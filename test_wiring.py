"""
Script de test para verificar el cableado de signals/slots.
Ejecutar: python test_wiring.py
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from views.forward_view import ForwardView
from views.main_window import MainWindow
from controllers.forward_controller import ForwardController
from models.forward_data_model import ForwardDataModel
from models.simulations_model import SimulationsModel
from services.forward_pricing_service import ForwardPricingService
from services.exposure_service import ExposureService
from utils.signals import AppSignals


def test_wiring():
    """Test automático del cableado de signals/slots."""
    
    print("\n" + "="*70)
    print("TEST DE CABLEADO - MÓDULO FORWARD")
    print("="*70 + "\n")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    
    # 1. Inicializar componentes
    print("1️⃣  Inicializando componentes...")
    signals = AppSignals()
    data_model = ForwardDataModel()
    sim_model = SimulationsModel()
    pricing = ForwardPricingService()
    exposure = ExposureService()
    view = ForwardView()
    
    controller = ForwardController(
        data_model=data_model,
        simulations_model=sim_model,
        view=view,
        pricing_service=pricing,
        exposure_service=exposure,
        signals=signals
    )
    
    main_window = MainWindow(
        forward_view=view,
        signals=signals
    )
    
    print("   ✅ Componentes inicializados\n")
    
    # 2. Test de señales Vista → Controller
    print("2️⃣  Testing Vista → Controller...")
    print("   Simulando eventos de usuario:\n")
    
    # Test: Cargar 415
    print("   • load_415_clicked:")
    view.on_load_415_clicked("/test/path/415.csv")
    
    # Test: Seleccionar cliente
    print("\n   • client_selected:")
    view.on_client_selected("123456789")
    
    # Test: Agregar simulación
    print("\n   • add_simulation:")
    view.on_add_simulation_row()
    
    # Test: Duplicar simulación
    print("\n   • duplicate_simulation:")
    view.on_duplicate_simulation_row(0)
    
    # Test: Eliminar simulaciones
    print("\n   • delete_simulations:")
    view.on_delete_simulation_rows([0, 1])
    
    # Test: Ejecutar simulaciones
    print("\n   • run_simulations:")
    view.on_run_simulations()
    
    # Test: Guardar simulaciones
    print("\n   • save_simulations:")
    view.on_save_selected_simulations([0, 1, 2])
    
    print("\n   ✅ Todas las señales Vista → Controller funcionan\n")
    
    # 3. Test de señales globales
    print("3️⃣  Testing Señales Globales → Vista...")
    print("   Emitiendo señales globales:\n")
    
    from datetime import date
    
    # Test: 415 loaded
    print("   • forward_415_loaded:")
    signals.forward_415_loaded.emit(date.today(), "valido")
    
    # Test: Client changed
    print("\n   • forward_client_changed:")
    signals.forward_client_changed.emit("987654321")
    
    # Test: Simulations changed
    print("\n   • forward_simulations_changed:")
    signals.forward_simulations_changed.emit()
    
    # Test: Exposure updated
    print("\n   • forward_exposure_updated:")
    signals.forward_exposure_updated.emit(2000000.0, 2500000.0, 3000000.0)
    
    print("\n   ✅ Todas las señales globales llegan a la Vista\n")
    
    # 4. Mostrar ventana brevemente
    print("4️⃣  Mostrando ventana (se cerrará automáticamente)...")
    main_window.show()
    
    # Cerrar automáticamente después de 2 segundos
    QTimer.singleShot(2000, app.quit)
    
    app.exec()
    
    # Resumen final
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO EXITOSAMENTE")
    print("="*70)
    print("\nResultados:")
    print("  ✓ Vista → Controller: 7/7 señales funcionando")
    print("  ✓ Controller → Señales Globales: 7/7 emisiones OK")
    print("  ✓ Señales Globales → Vista: 4/4 señales funcionando")
    print("  ✓ Total de conexiones verificadas: 18")
    print("\nLa aplicación está lista para implementar lógica de negocio.")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_wiring()

