"""
Test para validar la actualización automática de Tasa Forward.

Este test verifica que:
1. Cuando el usuario edita Spot, Tasa Forward se actualiza automáticamente
2. Cuando el usuario edita Puntos, Tasa Forward se actualiza automáticamente
3. Las fórmulas de Derecho/Obligación siguen usando los valores correctos
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtCore import QDate, QModelIndex, Qt
from src.models.qt.simulations_table_model import SimulationsTableModel


def test_tasa_forward_updates_on_spot_change():
    """
    Test: Al cambiar Spot, Tasa Forward se actualiza automáticamente.
    """
    print("\n" + "="*70)
    print("TEST 1: Tasa Forward se actualiza al cambiar Spot")
    print("="*70)
    
    model = SimulationsTableModel()
    
    # Agregar fila inicial
    model.add_row({
        "cliente": "Test Cliente",
        "punta_cli": "Compra",
        "nominal_usd": 1_000_000.0,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(180),
        "plazo": 180,
        "spot": 4000.0,
        "puntos": 100.0,
        "tasa_fwd": 4100.0,  # Valor inicial
        "tasa_ibr": 0.10,
    })
    
    model._recalc_row(0)
    
    # Verificar valores iniciales
    row_data = model.get_row_data(0)
    print(f"\n📊 Valores iniciales:")
    print(f"   Spot:         {row_data['spot']:,.2f}")
    print(f"   Puntos:       {row_data['puntos']:,.2f}")
    print(f"   Tasa Forward: {row_data['tasa_fwd']:,.2f}")
    
    assert row_data['spot'] == 4000.0, "Spot inicial incorrecto"
    assert row_data['puntos'] == 100.0, "Puntos inicial incorrecto"
    assert row_data['tasa_fwd'] == 4100.0, "Tasa Forward inicial incorrecta"
    
    # Cambiar Spot usando setData (simula edición del usuario)
    nuevo_spot = 4200.0
    index_spot = model.index(0, 7)  # Col 7 = Spot
    success = model.setData(index_spot, nuevo_spot, Qt.EditRole)
    
    assert success, "setData falló al actualizar Spot"
    
    # Verificar que Tasa Forward se actualizó automáticamente
    row_data = model.get_row_data(0)
    tasa_fwd_esperada = nuevo_spot + row_data['puntos']  # 4200 + 100 = 4300
    
    print(f"\n✅ Después de cambiar Spot a {nuevo_spot:,.2f}:")
    print(f"   Spot:         {row_data['spot']:,.2f}")
    print(f"   Puntos:       {row_data['puntos']:,.2f}")
    print(f"   Tasa Forward: {row_data['tasa_fwd']:,.2f}")
    print(f"   Esperado:     {tasa_fwd_esperada:,.2f}")
    
    assert row_data['spot'] == nuevo_spot, f"Spot no se actualizó: {row_data['spot']} != {nuevo_spot}"
    assert row_data['tasa_fwd'] == tasa_fwd_esperada, \
        f"Tasa Forward no se actualizó automáticamente: {row_data['tasa_fwd']} != {tasa_fwd_esperada}"
    
    print("\n✅ TEST PASADO: Tasa Forward se actualiza automáticamente al cambiar Spot")
    return True


def test_tasa_forward_updates_on_puntos_change():
    """
    Test: Al cambiar Puntos, Tasa Forward se actualiza automáticamente.
    """
    print("\n" + "="*70)
    print("TEST 2: Tasa Forward se actualiza al cambiar Puntos")
    print("="*70)
    
    model = SimulationsTableModel()
    
    # Agregar fila inicial
    model.add_row({
        "cliente": "Test Cliente",
        "punta_cli": "Venta",
        "nominal_usd": 500_000.0,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(90),
        "plazo": 90,
        "spot": 3900.0,
        "puntos": 50.0,
        "tasa_fwd": 3950.0,  # Valor inicial
        "tasa_ibr": 0.08,
    })
    
    model._recalc_row(0)
    
    # Verificar valores iniciales
    row_data = model.get_row_data(0)
    print(f"\n📊 Valores iniciales:")
    print(f"   Spot:         {row_data['spot']:,.2f}")
    print(f"   Puntos:       {row_data['puntos']:,.2f}")
    print(f"   Tasa Forward: {row_data['tasa_fwd']:,.2f}")
    
    assert row_data['spot'] == 3900.0, "Spot inicial incorrecto"
    assert row_data['puntos'] == 50.0, "Puntos inicial incorrecto"
    assert row_data['tasa_fwd'] == 3950.0, "Tasa Forward inicial incorrecta"
    
    # Cambiar Puntos usando setData (simula edición del usuario)
    nuevos_puntos = 150.0
    index_puntos = model.index(0, 8)  # Col 8 = Puntos
    success = model.setData(index_puntos, nuevos_puntos, Qt.EditRole)
    
    assert success, "setData falló al actualizar Puntos"
    
    # Verificar que Tasa Forward se actualizó automáticamente
    row_data = model.get_row_data(0)
    tasa_fwd_esperada = row_data['spot'] + nuevos_puntos  # 3900 + 150 = 4050
    
    print(f"\n✅ Después de cambiar Puntos a {nuevos_puntos:,.2f}:")
    print(f"   Spot:         {row_data['spot']:,.2f}")
    print(f"   Puntos:       {row_data['puntos']:,.2f}")
    print(f"   Tasa Forward: {row_data['tasa_fwd']:,.2f}")
    print(f"   Esperado:     {tasa_fwd_esperada:,.2f}")
    
    assert row_data['puntos'] == nuevos_puntos, f"Puntos no se actualizó: {row_data['puntos']} != {nuevos_puntos}"
    assert row_data['tasa_fwd'] == tasa_fwd_esperada, \
        f"Tasa Forward no se actualizó automáticamente: {row_data['tasa_fwd']} != {tasa_fwd_esperada}"
    
    print("\n✅ TEST PASADO: Tasa Forward se actualiza automáticamente al cambiar Puntos")
    return True


def test_formulas_still_use_correct_values():
    """
    Test: Verificar que Derecho/Obligación usan los valores correctos después de actualizar Spot/Puntos.
    """
    print("\n" + "="*70)
    print("TEST 3: Fórmulas usan valores correctos tras actualización automática")
    print("="*70)
    
    model = SimulationsTableModel()
    
    # Agregar fila con Cliente COMPRA
    model.add_row({
        "cliente": "Test Cliente",
        "punta_cli": "Compra",
        "nominal_usd": 1_000_000.0,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(180),
        "plazo": 180,
        "spot": 4000.0,
        "puntos": 100.0,
        "tasa_fwd": 4100.0,
        "tasa_ibr": 0.10,
    })
    
    model._recalc_row(0)
    
    print(f"\n📊 Valores iniciales:")
    row_data = model.get_row_data(0)
    print(f"   Spot:         {row_data['spot']:,.2f}")
    print(f"   Puntos:       {row_data['puntos']:,.2f}")
    print(f"   Tasa Forward: {row_data['tasa_fwd']:,.2f}")
    print(f"   Derecho:      $ {row_data['derecho']:,.2f}")
    print(f"   Obligación:   $ {row_data['obligacion']:,.2f}")
    
    # Cambiar Spot
    nuevo_spot = 4200.0
    index_spot = model.index(0, 7)
    model.setData(index_spot, nuevo_spot, Qt.EditRole)
    
    # Obtener valores actualizados
    row_data = model.get_row_data(0)
    spot = row_data['spot']
    puntos = row_data['puntos']
    tasa_fwd = row_data['tasa_fwd']
    plazo = row_data['plazo']
    nominal = row_data['nominal_usd']
    tasa_ibr = row_data['tasa_ibr']
    
    # Calcular valores esperados
    df = 1.0 + (tasa_ibr * 100.0 / 100.0) * (plazo / 360.0)
    
    # Cliente COMPRA (Empresa VENDE)
    # Derecho = (Spot + Puntos) / df * Nominal
    # Obligación = Tasa Forward / df * Nominal
    derecho_esperado = (spot + puntos) / df * nominal
    obligacion_esperada = tasa_fwd / df * nominal
    
    print(f"\n✅ Después de cambiar Spot a {nuevo_spot:,.2f}:")
    print(f"   Spot:         {spot:,.2f}")
    print(f"   Puntos:       {puntos:,.2f}")
    print(f"   Tasa Forward: {tasa_fwd:,.2f} (auto-actualizada)")
    print(f"\n   Derecho calculado:      $ {row_data['derecho']:,.2f}")
    print(f"   Derecho esperado:       $ {derecho_esperado:,.2f}")
    print(f"   ✓ Usa (Spot + Puntos) = {spot + puntos:,.2f}")
    
    print(f"\n   Obligación calculada:   $ {row_data['obligacion']:,.2f}")
    print(f"   Obligación esperada:    $ {obligacion_esperada:,.2f}")
    print(f"   ✓ Usa Tasa Forward = {tasa_fwd:,.2f}")
    
    # Validar con tolerancia
    tolerancia = 0.01
    assert abs(row_data['derecho'] - derecho_esperado) < tolerancia, \
        f"Derecho incorrecto: {row_data['derecho']} != {derecho_esperado}"
    
    assert abs(row_data['obligacion'] - obligacion_esperada) < tolerancia, \
        f"Obligación incorrecta: {row_data['obligacion']} != {obligacion_esperada}"
    
    # Verificar que Tasa Forward se actualizó correctamente
    tasa_fwd_esperada = spot + puntos
    assert abs(tasa_fwd - tasa_fwd_esperada) < tolerancia, \
        f"Tasa Forward incorrecta: {tasa_fwd} != {tasa_fwd_esperada}"
    
    print("\n✅ TEST PASADO: Fórmulas usan valores correctos tras actualización automática")
    return True


def test_multiple_edits_sequence():
    """
    Test: Verificar que múltiples ediciones consecutivas funcionan correctamente.
    """
    print("\n" + "="*70)
    print("TEST 4: Múltiples ediciones consecutivas")
    print("="*70)
    
    model = SimulationsTableModel()
    
    model.add_row({
        "cliente": "Test Cliente",
        "punta_cli": "Compra",
        "nominal_usd": 1_000_000.0,
        "fec_sim": QDate.currentDate(),
        "fec_venc": QDate.currentDate().addDays(180),
        "plazo": 180,
        "spot": 4000.0,
        "puntos": 100.0,
        "tasa_fwd": 4100.0,
        "tasa_ibr": 0.10,
    })
    
    model._recalc_row(0)
    
    print(f"\n📊 Secuencia de ediciones:")
    
    # Edición 1: Cambiar Spot
    model.setData(model.index(0, 7), 4200.0, Qt.EditRole)
    row_data = model.get_row_data(0)
    print(f"\n1. Spot → 4200: Tasa Forward = {row_data['tasa_fwd']:,.2f} (esperado: 4300)")
    assert row_data['tasa_fwd'] == 4300.0, "Tasa Forward incorrecta después de editar Spot"
    
    # Edición 2: Cambiar Puntos
    model.setData(model.index(0, 8), 150.0, Qt.EditRole)
    row_data = model.get_row_data(0)
    print(f"2. Puntos → 150: Tasa Forward = {row_data['tasa_fwd']:,.2f} (esperado: 4350)")
    assert row_data['tasa_fwd'] == 4350.0, "Tasa Forward incorrecta después de editar Puntos"
    
    # Edición 3: Cambiar Spot nuevamente
    model.setData(model.index(0, 7), 4100.0, Qt.EditRole)
    row_data = model.get_row_data(0)
    print(f"3. Spot → 4100: Tasa Forward = {row_data['tasa_fwd']:,.2f} (esperado: 4250)")
    assert row_data['tasa_fwd'] == 4250.0, "Tasa Forward incorrecta en tercera edición"
    
    print("\n✅ TEST PASADO: Múltiples ediciones funcionan correctamente")
    return True


def run_all_tests():
    """
    Ejecuta todos los tests y muestra resumen.
    """
    print("\n" + "="*70)
    print(" VALIDACIÓN DE ACTUALIZACIÓN AUTOMÁTICA DE TASA FORWARD ")
    print("="*70)
    print("\nObjetivo:")
    print("  • Tasa Forward se actualiza cuando cambian Spot o Puntos")
    print("  • Fórmulas de Derecho/Obligación permanecen intactas")
    print("  • Comportamiento consistente en múltiples ediciones")
    
    tests = [
        ("Actualización al cambiar Spot", test_tasa_forward_updates_on_spot_change),
        ("Actualización al cambiar Puntos", test_tasa_forward_updates_on_puntos_change),
        ("Fórmulas usan valores correctos", test_formulas_still_use_correct_values),
        ("Múltiples ediciones consecutivas", test_multiple_edits_sequence),
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
        print(f"  {resultado:50} - {nombre}")
    
    todos_pasaron = all("✅" in r for _, r in resultados)
    
    if todos_pasaron:
        print("\n✅ TODOS LOS TESTS PASARON EXITOSAMENTE\n")
        print("Comportamiento restaurado:")
        print("  • Tasa Forward = Spot + Puntos (actualización automática)")
        print("  • Ediciones de Spot o Puntos disparan recálculo")
        print("  • Fórmulas de Derecho/Obligación sin cambios")
        print("  • Compatible con múltiples ediciones consecutivas")
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

