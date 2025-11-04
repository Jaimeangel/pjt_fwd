# Fix: Agregar Simulación NO Modifica Exposición

## Resumen

Se corrigió el comportamiento del botón "Agregar simulación" para que **únicamente agregue una fila vacía** a la tabla de simulaciones, **sin modificar** los valores de exposición (Outstanding y Outstanding + simulación).

## Fecha de Implementación

Noviembre 3, 2025

## Problema Identificado

### Antes del Fix

❌ **Problema**: Al presionar "Agregar simulación", se establecían valores hardcodeados en los labels de exposición:
- Outstanding: $ 1,000,000.00
- Outstanding + simulación: $ 1,500,000.00
- Disponibilidad: $ 4,000,000.00

Estos valores eran **incorrectos** y **no correspondían** al cliente ni a las operaciones vigentes.

### Causa Raíz

El problema se originaba en `src/views/main_window.py`:

```python
# ❌ ANTES (INCORRECTO)
def _on_simulations_changed(self):
    """Handler para señal forward_simulations_changed."""
    print("[MainWindow] _on_simulations_changed")
    
    # Actualizar tabla de simulaciones (modelo dummy)
    self._forward_view.set_simulations_table(model=None)
    
    # ❌ Actualizar exposición con datos dummy hardcodeados
    self._forward_view.show_exposure(
        outstanding=1000000.0,        # ← Valor hardcodeado
        total_con_simulacion=1500000.0,  # ← Valor hardcodeado
        disponibilidad=4000000.0       # ← Valor hardcodeado
    )
```

Este handler se ejecutaba cada vez que se agregaba una simulación porque:
1. `add_simulation()` emitía la señal `forward_simulations_changed`
2. Esta señal estaba conectada a `_on_simulations_changed()`
3. El handler llamaba a `show_exposure()` con valores hardcodeados

## Solución Implementada

### 1. Corregir Handler en `main_window.py`

**Archivo**: `src/views/main_window.py`

```python
# ✅ DESPUÉS (CORRECTO)
def _on_simulations_changed(self):
    """Handler para señal forward_simulations_changed."""
    print("[MainWindow] _on_simulations_changed")
    
    # 🔒 NO actualizar exposición aquí.
    # Agregar/eliminar simulaciones no debe modificar los labels de exposición.
    # Solo el botón "Simular" actualiza Outstanding + simulación.
```

**Cambios:**
- ✅ Eliminada la llamada a `show_exposure()` con valores hardcodeados
- ✅ Agregado comentario explicativo
- ✅ El handler ahora es un "no-op" (no hace nada)

### 2. Actualizar `add_simulation()` en Controller

**Archivo**: `src/controllers/forward_controller.py`

```python
# ✅ CORRECTO
def add_simulation(self) -> None:
    """
    Agrega una nueva fila de simulación.
    
    IMPORTANTE: Este método NO debe modificar los valores de exposición
    (Outstanding, Outstanding+Sim). Solo agrega una fila vacía a la tabla.
    """
    from datetime import date
    
    print("[ForwardController] add_simulation")
    
    # Validar que hay un cliente seleccionado
    nit = self._data_model.get_current_client_nit() if self._data_model else None
    nombre = self._data_model.get_current_client_name() if self._data_model else None
    
    if not nit:
        print("   ⚠️  No hay cliente seleccionado")
        if self._view:
            self._view.notify("Seleccione primero una contraparte.", "warning")
        return
    
    print(f"   → Cliente seleccionado: {nombre}")
    
    # Crear una nueva fila vacía (sin modificar exposición)
    if self._simulations_table_model:
        self._simulations_table_model.add_row({
            "cliente": nombre,
            "nit": nit,
            "punta_cli": "Compra",
            "punta_emp": "Venta",
            "nominal_usd": 0.0,
            "fec_sim": date.today().strftime("%Y-%m-%d"),
            "fec_venc": None,
            "plazo": None,
            "spot": 0.0,
            "puntos": 0.0,
            "tasa_fwd": 0.0,
            "tasa_ibr": None,
            "derecho": None,
            "obligacion": None,
            "fair_value": None
        })
        print("   → Fila agregada a la tabla de simulaciones")
    
    # 🔒 Importante: NO tocar los labels de exposición aquí.
    # No llamar show_exposure ni modificar lblOutstanding ni lblOutstandingSim.
    # Solo el botón "Simular" actualiza Outstanding + simulación.
```

**Cambios:**
- ✅ Documentación clara del propósito
- ✅ Pasa diccionario completo a `add_row()` con estructura explícita
- ✅ Comentario de seguridad al final
- ✅ NO emite señal `forward_simulations_changed` (eliminada)
- ✅ NO llama a `show_exposure()`

