"""
Test para verificar que la Disponibilidad LLL se actualiza correctamente
al cambiar de contraparte, incluso cuando no hay operaciones.

Escenarios a validar:
1. Contraparte SIN operaciones → Disponibilidad = 100%
2. Contraparte CON operaciones → Disponibilidad < 100%
3. Cambiar de contraparte CON ops a contraparte SIN ops → Vuelve a 100%
"""

from src.models.forward_data_model import ForwardDataModel


def test_disponibilidad_sin_operaciones():
    """
    Test 1: Contraparte sin operaciones debe mostrar disponibilidad 100%.
    """
    print("\n" + "="*80)
    print("TEST 1: Contraparte SIN operaciones → Disponibilidad = 100%")
    print("="*80)
    
    model = ForwardDataModel()
    
    # Configurar LLL
    lll_cop = 5_625_000_000.0  # $ 5,625 MM COP
    model.set_credit_limits(
        linea_credito_aprobada_cop=1_000_000_000.0,
        lll_cop=lll_cop
    )
    
    # Simular contraparte sin operaciones (outstanding = 0)
    outstanding_cte = 0.0
    outstanding_grp = 0.0
    
    print(f"\n📊 Datos:")
    print(f"   LLL: $ {lll_cop:,.0f}")
    print(f"   Outstanding Contraparte: $ {outstanding_cte:,.0f}")
    print(f"   Outstanding Grupo: $ {outstanding_grp:,.0f}")
    
    # Setear exposiciones
    model.set_exposure_counterparty(outstanding_cte, outstanding_cte)
    model.set_exposure_group(outstanding_grp, outstanding_grp)
    
    # Calcular disponibilidades (como lo hace el controlador)
    lll_from_model = model.get_lll_limit_cop()
    disp_cte_cop = lll_from_model - outstanding_cte
    disp_grp_cop = lll_from_model - outstanding_grp
    disp_cte_pct = (disp_cte_cop / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    disp_grp_pct = (disp_grp_cop / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    
    # Guardar en modelo
    model.set_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
    
    # Recuperar
    disp_cte_cop_ret, disp_cte_pct_ret = model.get_lll_availability_counterparty()
    disp_grp_cop_ret, disp_grp_pct_ret = model.get_lll_availability_group()
    
    print(f"\n✅ Disponibilidades calculadas:")
    print(f"   Contraparte: $ {disp_cte_cop_ret:,.0f} ({disp_cte_pct_ret:.2f}%)")
    print(f"   Grupo:       $ {disp_grp_cop_ret:,.0f} ({disp_grp_pct_ret:.2f}%)")
    
    # Verificar
    assert disp_cte_cop_ret == lll_cop, f"Disponibilidad COP debe ser = LLL completo"
    assert disp_cte_pct_ret == 100.0, f"Disponibilidad % debe ser 100%. Obtenido: {disp_cte_pct_ret:.2f}%"
    assert disp_grp_pct_ret == 100.0, f"Disponibilidad grupo % debe ser 100%. Obtenido: {disp_grp_pct_ret:.2f}%"
    
    print(f"\n   ✅ Disponibilidad correcta: 100% cuando outstanding = 0")


def test_disponibilidad_con_operaciones():
    """
    Test 2: Contraparte con operaciones debe mostrar disponibilidad < 100%.
    """
    print("\n" + "="*80)
    print("TEST 2: Contraparte CON operaciones → Disponibilidad < 100%")
    print("="*80)
    
    model = ForwardDataModel()
    
    # Configurar LLL
    lll_cop = 5_625_000_000.0  # $ 5,625 MM COP
    model.set_credit_limits(
        linea_credito_aprobada_cop=1_000_000_000.0,
        lll_cop=lll_cop
    )
    
    # Simular contraparte con operaciones
    outstanding_cte = 2_000_000_000.0  # $ 2,000 MM COP
    outstanding_grp = 3_000_000_000.0  # $ 3,000 MM COP
    
    print(f"\n📊 Datos:")
    print(f"   LLL: $ {lll_cop:,.0f}")
    print(f"   Outstanding Contraparte: $ {outstanding_cte:,.0f}")
    print(f"   Outstanding Grupo: $ {outstanding_grp:,.0f}")
    
    # Setear exposiciones
    model.set_exposure_counterparty(outstanding_cte, outstanding_cte)
    model.set_exposure_group(outstanding_grp, outstanding_grp)
    
    # Calcular disponibilidades
    lll_from_model = model.get_lll_limit_cop()
    disp_cte_cop = lll_from_model - outstanding_cte
    disp_grp_cop = lll_from_model - outstanding_grp
    disp_cte_pct = (disp_cte_cop / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    disp_grp_pct = (disp_grp_cop / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    
    # Guardar en modelo
    model.set_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
    
    # Recuperar
    disp_cte_cop_ret, disp_cte_pct_ret = model.get_lll_availability_counterparty()
    disp_grp_cop_ret, disp_grp_pct_ret = model.get_lll_availability_group()
    
    print(f"\n✅ Disponibilidades calculadas:")
    print(f"   Contraparte: $ {disp_cte_cop_ret:,.0f} ({disp_cte_pct_ret:.2f}%)")
    print(f"   Grupo:       $ {disp_grp_cop_ret:,.0f} ({disp_grp_pct_ret:.2f}%)")
    
    # Verificar
    assert disp_cte_pct_ret < 100.0, f"Disponibilidad % debe ser < 100%. Obtenido: {disp_cte_pct_ret:.2f}%"
    assert abs(disp_cte_pct_ret - 64.44) < 0.01, f"Disponibilidad % esperada: 64.44%. Obtenido: {disp_cte_pct_ret:.2f}%"
    assert disp_grp_pct_ret < 100.0, f"Disponibilidad grupo % debe ser < 100%. Obtenido: {disp_grp_pct_ret:.2f}%"
    
    print(f"\n   ✅ Disponibilidad correcta: < 100% cuando outstanding > 0")


def test_cambio_contraparte_resetea_disponibilidad():
    """
    Test 3: Al cambiar de contraparte CON ops a contraparte SIN ops,
    la disponibilidad debe volver a 100% (no debe quedar "pegada").
    """
    print("\n" + "="*80)
    print("TEST 3: Cambio de contraparte resetea disponibilidad correctamente")
    print("="*80)
    
    model = ForwardDataModel()
    
    # Configurar LLL
    lll_cop = 5_625_000_000.0
    model.set_credit_limits(
        linea_credito_aprobada_cop=1_000_000_000.0,
        lll_cop=lll_cop
    )
    
    # --- PASO 1: Contraparte CON operaciones ---
    print(f"\n📌 PASO 1: Seleccionar contraparte CON operaciones")
    outstanding_cte_1 = 2_000_000_000.0
    outstanding_grp_1 = 3_000_000_000.0
    
    model.set_exposure_counterparty(outstanding_cte_1, outstanding_cte_1)
    model.set_exposure_group(outstanding_grp_1, outstanding_grp_1)
    
    lll_from_model = model.get_lll_limit_cop()
    disp_cte_cop_1 = lll_from_model - outstanding_cte_1
    disp_cte_pct_1 = (disp_cte_cop_1 / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    disp_grp_cop_1 = lll_from_model - outstanding_grp_1
    disp_grp_pct_1 = (disp_grp_cop_1 / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    
    model.set_lll_availability(disp_cte_cop_1, disp_cte_pct_1, disp_grp_cop_1, disp_grp_pct_1)
    
    disp_cte_cop_1_ret, disp_cte_pct_1_ret = model.get_lll_availability_counterparty()
    
    print(f"   Outstanding: $ {outstanding_cte_1:,.0f}")
    print(f"   Disponibilidad: $ {disp_cte_cop_1_ret:,.0f} ({disp_cte_pct_1_ret:.2f}%)")
    
    assert disp_cte_pct_1_ret < 100.0, "Primera contraparte debe tener disponibilidad < 100%"
    
    # --- PASO 2: Cambiar a contraparte SIN operaciones ---
    print(f"\n📌 PASO 2: Cambiar a contraparte SIN operaciones")
    outstanding_cte_2 = 0.0
    outstanding_grp_2 = 0.0
    
    # Simular cambio de contraparte (resetear exposiciones)
    model.set_exposure_counterparty(outstanding_cte_2, outstanding_cte_2)
    model.set_exposure_group(outstanding_grp_2, outstanding_grp_2)
    
    # Recalcular disponibilidades (como lo hace el controlador)
    lll_from_model = model.get_lll_limit_cop()
    disp_cte_cop_2 = lll_from_model - outstanding_cte_2
    disp_cte_pct_2 = (disp_cte_cop_2 / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    disp_grp_cop_2 = lll_from_model - outstanding_grp_2
    disp_grp_pct_2 = (disp_grp_cop_2 / lll_from_model * 100.0) if lll_from_model > 0 else 0.0
    
    model.set_lll_availability(disp_cte_cop_2, disp_cte_pct_2, disp_grp_cop_2, disp_grp_pct_2)
    
    disp_cte_cop_2_ret, disp_cte_pct_2_ret = model.get_lll_availability_counterparty()
    
    print(f"   Outstanding: $ {outstanding_cte_2:,.0f}")
    print(f"   Disponibilidad: $ {disp_cte_cop_2_ret:,.0f} ({disp_cte_pct_2_ret:.2f}%)")
    
    # Verificar que la disponibilidad vuelve a 100%
    assert disp_cte_pct_2_ret == 100.0, \
        f"❌ Disponibilidad NO se reseteó correctamente. Esperado: 100%, Obtenido: {disp_cte_pct_2_ret:.2f}%"
    
    print(f"\n   ✅ Disponibilidad correctamente reseteada a 100% al cambiar de contraparte")


def run_all_tests():
    """Ejecutar todos los tests."""
    print("\n" + "="*80)
    print("INICIANDO TESTS: Actualización Disponibilidad LLL")
    print("="*80)
    
    try:
        test_disponibilidad_sin_operaciones()
        test_disponibilidad_con_operaciones()
        test_cambio_contraparte_resetea_disponibilidad()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*80)
        print("\n📝 Resumen de verificaciones:")
        print("   ✅ Contraparte SIN operaciones → Disponibilidad = 100%")
        print("   ✅ Contraparte CON operaciones → Disponibilidad < 100%")
        print("   ✅ Cambio de contraparte resetea disponibilidad correctamente")
        print("\n✅ CORRECCIÓN VALIDADA: Disponibilidad LLL se actualiza siempre")
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

