"""
Test para verificar la lógica de grupo y UI de tags en Simulación Forward.

Este test valida:
1. El método get_group_members_by_nit() en SettingsModel
2. La lógica de exposición por grupo solo cuando tiene >1 miembro
3. El método update_group_members() en ForwardView
"""

import sys
from typing import List, Dict
import pandas as pd
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.models.settings_model import SettingsModel
from src.views.forward_view import ForwardView


def test_settings_model_group_members():
    """Test del método get_group_members_by_nit en SettingsModel."""
    print("\n" + "="*70)
    print("TEST 1: SettingsModel.get_group_members_by_nit()")
    print("="*70)
    
    model = SettingsModel()
    
    # Datos de prueba con grupos
    data = {
        "NIT": ["1234567890", "0987654321", "1111111111", "2222222222"],
        "Contraparte": ["Banco Alpha", "Banco Beta", "Banco Gamma", "Banco Delta"],
        "Grupo Conectado de Contrapartes": ["Grupo A", "Grupo A", "Grupo B", ""],
        "EUR (MM)": [100.0, 150.0, 200.0, 50.0],
        "COP (MM)": [500.0, 750.0, 1000.0, 250.0],
    }
    df = pd.DataFrame(data)
    model.set_lineas_credito(df)
    
    # Test 1: Grupo con 2 miembros
    print("\n1. Grupo A (debe tener 2 miembros):")
    members = model.get_group_members_by_nit("1234567890")
    print(f"   Miembros: {len(members)}")
    for m in members:
        print(f"   - {m['nombre']} (NIT: {m['nit']})")
    assert len(members) == 2, f"Se esperaban 2 miembros, se obtuvieron {len(members)}"
    print("   ✓ OK")
    
    # Test 2: Contraparte sin grupo
    print("\n2. Banco Delta (sin grupo):")
    members = model.get_group_members_by_nit("2222222222")
    print(f"   Miembros: {len(members)}")
    assert len(members) == 0, f"Se esperaba lista vacía, se obtuvieron {len(members)} miembros"
    print("   ✓ OK")
    
    # Test 3: Grupo con 1 solo miembro
    print("\n3. Grupo B (solo 1 miembro):")
    members = model.get_group_members_by_nit("1111111111")
    print(f"   Miembros: {len(members)}")
    for m in members:
        print(f"   - {m['nombre']} (NIT: {m['nit']})")
    # Aquí tenemos 1 miembro, pero la UI debería ocultarse si len <= 1
    print("   ✓ OK (UI debería ocultarse si len <= 1)")
    
    print("\n✅ SettingsModel.get_group_members_by_nit() funciona correctamente")


def test_forward_view_group_ui():
    """Test de la UI de tags de grupo en ForwardView."""
    print("\n" + "="*70)
    print("TEST 2: ForwardView.update_group_members() - UI de tags")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    view = ForwardView()
    view.show()
    
    # Test 1: Grupo con 2+ miembros (debe mostrarse)
    print("\n1. Grupo con 2 contrapartes:")
    members = [
        {"nit": "1234567890", "nombre": "Banco Alpha", "grupo": "Grupo A"},
        {"nit": "0987654321", "nombre": "Banco Beta", "grupo": "Grupo A"},
    ]
    view.update_group_members("Grupo A", members)
    
    assert view.lbl_group_title.isVisible(), "El título del grupo debería ser visible"
    assert view.group_wrapper_widget.isVisible(), "El contenedor de tags debería ser visible"
    assert view.group_tags_layout.count() >= 2, "Debería haber al menos 2 tags"
    
    # Verificar contenido del título
    title_text = view.lbl_group_title.text()
    assert "Grupo A" in title_text, f"El título debería contener 'Grupo A', pero tiene: {title_text}"
    print(f"   Título: {title_text}")
    print(f"   Tags visibles: {view.group_tags_layout.count() - 1}")  # -1 por el spacer
    print("   ✓ OK")
    
    # Test 2: Sin grupo (debe ocultarse)
    print("\n2. Sin grupo:")
    view.update_group_members(None, [])
    
    assert not view.lbl_group_title.isVisible(), "El título debería estar oculto"
    assert not view.group_wrapper_widget.isVisible(), "El contenedor debería estar oculto"
    print("   ✓ OK (UI oculta)")
    
    # Test 3: Grupo con 1 solo miembro (debe ocultarse)
    print("\n3. Grupo con 1 solo miembro:")
    members_single = [
        {"nit": "1111111111", "nombre": "Banco Gamma", "grupo": "Grupo B"},
    ]
    view.update_group_members("Grupo B", members_single)
    
    assert not view.lbl_group_title.isVisible(), "El título debería estar oculto (1 miembro)"
    assert not view.group_wrapper_widget.isVisible(), "El contenedor debería estar oculto (1 miembro)"
    print("   ✓ OK (UI oculta para grupo con 1 miembro)")
    
    # Test 4: Grupo con 3+ miembros
    print("\n4. Grupo con 3 contrapartes:")
    members_large = [
        {"nit": "1111", "nombre": "Banco Uno", "grupo": "Grupo Grande"},
        {"nit": "2222", "nombre": "Banco Dos", "grupo": "Grupo Grande"},
        {"nit": "3333", "nombre": "Banco Tres", "grupo": "Grupo Grande"},
    ]
    view.update_group_members("Grupo Grande", members_large)
    
    assert view.lbl_group_title.isVisible(), "El título debería ser visible"
    assert view.group_wrapper_widget.isVisible(), "El contenedor debería ser visible"
    tags_count = view.group_tags_layout.count() - 1  # -1 por el spacer
    assert tags_count == 3, f"Deberían haber 3 tags, pero hay {tags_count}"
    print(f"   Tags visibles: {tags_count}")
    print("   ✓ OK")
    
    print("\n✅ ForwardView.update_group_members() funciona correctamente")
    
    view.close()


