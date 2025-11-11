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
    
    def __init__(self, view=None, model=None):
        """
        Inicializa el controlador Settings.
        
        Args:
            view: Instancia de SettingsView
            model: Instancia de SettingsModel
        """
        self._view = view
        self._model = model
        self._recalc_in_progress = False  # Flag para evitar bucles infinitos
        
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
        self._view.trm_cop_eur.blockSignals(True)
        # inpLimEndeud no requiere bloqueo (es no editable)
        
        # Cargar valores SOLO si no son None
        trm_cop_usd = self._model.trm_cop_usd()
        if trm_cop_usd is not None:
            self._view.trm_cop_usd.setText(f"{trm_cop_usd:.6f}")
            print(f"   TRM COP/USD: {trm_cop_usd:,.6f}")
        else:
            self._view.trm_cop_usd.clear()
            print("   TRM COP/USD: (no configurado)")
        
        trm_cop_eur = self._model.trm_cop_eur()
        if trm_cop_eur is not None:
            self._view.trm_cop_eur.setText(f"{trm_cop_eur:.6f}")
            print(f"   TRM COP/EUR: {trm_cop_eur:,.6f}")
        else:
            self._view.trm_cop_eur.clear()
            print("   TRM COP/EUR: (no configurado)")
        
        # Parámetros normativos son fijos (LLL=25%, Colchón=10%)
        print("   Parámetros normativos: valores fijos (no editables)")
        
        # Desbloquear señales
        self._view.trm_cop_usd.blockSignals(False)
        self._view.trm_cop_eur.blockSignals(False)
    
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
        self._view.trm_cop_eur.textChanged.connect(self._model.set_trm_cop_eur)
        
        # Parámetros Normativos son fijos (no requieren conexiones)
        
        # Conectar señales del modelo para recalcular tabla cuando cambie TRM COP/EUR
        self._model.trm_cop_eurChanged.connect(self._recalc_lineas_credito_with_trm)
        
        # Conectar señal de cambio en líneas de crédito para recalcular al cargar CSV
        self._model.lineasCreditoChanged.connect(self._on_lineas_credito_loaded)
        
        print("   ✓ trm_cop_usd.textChanged → model.set_trm_cop_usd()")
        print("   ✓ trm_cop_eur.textChanged → model.set_trm_cop_eur()")
        print("   ✓ Parámetros normativos: valores fijos (sin conexiones)")
        print("   ✓ trm_cop_eurChanged → _recalc_lineas_credito_with_trm()")
        print("   ✓ lineasCreditoChanged → _on_lineas_credito_loaded()")
    
    def _recalc_lineas_credito_with_trm(self, trm_cop_eur) -> None:
        """
        Recalcula las columnas derivadas en la tabla de líneas de crédito con la TRM COP/EUR.
        
        Fórmulas aplicadas:
        - COP (MM) = EUR (MM) × TRM (COP/EUR)
        - LLL 25% (EUR) = LLL 25% (COP) ÷ TRM (COP/EUR)
        
        Args:
            trm_cop_eur: Valor de TRM COP/EUR (float o None)
        """
        import pandas as pd
        
        # Evitar bucles infinitos
        if self._recalc_in_progress:
            return
        
        if not self._model:
            return
        
        df = self._model.lineas_credito_df
        
        # Solo recalcular si hay datos cargados
        if df is None or df.empty:
            print("[SettingsController] No hay líneas de crédito cargadas, no se recalcula")
            return
        
        # Marcar que estamos recalculando para evitar bucles
        self._recalc_in_progress = True
        
        print(f"[SettingsController] Recalculando columnas derivadas con TRM COP/EUR...")
        
        df = df.copy()
        
        # Helper para normalizar series numéricas a MM
        def _to_mm(series: pd.Series) -> pd.Series:
            """Convierte strings a float en MILLONES (MM); limpia separadores/espacios."""
            return (series.astype(str).str.strip()
                    .str.replace(r"[^\d,.\-]", "", regex=True)
                    .str.replace(",", "", regex=False)
                    .pipe(pd.to_numeric, errors="coerce"))
        
        # Validar TRM
        if trm_cop_eur is None or pd.isna(trm_cop_eur) or trm_cop_eur == 0:
            # Sin TRM: no recalcular derivados; preservar valores existentes
            print(f"   ⚠️  TRM COP/EUR no disponible o inválida, se preservan valores existentes")
            self._model.set_lineas_credito(df)
            if self._view:
                self._view.mostrar_lineas_credito(df)
            self._recalc_in_progress = False
            return
        
        # Asegurar que las columnas base existen
        for col in ["EUR (MM)", "LLL 25% (COP)"]:
            if col not in df.columns:
                df[col] = pd.NA
                print(f"   ⚠️  Columna '{col}' no encontrada, creada vacía")
        
        # Normalizar columnas base a números (MM)
        df["EUR (MM)"] = _to_mm(df["EUR (MM)"]).fillna(0)
        df["LLL 25% (COP)"] = _to_mm(df["LLL 25% (COP)"]).fillna(0)
        
        # Recalcular columnas derivadas
        # 1) COP (MM) = EUR (MM) × TRM (COP/EUR)
        df["COP (MM)"] = df["EUR (MM)"] * float(trm_cop_eur)
        print(f"   ✓ COP (MM) = EUR (MM) × {trm_cop_eur:,.6f}")
        
        # 2) LLL 25% (EUR) = LLL 25% (COP) ÷ TRM (COP/EUR)
        df["LLL 25% (EUR)"] = df["LLL 25% (COP)"] / float(trm_cop_eur)
        print(f"   ✓ LLL 25% (EUR) = LLL 25% (COP) ÷ {trm_cop_eur:,.6f}")
        
        # Actualizar modelo y vista
        self._model.set_lineas_credito(df)
        
        if self._view:
            self._view.mostrar_lineas_credito(df)
        
        print(f"   ✅ Tabla actualizada con columnas derivadas recalculadas")
        
        # Liberar flag
        self._recalc_in_progress = False
    
    def _on_lineas_credito_loaded(self) -> None:
        """
        Callback que se ejecuta cuando se cargan/actualizan las líneas de crédito.
        Invoca el recálculo con la TRM COP/EUR actual.
        """
        if not self._model:
            return
        
        trm = self._model.trm_cop_eur()
        print(f"[SettingsController] Líneas de crédito cargadas, aplicando recálculo con TRM={trm}")
        self._recalc_lineas_credito_with_trm(trm)
    
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

