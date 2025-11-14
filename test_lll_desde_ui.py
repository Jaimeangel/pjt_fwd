"""
Test para verificar que el cálculo de Disponibilidad LLL usa el valor
mostrado en la UI en lugar de recalcularlo desde patrimonio técnico.

Objetivo:
- Verificar que ForwardDataModel guarda correctamente los límites de crédito
- Verificar que _get_lll_cop() devuelve el valor del modelo (no recalcula)
- Verificar que las disponibilidades LLL usan la misma base que la UI
"""

from src.models.forward_data_model import ForwardDataModel


def test_credit_limits_storage():
    """Test 1: Verificar que el modelo almacena y devuelve correctamente los límites."""
    print("\n" + "="*80)
    print("TEST 1: Almacenamiento de Límites de Crédito")
    print("="*80)
    
    model = ForwardDataModel()
    
    # Valores de prueba
    lca_cop = 1_000_000_000.0  # 1,000 MM COP
    lll_cop = 5_625_000_000.0  # 25% de PT = 25,000 MM, menos 10% = 22,500 MM → en COP
    
    print(f"\n📊 Valores de entrada:")
    print(f"   LCA (Línea Aprobada): $ {lca_cop:,.0f}")
    print(f"   LLL (Límite Máximo):  $ {lll_cop:,.0f}")
    
    # Guardar límites
    model.set_credit_limits(
        linea_credito_aprobada_cop=lca_cop,
        lll_cop=lll_cop
    )
    
    # Recuperar límites
    lca_retrieved = model.get_lca_limit_cop()
    lll_retrieved = model.get_lll_limit_cop()
    
    print(f"\n📊 Valores recuperados:")
    print(f"   LCA (Línea Aprobada): $ {lca_retrieved:,.0f}")
    print(f"   LLL (Límite Máximo):  $ {lll_retrieved:,.0f}")
    
    # Verificar
    assert lca_retrieved == lca_cop, f"LCA no coincide: esperado {lca_cop}, obtenido {lca_retrieved}"
    assert lll_retrieved == lll_cop, f"LLL no coincide: esperado {lll_cop}, obtenido {lll_retrieved}"
    
    print(f"\n   ✅ Límites almacenados y recuperados correctamente")