### 3. Verificación de `SimulationsTableModel.add_row()`

**Archivo**: `src/models/qt/simulations_table_model.py`

El método ya estaba correcto:

```python
# ✅ CORRECTO (no requirió cambios)
def add_row(self, row_data: Optional[Dict[str, Any]] = None, cliente_nombre: str = "") -> None:
    """
    Agrega una nueva fila a la tabla.
    
    Args:
        row_data: Datos de la fila (o None para fila vacía)
        cliente_nombre: Nombre del cliente seleccionado
    """
    from datetime import date
    
    row_count = len(self._rows)
    self.beginInsertRows(QModelIndex(), row_count, row_count)
    
    if row_data:
        self._rows.append(row_data)
    else:
        # Fila nueva con datos por defecto
        fecha_hoy = date.today().strftime("%Y-%m-%d")
        self._rows.append({
            "cliente": cliente_nombre,
            "punta_cli": "Compra",
            "punta_emp": "Venta",
            "nominal_usd": 0.0,
            "fec_sim": fecha_hoy,
            "fec_venc": None,
            "plazo": None,
            "spot": 0.0,
            "puntos": 0.0,
            "tasa_fwd": 0.0,
            "tasa_ibr": None,
            "derecho": None,
            "obligacion": None,
            "fair_value": None
        })
    
    self.endInsertRows()
```

**Verificación:**
- ✅ Solo emite `beginInsertRows()` y `endInsertRows()`
- ✅ NO emite `dataChanged`
- ✅ NO llama a funciones del controller
- ✅ NO dispara cálculos de exposición

## Flujo Corregido

### Antes del Fix (❌ Incorrecto)

```
Usuario hace clic en "Agregar simulación"
    ↓
ForwardView.on_add_simulation_row()
    ↓
ForwardView.add_simulation_requested.emit()
    ↓
ForwardController.add_simulation()
    ↓
SimulationsTableModel.add_row()  ← Agrega fila
    ↓
ForwardController._signals.forward_simulations_changed.emit()  ← Emite señal
    ↓
MainWindow._on_simulations_changed()
    ↓
ForwardView.show_exposure(1000000.0, 1500000.0, 4000000.0)  ❌ Valores hardcodeados
```

### Después del Fix (✅ Correcto)

```
Usuario hace clic en "Agregar simulación"
    ↓
ForwardView.on_add_simulation_row()
    ↓
ForwardView.add_simulation_requested.emit()
    ↓
ForwardController.add_simulation()
    ↓
SimulationsTableModel.add_row()  ← Agrega fila
    ↓
[FIN]  ← NO se modifican labels de exposición
```

## Tests Ejecutados

| # | Test | Descripción | Resultado |
|---|------|-------------|-----------|
| 1 | Configurar cliente | Establecer Outstanding inicial | ✅ PASS |
| 2 | Agregar 1ª simulación | Labels NO cambian | ✅ PASS |
| 3 | Agregar 2ª simulación | Labels NO cambian | ✅ PASS |
| 4 | Agregar 3ª simulación | Labels NO cambian | ✅ PASS |

### Ejemplo de Ejecución del Test

```
Test 2: Agregar primera simulación
------------------------------------------------------------
  ANTES:
    Outstanding: $ 275,000.00
    Outstanding+Sim: —
    Filas en tabla: 0

[Usuario hace clic en "Agregar simulación"]

  DESPUÉS:
    Outstanding: $ 275,000.00  ← NO cambió
    Outstanding+Sim: —         ← NO cambió
    Filas en tabla: 1          ← Se agregó la fila

✓ Se agregó 1 fila a la tabla
✓ Outstanding NO cambió
✓ Outstanding+Sim NO cambió
✓ Outstanding+Sim sigue en '—'
```

## Criterios de Aceptación Cumplidos

### ✅ Al pulsar "Agregar simulación":

1. **Se agrega una nueva fila vacía en la tabla**
   - ✅ Verificado: rowCount aumenta en 1
   - ✅ Fila contiene valores por defecto (0.0, None, etc.)

2. **Outstanding NO cambia**
   - ✅ Verificado: Valor permanece $ 275,000.00
   - ✅ Label `lblOutstanding` no se actualiza

3. **Outstanding + simulación NO cambia**
   - ✅ Verificado: Permanece en "—"
   - ✅ Label `lblOutstandingSim` no se actualiza

4. **Los valores en pantalla se mantienen idénticos**
   - ✅ Verificado para 3 simulaciones consecutivas
   - ✅ Sin efectos colaterales

