"""
Test para verificar la corrección de signos en el cálculo de forwards.

⚠️ PROBLEMA CORREGIDO:
Después de una corrección previa, se introdujo un error de signo:
- Al cambiar la punta, la exposición se comportaba al revés
- El fair value cambió de signo

CORRECCIÓN APLICADA:
1. Creado helper delta_from_punta_empresa() que devuelve +1 para "Compra", -1 para "Venta"
2. Todos los cálculos de exposición usan punta_empresa (no punta_cliente)
3. Fair value = derecho - obligacion (siempre desde perspectiva empresa)
4. Fórmulas de derecho/obligacion corregidas para que el signo sea consistente
"""

import sys
from datetime import date
from PySide6.QtWidgets import QApplication

# Importar módulos a testear
from src.models.qt.simulations_table_model import SimulationsTableModel
from src.utils.forward_utils import delta_from_punta_empresa, get_punta_opuesta
from src.services.forward_simulation_processor import ForwardSimulationProcessor


def test_helper_delta():
    """Test 1: Verificar que el helper delta_from_punta_empresa funciona correctamente."""
    print("\n" + "="*80)
    print("TEST 1: Helper delta_from_punta_empresa()")
    print("="*80)
    
    # Test casos válidos
    assert delta_from_punta_empresa("Compra") == 1, "Compra debe retornar +1"
    assert delta_from_punta_empresa("Venta") == -1, "Venta debe retornar -1"
    assert delta_from_punta_empresa("COMPRA") == 1, "COMPRA (mayúsculas) debe retornar +1"
    assert delta_from_punta_empresa("VENTA") == -1, "VENTA (mayúsculas) debe retornar -1"
    assert delta_from_punta_empresa("compra") == 1, "compra (minúsculas) debe retornar +1"
    assert delta_from_punta_empresa("venta") == -1, "venta (minúsculas) debe retornar -1"
    
    # Test casos inválidos
    assert delta_from_punta_empresa("") == 0, "String vacío debe retornar 0"
    assert delta_from_punta_empresa("Invalido") == 0, "Valor inválido debe retornar 0"
    assert delta_from_punta_empresa(None) == 0, "None debe retornar 0"
    
    print("   ✅ Helper delta_from_punta_empresa() funciona correctamente")
    
    # Test helper de punta opuesta
    assert get_punta_opuesta("Compra") == "Venta", "Opuesta de Compra es Venta"
    assert get_punta_opuesta("Venta") == "Compra", "Opuesta de Venta es Compra"
    assert get_punta_opuesta("COMPRA") == "VENTA", "Debe mantener case"
    
    print("   ✅ Helper get_punta_opuesta() funciona correctamente")


