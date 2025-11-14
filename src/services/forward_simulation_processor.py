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
        
        IMPORTANTE: Todos los cálculos (delta, VNA, VR, VNE, EPFp) se basan en la
        PUNTA EMPRESA, exactamente igual que en el cálculo del informe 415.
        
        Args:
            row: Diccionario con datos de la simulación (usar claves internas)
            nit: NIT de la contraparte
            nombre: Nombre de la contraparte
            fc: Factor de conversión (82FC) aplicable
            
        Returns:
            Diccionario con estructura compatible con pipeline 415
        """
        # Extraer datos de la fila con valores por defecto
        # IMPORTANTE: Usar punta_emp para todos los cálculos, igual que en el 415
        punta_emp = row.get("punta_emp", "Venta")  # Por defecto inverso de punta_cli
        # Si no existe punta_emp, calcularla como inverso de punta_cli
        if not punta_emp or punta_emp == "":
            punta_cli = row.get("punta_cli", "Compra")
            punta_emp = "Venta" if punta_cli == "Compra" else "Compra"
        
        nominal_usd = float(row.get("nominal_usd", 0) or 0)
        spot = float(row.get("spot", 0) or 0)
        puntos = float(row.get("puntos", 0) or 0)
        plazo = row.get("plazo")
        fecha_venc_str = row.get("fec_venc")
        fecha_sim_str = row.get("fec_sim")
        
        # Calcular DELTA basado en PUNTA EMPRESA (igual que en el 415)
        # delta = 1 si punta_empresa == "Compra", -1 si "Venta"
        punta_emp_upper = str(punta_emp).strip().upper()
        if punta_emp_upper == "COMPRA":
            delta = 1
        else:  # "VENTA" o cualquier otro valor
            delta = -1
        
        # Obtener Derecho y Obligación calculados desde perspectiva EMPRESA
        # ⚠️ CORRECCIÓN (2025-01-XX): Estos valores ahora se calculan directamente
        # desde la perspectiva de la EMPRESA usando punta_emp en el modelo de tabla.
        # Ya NO necesitamos intercambiarlos.
        derecho_empresa = row.get("derecho")
        obligacion_empresa = row.get("obligacion")
        
        # Calcular VR desde perspectiva EMPRESA
        # IMPORTANTE: En el 415, el VR se calcula como vr_derecho - vr_obligacion
        # donde vr_derecho y vr_obligacion son desde la perspectiva de la EMPRESA.
        if derecho_empresa is not None and obligacion_empresa is not None:
            # Usar directamente los valores calculados en la tabla
            # (ya están desde perspectiva empresa)
            vr_derecho_empresa = derecho_empresa
            vr_obligacion_empresa = obligacion_empresa
            vr = vr_derecho_empresa - vr_obligacion_empresa
        else:
            # Aproximación si no están calculados
            # VR ≈ puntos * nominal * delta (desde perspectiva empresa)
            vr = puntos * nominal_usd * delta
            vr_derecho_empresa = 0.0
            vr_obligacion_empresa = 0.0
        
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
        
        # Calcular VNA (Valor Nominal Ajustado)
        # En el 415: vna = nomin_der si delta == 1, nomin_obl si delta == -1
        # En la simulación, asumimos que nominal_usd representa el nominal correcto
        # según la punta empresa (equivalente a nomin_der si delta=1, nomin_obl si delta=-1)
        vna = nominal_usd
        
        # Calcular VNE (Valor Nominal Equivalente) = vna * trm * delta * t
        # Esta fórmula es la misma que en el 415
        vne = vna * spot * delta * t
        
        # Calcular EPFp (Exposición Potencial Futura) = fc * vne
        # Esta fórmula es la misma que en el 415
        epfp = fc * vne
        
        # Generar deal simulado
        timestamp = int(datetime.now().timestamp())
        rand_id = random.randint(1000, 9999)
        deal = f"SIM-{timestamp}-{rand_id}"
        
        # Construir operación 415-like
        # IMPORTANTE: tipo_operacion debe representar la PUNTA EMPRESA (COMPRA/VENTA)
        # igual que en el 415
        tipo_operacion_upper = punta_emp_upper  # Usar punta_emp en mayúsculas
        
        # Asignar vr_derecho y vr_obligacion desde perspectiva empresa
        if derecho_empresa is not None and obligacion_empresa is not None:
            vr_derecho_final = vr_derecho_empresa
            vr_obligacion_final = vr_obligacion_empresa
        else:
            # Si no hay valores calculados, usar 0.0 (o valores aproximados)
            vr_derecho_final = 0.0
            vr_obligacion_final = 0.0
        
        operation = {
            "contraparte": nombre,
            "nit": nit,
            "deal": deal,
            "tipo_operacion": tipo_operacion_upper,  # "COMPRA" o "VENTA" basado en punta_empresa
            "vr_derecho": vr_derecho_final,  # Desde perspectiva empresa
            "vr_obligacion": vr_obligacion_final,  # Desde perspectiva empresa
            "fc": fc,
            "vna": vna,  # VNA basado en punta empresa
            "trm": spot,
            "fecha_liquidacion": fecha_liquidacion,
            "fecha_corte": fecha_corte,
            "delta": delta,  # Delta basado en punta empresa
            "td": td,
            "t": t,
            "vne": vne,  # VNE calculado con delta basado en punta empresa
            "EPFp": epfp,  # EPFp calculado con VNE correcto
            "vr": vr,  # VR calculado desde perspectiva empresa (vr_derecho - vr_obligacion)
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
        
        # Calcular MGP (Market Gap Provision)
        # mgp = min(0.05 + 0.95 * exp(total_vr / (1.9 * total_epfp)), 1)
        # Esta fórmula es la misma que en el 415
        if total_epfp > 0:
            try:
                exponent = total_vr / (1.9 * total_epfp)
                mgp = min(0.05 + 0.95 * math.exp(exponent), 1.0)
            except (OverflowError, ZeroDivisionError, FloatingPointError):
                # Si hay overflow, usar valor por defecto (igual que en el 415)
                mgp = 1.0
        else:
            # Si total_epfp es 0, no hay exposición
            mgp = 0.0
        
        # Calcular CRP (Credit Risk Premium)
        # crp = max(total_vr - 0, 0) = max(total_vr, 0)
        # Esta fórmula es la misma que en el 415
        crp = max(total_vr, 0.0)
        
        # Calcular exposición crediticia total
        # exp_cred_total = 1.4 * (crp + (mgp * total_epfp))
        # Esta fórmula es la misma que en el 415
        exp_cred_total = 1.4 * (crp + (mgp * total_epfp))
        
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
        
        # Calcular MGP (Market Gap Provision)
        # mgp = min(0.05 + 0.95 * exp(total_vr / (1.9 * total_epfp)), 1)
        # Esta fórmula es la misma que en el 415
        if total_epfp > 0:
            try:
                exponent = total_vr / (1.9 * total_epfp)
                mgp = min(0.05 + 0.95 * math.exp(exponent), 1.0)
            except (OverflowError, ZeroDivisionError, FloatingPointError):
                # Si hay overflow, usar valor por defecto (igual que en el 415)
                mgp = 1.0
        else:
            # Si total_epfp es 0, no hay exposición
            mgp = 0.0
        
        # Calcular CRP (Credit Risk Premium)
        # crp = max(total_vr - 0, 0) = max(total_vr, 0)
        # Esta fórmula es la misma que en el 415
        crp = max(total_vr, 0.0)
        
        # Calcular exposición crediticia total
        # exp_cred_total = 1.4 * (crp + (mgp * total_epfp))
        # Esta fórmula es la misma que en el 415
        exp_cred_total = 1.4 * (crp + (mgp * total_epfp))
        
        return exp_cred_total

