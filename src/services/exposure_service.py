"""
Servicio de cálculo de exposición crediticia.
"""

from typing import Dict, Any, Optional
import math

import pandas as pd


class ExposureService:
    """
    Servicio de cálculo de exposición y límites (mock legacy).
    
    Se mantiene por compatibilidad con pruebas existentes, aunque la nueva
    implementación recomendada es la función calculate_exposure_from_operations.
    """
    
    def calc_simulated_exposure(self, fila_sim: Dict[str, Any]) -> float:
        nominal_usd = float(fila_sim.get("nominal_usd", 0))
        spot = float(fila_sim.get("spot", 4250.0))
        factor_exposicion = 0.15
        exposicion_cop = nominal_usd * spot * factor_exposicion
        return round(exposicion_cop, 2)
    
    def calc_outstanding_exposure(
        self,
        operaciones: list,
        spot: float = 4250.0
    ) -> float:
        if not operaciones:
            return 0.0
        
        total_exposure = 0.0
        for op in operaciones:
            nominal = float(op.get("nominal", 0))
            exposure = nominal * spot * 0.20
            total_exposure += exposure
        
        return round(total_exposure, 2)
    
    def calc_disponibilidad(
        self,
        outstanding: float,
        exposicion_simulada: float,
        linea_credito: float,
        colchon_pct: float
    ) -> Dict[str, float]:
        limite_max = linea_credito * (1 - colchon_pct)
        total_con_simulacion = outstanding + exposicion_simulada
        disponibilidad = limite_max - total_con_simulacion
        utilizacion_pct = (total_con_simulacion / limite_max * 100) if limite_max > 0 else 0
        
        return {
            "outstanding": round(outstanding, 2),
            "exposicion_simulada": round(exposicion_simulada, 2),
            "total_con_simulacion": round(total_con_simulacion, 2),
            "limite_max": round(limite_max, 2),
            "disponibilidad": round(disponibilidad, 2),
            "utilizacion_pct": round(utilizacion_pct, 2)
        }


def calculate_exposure_from_operations(df_ops: Optional[pd.DataFrame]) -> Dict[str, float]:
    """
    Calcula exposición crediticia a partir de un conjunto de operaciones (contraparte o grupo).
    
    Args:
        df_ops: DataFrame con columnas 'vne', 'vr', 'fc' (y demás columnas derivadas).
    
    Returns:
        Diccionario con métricas agregadas de exposición.
    """
    result = {
        "outstanding": 0.0,
        "total_vr": 0.0,
        "total_vne": 0.0,
        "epfp_total": 0.0,
        "mgp": 0.0,
        "crp": 0.0,
        "fc": 0.0,
        "operations_count": 0,
    }
    
    if df_ops is None or df_ops.empty:
        return result
    
    df = df_ops.copy()
    result["operations_count"] = len(df)
    
    # Sumas básicas
    if "vne" in df.columns:
        result["total_vne"] = float(df["vne"].fillna(0.0).sum())
    if "vr" in df.columns:
        result["total_vr"] = float(df["vr"].fillna(0.0).sum())
    
    # Factor de conversión (tomar primer valor no nulo)
    if "fc" in df.columns:
        fc_series = df["fc"].dropna()
        if not fc_series.empty:
            result["fc"] = float(fc_series.iloc[0])
    
    total_epfp = abs(result["total_vne"] * result["fc"])
    result["epfp_total"] = total_epfp
    
    # MgP
    if total_epfp > 0:
        try:
            exponent = result["total_vr"] / (1.9 * total_epfp)
            result["mgp"] = min(0.05 + 0.95 * math.exp(exponent), 1.0)
        except (OverflowError, ZeroDivisionError, ValueError):
            result["mgp"] = 1.0
    else:
        result["mgp"] = 0.0
    
    # CrP y exposición final
    result["crp"] = max(result["total_vr"], 0.0)
    result["outstanding"] = 1.4 * (result["crp"] + (result["mgp"] * total_epfp))
    
    return result