def test_fair_value_signos():
    """Test 2: Verificar que el fair value tiene el signo correcto."""
    print("\n" + "="*80)
    print("TEST 2: Signos del Fair Value")
    print("="*80)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Crear modelo
    model = SimulationsTableModel()
    
    # Datos de prueba
    spot = 4000.0
    puntos = 100.0  # Puntos positivos (forward es más caro que spot)
    nominal_usd = 1_000_000.0
    plazo = 90
    tasa_ibr = 0.11  # 11% anual
    
    print(f"\n📊 Datos de entrada:")
    print(f"   Spot: {spot:,.2f}")
    print(f"   Puntos: {puntos:,.2f} (positivos)")
    print(f"   Nominal USD: {nominal_usd:,.2f}")
    print(f"   Plazo: {plazo} días")
    print(f"   Tasa IBR: {tasa_ibr * 100:.2f}%")
    
    # =========================================================================
    # CASO 1: Cliente COMPRA → Empresa VENDE
    # =========================================================================
    print(f"\n{'─'*80}")
    print("CASO 1: Cliente COMPRA → Empresa VENDE")
    print(f"{'─'*80}")
    print("Expectativa: Fair Value POSITIVO (empresa gana)")
    print("Razón: Empresa recibe más COP por el USD que el valor spot")
    
    model.add_row({
        "cliente": "CLIENTE TEST 1",
        "nit": "123456789",
        "punta_cli": "Compra",  # Cliente compra
        "punta_emp": "Venta",    # Empresa vende
        "nominal_usd": nominal_usd,
        "fec_sim": date.today().strftime("%Y-%m-%d"),
        "fec_venc": date.today().strftime("%Y-%m-%d"),
        "plazo": plazo,
        "spot": spot,
        "puntos": puntos,
        "tasa_ibr": tasa_ibr,
    })
    
    # Forzar recálculo
    model._recalc_row(0)
    
    # Obtener valores
    row_0 = model._rows[0]
    fv_venta = row_0.get("fair_value")
    derecho_venta = row_0.get("derecho")
    obligacion_venta = row_0.get("obligacion")
    
    print(f"\n   Derecho (COP que recibe):     $ {derecho_venta:>15,.2f}")
    print(f"   Obligación (USD que entrega): $ {obligacion_venta:>15,.2f}")
    print(f"   Fair Value (Derecho - Oblig): $ {fv_venta:>15,.2f}")
    
    # Verificar signo
    assert fv_venta > 0, f"❌ Fair Value debe ser POSITIVO cuando empresa VENDE y puntos > 0. Obtenido: {fv_venta:,.2f}"
    print(f"\n   ✅ CORRECTO: Fair Value > 0 cuando empresa VENDE y puntos > 0")
    
    # =========================================================================
    # CASO 2: Cliente VENTA → Empresa COMPRA
    # =========================================================================
    print(f"\n{'─'*80}")
    print("CASO 2: Cliente VENTA → Empresa COMPRA")
    print(f"{'─'*80}")
    print("Expectativa: Fair Value NEGATIVO (empresa pierde)")
    print("Razón: Empresa paga más COP por el USD que el valor spot")
    
    model.add_row({
        "cliente": "CLIENTE TEST 2",
        "nit": "987654321",
        "punta_cli": "Venta",    # Cliente vende
        "punta_emp": "Compra",   # Empresa compra
        "nominal_usd": nominal_usd,
        "fec_sim": date.today().strftime("%Y-%m-%d"),
        "fec_venc": date.today().strftime("%Y-%m-%d"),
        "plazo": plazo,
        "spot": spot,
        "puntos": puntos,
        "tasa_ibr": tasa_ibr,
    })
    
    # Forzar recálculo
    model._recalc_row(1)
    
    # Obtener valores
    row_1 = model._rows[1]
    fv_compra = row_1.get("fair_value")
    derecho_compra = row_1.get("derecho")
    obligacion_compra = row_1.get("obligacion")
    
    print(f"\n   Derecho (USD que recibe):     $ {derecho_compra:>15,.2f}")
    print(f"   Obligación (COP que paga):    $ {obligacion_compra:>15,.2f}")
    print(f"   Fair Value (Derecho - Oblig): $ {fv_compra:>15,.2f}")
    
    # Verificar signo
    assert fv_compra < 0, f"❌ Fair Value debe ser NEGATIVO cuando empresa COMPRA y puntos > 0. Obtenido: {fv_compra:,.2f}"
    print(f"\n   ✅ CORRECTO: Fair Value < 0 cuando empresa COMPRA y puntos > 0")
    
    # =========================================================================
    # VERIFICACIÓN: Fair Values deben ser simétricos (opuestos)
    # =========================================================================
    print(f"\n{'─'*80}")
    print("VERIFICACIÓN: Fair Values deben ser simétricos")
    print(f"{'─'*80}")
    
    print(f"\n   FV (empresa VENDE):  $ {fv_venta:>15,.2f}")
    print(f"   FV (empresa COMPRA): $ {fv_compra:>15,.2f}")
    print(f"   Suma de ambos:       $ {fv_venta + fv_compra:>15,.2f}")
    
    # Los fair values deben ser simétricos (suma ≈ 0)
    assert abs(fv_venta + fv_compra) < 1.0, f"❌ Fair Values no son simétricos. Suma: {fv_venta + fv_compra:,.2f}"
    
    print(f"\n   ✅ CORRECTO: Fair Values son simétricos (suma ≈ 0)")


