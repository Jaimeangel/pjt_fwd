"""
Test para verificar los cambios en la UI de grupo:
1. Tags responsivos con QGridLayout (varias filas)
2. Ocultación completa de la columna de grupo en Exposición cuando no aplique
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.views.forward_view import ForwardView


def test_tags_responsivos():
    """Test 1: Tags responsivos con QGridLayout (varias filas)."""
    print("\n" + "="*70)
    print("TEST 1: Tags responsivos con QGridLayout")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Test con 2 contrapartes (1 fila, 2 columnas)
    print("\n1. Grupo con 2 contrapartes (1 fila):")
    members_2 = [
        {"nit": "111", "nombre": "Banco Alpha", "grupo": "Grupo A"},
        {"nit": "222", "nombre": "Banco Beta", "grupo": "Grupo A"},
    ]
    view.update_group_members("Grupo A", members_2)
    
    assert view.lbl_group_title.isVisible(), "Título debería ser visible"
    assert view.group_wrapper_widget.isVisible(), "Contenedor debería ser visible"
    assert view.group_exposure_container.isVisible(), "Columna de grupo en Exposición debería ser visible"
    
    # Verificar que hay 2 tags en el grid
    tags_count = view.group_tags_layout.count()
    assert tags_count == 2, f"Debería haber 2 tags, hay {tags_count}"
    print(f"   ✓ 2 tags en el grid (1 fila)")
    
    # Test con 5 contrapartes (2 filas: 3 + 2)
    print("\n2. Grupo con 5 contrapartes (2 filas: 3 + 2):")
    members_5 = [
        {"nit": "111", "nombre": "Banco Uno", "grupo": "Grupo Grande"},
        {"nit": "222", "nombre": "Banco Dos", "grupo": "Grupo Grande"},
        {"nit": "333", "nombre": "Banco Tres", "grupo": "Grupo Grande"},
        {"nit": "444", "nombre": "Banco Cuatro", "grupo": "Grupo Grande"},
        {"nit": "555", "nombre": "Banco Cinco", "grupo": "Grupo Grande"},
    ]
    view.update_group_members("Grupo Grande", members_5)
    
    tags_count = view.group_tags_layout.count()
    assert tags_count == 5, f"Debería haber 5 tags, hay {tags_count}"
    
    # Verificar distribución en filas y columnas
    # Con max_per_row=3: tag[0] -> (0,0), tag[1] -> (0,1), tag[2] -> (0,2), tag[3] -> (1,0), tag[4] -> (1,1)
    for index in range(5):
        expected_row = index // 3
        expected_col = index % 3
        item = view.group_tags_layout.itemAtPosition(expected_row, expected_col)
        assert item is not None, f"Debería haber un widget en posición ({expected_row}, {expected_col})"
        widget = item.widget()
        assert widget is not None, f"Widget en ({expected_row}, {expected_col}) debería existir"
    
    print(f"   ✓ 5 tags distribuidos en 2 filas (3 + 2)")
    
    # Test con 7 contrapartes (3 filas: 3 + 3 + 1)
    print("\n3. Grupo con 7 contrapartes (3 filas: 3 + 3 + 1):")
    members_7 = [
        {"nit": str(i), "nombre": f"Banco {i}", "grupo": "Grupo Muy Grande"}
        for i in range(1, 8)
    ]
    view.update_group_members("Grupo Muy Grande", members_7)
    
    tags_count = view.group_tags_layout.count()
    assert tags_count == 7, f"Debería haber 7 tags, hay {tags_count}"
    
    # Verificar que hay tags en 3 filas
    has_row_0 = view.group_tags_layout.itemAtPosition(0, 0) is not None
    has_row_1 = view.group_tags_layout.itemAtPosition(1, 0) is not None
    has_row_2 = view.group_tags_layout.itemAtPosition(2, 0) is not None
    
    assert has_row_0 and has_row_1 and has_row_2, "Deberían haber 3 filas con tags"
    print(f"   ✓ 7 tags distribuidos en 3 filas")
    
    print("\n✅ Tags responsivos funcionan correctamente")
    view.close()


def test_ocultar_columna_grupo():
    """Test 2: Ocultación completa de la columna de grupo en Exposición."""
    print("\n" + "="*70)
    print("TEST 2: Ocultación de columna de grupo en Exposición")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Test 1: Grupo real (2+ miembros) -> Mostrar todo
    print("\n1. Grupo con 2+ miembros (debe mostrar columna de grupo):")
    members = [
        {"nit": "111", "nombre": "Banco A", "grupo": "Grupo X"},
        {"nit": "222", "nombre": "Banco B", "grupo": "Grupo X"},
    ]
    view.update_group_members("Grupo X", members)
    
    assert view.lbl_group_title.isVisible(), "Título de grupo debería ser visible"
    assert view.group_wrapper_widget.isVisible(), "Tags de grupo deberían ser visibles"
    assert view.group_exposure_container.isVisible(), "Columna de grupo en Exposición debería ser visible"
    print("   ✓ Tags visibles")
    print("   ✓ Columna de grupo en Exposición visible")
    
    # Test 2: Sin grupo -> Ocultar todo
    print("\n2. Sin grupo (debe ocultar todo):")
    view.update_group_members(None, [])
    
    assert not view.lbl_group_title.isVisible(), "Título de grupo debería estar oculto"
    assert not view.group_wrapper_widget.isVisible(), "Tags deberían estar ocultos"
    assert not view.group_exposure_container.isVisible(), "Columna de grupo en Exposición debería estar oculta"
    print("   ✓ Tags ocultos")
    print("   ✓ Columna de grupo en Exposición oculta")
    
    # Test 3: Grupo con 1 solo miembro -> Ocultar todo
    print("\n3. Grupo con 1 solo miembro (debe ocultar todo):")
    members_single = [
        {"nit": "333", "nombre": "Banco C", "grupo": "Grupo Solo"},
    ]
    view.update_group_members("Grupo Solo", members_single)
    
    assert not view.lbl_group_title.isVisible(), "Título de grupo debería estar oculto (1 miembro)"
    assert not view.group_wrapper_widget.isVisible(), "Tags deberían estar ocultos (1 miembro)"
    assert not view.group_exposure_container.isVisible(), "Columna de grupo debería estar oculta (1 miembro)"
    print("   ✓ Tags ocultos (grupo unitario)")
    print("   ✓ Columna de grupo en Exposición oculta (grupo unitario)")
    
    # Test 4: Verificar que los valores se limpian al ocultar
    print("\n4. Verificar limpieza de valores al ocultar:")
    # Primero mostrar con valores
    view.update_group_members("Grupo X", members)
    view.lbl_out_grp_value.setText("$100,000,000")
    view.lbl_out_grp_sim_value.setText("$120,000,000")
    view.lbl_disp_lll_grp_value.setText("$380,000,000  76%")
    
    # Ahora ocultar
    view.set_group_exposure_visible(False)
    
    # Verificar que se limpiaron
    assert view.lbl_out_grp_value.text() == "—", "Outstanding grupo debería limpiarse"
    assert view.lbl_out_grp_sim_value.text() == "—", "Outstanding grupo + sim debería limpiarse"
    assert view.lbl_disp_lll_grp_value.text() == "—", "Disponibilidad grupo debería limpiarse"
    print("   ✓ Valores de grupo limpiados al ocultar")
    
    print("\n✅ Ocultación de columna de grupo funciona correctamente")
    view.close()


def test_metodo_set_group_exposure_visible():
    """Test 3: Método set_group_exposure_visible()."""
    print("\n" + "="*70)
    print("TEST 3: Método set_group_exposure_visible()")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    view = ForwardView()
    view.show()
    
    # Test mostrar
    print("\n1. Llamar set_group_exposure_visible(True):")
    view.set_group_exposure_visible(True)
    assert view.group_exposure_container.isVisible(), "Contenedor debería ser visible"
    print("   ✓ Contenedor visible")
    
    # Test ocultar
    print("\n2. Llamar set_group_exposure_visible(False):")
    view.set_group_exposure_visible(False)
    assert not view.group_exposure_container.isVisible(), "Contenedor debería estar oculto"
    print("   ✓ Contenedor oculto")
    
    # Test toggle múltiple
    print("\n3. Toggle múltiple:")
    view.set_group_exposure_visible(True)
    assert view.group_exposure_container.isVisible()
    view.set_group_exposure_visible(False)
    assert not view.group_exposure_container.isVisible()
    view.set_group_exposure_visible(True)
    assert view.group_exposure_container.isVisible()
    print("   ✓ Toggle funciona correctamente")
    
    print("\n✅ Método set_group_exposure_visible() funciona correctamente")
    view.close()


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("TESTS DE UI DE GRUPO: TAGS RESPONSIVOS Y OCULTACIÓN")
    print("="*70)
    
    try:
        # Test 1: Tags responsivos
        test_tags_responsivos()
        
        # Test 2: Ocultación de columna de grupo
        test_ocultar_columna_grupo()
        
        # Test 3: Método específico
        test_metodo_set_group_exposure_visible()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
        print("\nResumen:")
        print("1. Tags responsivos con QGridLayout (varias filas) ✓")
        print("2. Ocultación completa de columna de grupo ✓")
        print("3. Método set_group_exposure_visible() ✓")
        print("4. Limpieza de valores al ocultar ✓")
        
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

