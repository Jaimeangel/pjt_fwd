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
        Carga los valores iniciales del modelo en la vista SOLO si existen (no son None).
        Bloquea señales durante la carga para evitar actualizaciones circulares.
        """
        if not self._model or not self._view:
            return
        
        print("[SettingsController] Cargando valores iniciales del modelo...")
        
        # Bloquear señales temporalmente
        self._view.trm_cop_usd.blockSignals(True)
        self._view.trm_eur_usd.blockSignals(True)
        self._view.inpLimEndeud.blockSignals(True)
        self._view.inpLimEntFin.blockSignals(True)
        
        # Cargar valores SOLO si no son None
        trm_cop = self._model.trm_cop_usd()
        if trm_cop is not None:
            self._view.trm_cop_usd.setText(f"{trm_cop:.6f}")
            print(f"   TRM COP/USD: {trm_cop:,.6f}")
        else:
            self._view.trm_cop_usd.clear()
            print("   TRM COP/USD: (no configurado)")
        
        trm_eur = self._model.trm_eur_usd()
        if trm_eur is not None:
            self._view.trm_eur_usd.setText(f"{trm_eur:.6f}")
            print(f"   TRM EUR/USD: {trm_eur:,.6f}")
        else:
            self._view.trm_eur_usd.clear()
            print("   TRM EUR/USD: (no configurado)")
        
        # Parámetros normativos (pueden o no tener defaults)
        lim_end = self._model.lim_endeud()
        if lim_end is not None:
            self._view.inpLimEndeud.setValue(lim_end)
        else:
            self._view.inpLimEndeud.clear()
        
        lim_ent = self._model.lim_entfin()
        if lim_ent is not None:
            self._view.inpLimEntFin.setValue(lim_ent)
        else:
            self._view.inpLimEntFin.clear()
        
        # Desbloquear señales
        self._view.trm_cop_usd.blockSignals(False)
        self._view.trm_eur_usd.blockSignals(False)
        self._view.inpLimEndeud.blockSignals(False)
        self._view.inpLimEntFin.blockSignals(False)
    
    def _connect_signals(self) -> None:
        """
        Conecta las señales de la vista con los métodos del modelo.
        Los cambios en los inputs se propagan automáticamente al modelo,
        que a su vez emite señales para actualizar otras vistas.
        """
        if not self._model or not self._view:
            return
        
        print("[SettingsController] Conectando señales...")
        
        # Conectar cambios de Parámetros Generales (TRMs)
        self._view.trm_cop_usd.textChanged.connect(self._model.set_trm_cop_usd)
        self._view.trm_eur_usd.textChanged.connect(self._model.set_trm_eur_usd)
        
        # Conectar cambios de Parámetros Normativos
        self._view.inpLimEndeud.valueChanged.connect(self._model.set_lim_endeud)
        self._view.inpLimEntFin.valueChanged.connect(self._model.set_lim_entfin)
        
        # Conectar señales del modelo para recalcular tabla cuando cambie TRM
        self._model.trm_cop_usdChanged.connect(self._update_lineas_credito_with_trm)
        self._model.trm_eur_usdChanged.connect(self._update_lineas_credito_with_trm)
        
        print("   ✓ trm_cop_usd.textChanged → model.set_trm_cop_usd()")
        print("   ✓ trm_eur_usd.textChanged → model.set_trm_eur_usd()")
        print("   ✓ LimEndeud.valueChanged → model.set_lim_endeud()")
        print("   ✓ LimEntFin.valueChanged → model.set_lim_entfin()")
        print("   ✓ trm_cop_usdChanged → _update_lineas_credito_with_trm()")
        print("   ✓ trm_eur_usdChanged → _update_lineas_credito_with_trm()")
    
    def _update_lineas_credito_with_trm(self, trm_value) -> None:
        """
        Recalcula las columnas dependientes de TRM en la tabla de líneas de crédito.
        
        Args:
            trm_value: Nuevo valor de TRM (float o None)
        """
        if not self._view or not self._model:
            return
        
        # Solo recalcular si hay datos cargados
        if self._view.df_lineas_credito is None or self._view.df_lineas_credito.empty:
            print("[SettingsController] No hay líneas de crédito cargadas, no se recalcula")
            return
        
        print(f"[SettingsController] Recalculando columnas con TRM actualizado...")
        
        df = self._view.df_lineas_credito.copy()
        
        trm_cop_usd = self._model.trm_cop_usd()
        trm_eur_usd = self._model.trm_eur_usd()
        
        # Recalcular LLL 25% (EUR) si TRM COP/USD está disponible
        if "LLL 25% (COP)" in df.columns:
            if trm_cop_usd and trm_cop_usd > 0:
                df["LLL 25% (EUR)"] = df["LLL 25% (COP)"] / trm_cop_usd
                print(f"   ✓ LLL 25% (EUR) recalculado con TRM COP/USD = {trm_cop_usd:,.6f}")
            else:
                df["LLL 25% (EUR)"] = None
                print(f"   ⚠️  LLL 25% (EUR) limpiado (TRM COP/USD no disponible)")
        
        # Recalcular COP (MM) si TRM COP/USD está disponible
        if "EUR (MM)" in df.columns:
            if trm_cop_usd and trm_cop_usd > 0:
                df["COP (MM)"] = df["EUR (MM)"] * trm_cop_usd
                print(f"   ✓ COP (MM) recalculado con TRM COP/USD = {trm_cop_usd:,.6f}")
            else:
                df["COP (MM)"] = None
                print(f"   ⚠️  COP (MM) limpiado (TRM COP/USD no disponible)")
        
        # Actualizar el DataFrame en la vista y en el modelo
        self._view.df_lineas_credito = df
        self._model.set_lineas_credito(df)
        
        # Actualizar la tabla en la UI
        self._view.mostrar_lineas_credito(df)
        
        print(f"   ✅ Tabla actualizada con nuevos valores de TRM")
    
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

