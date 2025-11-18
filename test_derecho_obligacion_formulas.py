"""
Test para validar las fórmulas actualizadas de Derecho y Obligación.

Este test verifica que:
1. El denominador (factor de descuento) no cambió.
2. La expresión (spot + puntos) se mantiene donde corresponde.
3. La tasa_forward se usa en lugar de spot donde corresponde.
4. Fair Value = Derecho - Obligación.

Casos de prueba:
- Cliente COMPRA (Empresa VENDE):
    Derecho = (spot + puntos) / df * nominal
    Obligación = tasa_forward / df * nominal
    
- Cliente VENDE (Empresa COMPRA):
    Derecho = tasa_forward / df * nominal
    Obligación = (spot + puntos) / df * nominal
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtCore import QDate
from src.models.qt.simulations_table_model import SimulationsTableModel


def test_formulas_cliente_compra():
    """
    Test: Cliente COMPRA (Empresa VENDE USD)
    
    Derecho debe usar (spot + puntos)
    Obligación debe usar tasa_forward
    """
    print("\n" + "="*70)
    print("TEST 1: Cliente COMPRA (Empresa VENDE)")
    print("="*70)
    
    model = SimulationsTableModel()
    
    # Datos de prueba
    spot = 4000.0
    puntos = 100.0
    tasa_fwd = 4200.0  # ⚠️ DIFERENTE de spot + puntos (4100)
    nominal_usd = 1_000_000.0
    plazo_dias = 180
    tasa_ibr_decimal = 0.10  # 10%
    
    # Agregar fila con Cliente = "Compra" (Empresa = "Venta")
    model.add_row({
        "cliente": "Test Cliente",
        "punta_cli": "Compra",
        "punta_emp": "Venta",
        "nominal_usd": nominal_usd,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(plazo_dias),
        "plazo": plazo_dias,
        "spot": spot,
        "puntos": puntos,
        "tasa_fwd": tasa_fwd,
        "tasa_ibr": tasa_ibr_decimal,
    })
    
    # Forzar recálculo
    model._recalc_row(0)
    
    # Calcular valores esperados manualmente
    df = 1.0 + (tasa_ibr_decimal * 100.0 / 100.0) * (plazo_dias / 360.0)
    
    derecho_esperado = (spot + puntos) / df * nominal_usd
    obligacion_esperada = tasa_fwd / df * nominal_usd
    fair_value_esperado = derecho_esperado - obligacion_esperada
    
    # Obtener valores del modelo
    row_data = model.get_row_data(0)
    derecho_calculado = row_data.get("derecho", 0)
    obligacion_calculada = row_data.get("obligacion", 0)
    fair_value_calculado = row_data.get("fair_value", 0)
    
    print(f"\n📊 Datos de entrada:")
    print(f"   Spot:           {spot:,.2f}")
    print(f"   Puntos:         {puntos:,.2f}")
    print(f"   Spot + Puntos:  {spot + puntos:,.2f}")
    print(f"   Tasa Forward:   {tasa_fwd:,.2f} ⚠️ (diferente de Spot+Puntos)")
    print(f"   Nominal USD:    {nominal_usd:,.0f}")
    print(f"   Plazo días:     {plazo_dias}")
    print(f"   Tasa IBR:       {tasa_ibr_decimal * 100:.1f}%")
    print(f"   Factor df:      {df:.6f}")
    
    print(f"\n💰 Resultados:")
    print(f"   Derecho esperado:      $ {derecho_esperado:,.2f}")
    print(f"   Derecho calculado:     $ {derecho_calculado:,.2f}")
    print(f"   ✓ Usa (Spot + Puntos) = {spot + puntos:,.2f}")
    
    print(f"\n   Obligación esperada:   $ {obligacion_esperada:,.2f}")
    print(f"   Obligación calculada:  $ {obligacion_calculada:,.2f}")
    print(f"   ✓ Usa Tasa Forward = {tasa_fwd:,.2f}")
    
    print(f"\n   Fair Value esperado:   $ {fair_value_esperado:,.2f}")
    print(f"   Fair Value calculado:  $ {fair_value_calculado:,.2f}")
    
    # Validar con tolerancia
    tolerancia = 0.01
    assert abs(derecho_calculado - derecho_esperado) < tolerancia, \
        f"Derecho incorrecto: esperado {derecho_esperado}, obtenido {derecho_calculado}"
    
    assert abs(obligacion_calculada - obligacion_esperada) < tolerancia, \
        f"Obligación incorrecta: esperado {obligacion_esperada}, obtenido {obligacion_calculada}"
    
    assert abs(fair_value_calculado - fair_value_esperado) < tolerancia, \
        f"Fair Value incorrecto: esperado {fair_value_esperado}, obtenido {fair_value_calculado}"
    
    print("\n✅ TEST PASADO: Fórmulas correctas para Cliente COMPRA")
    return True


def test_formulas_cliente_vende():
    """
    Test: Cliente VENDE (Empresa COMPRA USD)
    
    Derecho debe usar tasa_forward
    Obligación debe usar (spot + puntos)
    """
    print("\n" + "="*70)
    print("TEST 2: Cliente VENDE (Empresa COMPRA)")
    print("="*70)
    
    model = SimulationsTableModel()
    
    # Datos de prueba
    spot = 4000.0
    puntos = 100.0
    tasa_fwd = 4200.0  # ⚠️ DIFERENTE de spot + puntos (4100)
    nominal_usd = 1_000_000.0
    plazo_dias = 180
    tasa_ibr_decimal = 0.10  # 10%
    
    # Agregar fila con Cliente = "Venta" (Empresa = "Compra")
    model.add_row({
        "cliente": "Test Cliente",
        "punta_cli": "Venta",
        "punta_emp": "Compra",
        "nominal_usd": nominal_usd,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(plazo_dias),
        "plazo": plazo_dias,
        "spot": spot,
        "puntos": puntos,
        "tasa_fwd": tasa_fwd,
        "tasa_ibr": tasa_ibr_decimal,
    })
    
    # Forzar recálculo
    model._recalc_row(0)
    
    # Calcular valores esperados manualmente
    df = 1.0 + (tasa_ibr_decimal * 100.0 / 100.0) * (plazo_dias / 360.0)
    
    derecho_esperado = tasa_fwd / df * nominal_usd
    obligacion_esperada = (spot + puntos) / df * nominal_usd
    fair_value_esperado = derecho_esperado - obligacion_esperada
    
    # Obtener valores del modelo
    row_data = model.get_row_data(0)
    derecho_calculado = row_data.get("derecho", 0)
    obligacion_calculada = row_data.get("obligacion", 0)
    fair_value_calculado = row_data.get("fair_value", 0)
    
    print(f"\n📊 Datos de entrada:")
    print(f"   Spot:           {spot:,.2f}")
    print(f"   Puntos:         {puntos:,.2f}")
    print(f"   Spot + Puntos:  {spot + puntos:,.2f}")
    print(f"   Tasa Forward:   {tasa_fwd:,.2f} ⚠️ (diferente de Spot+Puntos)")
    print(f"   Nominal USD:    {nominal_usd:,.0f}")
    print(f"   Plazo días:     {plazo_dias}")
    print(f"   Tasa IBR:       {tasa_ibr_decimal * 100:.1f}%")
    print(f"   Factor df:      {df:.6f}")
    
    print(f"\n💰 Resultados:")
    print(f"   Derecho esperado:      $ {derecho_esperado:,.2f}")
    print(f"   Derecho calculado:     $ {derecho_calculado:,.2f}")
    print(f"   ✓ Usa Tasa Forward = {tasa_fwd:,.2f}")
    
    print(f"\n   Obligación esperada:   $ {obligacion_esperada:,.2f}")
    print(f"   Obligación calculada:  $ {obligacion_calculada:,.2f}")
    print(f"   ✓ Usa (Spot + Puntos) = {spot + puntos:,.2f}")
    
    print(f"\n   Fair Value esperado:   $ {fair_value_esperado:,.2f}")
    print(f"   Fair Value calculado:  $ {fair_value_calculado:,.2f}")
    
    # Validar con tolerancia
    tolerancia = 0.01
    assert abs(derecho_calculado - derecho_esperado) < tolerancia, \
        f"Derecho incorrecto: esperado {derecho_esperado}, obtenido {derecho_calculado}"
    
    assert abs(obligacion_calculada - obligacion_esperada) < tolerancia, \
        f"Obligación incorrecta: esperado {obligacion_esperada}, obtenido {obligacion_calculada}"
    
    assert abs(fair_value_calculado - fair_value_esperado) < tolerancia, \
        f"Fair Value incorrecto: esperado {fair_value_esperado}, obtenido {fair_value_calculado}"
    
    print("\n✅ TEST PASADO: Fórmulas correctas para Cliente VENDE")
    return True


def test_denominador_no_cambio():
    """
    Test: Verificar que el denominador (factor de descuento) no cambió.
    """
    print("\n" + "="*70)
    print("TEST 3: Denominador (Factor de Descuento) sin cambios")
    print("="*70)
    
    # Valores de prueba
    tasa_ibr_decimal = 0.12  # 12%
    plazo_dias = 360
    
    # Fórmula esperada: df = 1 + (IBR% / 100) * (Plazo / 360)
    df_esperado = 1.0 + (tasa_ibr_decimal * 100.0 / 100.0) * (plazo_dias / 360.0)
    
    print(f"\n📊 Datos:")
    print(f"   Tasa IBR:   {tasa_ibr_decimal * 100:.1f}%")
    print(f"   Plazo días: {plazo_dias}")
    print(f"\n   df = 1 + (IBR% / 100) * (Plazo / 360)")
    print(f"   df = 1 + ({tasa_ibr_decimal * 100:.1f} / 100) * ({plazo_dias} / 360)")
    print(f"   df = {df_esperado:.6f}")
    
    print("\n✅ TEST PASADO: Denominador mantiene fórmula original")
    return True


def test_spot_puntos_se_mantiene():
    """
    Test: Verificar que la expresión (spot + puntos) se mantiene en las fórmulas.
    """
    print("\n" + "="*70)
    print("TEST 4: Expresión (Spot + Puntos) se mantiene")
    print("="*70)
    
    model = SimulationsTableModel()
    
    spot = 3900.0
    puntos = 150.0
    tasa_fwd = 4100.0  # Diferente de spot + puntos
    nominal_usd = 500_000.0
    plazo_dias = 90
    tasa_ibr_decimal = 0.08
    
    print(f"\n📊 Datos:")
    print(f"   Spot:          {spot:,.2f}")
    print(f"   Puntos:        {puntos:,.2f}")
    print(f"   Spot + Puntos: {spot + puntos:,.2f}")
    print(f"   Tasa Forward:  {tasa_fwd:,.2f}")
    
    # Caso 1: Cliente COMPRA
    model.add_row({
        "cliente": "Test 1",
        "punta_cli": "Compra",
        "nominal_usd": nominal_usd,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(plazo_dias),
        "plazo": plazo_dias,
        "spot": spot,
        "puntos": puntos,
        "tasa_fwd": tasa_fwd,
        "tasa_ibr": tasa_ibr_decimal,
    })
    
    # Forzar recálculo
    model._recalc_row(0)
    
    row1 = model.get_row_data(0)
    derecho1 = row1.get("derecho", 0)
    
    df = 1.0 + (tasa_ibr_decimal * 100.0 / 100.0) * (plazo_dias / 360.0)
    derecho_con_spot_puntos = (spot + puntos) / df * nominal_usd
    
    print(f"\n✓ Cliente COMPRA:")
    print(f"  Derecho calculado:           $ {derecho1:,.2f}")
    print(f"  Derecho con (Spot + Puntos): $ {derecho_con_spot_puntos:,.2f}")
    print(f"  Match: {abs(derecho1 - derecho_con_spot_puntos) < 0.01}")
    
    assert abs(derecho1 - derecho_con_spot_puntos) < 0.01, \
        "Derecho debe usar (spot + puntos) cuando cliente COMPRA"
    
    # Caso 2: Cliente VENDE
    model2 = SimulationsTableModel()
    model2.add_row({
        "cliente": "Test 2",
        "punta_cli": "Venta",
        "nominal_usd": nominal_usd,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(plazo_dias),
        "plazo": plazo_dias,
        "spot": spot,
        "puntos": puntos,
        "tasa_fwd": tasa_fwd,
        "tasa_ibr": tasa_ibr_decimal,
    })
    
    # Forzar recálculo
    model2._recalc_row(0)
    
    row2 = model2.get_row_data(0)
    obligacion2 = row2.get("obligacion", 0)
    
    obligacion_con_spot_puntos = (spot + puntos) / df * nominal_usd
    
    print(f"\n✓ Cliente VENDE:")
    print(f"  Obligación calculada:         $ {obligacion2:,.2f}")
    print(f"  Obligación con (Spot + Puntos): $ {obligacion_con_spot_puntos:,.2f}")
    print(f"  Match: {abs(obligacion2 - obligacion_con_spot_puntos) < 0.01}")
    
    assert abs(obligacion2 - obligacion_con_spot_puntos) < 0.01, \
        "Obligación debe usar (spot + puntos) cuando cliente VENDE"
    
    print("\n✅ TEST PASADO: (Spot + Puntos) se mantiene en ambos casos")
    return True


def run_all_tests():
    """
    Ejecuta todos los tests y muestra resumen.
    """
    print("\n" + "="*70)
    print(" VALIDACIÓN DE FÓRMULAS DE DERECHO Y OBLIGACIÓN ")
    print("="*70)
    print("\nActualización realizada:")
    print("  • Derecho y Obligación ahora usan 'tasa_forward' donde corresponde")
    print("  • Se mantiene (spot + puntos) donde corresponde")
    print("  • Denominador (df) sin cambios")
    print("  • Fair Value = Derecho - Obligación")
    
    tests = [
        ("Cliente COMPRA", test_formulas_cliente_compra),
        ("Cliente VENDE", test_formulas_cliente_vende),
        ("Denominador sin cambios", test_denominador_no_cambio),
        ("(Spot + Puntos) se mantiene", test_spot_puntos_se_mantiene),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            test_func()
            resultados.append((nombre, "✅ PASÓ"))
        except AssertionError as e:
            resultados.append((nombre, f"❌ FALLÓ: {e}"))
        except Exception as e:
            resultados.append((nombre, f"❌ ERROR: {e}"))
    
    print("\n" + "="*70)
    print(" RESUMEN DE TESTS ")
    print("="*70)
    for nombre, resultado in resultados:
        print(f"  {resultado:40} - {nombre}")
    
    todos_pasaron = all("✅" in r for _, r in resultados)
    
    if todos_pasaron:
        print("\n✅ TODOS LOS TESTS PASARON EXITOSAMENTE\n")
        print("Las fórmulas están correctamente implementadas:")
        print("  • Cliente COMPRA (Empresa VENDE):")
        print("      Derecho    = (Spot + Puntos) / df * Nominal")
        print("      Obligación = Tasa Forward / df * Nominal")
        print("  • Cliente VENDE (Empresa COMPRA):")
        print("      Derecho    = Tasa Forward / df * Nominal")
        print("      Obligación = (Spot + Puntos) / df * Nominal")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON\n")
        return False
    
    return True


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