def test_group_logic_integration():
    """Test de integración: lógica completa de grupo."""
    print("\n" + "="*70)
    print("TEST 3: Integración - Lógica de grupo completa")
    print("="*70)
    
    model = SettingsModel()
    
    # Datos de prueba
    data = {
        "NIT": ["111", "222", "333", "444"],
        "Contraparte": ["Empresa A", "Empresa B", "Empresa C", "Empresa D"],
        "Grupo Conectado de Contrapartes": ["Grupo X", "Grupo X", "Grupo Y", ""],
        "EUR (MM)": [100.0, 150.0, 200.0, 50.0],
        "COP (MM)": [500.0, 750.0, 1000.0, 250.0],
    }
    df = pd.DataFrame(data)
    model.set_lineas_credito(df)
    
    # Simulación de lógica del controller
    test_cases = [
        ("111", "Empresa A", True, 2),   # Grupo X, 2 miembros -> has_real_group = True
        ("222", "Empresa B", True, 2),   # Grupo X, 2 miembros -> has_real_group = True
        ("333", "Empresa C", False, 1),  # Grupo Y, 1 miembro -> has_real_group = False
        ("444", "Empresa D", False, 0),  # Sin grupo -> has_real_group = False
    ]
    
    for nit, nombre, expected_real_group, expected_count in test_cases:
        print(f"\n→ Procesando: {nombre} (NIT: {nit})")
        
        members_list = model.get_group_members_by_nit(nit)
        has_real_group = members_list is not None and len(members_list) > 1
        
        print(f"   Miembros encontrados: {len(members_list)}")
        print(f"   has_real_group: {has_real_group}")
        
        assert has_real_group == expected_real_group, \
            f"Se esperaba has_real_group={expected_real_group}, se obtuvo {has_real_group}"
        assert len(members_list) == expected_count, \
            f"Se esperaban {expected_count} miembros, se obtuvieron {len(members_list)}"
        
        # Simular lógica de exposición
        if has_real_group:
            print(f"   → Calcular exposición de grupo para {len(members_list)} contrapartes")
            group_nits = [m["nit"] for m in members_list]
            print(f"      NITs del grupo: {group_nits}")
        else:
            print(f"   → Sin grupo real, exposición grupo = 0")
        
        print("   ✓ OK")
    
    print("\n✅ Integración de lógica de grupo funciona correctamente")


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("TESTS DE LÓGICA DE GRUPO Y UI DE TAGS")
    print("="*70)
    
    try:
        # Test 1: Modelo
        test_settings_model_group_members()
        
        # Test 2: Vista
        test_forward_view_group_ui()
        
        # Test 3: Integración
        test_group_logic_integration()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
        print("\nResumen:")
        print("1. SettingsModel.get_group_members_by_nit() ✓")
        print("2. ForwardView.update_group_members() ✓")
        print("3. Lógica de has_real_group ✓")
        print("4. UI de tags (mostrar/ocultar) ✓")
        
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

