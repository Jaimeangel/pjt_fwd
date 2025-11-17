"""
Test para verificar la eliminación del zoom y ocultación de leyenda en la gráfica de consumo.

Este test valida que:
1. El checkbox "Zoom consumo" ya no existe en la UI
2. La gráfica funciona correctamente sin el parámetro zoom
3. La leyenda está oculta
4. Las barras se muestran correctamente
"""

import sys
from PySide6.QtWidgets import QApplication

from src.views.forward_view import ForwardView


def test_checkbox_zoom_eliminado():
    """Test 1: Verificar que el checkbox de zoom fue eliminado."""
    print("\n" + "="*70)
    print("TEST 1: Checkbox 'Zoom consumo' eliminado")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Verificar que el checkbox NO existe
    assert not hasattr(view, 'cbZoomConsumo') or view.cbZoomConsumo is None, \
        "El checkbox cbZoomConsumo NO debería existir o debería ser None"
    
    print("   ✓ Checkbox 'cbZoomConsumo' no existe o es None")
    
    # Verificar que la gráfica existe
    assert hasattr(view, 'fig_consumo2') and view.fig_consumo2 is not None, \
        "La gráfica debería existir"
    assert hasattr(view, 'ax_consumo2') and view.ax_consumo2 is not None, \
        "El eje de la gráfica debería existir"
    assert hasattr(view, 'canvas_consumo2') and view.canvas_consumo2 is not None, \
        "El canvas debería existir"
    
    print("   ✓ Gráfica existe correctamente")
    
    print("\n✅ Checkbox de zoom eliminado correctamente")
    view.close()


def test_grafica_sin_parametro_zoom():
    """Test 2: Verificar que la gráfica funciona sin parámetro zoom."""
    print("\n" + "="*70)
    print("TEST 2: Gráfica funciona sin parámetro zoom")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Test 1: Llamar con los parámetros normales (sin zoom)
    print("\n1. Llamar update_consumo_dual_chart sin parámetro zoom:")
    try:
        view.update_consumo_dual_chart(
            lca_total=1_000_000_000.0,
            outstanding=500_000_000.0,
            outstanding_with_sim=600_000_000.0
        )
        print("   ✓ Método funciona sin parámetro zoom")
    except TypeError as e:
        if "zoom" in str(e):
            assert False, f"No debería requerir parámetro zoom: {e}"
        raise
    
    # Test 2: Verificar que intenta usar zoom falla (no debería existir el parámetro)
    print("\n2. Verificar que el parámetro zoom ya no existe:")
    try:
        view.update_consumo_dual_chart(
            lca_total=1_000_000_000.0,
            outstanding=500_000_000.0,
            outstanding_with_sim=600_000_000.0,
            zoom=True  # Este parámetro NO debería existir
        )
        # Si llegamos aquí, el parámetro aún existe (error)
        assert False, "El parámetro 'zoom' NO debería aceptarse"
    except TypeError as e:
        if "zoom" in str(e):
            print("   ✓ Parámetro zoom correctamente eliminado")
        else:
            raise
    
    print("\n✅ Gráfica funciona correctamente sin parámetro zoom")
    view.close()


def test_leyenda_oculta():
    """Test 3: Verificar que la leyenda está oculta."""
    print("\n" + "="*70)
    print("TEST 3: Leyenda de la gráfica oculta")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Actualizar la gráfica
    view.update_consumo_dual_chart(
        lca_total=1_000_000_000.0,
        outstanding=500_000_000.0,
        outstanding_with_sim=600_000_000.0
    )
    
    # Verificar que la leyenda existe pero está oculta
    ax = view.ax_consumo2
    legend = ax.get_legend()
    
    assert legend is not None, "La leyenda debería existir"
    assert not legend.get_visible(), "La leyenda debería estar oculta (visible=False)"
    
    print("   ✓ Leyenda existe")
    print("   ✓ Leyenda está oculta (visible=False)")
    
    print("\n✅ Leyenda correctamente oculta")
    view.close()


