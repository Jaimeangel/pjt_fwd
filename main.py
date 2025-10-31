"""
Punto de entrada principal del Simulador Forward.
Inicializa la aplicación y carga la ventana principal.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar componentes del módulo Forward
from views.forward_view import ForwardView
from views.main_window import MainWindow
from controllers.forward_controller import ForwardController
from models.forward_data_model import ForwardDataModel
from models.simulations_model import SimulationsModel
from services.forward_pricing_service import ForwardPricingService
from services.exposure_service import ExposureService
from services.client_service import ClientService
from utils.signals import AppSignals


class SimuladorForwardApp:
    """
    Clase principal de la aplicación Simulador Forward.
    
    Responsabilidades:
    - Inicializar la aplicación Qt
    - Crear e instanciar componentes principales (MVC)
    - Realizar el wiring de signals/slots
    - Gestionar el ciclo de vida de la aplicación
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.app = None
        self.main_window = None
        self.signals = None
        self.forward_view = None
        self.forward_controller = None
        
        # Modelos
        self.forward_data_model = None
        self.simulations_model = None
        
        # Servicios
        self.pricing_service = None
        self.exposure_service = None
        self.client_service = None
        
        self._initialize_application()
    
    def _initialize_application(self) -> None:
        """Inicializa los componentes de la aplicación."""
        print("\n" + "="*60)
        print("SIMULADOR FORWARD - INICIALIZACIÓN")
        print("="*60 + "\n")
        
        # 1. Crear aplicación Qt
        print("[App] Creando QApplication...")
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Simulador Forward")
        self.app.setOrganizationName("SimuladorForward")
        
        # 2. Crear señales globales
        print("[App] Creando señales globales...")
        self.signals = AppSignals()
        
        # 3. Crear modelos (stubs)
        print("[App] Creando modelos...")
        self.forward_data_model = ForwardDataModel()
        self.simulations_model = SimulationsModel()
        
        # 4. Crear servicios (con lógica mock)
        print("[App] Creando servicios...")
        self.pricing_service = ForwardPricingService()
        self.exposure_service = ExposureService()
        self.client_service = ClientService()
        
        # 5. Crear vista
        print("[App] Creando ForwardView...")
        self.forward_view = ForwardView()
        
        # 6. Crear ventana principal (conecta señales globales y crea modelos de tabla)
        print("[App] Creando MainWindow...")
        self.main_window = MainWindow(
            forward_view=self.forward_view,
            signals=self.signals
        )
        
        # 7. Crear controlador (conecta vista automáticamente y recibe modelos de tabla)
        print("[App] Creando ForwardController...")
        self.forward_controller = ForwardController(
            data_model=self.forward_data_model,
            simulations_model=self.simulations_model,
            view=self.forward_view,
            pricing_service=self.pricing_service,
            exposure_service=self.exposure_service,
            signals=self.signals,
            simulations_table_model=self.main_window._simulations_model,
            operations_table_model=self.main_window._operations_model,
            client_service=self.client_service
        )
        
        print("\n[App] ✅ Aplicación inicializada correctamente")
        print("\n" + "="*60)
        print("MAPA DE CONEXIONES:")
        print("="*60)
        print("Vista → Controller:")
        print("  - load_415_requested → controller.load_415()")
        print("  - client_selected → controller.select_client()")
        print("  - add_simulation_requested → controller.add_simulation()")
        print("  - duplicate_simulation_requested → controller.duplicate_simulation()")
        print("  - delete_simulations_requested → controller.delete_simulations()")
        print("  - run_simulations_requested → controller.run_simulations()")
        print("  - save_simulations_requested → controller.save_simulations()")
        print("\nController → Señales Globales → Vista:")
        print("  - forward_415_loaded → view.show_basic_info()")
        print("  - forward_client_changed → view.show_client_limits(), etc.")
        print("  - forward_simulations_changed → view.set_simulations_table(), etc.")
        print("  - forward_exposure_updated → view.show_exposure(), etc.")
        print("="*60 + "\n")
    
    def run(self) -> int:
        """
        Ejecuta la aplicación.
        
        Returns:
            Código de salida de la aplicación
        """
        print("[App] Mostrando ventana principal...")
        self.main_window.show()
        
        print("[App] Iniciando event loop...\n")
        print("="*60)
        print("APLICACIÓN EN EJECUCIÓN")
        print("="*60)
        print("Prueba hacer clic en los botones para ver el flujo de señales")
        print("="*60 + "\n")
        
        # Ejecutar loop de eventos
        return self.app.exec()
    
    def shutdown(self) -> None:
        """Cierra la aplicación de forma ordenada."""
        print("\n[App] Cerrando aplicación...")
        
        # Cerrar ventana principal
        if self.main_window:
            self.main_window.close()


def main():
    """Función principal de entrada."""
    # Nota: En PySide6 6.0+, high DPI scaling está habilitado por defecto
    # Los atributos AA_EnableHighDpiScaling y AA_UseHighDpiPixmaps están deprecated
    
    # Crear y ejecutar aplicación
    app = SimuladorForwardApp()
    exit_code = app.run()
    
    # Cerrar aplicación
    app.shutdown()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
