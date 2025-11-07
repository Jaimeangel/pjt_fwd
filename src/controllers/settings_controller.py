"""
Controlador para el módulo Settings.
Coordina entre el modelo y la vista de configuración, conectando cambios en tiempo real.
"""

from typing import Optional, Dict, Any


class SettingsController:
    """
    Controlador del módulo Settings.
    
    Responsabilidades:
    - Coordinar entre SettingsModel y SettingsView
    - Conectar cambios de inputs con métodos del modelo
    - Inicializar vista con valores del modelo
    - Propagar cambios automáticamente mediante señales Qt
    """
    
    def __init__(self, model=None, view=None):
        """
        Inicializa el controlador Settings.
        
        Args:
            model: Instancia de SettingsModel
            view: Instancia de SettingsView
        """
        self._model = model
        self._view = view
        
        print("[SettingsController] Inicializando...")
        
        # Cargar valores iniciales del modelo en la vista
        self._load_initial_values()
        
        # Conectar señales de la vista al modelo
        self._connect_signals()
        
        print("[SettingsController] Inicializado correctamente")
    
    def _load_initial_values(self) -> None:
        """
        Carga los valores iniciales del modelo en la vista.
        Bloquea señales durante la carga para evitar actualizaciones circulares.
        """
        if not self._model or not self._view:
            return
        
        print("[SettingsController] Cargando valores iniciales del modelo...")
        
        # Bloquear señales temporalmente
        self._view.inpPatrimonio.blockSignals(True)
        self._view.inpTRM.blockSignals(True)
        self._view.inpLimEndeud.blockSignals(True)
        self._view.inpLimEntFin.blockSignals(True)
        self._view.inpColchon.blockSignals(True)
        
        # Cargar valores
        self._view.inpPatrimonio.setValue(self._model.patrimonio())
        self._view.inpTRM.setValue(self._model.trm())
        self._view.inpLimEndeud.setValue(self._model.lim_endeud())
        self._view.inpLimEntFin.setValue(self._model.lim_entfin())
        self._view.inpColchon.setValue(self._model.colchon())
        
        # Desbloquear señales
        self._view.inpPatrimonio.blockSignals(False)
        self._view.inpTRM.blockSignals(False)
        self._view.inpLimEndeud.blockSignals(False)
        self._view.inpLimEntFin.blockSignals(False)
        self._view.inpColchon.blockSignals(False)
        
        print(f"   Patrimonio: $ {self._model.patrimonio():,.2f}")
        print(f"   TRM: $ {self._model.trm():,.2f}")
    
    def _connect_signals(self) -> None:
        """
        Conecta las señales de la vista con los métodos del modelo.
        Los cambios en los inputs se propagan automáticamente al modelo,
        que a su vez emite señales para actualizar otras vistas.
        """
        if not self._model or not self._view:
            return
        
        print("[SettingsController] Conectando señales...")
        
        # Conectar cambios de Parámetros Generales
        self._view.inpPatrimonio.valueChanged.connect(self._model.set_patrimonio)
        self._view.inpTRM.valueChanged.connect(self._model.set_trm)
        
        # Conectar cambios de Parámetros Normativos
        self._view.inpLimEndeud.valueChanged.connect(self._model.set_lim_endeud)
        self._view.inpLimEntFin.valueChanged.connect(self._model.set_lim_entfin)
        self._view.inpColchon.valueChanged.connect(self._model.set_colchon)
        
        print("   ✓ Patrimonio.valueChanged → model.set_patrimonio()")
        print("   ✓ TRM.valueChanged → model.set_trm()")
        print("   ✓ LimEndeud.valueChanged → model.set_lim_endeud()")
        print("   ✓ LimEntFin.valueChanged → model.set_lim_entfin()")
        print("   ✓ Colchon.valueChanged → model.set_colchon()")
    
    def handle_setting_change(self, key: str, value: Any) -> None:
        """
        Maneja el cambio de una configuración.
        
        Args:
            key: Clave de la configuración
            value: Nuevo valor
        """
        pass
    
    def handle_save_request(self) -> None:
        """
        Maneja la solicitud de guardar configuraciones.
        """
        pass
    
    def handle_reset_request(self) -> None:
        """
        Maneja la solicitud de restablecer configuraciones.
        """
        pass
    
    def load_settings(self) -> None:
        """
        Carga las configuraciones en la vista.
        """
        pass
    
    def save_settings(self) -> bool:
        """
        Guarda las configuraciones actuales.
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        pass
    
    def apply_settings(self) -> None:
        """
        Aplica las configuraciones al sistema.
        """
        pass
    
    def reset_to_defaults(self) -> None:
        """
        Restablece las configuraciones a valores predeterminados.
        """
        pass
    
    def validate_setting(self, key: str, value: Any) -> tuple[bool, str]:
        """
        Valida un valor de configuración.
        
        Args:
            key: Clave de la configuración
            value: Valor a validar
            
        Returns:
            Tupla (es_valido, mensaje)
        """
        pass
    
    def export_settings(self, file_path: str) -> bool:
        """
        Exporta las configuraciones a un archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si se exportó correctamente, False en caso contrario
        """
        pass
    
    def import_settings(self, file_path: str) -> bool:
        """
        Importa configuraciones desde un archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si se importó correctamente, False en caso contrario
        """
        pass