5. **Solo al presionar "Simular", el sistema recalcula**
   - ✅ Verificado en test anterior (test_fixes_dropdown_y_exposicion.py)
   - ✅ `simulate_selected_row()` es la única función que actualiza

## Antes y Después

### Caso de Uso: Cliente con Outstanding de $ 275,000

#### ❌ Antes del Fix

```
1. Cliente seleccionado
   Outstanding: $ 275,000.00
   Outstanding+Sim: —

2. Usuario hace clic en "Agregar simulación"
   Outstanding: $ 1,000,000.00  ← ❌ Valor incorrecto hardcodeado
   Outstanding+Sim: $ 1,500,000.00  ← ❌ Valor incorrecto hardcodeado

3. Usuario hace clic en "Agregar simulación" nuevamente
   Outstanding: $ 1,000,000.00  ← ❌ Se mantiene incorrecto
   Outstanding+Sim: $ 1,500,000.00  ← ❌ Se mantiene incorrecto
```

#### ✅ Después del Fix

```
1. Cliente seleccionado
   Outstanding: $ 275,000.00
   Outstanding+Sim: —

2. Usuario hace clic en "Agregar simulación"
   Outstanding: $ 275,000.00  ← ✅ NO cambió
   Outstanding+Sim: —  ← ✅ NO cambió
   [1 fila agregada a la tabla]

3. Usuario hace clic en "Agregar simulación" nuevamente
   Outstanding: $ 275,000.00  ← ✅ NO cambió
   Outstanding+Sim: —  ← ✅ NO cambió
   [2 filas en la tabla]

4. Usuario configura la simulación y hace clic en "Simular"
   Outstanding: $ 275,000.00  ← ✅ NO cambió
   Outstanding+Sim: $ 607,715,956.82  ← ✅ SE ACTUALIZA (correcto)
```

## Archivos Modificados

1. **`src/views/main_window.py`**
   - Eliminada llamada a `show_exposure()` con valores hardcodeados
   - Handler `_on_simulations_changed()` ahora es no-op

2. **`src/controllers/forward_controller.py`**
   - Documentación mejorada de `add_simulation()`
   - Eliminada emisión de señal `forward_simulations_changed`
   - Comentarios de seguridad agregados

3. **`src/models/qt/simulations_table_model.py`**
   - No requirió cambios (ya estaba correcto)

## Verificaciones Adicionales Realizadas

### ✅ No hay conexiones indebidas

Verificado que NO existen estas conexiones problemáticas:
```python
# ❌ Estas NO existen (verificado)
self.btnAddSim.clicked.connect(self.on_client_selected_by_name)
self.btnAddSim.clicked.connect(self.simulate_selected_row)
self.tblSimulaciones.model().rowsInserted.connect(self.update_exposure)
```

### ✅ `show_exposure()` solo se invoca desde:

1. `ForwardController.select_client()` - Al seleccionar un cliente
2. `ForwardController.simulate_selected_row()` - Al pulsar "Simular"

**NUNCA desde:**
- ❌ `add_simulation()`
- ❌ `add_row()` del modelo
- ❌ Señales de tabla como `rowsInserted`

## Ventajas del Fix

1. **🎯 Comportamiento Predecible**: Agregar una simulación solo afecta la tabla
2. **🧹 Sin Valores Fantasma**: No aparecen valores hardcodeados incorrectos
3. **🔒 Separación de Responsabilidades**: Agregar ≠ Calcular
4. **👤 Control del Usuario**: Solo "Simular" actualiza exposiciones
5. **🐛 Sin Bugs**: Eliminada la fuente de valores incorrectos

## Conclusión

El fix garantiza que el botón "Agregar simulación" tiene una **única responsabilidad**: agregar una fila vacía a la tabla de simulaciones. **No modifica** los valores de exposición bajo ninguna circunstancia.

Los valores de exposición solo se actualizan cuando el usuario **explícitamente** presiona el botón "Simular", lo cual es el comportamiento esperado y correcto.

### Resumen del Fix

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Agregar simulación** | Seteaba valores hardcodeados | Solo agrega fila |
| **Outstanding** | Cambiaba a $ 1,000,000 | Permanece inalterado |
| **Outstanding+Sim** | Cambiaba a $ 1,500,000 | Permanece en "—" |
| **Señal emitida** | `forward_simulations_changed` | Ninguna |
| **Handler ejecutado** | `_on_simulations_changed()` con `show_exposure()` | No-op (vacío) |
| **Efectos colaterales** | Múltiples (incorrectos) | Ninguno |

✅ **Fix verificado y funcionando correctamente**

