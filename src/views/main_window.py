"""
Ventana principal de la aplicación con Top Navigation Bar.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import date
import sys
from pathlib import Path

# Asegurar que src está en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.qt import OperationsTableModel, SimulationsTableModel


class MainWindow(QMainWindow):
    """
    Ventana principal del Simulador Forward con Top Navigation Bar.
    
    Responsabilidades:
    - Contener los módulos principales (Forward, Settings)
    - Proveer navegación superior mediante botones
    - Conectar señales globales a métodos de actualización
    - Gestionar el ciclo de vida de la aplicación
    """
    
    def __init__(self, forward_view=None, settings_view=None, signals=None):
        """
        Inicializa la ventana principal.
        
        Args:
            forward_view: Instancia de ForwardView
            settings_view: Instancia de SettingsView
            signals: Instancia de AppSignals (señales globales)
        """
        super().__init__()
        
        self._forward_view = forward_view
        self._settings_view = settings_view
        self._signals = signals
        
        # Crear modelos de tabla
        self._operations_model = None
        self._simulations_model = None
        
        self._setup_ui()
        self._setup_table_models()
        self._connect_global_signals()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario con Top Navigation Bar."""
        self.setWindowTitle("Simulador de Negociación Forward")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (vertical)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === TOP NAVIGATION BAR ===
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
        # === MAIN CONTENT (QStackedWidget) ===
        self.stack = QStackedWidget()
        self.stack.setObjectName("MainContent")
        
        # Agregar los módulos al stack
        if self._forward_view:
            self.stack.addWidget(self._forward_view)
        else:
            # Widget placeholder si no hay forward_view
            placeholder_forward = QWidget()
            self.stack.addWidget(placeholder_forward)
        
        if self._settings_view:
            self.stack.addWidget(self._settings_view)
        else:
            # Widget placeholder si no hay settings_view
            placeholder_settings = QWidget()
            self.stack.addWidget(placeholder_settings)
        
        main_layout.addWidget(self.stack)
        
        # Estado inicial: Mostrar módulo Forward
        self.switch_module(0)
        
        # Aplicar estilos
        self._apply_styles()
        
        print("[MainWindow] UI configurada con Top Navigation Bar")
    
    def _create_top_bar(self) -> QFrame:
        """
        Crea la barra superior de navegación.
        
        Returns:
            QFrame con los botones de navegación
        """
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(50)
        
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(10, 5, 10, 5)
        top_bar_layout.setSpacing(20)
        
        # Fuente para los botones
        font_btn = QFont()
        font_btn.setPointSize(10)
        
        # Botón: Simulación Forward
        self.btnForward = QPushButton("📊 Simulación Forward")
        self.btnForward.setFont(font_btn)
        self.btnForward.setCheckable(True)
        self.btnForward.setObjectName("btnForward")
        self.btnForward.setCursor(Qt.PointingHandCursor)
        self.btnForward.clicked.connect(lambda: self.switch_module(0))
        
        # Botón: Configuraciones
        self.btnSettings = QPushButton("⚙️ Configuraciones")
        self.btnSettings.setFont(font_btn)
        self.btnSettings.setCheckable(True)
        self.btnSettings.setObjectName("btnSettings")
        self.btnSettings.setCursor(Qt.PointingHandCursor)
        self.btnSettings.clicked.connect(lambda: self.switch_module(1))
        
        # Añadir botones al layout
        top_bar_layout.addWidget(self.btnForward, alignment=Qt.AlignLeft)
        top_bar_layout.addWidget(self.btnSettings, alignment=Qt.AlignLeft)
        top_bar_layout.addStretch()  # Empuja los botones a la izquierda
        
        return top_bar
    
    def switch_module(self, index: int):
        """
        Cambia entre módulos y actualiza estado de los botones.
        
        Args:
            index: Índice del módulo (0=Forward, 1=Settings)
        """
        self.stack.setCurrentIndex(index)
        
        # Actualizar estado de los botones
        self.btnForward.setChecked(index == 0)
        self.btnSettings.setChecked(index == 1)
        
        # Log del cambio
        module_name = "Forward" if index == 0 else "Settings"
        print(f"[MainWindow] Cambiado a módulo: {module_name}")
    
    def _apply_styles(self):
        """Aplica los estilos CSS a la ventana principal."""
        self.setStyleSheet("""
            /* Top Navigation Bar */
            #TopBar {
                background-color: #f8f9fa;
                border-bottom: 2px solid #d0d0d0;
            }
            
            /* Botones de navegación */
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                color: #333333;
            }
            
            QPushButton:hover {
                background-color: #e6e9ed;
            }
            
            QPushButton:checked {
                background-color: #0078D7;
                color: white;
                font-weight: bold;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            /* Main Content Area */
            #MainContent {
                background-color: white;
            }
        """)
    
    def _setup_table_models(self):
        """Crea e inyecta los modelos de tabla a la vista."""
        if not self._forward_view:
            return
        
        print("[MainWindow] Creando modelos de tabla...")
        
        # Crear modelo de operaciones vigentes (solo lectura)
        self._operations_model = OperationsTableModel()
        print(f"   [OK] OperationsTableModel creado con {self._operations_model.rowCount()} filas")
        
        # Crear modelo de simulaciones (editable)
        self._simulations_model = SimulationsTableModel()
        print(f"   [OK] SimulationsTableModel creado con {self._simulations_model.rowCount()} filas")
        
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
