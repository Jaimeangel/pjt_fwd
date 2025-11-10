"""
Modelo para Settings (Configuración del Sistema).
Gestiona la configuración y parámetros de la aplicación con señales Qt para actualización en tiempo real.
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any
import pandas as pd


class SettingsModel(QObject):
    """
    Modelo de datos para la configuración del sistema.
    
    Usa señales Qt para notificar cambios en tiempo real a todas las vistas conectadas.
    
    Responsabilidades:
    - Gestionar TRM COP/USD vigente
    - Gestionar TRM EUR/USD vigente
    - Gestionar parámetros normativos
    - Gestionar líneas de crédito vigentes
    - Notificar cambios en tiempo real mediante señales
    """
    
    # Señales para cambios en tiempo real (pueden emitir float o None)
    trm_cop_usdChanged = Signal(object)  # float | None
    trm_eur_usdChanged = Signal(object)  # float | None
    lineasCreditoChanged = Signal()      # Aviso de cambios en DataFrame
    
    def __init__(self):
        """
        Inicializa el modelo de configuración SIN valores por defecto.
        Todos los parámetros inician en None hasta que el usuario los configure.
        """
        super().__init__()
        
        # Parámetros Generales (TRMs)
        self._trm_cop_usd: Optional[float] = None  # TRM COP/USD
        self._trm_eur_usd: Optional[float] = None  # TRM EUR/USD
        
        # Parámetros Normativos
        self._lim_endeud: Optional[float] = None
        self._lim_entfin: Optional[float] = None
        
        # Líneas de Crédito Vigentes
        self.lineas_credito_df = pd.DataFrame()  # DataFrame con líneas de crédito cargadas
        
        print("[SettingsModel] Inicializado SIN valores por defecto (todos en None)")
    
    # === Parámetros Generales ===
    
    def set_trm_cop_usd(self, v) -> None:
        """
        Establece la TRM COP/USD vigente y emite señal si cambió.
        Acepta None, float, o string.
        
        Args:
            v: Nuevo valor de TRM COP/USD (float, str o None)
        """
        try:
            val = float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            val = None
        
        if val != self._trm_cop_usd:
            self._trm_cop_usd = val
            self.trm_cop_usdChanged.emit(val)
            if val is not None:
                print(f"[SettingsModel] TRM COP/USD actualizada: {val:,.6f}")
            else:
                print("[SettingsModel] TRM COP/USD limpiada (None)")
    
    def trm_cop_usd(self) -> Optional[float]:
        """
        Obtiene la TRM COP/USD vigente.
        
        Returns:
            Valor de TRM COP/USD o None si no está configurado
        """
        return self._trm_cop_usd
    
    def set_trm_eur_usd(self, v) -> None:
        """
        Establece la TRM EUR/USD vigente y emite señal si cambió.
        Acepta None, float, o string.
        
        Args:
            v: Nuevo valor de TRM EUR/USD (float, str o None)
        """
        try:
            val = float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            val = None
        
        if val != self._trm_eur_usd:
            self._trm_eur_usd = val
            self.trm_eur_usdChanged.emit(val)
            if val is not None:
                print(f"[SettingsModel] TRM EUR/USD actualizada: {val:,.6f}")
            else:
                print("[SettingsModel] TRM EUR/USD limpiada (None)")
    
    def trm_eur_usd(self) -> Optional[float]:
        """
        Obtiene la TRM EUR/USD vigente.
        
        Returns:
            Valor de TRM EUR/USD o None si no está configurado
        """
        return self._trm_eur_usd
    
    # === Parámetros Normativos ===
    
    def set_lim_endeud(self, v: float) -> None:
        """Establece el límite máximo de endeudamiento individual (%)."""
        self._lim_endeud = v
    
    def lim_endeud(self) -> float:
        """Obtiene el límite máximo de endeudamiento individual (%)."""
        return self._lim_endeud
    
    def set_lim_entfin(self, v: float) -> None:
        """Establece el límite máximo de concentración con entidades financieras (%)."""
        self._lim_entfin = v
    
    def lim_entfin(self) -> float:
        """Obtiene el límite máximo de concentración con entidades financieras (%)."""
        return self._lim_entfin
    
    # === Líneas de Crédito ===
    
    def set_lineas_credito(self, df: pd.DataFrame) -> None:
        """
        Establece el DataFrame de líneas de crédito vigentes.
        Normaliza el NIT (elimina guiones) antes de almacenar.
        
        Args:
            df: DataFrame con columnas NIT, Contraparte, Grupo Conectado de Contrapartes, Monto (COP)
        """
        # Normalizar NIT sin guiones
        df = df.copy()
        df["NIT"] = df["NIT"].astype(str).str.replace("-", "", regex=False).str.strip()
        self.lineas_credito_df = df
        self.lineasCreditoChanged.emit()
        print(f"[SettingsModel] Líneas de crédito actualizadas: {len(df)} registros")
    
    def get_linea_credito_por_nit(self, nit: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la línea de crédito para un NIT específico.
        
        Args:
            nit: NIT del cliente (sin guiones)
            
        Returns:
            Diccionario con datos del cliente o None si no se encuentra
        """
        if self.lineas_credito_df.empty:
            return None
        
        # Buscar cliente por NIT
        cliente_info = self.lineas_credito_df[self.lineas_credito_df["NIT"] == nit]
        
        if cliente_info.empty:
            return None
        
        # Retornar primera coincidencia como diccionario
        result = {
            "nit": str(cliente_info["NIT"].iloc[0]),
            "contraparte": str(cliente_info["Contraparte"].iloc[0]),
            "grupo": str(cliente_info["Grupo Conectado de Contrapartes"].iloc[0]),
            "monto_cop": float(cliente_info["Monto (COP)"].iloc[0])
        }
        
        # Incluir columnas adicionales si existen
        if "Patrimonio técnico" in cliente_info.columns:
            result["patrimonio_tecnico"] = float(cliente_info["Patrimonio técnico"].iloc[0])
        if "LLL 25% (COP)" in cliente_info.columns:
            result["lll_cop"] = float(cliente_info["LLL 25% (COP)"].iloc[0])
        if "LLL 25% (EUR)" in cliente_info.columns:
            lll_eur = cliente_info["LLL 25% (EUR)"].iloc[0]
            result["lll_eur"] = float(lll_eur) if pd.notna(lll_eur) else None
        if "COP (MM)" in cliente_info.columns:
            cop_mm = cliente_info["COP (MM)"].iloc[0]
            result["cop_mm"] = float(cop_mm) if pd.notna(cop_mm) else None
        if "EUR (MM)" in cliente_info.columns:
            result["eur_mm"] = float(cliente_info["EUR (MM)"].iloc[0])
        
        return result
    
    # === Métodos de utilidad ===
    
    def get_all_params(self) -> Dict[str, Any]:
        """
        Obtiene todos los parámetros como diccionario.
        
        Returns:
            Diccionario con todos los parámetros
        """
        return {
            "trm_cop_usd": self._trm_cop_usd,
            "trm_eur_usd": self._trm_eur_usd,
            "lim_endeud": self._lim_endeud,
            "lim_entfin": self._lim_entfin
        }

