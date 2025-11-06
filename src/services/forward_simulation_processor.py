"""
Servicio para procesar simulaciones de operaciones Forward.

Este módulo convierte filas de simulación en operaciones "415-like"
y recalcula la exposición crediticia total incluyendo operaciones vigentes.
"""

from typing import Dict, List, Any
from datetime import date, datetime
import math
import random


class ForwardSimulationProcessor:
    """
    Procesador de simulaciones de operaciones Forward.
    
    Responsabilidades:
    - Convertir fila de simulación a operación "415-like"
    - Recalcular exposición crediticia total (vigentes + simulada)
    - Aplicar las mismas fórmulas usadas para Outstanding
    """
    
    def __init__(self):
        """Inicializa el procesador de simulaciones."""
        pass
    
    def build_simulated_operation(self, row: Dict[str, Any], nit: str, nombre: str, fc: float) -> Dict[str, Any]:
        """
        Construye una operación "415-like" a partir de una fila de simulación.
        
        Args:
            row: Diccionario con datos de la simulación (usar claves internas)
            nit: NIT de la contraparte
            nombre: Nombre de la contraparte
            fc: Factor de conversión (82FC) aplicable
            
        Returns:
            Diccionario con estructura compatible con pipeline 415
        """
        # Extraer datos de la fila con valores por defecto
        punta_cli = row.get("punta_cli", "Compra")
        nominal_usd = float(row.get("nominal_usd", 0) or 0)
        spot = float(row.get("spot", 0) or 0)
        puntos = float(row.get("puntos", 0) or 0)
        plazo = row.get("plazo")
        fecha_venc_str = row.get("fec_venc")
        fecha_sim_str = row.get("fec_sim")
        
        # Obtener Derecho y Obligación si existen (ya calculados)
        derecho = row.get("derecho")
        obligacion = row.get("obligacion")
        
        # Calcular vr (valoración)
        if derecho is not None and obligacion is not None:
            vr = derecho - obligacion
        else:
            # Aproximación si no están calculados: vr ≈ puntos * nominal * delta
            delta = 1 if punta_cli == "Compra" else -1
            vr = puntos * nominal_usd * delta
        
        # Convertir delta
        delta = 1 if punta_cli == "Compra" else -1
        
        # Validar y convertir fechas
        try:
            if isinstance(fecha_venc_str, str) and fecha_venc_str:
                fecha_liquidacion = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()
            else:
                fecha_liquidacion = date.today()
        except (ValueError, AttributeError):
            fecha_liquidacion = date.today()
        
        try:
            if isinstance(fecha_sim_str, str) and fecha_sim_str:
                fecha_corte = datetime.strptime(fecha_sim_str, "%Y-%m-%d").date()
            else:
                fecha_corte = date.today()
        except (ValueError, AttributeError):
            fecha_corte = date.today()
        
        # Calcular td (plazo en días HÁBILES Colombia)
        # Usar la misma lógica que el informe 415
        from src.utils.date_utils import dias_habiles_colombia, aplicar_reglas_plazo
        
        if plazo is not None and plazo >= 0:
            # Si ya viene calculado, usarlo (pero verificar que sea hábil)
            td = plazo
        else:
            # Calcular días hábiles entre fecha_corte y fecha_venc
            td = dias_habiles_colombia(fecha_corte, fecha_liquidacion)
            # Aplicar reglas: -1 y piso de 10
            td = aplicar_reglas_plazo(td)
        
        # Calcular t = sqrt(min(td, 252) / 252)
        t = math.sqrt(min(td, 252) / 252.0) if td >= 0 else 0.0
        
        # Calcular vne = vna * trm * delta * t
        vne = nominal_usd * spot * delta * t
        
        # Calcular EPFp = fc * vne
        epfp = fc * vne
        
        # Generar deal simulado
        timestamp = int(datetime.now().timestamp())
        rand_id = random.randint(1000, 9999)
        deal = f"SIM-{timestamp}-{rand_id}"
        
        # Construir operación 415-like
        operation = {
            "contraparte": nombre,
            "nit": nit,
            "deal": deal,
            "tipo_operacion": punta_cli.upper(),  # "COMPRA" o "VENTA"
            "vr_derecho": derecho if derecho is not None else 0.0,
            "vr_obligacion": obligacion if obligacion is not None else 0.0,
            "fc": fc,
            "vna": nominal_usd,
            "trm": spot,
            "fecha_liquidacion": fecha_liquidacion,
            "fecha_corte": fecha_corte,
            "delta": delta,
            "td": td,
            "t": t,
            "vne": vne,
            "EPFp": epfp,
            "vr": vr,
            # Campos adicionales para compatibilidad
            "nominal_usd": nominal_usd,
            "spot": spot,
            "puntos": puntos,
            "plazo": td,
        }
        
        return operation
    
    def recalc_exposure_with_simulation(
        self,
        ops_vigentes: List[Dict[str, Any]],
        simulated_op: Dict[str, Any]
    ) -> float:
        """
        Recalcula la exposición crediticia total incluyendo una operación simulada.
        
        Combina operaciones vigentes con la operación simulada y aplica
        las mismas fórmulas usadas en el cálculo de Outstanding.
        
        Args:
            ops_vigentes: Lista de operaciones vigentes del cliente
            simulated_op: Operación simulada (estructura 415-like)
            
        Returns:
            Exposición crediticia total (vigentes + simulada)
        """
        # Combinar operaciones
        todas_ops = ops_vigentes + [simulated_op]
        
        if not todas_ops:
            return 0.0
        
        # Obtener fc de la primera operación (debe ser igual para todas del mismo NIT)
        fc = todas_ops[0].get("fc", 0.0)
        
        # Sumar VNE y VR de todas las operaciones
        total_vne = sum(float(op.get("vne", 0) or 0) for op in todas_ops)
        total_vr = sum(float(op.get("vr", 0) or 0) for op in todas_ops)
        
        # Calcular EPFp total
        total_epfp = abs(total_vne * fc)
        
        # Calcular MGP (Market Gain Potential)
        if total_epfp > 0:
            try:
                exponent = (total_vr - 0) / (1.9 * total_epfp)
                mgp = min(0.05 + 0.95 * math.exp(exponent), 1.0)
            except (OverflowError, ZeroDivisionError):
                mgp = 0.0
        else:
            mgp = 0.0
        
        # Calcular CRP (Current Replacement Price)
        crp = max(total_vr - 0, 0.0)
        
        # Calcular exposición crediticia total
        exp_cred_total = 1.4 * (crp + mgp * total_epfp)
        
        return exp_cred_total
    
    def recalc_exposure_with_multiple_simulations(
        self,
        ops_vigentes: List[Dict[str, Any]],
        simulated_ops: List[Dict[str, Any]]
    ) -> float:
        """
        Recalcula la exposición crediticia total incluyendo múltiples operaciones simuladas.
        
        Combina operaciones vigentes con todas las operaciones simuladas y aplica
        las mismas fórmulas usadas en el cálculo de Outstanding.
        
        Args:
            ops_vigentes: Lista de operaciones vigentes del cliente
            simulated_ops: Lista de operaciones simuladas (estructura 415-like)
            
        Returns:
            Exposición crediticia total (vigentes + todas las simuladas)
        """
        # Combinar operaciones vigentes con todas las simuladas
        todas_ops = ops_vigentes + simulated_ops
        
        if not todas_ops:
            return 0.0
        
        # Obtener fc de la primera operación (debe ser igual para todas del mismo NIT)
        fc = todas_ops[0].get("fc", 0.0)
        
        # Sumar VNE y VR de todas las operaciones
        total_vne = sum(float(op.get("vne", 0) or 0) for op in todas_ops)
        total_vr = sum(float(op.get("vr", 0) or 0) for op in todas_ops)
        
        # Calcular EPFp total
        total_epfp = abs(total_vne * fc)
        
        # Calcular MGP (Market Gain Potential)
        if total_epfp > 0:
            try:
                exponent = (total_vr - 0) / (1.9 * total_epfp)
                mgp = min(0.05 + 0.95 * math.exp(exponent), 1.0)
            except (OverflowError, ZeroDivisionError):
                mgp = 0.0
        else:
            mgp = 0.0
        
        # Calcular CRP (Current Replacement Price)
        crp = max(total_vr - 0, 0.0)
        
        # Calcular exposición crediticia total
        exp_cred_total = 1.4 * (crp + mgp * total_epfp)
        
        return exp_cred_total

