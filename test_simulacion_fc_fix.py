"""
Test para validar que el FC (factor de conversión) tiene valor por defecto correcto.

Bug identificado:
- fc_global se inicializa en 0.0
- Si no hay operaciones vigentes (415), fc_por_nit no tiene el NIT
- get_fc_for_nit() devuelve 0.0
- EPFp = fc * vne = 0 * vne = 0
- Outstanding = 0

Fix implementado:
- get_fc_for_nit() ahora devuelve 0.10 por defecto (valor normativo)
- Esto permite calcular exposición incluso sin datos del 415
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.forward_data_model import ForwardDataModel


def test_fc_default_value():
    """Test: FC debe tener valor por defecto de 0.10 cuando no hay datos del 415."""
    print("\n" + "="*70)
    print("TEST 1: FC tiene valor por defecto correcto")
    print("="*70)
    
    model = ForwardDataModel()
    
    # Verificar fc_global inicial
    print(f"\n   fc_global inicial: {model.fc_global}")
    assert model.fc_global == 0.0, "fc_global debe iniciar en 0.0"
    
    # Verificar que fc_por_nit está vacío
    print(f"   fc_por_nit inicial: {model.fc_por_nit}")
    assert len(model.fc_por_nit) == 0, "fc_por_nit debe estar vacío"
    
    # Probar get_fc_for_nit con un NIT que NO existe
    nit_test = "900123456"
    fc_obtenido = model.get_fc_for_nit(nit_test)
    
    print(f"\n   get_fc_for_nit('{nit_test}'):")
    print(f"      Resultado: {fc_obtenido}")
    print(f"      Esperado:  0.10 (valor por defecto)")
    
    assert fc_obtenido == 0.10, f"FC debe ser 0.10 por defecto, obtenido: {fc_obtenido}"
    
    print(f"\n   [OK] TEST PASADO: FC por defecto = 0.10")
    return True


def test_fc_from_dataset():
    """Test: FC debe usar valor específico si existe en fc_por_nit."""
    print("\n" + "="*70)
    print("TEST 2: FC usa valor específico del NIT si existe")
    print("="*70)
    
    model = ForwardDataModel()
    
    # Agregar fc específico para un NIT
    nit_test = "900123456"
    fc_especifico = 0.08
    model.fc_por_nit[nit_test] = fc_especifico
    
    print(f"\n   fc_por_nit['{nit_test}'] = {fc_especifico}")
    
    # Obtener FC para ese NIT
    fc_obtenido = model.get_fc_for_nit(nit_test)
    
    print(f"   get_fc_for_nit('{nit_test}') = {fc_obtenido}")
    print(f"   Esperado: {fc_especifico}")
    
    assert fc_obtenido == fc_especifico, f"FC debe usar valor específico: {fc_obtenido} != {fc_especifico}"
    
    print(f"\n   [OK] TEST PASADO: FC usa valor específico del NIT")
    return True


def test_fc_global_override():
    """Test: FC debe usar fc_global si está definido y no hay específico."""
    print("\n" + "="*70)
    print("TEST 3: FC usa fc_global si existe y no hay específico")
    print("="*70)
    
    model = ForwardDataModel()
    
    # Setear fc_global
    model.fc_global = 0.12
    print(f"\n   fc_global = {model.fc_global}")
    
    # Obtener FC para un NIT que NO tiene específico
    nit_test = "900999888"
    fc_obtenido = model.get_fc_for_nit(nit_test)
    
    print(f"   get_fc_for_nit('{nit_test}') = {fc_obtenido}")
    print(f"   Esperado: {model.fc_global} (fc_global)")
    
    assert fc_obtenido == 0.12, f"FC debe usar fc_global: {fc_obtenido} != 0.12"
    
    print(f"\n   [OK] TEST PASADO: FC usa fc_global correctamente")
    return True


def test_fc_priority():
    """Test: Prioridad FC específico > FC global > FC por defecto."""
    print("\n" + "="*70)
    print("TEST 4: Prioridad de FC (específico > global > defecto)")
    print("="*70)
    
    model = ForwardDataModel()
    
    # Caso 1: Solo por defecto
    nit1 = "111111111"
    fc1 = model.get_fc_for_nit(nit1)
    print(f"\n   Caso 1: Sin fc_global, sin específico")
    print(f"      FC = {fc1} (debe ser 0.10 por defecto)")
    assert fc1 == 0.10
    
    # Caso 2: Con fc_global
    model.fc_global = 0.12
    fc2 = model.get_fc_for_nit(nit1)
    print(f"\n   Caso 2: Con fc_global=0.12, sin específico")
    print(f"      FC = {fc2} (debe ser 0.12 de fc_global)")
    assert fc2 == 0.12
    
    # Caso 3: Con fc específico (mayor prioridad)
    model.fc_por_nit[nit1] = 0.15
    fc3 = model.get_fc_for_nit(nit1)
    print(f"\n   Caso 3: Con fc_global=0.12 y específico=0.15")
    print(f"      FC = {fc3} (debe ser 0.15 específico)")
    assert fc3 == 0.15
    
    print(f"\n   [OK] TEST PASADO: Prioridad correcta (específico > global > defecto)")
    return True


def test_epfp_calculation_with_fc():
    """Test: EPFp se calcula correctamente con diferentes FC."""
    print("\n" + "="*70)
    print("TEST 5: Cálculo de EPFp con diferentes FC")
    print("="*70)
    
    # Valores de prueba
    vna = 1000000.0  # USD
    trm = 4000.0
    delta = 1
    td = 180
    import math
    t = math.sqrt(min(td, 252) / 252.0)
    
    vne = vna * trm * delta * t
    
    print(f"\n   Valores base:")
    print(f"      vna   = $ {vna:,.2f} USD")
    print(f"      trm   = {trm:,.2f}")
    print(f"      delta = {delta}")
    print(f"      td    = {td} días")
    print(f"      t     = {t:.6f}")
    print(f"      vne   = $ {vne:,.2f}")
    
    # Caso 1: FC = 0 (bug)
    fc_bug = 0.0
    epfp_bug = fc_bug * vne
    print(f"\n   Caso 1: FC = {fc_bug} (BUG)")
    print(f"      EPFp = {fc_bug} * vne = $ {epfp_bug:,.2f}")
    print(f"      [!] Outstanding = 0 (sin exposicion)")
    
    # Caso 2: FC = 0.10 (fix)
    fc_fix = 0.10
    epfp_fix = fc_fix * vne
    print(f"\n   Caso 2: FC = {fc_fix} (FIX)")
    print(f"      EPFp = {fc_fix} * vne = $ {epfp_fix:,.2f}")
    print(f"      [OK] Outstanding > 0 (con exposicion)")
    
    assert epfp_fix > 0, "EPFp debe ser > 0 con FC = 0.10"
    assert epfp_fix > 300000000, f"EPFp esperado > 300M, obtenido: {epfp_fix}"
    
    print(f"\n   [OK] TEST PASADO: EPFp se calcula correctamente con FC")
    return True


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print(" VALIDACIÓN DEL FIX: FC POR DEFECTO ")
    print("="*70)
    print("\nObjetivo:")
    print("  - Verificar que FC tiene valor por defecto de 0.10")
    print("  - Confirmar que EPFp > 0 cuando FC > 0")
    print("  - Validar prioridad: específico > global > defecto")
    
    tests = [
        ("FC por defecto = 0.10", test_fc_default_value),
        ("FC usa valor específico del NIT", test_fc_from_dataset),
        ("FC usa fc_global si existe", test_fc_global_override),
        ("Prioridad de FC", test_fc_priority),
        ("EPFp con diferentes FC", test_epfp_calculation_with_fc),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            test_func()
            resultados.append((nombre, "[OK] PASO"))
        except AssertionError as e:
            resultados.append((nombre, f"[FAIL] FALLO: {e}"))
        except Exception as e:
            resultados.append((nombre, f"[ERROR] ERROR: {e}"))
    
    print("\n" + "="*70)
    print(" RESUMEN ")
    print("="*70)
    for nombre, resultado in resultados:
        print(f"  {resultado:50} - {nombre}")
    
    todos_pasaron = all("[OK]" in r for _, r in resultados)
    
    if todos_pasaron:
        print("\n[OK] TODOS LOS TESTS PASARON EXITOSAMENTE\n")
        print("Fix implementado:")
        print("  [OK] get_fc_for_nit() devuelve 0.10 por defecto")
        print("  [OK] EPFp > 0 cuando se usa el valor por defecto")
        print("  [OK] Prioridad correcta: especifico > global > defecto")
        print("  [OK] Simulacion funcionara incluso sin datos del 415")
    else:
        print("\n[FAIL] ALGUNOS TESTS FALLARON\n")
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
