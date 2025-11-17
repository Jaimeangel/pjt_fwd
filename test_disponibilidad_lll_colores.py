"""
Test para verificar el coloreo de porcentajes en Disponibilidad LLL.

Este test valida que:
1. El porcentaje se muestre en verde cuando es >= 0
2. El porcentaje se muestre en rojo cuando es < 0
3. Los valores numéricos no cambien (solo el color)
4. El formato HTML se aplique correctamente
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.views.forward_view import ForwardView


def test_colores_porcentaje_positivo():
    """Test 1: Porcentajes positivos deben mostrarse en verde."""
    print("\n" + "="*70)
    print("TEST 1: Porcentajes positivos (>= 0) en verde")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Caso 1: Disponibilidad positiva (contraparte)
    print("\n1. Disponibilidad contraparte positiva:")
    view.update_lll_availability(
        disp_cte_cop=9_941_985_173.0,
        disp_cte_pct=34.5,
        disp_grp_cop=8_000_000_000.0,
        disp_grp_pct=28.0
    )
    
    texto_cte = view.lbl_disp_lll_cte_value.text()
    texto_grp = view.lbl_disp_lll_grp_value.text()
    
    # Verificar que contiene "green" y el porcentaje
    assert "green" in texto_cte, f"Debería contener 'green', texto: {texto_cte}"
    assert "34%" in texto_cte or "35%" in texto_cte, f"Debería contener el porcentaje, texto: {texto_cte}"
    print(f"   Texto contraparte: {texto_cte}")
    print("   ✓ Verde para porcentaje positivo")
    
    # Verificar formato HTML
    assert view.lbl_disp_lll_cte_value.textFormat() == Qt.RichText, "Debería usar RichText"
    print("   ✓ Formato HTML habilitado")
    
    # Caso 2: Disponibilidad cero (debe ser verde, pues >= 0)
    print("\n2. Disponibilidad exactamente cero:")
    view.update_lll_availability(
        disp_cte_cop=0.0,
        disp_cte_pct=0.0,
        disp_grp_cop=0.0,
        disp_grp_pct=0.0
    )
    
    texto_cte = view.lbl_disp_lll_cte_value.text()
    assert "green" in texto_cte, f"0% debería ser verde (>= 0), texto: {texto_cte}"
    print(f"   Texto: {texto_cte}")
    print("   ✓ 0% se muestra en verde")
    
    print("\n✅ Porcentajes positivos se muestran correctamente en verde")
    view.close()


def test_colores_porcentaje_negativo():
    """Test 2: Porcentajes negativos deben mostrarse en rojo."""
    print("\n" + "="*70)
    print("TEST 2: Porcentajes negativos (< 0) en rojo")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Caso 1: Disponibilidad negativa (sobreconsumo)
    print("\n1. Disponibilidad contraparte negativa (sobreconsumo):")
    view.update_lll_availability(
        disp_cte_cop=-1_200_000_000.0,
        disp_cte_pct=-4.2,
        disp_grp_cop=-500_000_000.0,
        disp_grp_pct=-1.8
    )
    
    texto_cte = view.lbl_disp_lll_cte_value.text()
    texto_grp = view.lbl_disp_lll_grp_value.text()
    
    # Verificar que contiene "red" y el porcentaje negativo
    assert "red" in texto_cte, f"Debería contener 'red', texto: {texto_cte}"
    assert "-4" in texto_cte, f"Debería contener el porcentaje negativo, texto: {texto_cte}"
    print(f"   Texto contraparte: {texto_cte}")
    print("   ✓ Rojo para porcentaje negativo")
    
    assert "red" in texto_grp, f"Grupo debería contener 'red', texto: {texto_grp}"
    print(f"   Texto grupo: {texto_grp}")
    print("   ✓ Rojo para porcentaje negativo (grupo)")
    
    # Caso 2: Disponibilidad ligeramente negativa
    print("\n2. Disponibilidad ligeramente negativa:")
    view.update_lll_availability(
        disp_cte_cop=-100_000.0,
        disp_cte_pct=-0.01,
        disp_grp_cop=0.0,
        disp_grp_pct=0.0
    )
    
    texto_cte = view.lbl_disp_lll_cte_value.text()
    assert "red" in texto_cte, f"-0.01% debería ser rojo (< 0), texto: {texto_cte}"
    print(f"   Texto: {texto_cte}")
    print("   ✓ -0.01% se muestra en rojo")
    
    print("\n✅ Porcentajes negativos se muestran correctamente en rojo")
    view.close()


def test_valores_no_cambian():
    """Test 3: Verificar que los valores numéricos no cambian, solo el color."""
    print("\n" + "="*70)
    print("TEST 3: Valores numéricos no cambian")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Test con valores específicos
    print("\n1. Verificar que los valores se mantienen:")
    cop_value = 9_941_985_173.0
    pct_value = 34.5
    
    view.update_lll_availability(
        disp_cte_cop=cop_value,
        disp_cte_pct=pct_value,
        disp_grp_cop=0.0,
        disp_grp_pct=0.0
    )
    
    texto = view.lbl_disp_lll_cte_value.text()
    
    # El texto debería contener el valor formateado de COP
    assert "9,941,985,173" in texto or "9.941" in texto, f"Debería contener el valor COP, texto: {texto}"
    
    # El texto debería contener el porcentaje
    assert "34.5" in texto or "34" in texto or "35" in texto, f"Debería contener el porcentaje, texto: {texto}"
    
    print(f"   Texto: {texto}")
    print("   ✓ Valores numéricos presentes en el texto")
    
    # Test con valor negativo
    print("\n2. Verificar que los valores negativos se mantienen:")
    view.update_lll_availability(
        disp_cte_cop=-1_200_000_000.0,
        disp_cte_pct=-4.2,
        disp_grp_cop=0.0,
        disp_grp_pct=0.0
    )
    
    texto = view.lbl_disp_lll_cte_value.text()
    
    # El signo negativo debe estar presente
    assert "-1,200,000,000" in texto or "-1.200" in texto or "- $" in texto, \
        f"Debería contener el valor COP negativo, texto: {texto}"
    assert "-4" in texto, f"Debería contener el porcentaje negativo, texto: {texto}"
    
    print(f"   Texto: {texto}")
    print("   ✓ Valores negativos se mantienen correctamente")
    
    print("\n✅ Los valores numéricos no cambian, solo el color del porcentaje")
    view.close()


def test_casos_especiales():
    """Test 4: Casos especiales (None, valores extremos)."""
    print("\n" + "="*70)
    print("TEST 4: Casos especiales")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Caso 1: Valores None
    print("\n1. Valores None:")
    view.update_lll_availability(
        disp_cte_cop=None,
        disp_cte_pct=None,
        disp_grp_cop=None,
        disp_grp_pct=None
    )
    
    texto_cte = view.lbl_disp_lll_cte_value.text()
    # Debería mostrar "—" o similar para valores None
    assert "—" in texto_cte or "N/A" in texto_cte or "span" in texto_cte, \
        f"Debería manejar None correctamente, texto: {texto_cte}"
    print(f"   Texto: {texto_cte}")
    print("   ✓ Maneja None sin errores")
    
    # Caso 2: Mix de positivo y negativo
    print("\n2. Mix: contraparte positiva, grupo negativo:")
    view.update_lll_availability(
        disp_cte_cop=5_000_000_000.0,
        disp_cte_pct=50.0,
        disp_grp_cop=-2_000_000_000.0,
        disp_grp_pct=-20.0
    )
    
    texto_cte = view.lbl_disp_lll_cte_value.text()
    texto_grp = view.lbl_disp_lll_grp_value.text()
    
    assert "green" in texto_cte, f"Contraparte debería ser verde, texto: {texto_cte}"
    assert "red" in texto_grp, f"Grupo debería ser rojo, texto: {texto_grp}"
    print(f"   Contraparte (verde): {texto_cte}")
    print(f"   Grupo (rojo): {texto_grp}")
    print("   ✓ Colores independientes para cada columna")
    
    print("\n✅ Casos especiales manejados correctamente")
    view.close()


def test_formato_html():
    """Test 5: Verificar que el formato HTML se aplica correctamente."""
    print("\n" + "="*70)
    print("TEST 5: Formato HTML")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Actualizar con valores
    view.update_lll_availability(
        disp_cte_cop=1_000_000_000.0,
        disp_cte_pct=10.0,
        disp_grp_cop=500_000_000.0,
        disp_grp_pct=5.0
    )
    
    # Verificar que los labels usan RichText
    assert view.lbl_disp_lll_cte_value.textFormat() == Qt.RichText, \
        "Label contraparte debe usar RichText"
    assert view.lbl_disp_lll_grp_value.textFormat() == Qt.RichText, \
        "Label grupo debe usar RichText"
    
    print("   ✓ Label contraparte usa Qt.RichText")
    print("   ✓ Label grupo usa Qt.RichText")
    
    # Verificar estructura HTML básica
    texto_cte = view.lbl_disp_lll_cte_value.text()
    assert "<span" in texto_cte, "Debería contener etiqueta <span>"
    assert "style=" in texto_cte, "Debería contener atributo style"
    assert "color:" in texto_cte, "Debería especificar color"
    assert "</span>" in texto_cte, "Debería cerrar etiqueta </span>"
    
    print(f"   Estructura HTML: {texto_cte[:100]}...")
    print("   ✓ Estructura HTML correcta")
    
    print("\n✅ Formato HTML aplicado correctamente")
    view.close()


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("TESTS DE COLOREO DE PORCENTAJES EN DISPONIBILIDAD LLL")
    print("="*70)
    
    try:
        # Test 1: Porcentajes positivos en verde
        test_colores_porcentaje_positivo()
        
        # Test 2: Porcentajes negativos en rojo
        test_colores_porcentaje_negativo()
        
        # Test 3: Valores no cambian
        test_valores_no_cambian()
        
        # Test 4: Casos especiales
        test_casos_especiales()
        
        # Test 5: Formato HTML
        test_formato_html()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
        print("\nResumen:")
        print("1. Porcentajes >= 0 se muestran en verde ✓")
        print("2. Porcentajes < 0 se muestran en rojo ✓")
        print("3. Valores numéricos no cambian ✓")
        print("4. Casos especiales manejados ✓")
        print("5. Formato HTML correcto ✓")
        
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

