"""
Señales personalizadas de la aplicación.
"""

from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    """
    Señales personalizadas de la aplicación.
    
    Responsabilidades:
    - Definir señales globales de la aplicación
    - Facilitar comunicación entre componentes
    """
    
    # Señales del módulo Forward
    
    # Emitida cuando se carga un archivo 415
    forward_415_loaded = Signal(object, str)  # (corte_415, estado_415)
    
    # Emitida cuando se cambia el cliente seleccionado
    forward_client_changed = Signal(str)  # nit
    
    # Emitida cuando cambian las simulaciones
    forward_simulations_changed = Signal()
    
    # Emitida cuando se actualiza la exposición
    forward_exposure_updated = Signal(float, float, float)  # (outstanding, total_con_sim, disponibilidad)
    
    def __init__(self):
        """Inicializa las señales de la aplicación."""
        super().__init__()
