"""
Ventana principal de la aplicación.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from datetime import date
import sys
from pathlib import Path

# Asegurar que src está en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.qt import OperationsTableModel, SimulationsTableModel


class MainWindow(QMainWindow):
    """
    Ventana principal del Simulador Forward.
    
    Responsabilidades:
    - Contener la vista del módulo Forward
    - Conectar señales globales a métodos de actualización de la vista
    - Gestionar el ciclo de vida de la aplicación
    """
    
    def __init__(self, forward_view=None, signals=None):
        """
        Inicializa la ventana principal.
        
        Args:
            forward_view: Instancia de ForwardView
            signals: Instancia de AppSignals (señales globales)
        """
        super().__init__()
        
        self._forward_view = forward_view
        self._signals = signals
        
        # Crear modelos de tabla
        self._operations_model = None
        self._simulations_model = None
        
        self._setup_ui()
        self._setup_table_models()
        self._connect_global_signals()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Simulador Forward - MVC Demo")
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Agregar ForwardView si existe
        if self._forward_view:
            layout.addWidget(self._forward_view)
        
        print("[MainWindow] UI configurada")
    
    def _setup_table_models(self):
        """Crea e inyecta los modelos de tabla a la vista."""
        if not self._forward_view:
            return
        
        print("[MainWindow] Creando modelos de tabla...")
        
        # Crear modelo de operaciones vigentes (solo lectura)
        self._operations_model = OperationsTableModel()
        print(f"   ✓ OperationsTableModel creado con {self._operations_model.rowCount()} filas")
        
        # Crear modelo de simulaciones (editable)
        self._simulations_model = SimulationsTableModel()
        print(f"   ✓ SimulationsTableModel creado con {self._simulations_model.rowCount()} filas")
        
        # Conectar modelos a la vista
        self._forward_view.set_operations_table(self._operations_model)
        self._forward_view.set_simulations_table(self._simulations_model)
        
        print("[MainWindow] Modelos de tabla conectados a la vista")
    
    def _connect_global_signals(self):
        """Conecta las señales globales a los métodos de actualización de la vista."""
        if not self._signals or not self._forward_view:
            return
        
        # Señal: 415_loaded -> actualizar info básica
        self._signals.forward_415_loaded.connect(self._on_415_loaded)
        
        # Señal: client_changed -> actualizar límites, tabla ops, chart
        self._signals.forward_client_changed.connect(self._on_client_changed)
        
        # Señal: simulations_changed -> actualizar tabla sims, exposición
        self._signals.forward_simulations_changed.connect(self._on_simulations_changed)
        
        # Señal: exposure_updated -> actualizar exposición y chart
        self._signals.forward_exposure_updated.connect(self._on_exposure_updated)
        
        print("[MainWindow] Señales globales conectadas")
    
    # Handlers de señales globales (con datos dummy)
    
    def _on_415_loaded(self, corte_415: date, estado_415: str):
        """
        Handler para señal forward_415_loaded.
        
        Args:
            corte_415: Fecha de corte del 415
            estado_415: Estado del archivo
        """
        print(f"[MainWindow] _on_415_loaded: corte={corte_415}, estado={estado_415}")
        
        # Actualizar vista con datos dummy
        patrimonio_dummy = 50000000000.0  # 50 mil millones
        trm_dummy = 4200.50
        
        self._forward_view.show_basic_info(
            patrimonio=patrimonio_dummy,
            trm=trm_dummy,
            corte_415=corte_415,
            estado_415=estado_415
        )
    
    def _on_client_changed(self, nit: str):
        """
        Handler para señal forward_client_changed.
        
        Args:
            nit: NIT del cliente seleccionado
        """
        print(f"[MainWindow] _on_client_changed: nit={nit}")
        
        # Actualizar límites del cliente (datos dummy)
        linea_dummy = 5000000.0  # 5 millones
        colchon_pct_dummy = 0.10  # 10%
        limite_max_dummy = 5500000.0  # 5.5 millones
        
        self._forward_view.show_client_limits(
            linea=linea_dummy,
            colchon_pct=colchon_pct_dummy,
            limite_max=limite_max_dummy
        )
        
        # Actualizar tabla de operaciones vigentes (modelo dummy)
        self._forward_view.set_operations_table(model=None)
        
        # Actualizar chart (datos dummy)
        chart_data_dummy = {
            'limite_max': limite_max_dummy,
            'outstanding': 1000000.0,
            'total_con_simulacion': 1500000.0
        }
        self._forward_view.update_chart(chart_data_dummy)
    
    def _on_simulations_changed(self):
        """Handler para señal forward_simulations_changed."""
        print("[MainWindow] _on_simulations_changed")
        
        # 🔒 NO actualizar exposición aquí.
        # Agregar/eliminar simulaciones no debe modificar los labels de exposición.
        # Solo el botón "Simular" actualiza Outstanding + simulación.
    
    def _on_exposure_updated(self, outstanding: float, 
                            total_con_simulacion: float,
                            disponibilidad: float):
        """
        Handler para señal forward_exposure_updated.
        
        Args:
            outstanding: Exposición actual
            total_con_simulacion: Exposición total con simulaciones
            disponibilidad: Límite disponible
        """
        print(f"[MainWindow] _on_exposure_updated: outstanding={outstanding}, "
              f"total={total_con_simulacion}, disponibilidad={disponibilidad}")
        
        # Actualizar exposición en la vista
        self._forward_view.show_exposure(
            outstanding=outstanding,
            total_con_simulacion=total_con_simulacion,
            disponibilidad=disponibilidad
        )
        
        # Actualizar chart con nuevos datos
        chart_data = {
            'limite_max': 5500000.0,
            'outstanding': outstanding,
            'total_con_simulacion': total_con_simulacion
        }
        self._forward_view.update_chart(chart_data)
