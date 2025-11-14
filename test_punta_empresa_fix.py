"""
Test para verificar que el cálculo de forwards usa la PUNTA EMPRESA correctamente.

⚠️ PROBLEMA CORREGIDO:
El cálculo del forward NO debe hacerse usando la "punta del cliente".
Debe hacerse usando la punta de la empresa, que es siempre el valor opuesto a la punta del cliente.

Ejemplo:
- Si el cliente es Compra, la empresa es Venta → usar punta Venta para cálculos
- Si el cliente es Venta, la empresa es Compra → usar punta Compra para cálculos
"""

import sys
from datetime import date
from PySide6.QtWidgets import QApplication

# Importar el modelo de tabla de simulaciones
from src.models.qt.simulations_table_model import SimulationsTableModel


def test_punta_empresa_calculations():
    """
    Verifica que Derecho y Obligación se calculen usando PUNTA EMPRESA.
    """
    print("\n" + "="*80)
    print("TEST: Verificar cálculo con PUNTA EMPRESA (no punta cliente)")
    print("="*80)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Crear modelo
    model = SimulationsTableModel()
    
    # Datos de prueba
    spot = 4000.0
    puntos = 100.0
    nominal_usd = 1_000_000.0
    plazo = 90
    tasa_ibr = 0.11  # 11% anual
    
    # Calcular factor de descuento
    df = 1.0 + (tasa_ibr * plazo / 360.0)
    print(f"\n📊 Datos de entrada:")
    print(f"   Spot: {spot:,.2f}")
    print(f"   Puntos: {puntos:,.2f}")
    print(f"   Nominal USD: {nominal_usd:,.2f}")
    print(f"   Plazo: {plazo} días")
    print(f"   Tasa IBR: {tasa_ibr * 100:.2f}%")
    print(f"   Factor descuento (df): {df:.6f}")
    
    # =========================================================================
    # CASO 1: Cliente COMPRA → Empresa VENTA
    # =========================================================================
    print(f"\n{'─'*80}")
    print("CASO 1: Cliente COMPRA → Empresa VENTA")
    print(f"{'─'*80}")
    
    model.add_row({
        "cliente": "CLIENTE TEST 1",
        "nit": "123456789",
        "punta_cli": "Compra",
        "punta_emp": "Venta",
        "nominal_usd": nominal_usd,
        "fec_sim": date.today().strftime("%Y-%m-%d"),
        "fec_venc": date.today().strftime("%Y-%m-%d"),
        "plazo": plazo,
        "spot": spot,
        "puntos": puntos,
        "tasa_ibr": tasa_ibr,
    })
    
    # Forzar recálculo de la fila
    model._recalc_row(0)
    
    # Obtener valores calculados
    row_0 = model._rows[0]
    derecho_1 = row_0.get("derecho")
    obligacion_1 = row_0.get("obligacion")
    fair_value_1 = row_0.get("fair_value")
    
    # Valores ESPERADOS cuando EMPRESA es VENTA:
    # Derecho = Spot/df * Nominal
    # Obligación = (Spot + Puntos)/df * Nominal
    expected_derecho_venta = spot / df * nominal_usd
    expected_obligacion_venta = (spot + puntos) / df * nominal_usd
    expected_fv_venta = expected_derecho_venta - expected_obligacion_venta
    
    print(f"\n   Punta Cliente: Compra")
    print(f"   Punta Empresa: Venta ← ESTA se debe usar para cálculos")
    print(f"\n   Valores CALCULADOS:")
    print(f"   - Derecho:     $ {derecho_1:>15,.2f}")
    print(f"   - Obligación:  $ {obligacion_1:>15,.2f}")
    print(f"   - Fair Value:  $ {fair_value_1:>15,.2f}")
    print(f"\n   Valores ESPERADOS (punta VENTA):")
    print(f"   - Derecho:     $ {expected_derecho_venta:>15,.2f}")
    print(f"   - Obligación:  $ {expected_obligacion_venta:>15,.2f}")
    print(f"   - Fair Value:  $ {expected_fv_venta:>15,.2f}")
    
    # Verificar
    assert abs(derecho_1 - expected_derecho_venta) < 0.01, \
        f"❌ Derecho incorrecto. Esperado: {expected_derecho_venta:,.2f}, Obtenido: {derecho_1:,.2f}"
    assert abs(obligacion_1 - expected_obligacion_venta) < 0.01, \
        f"❌ Obligación incorrecta. Esperado: {expected_obligacion_venta:,.2f}, Obtenido: {obligacion_1:,.2f}"
    assert abs(fair_value_1 - expected_fv_venta) < 0.01, \
        f"❌ Fair Value incorrecto. Esperado: {expected_fv_venta:,.2f}, Obtenido: {fair_value_1:,.2f}"
    
    print(f"\n   ✅ CASO 1 CORRECTO: Usa punta EMPRESA (Venta)")
    
    # =========================================================================
    # CASO 2: Cliente VENTA → Empresa COMPRA
    # =========================================================================
    print(f"\n{'─'*80}")
    print("CASO 2: Cliente VENTA → Empresa COMPRA")
    print(f"{'─'*80}")
    
    model.add_row({
        "cliente": "CLIENTE TEST 2",
        "nit": "987654321",
        "punta_cli": "Venta",
        "punta_emp": "Compra",
        "nominal_usd": nominal_usd,
        "fec_sim": date.today().strftime("%Y-%m-%d"),
        "fec_venc": date.today().strftime("%Y-%m-%d"),
        "plazo": plazo,
        "spot": spot,
        "puntos": puntos,
        "tasa_ibr": tasa_ibr,
    })
    
    # Forzar recálculo de la fila
    model._recalc_row(1)
    
    # Obtener valores calculados
    row_1 = model._rows[1]
    derecho_2 = row_1.get("derecho")
    obligacion_2 = row_1.get("obligacion")
    fair_value_2 = row_1.get("fair_value")
    
    # Valores ESPERADOS cuando EMPRESA es COMPRA:
    # Derecho = (Spot + Puntos)/df * Nominal
    # Obligación = Spot/df * Nominal
    expected_derecho_compra = (spot + puntos) / df * nominal_usd
    expected_obligacion_compra = spot / df * nominal_usd
    expected_fv_compra = expected_derecho_compra - expected_obligacion_compra
    
    print(f"\n   Punta Cliente: Venta")
    print(f"   Punta Empresa: Compra ← ESTA se debe usar para cálculos")
    print(f"\n   Valores CALCULADOS:")
    print(f"   - Derecho:     $ {derecho_2:>15,.2f}")
    print(f"   - Obligación:  $ {obligacion_2:>15,.2f}")
    print(f"   - Fair Value:  $ {fair_value_2:>15,.2f}")
    print(f"\n   Valores ESPERADOS (punta COMPRA):")
    print(f"   - Derecho:     $ {expected_derecho_compra:>15,.2f}")
    print(f"   - Obligación:  $ {expected_obligacion_compra:>15,.2f}")
    print(f"   - Fair Value:  $ {expected_fv_compra:>15,.2f}")
    
    # Verificar
    assert abs(derecho_2 - expected_derecho_compra) < 0.01, \
        f"❌ Derecho incorrecto. Esperado: {expected_derecho_compra:,.2f}, Obtenido: {derecho_2:,.2f}"
    assert abs(obligacion_2 - expected_obligacion_compra) < 0.01, \
        f"❌ Obligación incorrecta. Esperado: {expected_obligacion_compra:,.2f}, Obtenido: {obligacion_2:,.2f}"
    assert abs(fair_value_2 - expected_fv_compra) < 0.01, \
        f"❌ Fair Value incorrecto. Esperado: {expected_fv_compra:,.2f}, Obtenido: {fair_value_2:,.2f}"
    
    print(f"\n   ✅ CASO 2 CORRECTO: Usa punta EMPRESA (Compra)")
    
    # =========================================================================
    # VERIFICACIÓN ADICIONAL: Fair Values tienen SIGNOS OPUESTOS
    # =========================================================================
    print(f"\n{'─'*80}")
    print("VERIFICACIÓN: Fair Values deben tener signos opuestos")
    print(f"{'─'*80}")
    
    print(f"\n   Fair Value (empresa VENTA):  $ {fair_value_1:>15,.2f}")
    print(f"   Fair Value (empresa COMPRA): $ {fair_value_2:>15,.2f}")
    print(f"   Suma de ambos:               $ {fair_value_1 + fair_value_2:>15,.2f}")
    
    # Los fair values deben ser negativos uno del otro (signos opuestos)
    assert abs(fair_value_1 + fair_value_2) < 0.01, \
        f"❌ Fair Values no son opuestos. FV1: {fair_value_1:,.2f}, FV2: {fair_value_2:,.2f}"
    
    print(f"\n   ✅ CORRECTO: Fair Values son opuestos (suma ≈ 0)")
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print(f"\n{'='*80}")
    print("✅ TODOS LOS TESTS PASARON")
    print("="*80)
    print("\n✅ CONFIRMADO: El cálculo ahora usa PUNTA EMPRESA correctamente")
    print("✅ CONFIRMADO: Ya NO usa la punta del cliente (error corregido)")
    print("\n📝 Resumen:")
    print("   - Cliente COMPRA → Empresa VENTA → Cálculos con punta VENTA ✅")
    print("   - Cliente VENTA → Empresa COMPRA → Cálculos con punta COMPRA ✅")
    print("   - Fair Values tienen signos opuestos ✅")
    print()


if __name__ == "__main__":
    test_punta_empresa_calculations()