def test_barras_se_muestran_correctamente():
    """Test 4: Verificar que las barras se muestran correctamente."""
    print("\n" + "="*70)
    print("TEST 4: Barras se muestran correctamente")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Test con valores típicos
    print("\n1. Gráfica con LCA y consumo:")
    view.update_consumo_dual_chart(
        lca_total=1_000_000_000.0,
        outstanding=500_000_000.0,
        outstanding_with_sim=600_000_000.0
    )
    
    ax = view.ax_consumo2
    
    # Verificar que hay barras en la gráfica
    patches = ax.patches
    assert len(patches) > 0, "Debería haber barras en la gráfica"
    
    # Debería haber al menos 3 barras: LCA + Outstanding + Simulación
    # (puede haber más dependiendo de la implementación)
    assert len(patches) >= 3, f"Debería haber al menos 3 barras, hay {len(patches)}"
    
    print(f"   ✓ {len(patches)} barras encontradas")
    print("   ✓ Gráfica renderiza correctamente")
    
    # Test con solo LCA (sin consumo)
    print("\n2. Gráfica con solo LCA:")
    view.update_consumo_dual_chart(
        lca_total=1_000_000_000.0,
        outstanding=0.0,
        outstanding_with_sim=0.0
    )
    
    patches = ax.patches
    assert len(patches) >= 1, "Debería haber al menos la barra de LCA"
    print(f"   ✓ {len(patches)} barra(s) encontrada(s)")
    
    print("\n✅ Barras se muestran correctamente en todos los casos")
    view.close()


def test_ejes_funcionan_correctamente():
    """Test 5: Verificar que los ejes funcionan correctamente."""
    print("\n" + "="*70)
    print("TEST 5: Ejes funcionan correctamente")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Actualizar con valores conocidos
    lca = 1_000_000_000.0
    outstanding = 500_000_000.0
    outstanding_sim = 600_000_000.0
    
    view.update_consumo_dual_chart(
        lca_total=lca,
        outstanding=outstanding,
        outstanding_with_sim=outstanding_sim
    )
    
    ax = view.ax_consumo2
    
    # Verificar límites del eje Y
    ymin, ymax = ax.get_ylim()
    
    assert ymin == 0, f"El límite inferior del eje Y debería ser 0, es {ymin}"
    assert ymax > lca, f"El límite superior debería ser mayor que LCA ({lca}), es {ymax}"
    
    # Verificar que el margen superior es aproximadamente 10%
    expected_ymax = lca * 1.10
    tolerance = lca * 0.05  # 5% de tolerancia
    assert abs(ymax - expected_ymax) < tolerance, \
        f"ymax debería ser ~{expected_ymax:,.0f} (LCA*1.10), es {ymax:,.0f}"
    
    print(f"   ✓ Eje Y: min={ymin}, max={ymax:,.0f}")
    print(f"   ✓ Margen superior correcto (~10%)")
    
    # Verificar formato del eje Y (sin notación científica)
    formatter = ax.yaxis.get_major_formatter()
    test_value = 1_000_000
    formatted = formatter(test_value)
    
    # No debería contener notación científica (e, E, etc.)
    assert 'e' not in formatted.lower(), \
        f"No debería usar notación científica: {formatted}"
    
    print(f"   ✓ Formato del eje Y correcto (sin notación científica)")
    
    print("\n✅ Ejes funcionan correctamente")
    view.close()


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("TESTS: ELIMINACIÓN DE ZOOM Y OCULTACIÓN DE LEYENDA")
    print("="*70)
    
    try:
        # Test 1: Checkbox eliminado
        test_checkbox_zoom_eliminado()
        
        # Test 2: Gráfica sin parámetro zoom
        test_grafica_sin_parametro_zoom()
        
        # Test 3: Leyenda oculta
        test_leyenda_oculta()
        
        # Test 4: Barras correctas
        test_barras_se_muestran_correctamente()
        
        # Test 5: Ejes correctos
        test_ejes_funcionan_correctamente()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
        print("\nResumen:")
        print("1. Checkbox 'Zoom consumo' eliminado ✓")
        print("2. Gráfica funciona sin parámetro zoom ✓")
        print("3. Leyenda oculta correctamente ✓")
        print("4. Barras se muestran correctamente ✓")
        print("5. Ejes funcionan correctamente ✓")
        
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

