"""
Controlador para el módulo Settings.
Coordina entre el modelo y la vista de configuración, conectando cambios en tiempo real.
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, QEvent


class SettingsController(QObject):
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
        super().__init__()
        self._view = view
        self._model = model
        
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
        self._view.lePatrimonioTecCOP.blockSignals(True)
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
        
        patrimonio_tec = self._model.patrimonio_tec_cop()
        if patrimonio_tec is not None:
            self._view.lePatrimonioTecCOP.setText(f"{patrimonio_tec:.2f}")
            print(f"   Patrimonio técnico vigente (COP): $ {patrimonio_tec:,.2f}")
        else:
            self._view.lePatrimonioTecCOP.clear()
            print("   Patrimonio técnico vigente (COP): (no configurado)")
        
        # Parámetros normativos son fijos (LLL=25%, Colchón=10%)
        print("   Parámetros normativos: valores fijos (no editables)")
        
        # Desbloquear señales
        self._view.trm_cop_usd.blockSignals(False)
        self._view.trm_cop_eur.blockSignals(False)
        self._view.lePatrimonioTecCOP.blockSignals(False)
    
    def _connect_signals(self) -> None:
        """
        Conecta las señales de la vista con los métodos del modelo.
        Los cambios en los inputs se propagan automáticamente al modelo,
        que a su vez emite señales para actualizar otras vistas.
        """
        if not self._model or not self._view:
            return
        
        print("[SettingsController] Conectando señales...")
        
        # Conectar cambios de Parámetros Generales (TRMs y Patrimonio)
        self._view.trm_cop_usd.textChanged.connect(self._model.set_trm_cop_usd)
        self._view.trm_cop_eur.textChanged.connect(self._model.set_trm_cop_eur)
        self._view.lePatrimonioTecCOP.textChanged.connect(self._model.set_patrimonio_tec_cop)
        
        # Conectar señal de modelo a vista (para actualización desde código)
        self._model.patrimonioTecCopChanged.connect(self._on_patrimonio_changed)
        
        # Instalar filtro de eventos para formatear al perder/ganar foco
        self._view.lePatrimonioTecCOP.installEventFilter(self)
        self._view.trm_cop_usd.installEventFilter(self)
        self._view.trm_cop_eur.installEventFilter(self)
        
        # Parámetros Normativos son fijos (no requieren conexiones)
        
        # Conectar señal de cambio en contrapartes para refrescar la tabla al cargar CSV
        self._model.lineasCreditoChanged.connect(self._on_lineas_credito_loaded)
        
        print("   ✓ trm_cop_usd.textChanged → model.set_trm_cop_usd()")
        print("   ✓ trm_cop_eur.textChanged → model.set_trm_cop_eur()")
        print("   ✓ lePatrimonioTecCOP.textChanged → model.set_patrimonio_tec_cop()")
        print("   ✓ patrimonioTecCopChanged → _on_patrimonio_changed()")
        print("   ✓ Parámetros normativos: valores fijos (sin conexiones)")
        print("   ✓ lineasCreditoChanged → _on_lineas_credito_loaded()")
    
    def _on_lineas_credito_loaded(self) -> None:
        """
        Callback que se ejecuta cuando se cargan/actualizan las contrapartes.
        """
        if not self._model:
            return
        if not self._view:
            return
        
        df = self._model.lineas_credito_df
        if df is None:
            return
        
        print(f"[SettingsController] Contrapartes cargadas, actualizando tabla...")
        self._view.mostrar_lineas_credito(df)
    
    def _on_patrimonio_changed(self, v) -> None:
        """
        Callback que se ejecuta cuando cambia el Patrimonio técnico vigente desde el modelo.
        Actualiza la vista solo si el valor difiere del texto actual (evita bucles).
        
        Args:
            v: Nuevo valor de patrimonio técnico (float o None)
        """
        if not self._view:
            return
        
        # Actualizar vista solo si es necesario (evitar bucles)
        if v is None:
            if self._view.lePatrimonioTecCOP.text() != "":
                self._view.lePatrimonioTecCOP.setText("")
        else:
            # Evitar bucles: solo actualizar si el texto no coincide con el valor
            cur = self._view.lePatrimonioTecCOP.text()
            try:
                cur_f = float(cur)
            except (ValueError, TypeError):
                cur_f = None
            
            if cur_f != v:
                # Formatear con 2 decimales
                self._view.lePatrimonioTecCOP.setText(f"{v:.2f}")
    
    def eventFilter(self, obj, event):
        """
        Filtro de eventos para formatear campos numéricos (Patrimonio técnico y TRMs).
        
        Al perder el foco (FocusOut): formatea con separador de miles
        Al ganar el foco (FocusIn): remueve formato para facilitar edición
        
        Args:
            obj: Objeto que generó el evento
            event: Evento capturado
            
        Returns:
            False para permitir que el evento continúe su propagación
        """
        # Determinar el campo y sus decimales
        campo = None
        decimales = 2  # Por defecto
        
        if obj == self._view.lePatrimonioTecCOP:
            campo = self._view.lePatrimonioTecCOP
            decimales = 2
        elif obj == self._view.trm_cop_usd:
            campo = self._view.trm_cop_usd
            decimales = 6
        elif obj == self._view.trm_cop_eur:
            campo = self._view.trm_cop_eur
            decimales = 6
        
        if campo is not None:
            if event.type() == QEvent.FocusOut:
                # Al perder el foco: formatear con separador de miles
                texto = campo.text().strip()
                if texto:
                    try:
                        # Limpiar separadores existentes y convertir
                        valor = float(texto.replace(',', ''))
                        # Formatear con separador de miles y decimales apropiados
                        texto_formateado = f"{valor:,.{decimales}f}"
                        # Bloquear señales para evitar trigger de textChanged
                        campo.blockSignals(True)
                        campo.setText(texto_formateado)
                        campo.blockSignals(False)
                    except (ValueError, TypeError):
                        pass  # Si no es un número válido, dejar como está
            
            elif event.type() == QEvent.FocusIn:
                # Al ganar el foco: remover separadores para facilitar edición
                texto = campo.text().strip()
                if texto:
                    try:
                        # Limpiar separadores
                        valor = float(texto.replace(',', ''))
                        # Mostrar sin separadores (solo el número)
                        texto_sin_formato = f"{valor:.{decimales}f}"
                        # Bloquear señales para evitar trigger de textChanged
                        campo.blockSignals(True)
                        campo.setText(texto_sin_formato)
                        campo.blockSignals(False)
                    except (ValueError, TypeError):
                        pass  # Si no es un número válido, dejar como está
        
        # Permitir que el evento continúe su propagación
        return False
    
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

