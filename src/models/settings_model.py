"""
Modelo para Settings (Configuración del Sistema).
Gestiona la configuración y parámetros de la aplicación con señales Qt para actualización en tiempo real.
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any, List
import pandas as pd
from src.utils.ids import normalize_nit


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
    trm_cop_eurChanged = Signal(object)  # float | None
    patrimonioTecCopChanged = Signal(object)  # float | None
    colchonSeguridadChanged = Signal(object)  # float | None
    lineasCreditoChanged = Signal()      # Aviso de cambios en DataFrame
    counterpartiesChanged = Signal()     # Aviso de cambios en catálogo de contrapartes
    
    def __init__(self):
        """
        Inicializa el modelo de configuración SIN valores por defecto.
        Todos los parámetros inician en None hasta que el usuario los configure.
        """
        super().__init__()
        
        # Parámetros Generales (TRMs y Patrimonio)
        self._trm_cop_usd: Optional[float] = None  # TRM COP/USD
        self._trm_cop_eur: Optional[float] = None  # TRM COP/EUR
        self._patrimonio_tec_cop: Optional[float] = None  # Patrimonio técnico en COP
        
        # Parámetros Normativos
        self._lim_endeud: Optional[float] = None
        self._lim_entfin: Optional[float] = None
        self._colchon_seguridad: float = 0.10  # Colchón de seguridad (10% por defecto)
        
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
    
    def set_trm_cop_eur(self, v) -> None:
        """
        Establece la TRM COP/EUR vigente y emite señal si cambió.
        Acepta None, float, o string.
        
        Args:
            v: Nuevo valor de TRM COP/EUR (float, str o None)
        """
        try:
            val = float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            val = None
        
        if val != self._trm_cop_eur:
            self._trm_cop_eur = val
            self.trm_cop_eurChanged.emit(val)
            if val is not None:
                print(f"[SettingsModel] TRM COP/EUR actualizada: {val:,.6f}")
            else:
                print("[SettingsModel] TRM COP/EUR limpiada (None)")
    
    def trm_cop_eur(self) -> Optional[float]:
        """
        Obtiene la TRM COP/EUR vigente.
        
        Returns:
            Valor de TRM COP/EUR o None si no está configurado
        """
        return self._trm_cop_eur
    
    def set_patrimonio_tec_cop(self, value) -> None:
        """
        Establece el Patrimonio técnico vigente en COP y emite señal si cambió.
        Acepta None, float, o string. Valida que no sea NaN ni infinito.
        
        Args:
            value: Nuevo valor de Patrimonio técnico en COP (float, str o None)
        """
        import math
        
        try:
            val = float(value) if value not in (None, "") else None
            if val is not None and (math.isnan(val) or math.isinf(val)):
                val = None
        except (TypeError, ValueError):
            val = None
        
        if val != self._patrimonio_tec_cop:
            self._patrimonio_tec_cop = val
            self.patrimonioTecCopChanged.emit(val)
            if val is not None:
                print(f"[SettingsModel] Patrimonio técnico vigente actualizado: $ {val:,.2f} COP")
            else:
                print("[SettingsModel] Patrimonio técnico vigente limpiado (None)")
    
    def patrimonio_tec_cop(self) -> Optional[float]:
        """
        Obtiene el Patrimonio técnico vigente en COP.
        
        Returns:
            Valor de Patrimonio técnico en COP o None si no está configurado
        """
        return self._patrimonio_tec_cop
    
    def lll_cop(self) -> Optional[float]:
        """
        Calcula el LLL (Límite de Liquidez Legal) global en COP.
        LLL = 25% del Patrimonio técnico vigente × (1 - Colchón de seguridad).
        
        Ejemplo:
        - PT = 8,000,000,000,000 COP
        - Colchón = 10% (0.10)
        - LLL = 8,000,000,000,000 × 0.25 × (1 - 0.10) = 1,800,000,000,000 COP
        
        Returns:
            float: LLL en COP reales, o None si no hay patrimonio configurado
        """
        pt = self._patrimonio_tec_cop
        if pt is None:
            return None
        try:
            colchon = self._colchon_seguridad
            # LLL = 25% del PT × (1 - colchón)
            return 0.25 * float(pt) * (1 - colchon)
        except (TypeError, ValueError):
            return None
    
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
    
    def set_colchon_seguridad(self, v: float) -> None:
        """
        Establece el colchón de seguridad (%).
        
        Args:
            v: Colchón de seguridad en porcentaje (ej: 0.10 para 10%)
        """
        if v != self._colchon_seguridad:
            self._colchon_seguridad = v
            self.colchonSeguridadChanged.emit(v)
            print(f"[SettingsModel] Colchón de seguridad actualizado: {v * 100:.1f}%")
    
    def colchon_seguridad(self) -> float:
        """Obtiene el colchón de seguridad (%)."""
        return self._colchon_seguridad
    
    # === Líneas de Crédito ===
    
    def set_lineas_credito(self, df: pd.DataFrame) -> None:
        """
        Establece el DataFrame de líneas de crédito vigentes.
        Normaliza el NIT (elimina guiones, espacios, ceros a la izquierda) antes de almacenar.
        
        Args:
            df: DataFrame con columnas NIT, Contraparte, Grupo, EUR (MM), COP (MM)
        """
        # Normalizar NIT usando la función de utilidades
        df = df.copy()
        if "NIT" in df.columns:
            df["NIT_norm"] = df["NIT"].map(normalize_nit)
        self.lineas_credito_df = df
        self.lineasCreditoChanged.emit()
        self.counterpartiesChanged.emit()
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
            "grupo": str(cliente_info["Grupo Conectado de Contrapartes"].iloc[0])
        }
        
        # COP (MM) es la línea aprobada en COP (millones)
        if "COP (MM)" in cliente_info.columns:
            cop_mm = cliente_info["COP (MM)"].iloc[0]
            result["linea_cop_mm"] = float(cop_mm) if pd.notna(cop_mm) else 0.0
        
        # EUR (MM) si existe
        if "EUR (MM)" in cliente_info.columns:
            eur_mm = cliente_info["EUR (MM)"].iloc[0]
            result["eur_mm"] = float(eur_mm) if pd.notna(eur_mm) else None
        
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
            "trm_cop_eur": self._trm_cop_eur,
            "lim_endeud": self._lim_endeud,
            "lim_entfin": self._lim_entfin
        }
    
    def get_counterparties(self) -> List[Dict[str, Any]]:
        """
        Devuelve el catálogo de contrapartes desde la tabla de Líneas de Crédito.
        
        Returns:
            Lista de diccionarios con estructura:
            [{nit, nombre, grupo, eur_mm, cop_mm}, ...]
            
        Notes:
            - Devuelve lista vacía si no hay líneas de crédito cargadas
            - Deduplicación por NIT normalizado (mantiene primer registro)
            - NITs normalizados (sin espacios, guiones, ceros a la izquierda)
        """
        if self.lineas_credito_df is None or self.lineas_credito_df.empty:
            return []
        
        df = self.lineas_credito_df
        cols = df.columns
        out = []
        
        for _, row in df.iterrows():
            # Usar NIT_norm si existe, sino normalizar NIT original
            nit_norm = row.get("NIT_norm") if "NIT_norm" in cols else normalize_nit(row.get("NIT", ""))
            
            out.append({
                "nit": nit_norm,
                "nombre": row.get("Contraparte", ""),
                "grupo": row.get("Grupo Conectado de Contrapartes", ""),
                "eur_mm": row.get("EUR (MM)") if "EUR (MM)" in cols else None,
                "cop_mm": row.get("COP (MM)") if "COP (MM)" in cols else None,
            })
        
        # Deduplicar por NIT (mantener primero)
        seen = set()
        dedup = []
        for c in out:
            if c["nit"] in seen:
                continue
            seen.add(c["nit"])
            dedup.append(c)
        
        print(f"[SettingsModel] Catálogo de contrapartes: {len(dedup)} registros")
        return dedup