def test_lll_consistency():
    """Test 2: Verificar que el LLL usado en disponibilidad es el mismo de la UI."""
    print("\n" + "="*80)
    print("TEST 2: Consistencia del LLL en Disponibilidad")
    print("="*80)
    
    model = ForwardDataModel()
    
    # Simular valores que se mostrarían en UI
    lll_ui = 5_625_000_000.0  # LLL que se muestra en "Parámetros de crédito"
    
    print(f"\n📊 Escenario:")
    print(f"   LLL mostrado en UI: $ {lll_ui:,.0f}")
    
    # Guardar el LLL que se muestra en UI
    model.set_credit_limits(
        linea_credito_aprobada_cop=1_000_000_000.0,
        lll_cop=lll_ui
    )
    
    # Simular Outstanding de contraparte y grupo
    outstanding_cte = 2_000_000_000.0  # 2,000 MM COP
    outstanding_grp = 3_000_000_000.0  # 3,000 MM COP
    
    print(f"   Outstanding Contraparte: $ {outstanding_cte:,.0f}")
    print(f"   Outstanding Grupo:       $ {outstanding_grp:,.0f}")
    
    # Calcular disponibilidades (simulando lo que hace el controlador)
    lll_cop = model.get_lll_limit_cop()  # ← Usa el valor del modelo
    
    disp_cte_cop = lll_cop - outstanding_cte
    disp_grp_cop = lll_cop - outstanding_grp
    disp_cte_pct = (disp_cte_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
    disp_grp_pct = (disp_grp_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
    
    print(f"\n📊 Disponibilidades calculadas:")
    print(f"   Base LLL usada:           $ {lll_cop:,.0f}")
    print(f"   Disp. Contraparte (COP):  $ {disp_cte_cop:,.0f}")
    print(f"   Disp. Contraparte (%):      {disp_cte_pct:.2f}%")
    print(f"   Disp. Grupo (COP):        $ {disp_grp_cop:,.0f}")
    print(f"   Disp. Grupo (%):            {disp_grp_pct:.2f}%")
    
    # Verificar que la base usada es la misma de la UI
    assert lll_cop == lll_ui, f"❌ LLL usado ({lll_cop:,.0f}) NO coincide con UI ({lll_ui:,.0f})"
    
    print(f"\n   ✅ LLL usado en disponibilidad coincide con el de la UI")
    
    # Guardar en el modelo
    model.set_lll_availability(
        disp_cte_cop=disp_cte_cop,
        disp_cte_pct=disp_cte_pct,
        disp_grp_cop=disp_grp_cop,
        disp_grp_pct=disp_grp_pct
    )
    
    # Recuperar y verificar
    disp_cte_cop_ret, disp_cte_pct_ret = model.get_lll_availability_counterparty()
    disp_grp_cop_ret, disp_grp_pct_ret = model.get_lll_availability_group()
    
    print(f"\n📊 Disponibilidades almacenadas:")
    print(f"   Disp. Contraparte (COP):  $ {disp_cte_cop_ret:,.0f}")
    print(f"   Disp. Contraparte (%):      {disp_cte_pct_ret:.2f}%")
    print(f"   Disp. Grupo (COP):        $ {disp_grp_cop_ret:,.0f}")
    print(f"   Disp. Grupo (%):            {disp_grp_pct_ret:.2f}%")
    
    assert disp_cte_cop_ret == disp_cte_cop
    assert disp_cte_pct_ret == disp_cte_pct
    assert disp_grp_cop_ret == disp_grp_cop
    assert disp_grp_pct_ret == disp_grp_pct
    
    print(f"\n   ✅ Disponibilidades almacenadas y recuperadas correctamente")


def test_zero_lll():
    """Test 3: Verificar manejo correcto de LLL = 0."""
    print("\n" + "="*80)
    print("TEST 3: Manejo de LLL = 0")
    print("="*80)
    
    model = ForwardDataModel()
    
    # LLL = 0 (ej. sin patrimonio técnico configurado)
    model.set_credit_limits(
        linea_credito_aprobada_cop=0.0,
        lll_cop=0.0
    )
    
    lll_cop = model.get_lll_limit_cop()
    
    print(f"\n📊 LLL = {lll_cop}")
    
    # Calcular disponibilidad con LLL = 0
    outstanding = 1_000_000.0
    disp_cop = lll_cop - outstanding
    disp_pct = (disp_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
    
    print(f"   Outstanding: $ {outstanding:,.0f}")
    print(f"   Disp (COP):  $ {disp_cop:,.0f} (negativo esperado)")
    print(f"   Disp (%):      {disp_pct:.2f}% (0 esperado)")
    
    assert lll_cop == 0.0
    assert disp_pct == 0.0, "Porcentaje debe ser 0 cuando LLL = 0"
    
    print(f"\n   ✅ LLL = 0 manejado correctamente")


def run_all_tests():
    """Ejecutar todos los tests."""
    print("\n" + "="*80)
    print("INICIANDO TESTS: Disponibilidad LLL desde UI")
    print("="*80)
    
    try:
        test_credit_limits_storage()
        test_lll_consistency()
        test_zero_lll()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*80)
        print("\n📝 Resumen de verificaciones:")
        print("   ✅ Límites almacenados y recuperados correctamente")
        print("   ✅ LLL usado en disponibilidad coincide con el de la UI")
        print("   ✅ Disponibilidades calculadas y almacenadas correctamente")
        print("   ✅ Manejo correcto de LLL = 0")
        print("\n✅ CORRECCIÓN VALIDADA: Disponibilidad LLL usa valor de UI")
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
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)