def test_exposicion_delta():
    """Test 3: Verificar que el delta se calcula con punta empresa y afecta correctamente la exposición."""
    print("\n" + "="*80)
    print("TEST 3: Delta basado en Punta Empresa")
    print("="*80)
    
    # Crear procesador de simulaciones
    processor = ForwardSimulationProcessor()
    
    # Datos de prueba
    spot = 4000.0
    puntos = 100.0
    nominal_usd = 1_000_000.0
    plazo = 90
    fc = 0.05
    
    # =========================================================================
    # CASO 1: Cliente COMPRA → Empresa VENDE
    # =========================================================================
    print(f"\n{'─'*80}")
    print("CASO 1: Cliente COMPRA → Empresa VENDE")
    print(f"{'─'*80}")
    
    row_venta = {
        "cliente": "TEST",
        "nit": "123",
        "punta_cli": "Compra",
        "punta_emp": "Venta",
        "nominal_usd": nominal_usd,
        "spot": spot,
        "puntos": puntos,
        "plazo": plazo,
        "fec_sim": date.today().strftime("%Y-%m-%d"),
        "fec_venc": date.today().strftime("%Y-%m-%d"),
        "derecho": (spot + puntos) * nominal_usd / 1.02,  # Valores aproximados
        "obligacion": spot * nominal_usd / 1.02,
    }
    
    op_venta = processor.build_simulated_operation(row_venta, "123", "TEST", fc)
    
    print(f"\n   Punta Cliente: Compra")
    print(f"   Punta Empresa: Venta ← Usada para cálculo de delta")
    print(f"   Delta: {op_venta['delta']}")
    print(f"   VNE: $ {op_venta['vne']:,.2f}")
    print(f"   EPFp: $ {op_venta['EPFp']:,.2f}")
    
    # Verificar delta
    assert op_venta['delta'] == -1, f"❌ Delta debe ser -1 para empresa VENTA. Obtenido: {op_venta['delta']}"
    print(f"\n   ✅ CORRECTO: Delta = -1 para empresa VENTA")
    
    # =========================================================================
    # CASO 2: Cliente VENTA → Empresa COMPRA
    # =========================================================================
    print(f"\n{'─'*80}")
    print("CASO 2: Cliente VENTA → Empresa COMPRA")
    print(f"{'─'*80}")
    
    row_compra = {
        "cliente": "TEST",
        "nit": "456",
        "punta_cli": "Venta",
        "punta_emp": "Compra",
        "nominal_usd": nominal_usd,
        "spot": spot,
        "puntos": puntos,
        "plazo": plazo,
        "fec_sim": date.today().strftime("%Y-%m-%d"),
        "fec_venc": date.today().strftime("%Y-%m-%d"),
        "derecho": spot * nominal_usd / 1.02,  # Valores aproximados
        "obligacion": (spot + puntos) * nominal_usd / 1.02,
    }
    
    op_compra = processor.build_simulated_operation(row_compra, "456", "TEST", fc)
    
    print(f"\n   Punta Cliente: Venta")
    print(f"   Punta Empresa: Compra ← Usada para cálculo de delta")
    print(f"   Delta: {op_compra['delta']}")
    print(f"   VNE: $ {op_compra['vne']:,.2f}")
    print(f"   EPFp: $ {op_compra['EPFp']:,.2f}")
    
    # Verificar delta
    assert op_compra['delta'] == 1, f"❌ Delta debe ser +1 para empresa COMPRA. Obtenido: {op_compra['delta']}"
    print(f"\n   ✅ CORRECTO: Delta = +1 para empresa COMPRA")


def run_all_tests():
    """Ejecutar todos los tests."""
    print("\n" + "="*80)
    print("INICIANDO TESTS DE CORRECCIÓN DE SIGNOS")
    print("="*80)
    
    try:
        test_helper_delta()
        test_fair_value_signos()
        test_exposicion_delta()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*80)
        print("\n📝 Resumen de correcciones verificadas:")
        print("   ✅ Helper delta_from_punta_empresa() funciona correctamente")
        print("   ✅ Helper get_punta_opuesta() funciona correctamente")
        print("   ✅ Fair Value POSITIVO cuando empresa VENDE y puntos > 0")
        print("   ✅ Fair Value NEGATIVO cuando empresa COMPRA y puntos > 0")
        print("   ✅ Fair Values son simétricos (suma ≈ 0)")
        print("   ✅ Delta = -1 cuando empresa VENDE (punta Venta)")
        print("   ✅ Delta = +1 cuando empresa COMPRA (punta Compra)")
        print("\n✅ CORRECCIÓN COMPLETA: Signos están correctos")
        print()
        return True
        
    except AssertionError as e:
        print("\n" + "="*80)
        print("❌ TEST FALLÓ")
        print("="*80)
        print(f"\nError: {e}")
        return False
    except Exception as e:
        print("\n" + "="*80)
        print("❌ ERROR INESPERADO")
        print("="*80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

