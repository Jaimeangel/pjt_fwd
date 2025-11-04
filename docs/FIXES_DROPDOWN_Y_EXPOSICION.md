# Fixes: Dropdown y Exposición

## Resumen

Se han implementado 4 fixes críticos en el módulo Forward para mejorar la experiencia de usuario y evitar comportamientos automáticos no deseados. Los fixes garantizan que:

1. El dropdown de contrapartes inicia vacío sin valores por defecto
2. "Outstanding + simulación" NO se rellena automáticamente (solo tras pulsar "Simular")
3. Agregar simulación NO altera ningún cálculo de exposición
4. El botón "Simular" ejecuta correctamente la simulación y actualiza únicamente "Outstanding + simulación"

## Fecha de Implementación

Noviembre 3, 2025

## Problema Identificado

### Antes de los Fixes

❌ **Problema 1**: Dropdown mostraba clientes mock y seleccionaba automáticamente  
❌ **Problema 2**: "Outstanding + simulación" se igualaba automáticamente al "Outstanding"  
❌ **Problema 3**: Agregar simulación podía disparar cálculos no deseados  
❌ **Problema 4**: No era claro cuándo "Outstanding + simulación" se actualizaba  

### Después de los Fixes

✅ **Solución 1**: Dropdown inicia vacío, se llena solo tras cargar 415, sin selección automática  
✅ **Solución 2**: "Outstanding + simulación" permanece en "—" hasta pulsar "Simular"  
✅ **Solución 3**: Agregar simulación solo afecta la tabla, no los labels  
✅ **Solución 4**: Solo el botón "Simular" actualiza "Outstanding + simulación"  

## Cambios Implementados

### Fix 1: Dropdown de Contrapartes Sin Valores por Defecto

#### Vista (`src/views/forward_view.py`)

**Inicialización vacía del combo:**
```python
# ComboBox de clientes (sin campo de búsqueda)
lbl_cliente = QLabel("Seleccionar contraparte:")
self.cmbClientes = QComboBox()
self.cmbClientes.setObjectName("cmbClientes")
# Iniciar vacío, sin selección
self.cmbClientes.setCurrentIndex(-1)
self.cmbClientes.currentTextChanged.connect(self._on_client_combo_changed)
```

**Método `set_client_list()` actualizado:**
```python
def set_client_list(self, clientes: List[str]) -> None:
    """
    Carga la lista de clientes en el combo box sin seleccionar automáticamente.
    
    Args:
        clientes: Lista de nombres de clientes
    """
    print(f"[ForwardView] set_client_list: {len(clientes)} clientes")
    
    # Bloquear señales para evitar triggers automáticos
    self.cmbClientes.blockSignals(True)
    
    # Limpiar combo
    self.cmbClientes.clear()
    
    # Agregar clientes
    for nombre in sorted(clientes):
        self.cmbClientes.addItem(nombre)
    
    # NO seleccionar automáticamente ningún cliente
    self.cmbClientes.setCurrentIndex(-1)
    
    # Desbloquear señales
    self.cmbClientes.blockSignals(False)
    
    print(f"   ✓ Combo de clientes actualizado con {len(clientes)} opciones (sin selección)")
```

**Cambios clave:**
- ✅ Se eliminaron los items mock ("-- Seleccione un cliente --", clientes de ejemplo)
- ✅ `setCurrentIndex(-1)` para no tener selección por defecto
- ✅ `blockSignals()` para evitar disparar eventos durante la actualización
- ✅ No se agrega opción "-- Seleccione un cliente --"

### Fix 2: No Rellenar "Outstanding + simulación" por Defecto

#### Vista (`src/views/forward_view.py`)

**Inicialización de labels con "—":**
```python
# Outstanding (columna 0)
lbl_out_title = QLabel("Outstanding")
lbl_out_title.setAlignment(Qt.AlignCenter)
self.lblOutstanding = QLabel("—")  # Iniciar sin valor
self.lblOutstanding.setObjectName("lblOutstanding")
self.lblOutstanding.setFont(font_value)
self.lblOutstanding.setAlignment(Qt.AlignCenter)

# Outstanding + simulación (columna 1)
lbl_outsim_title = QLabel("Outst. + simulación")
lbl_outsim_title.setAlignment(Qt.AlignCenter)
self.lblOutstandingSim = QLabel("—")  # Iniciar sin valor
self.lblOutstandingSim.setObjectName("lblOutstandingSim")
self.lblOutstandingSim.setFont(font_value)
self.lblOutstandingSim.setAlignment(Qt.AlignCenter)

# Disponibilidad (columna 2)
lbl_disp_title = QLabel("Disponibilidad de línea")
lbl_disp_title.setAlignment(Qt.AlignCenter)
self.lblDisponibilidad = QLabel("—")  # Iniciar sin valor
```

**Método `show_exposure()` actualizado:**
```python
def show_exposure(self, outstanding: float = None, total_con_simulacion: float = None,
                 disponibilidad: float = None) -> None:
    """
    Actualiza la información de exposición.
    
    Args:
        outstanding: Exposición actual (opcional)
        total_con_simulacion: Exposición total con simulaciones (opcional)
        disponibilidad: Límite disponible (opcional)
    """
    print(f"[ForwardView] show_exposure: outstanding={outstanding}, "
          f"total={total_con_simulacion}, disponibilidad={disponibilidad}")
    
    # Actualizar solo los valores que no sean None
    if outstanding is not None:
        self.lblOutstanding.setText(f"$ {outstanding:,.2f}")
    else:
        self.lblOutstanding.setText("—")
    
    # Outstanding + simulación: solo mostrar si se proporcionó un valor
    if total_con_simulacion is not None:
        self.lblOutstandingSim.setText(f"$ {total_con_simulacion:,.2f}")
    else:
        self.lblOutstandingSim.setText("—")  # No igualar al Outstanding
    
    if disponibilidad is not None:
        self.lblDisponibilidad.setText(f"$ {disponibilidad:,.2f}")
        
        # Cambiar color según disponibilidad
        if disponibilidad < 0:
            self.lblDisponibilidad.setStyleSheet("QLabel { color: #d32f2f; font-weight: bold; }")
        elif disponibilidad < 1000000:  # Menos de 1 millón
            self.lblDisponibilidad.setStyleSheet("QLabel { color: #f57c00; font-weight: bold; }")
        else:
            self.lblDisponibilidad.setStyleSheet("QLabel { color: #2e7d32; font-weight: bold; }")
    else:
        self.lblDisponibilidad.setText("—")
```

**Cambios clave:**
- ✅ Labels inician en "—" en lugar de "$ 0.00"
- ✅ `show_exposure()` solo actualiza si se pasa valor no None
- ✅ Si `total_con_simulacion` es None, se muestra "—" explícitamente

#### Controlador (`src/controllers/forward_controller.py`)

**Método `select_client()` actualizado:**

**Caso: Sin cliente válido**
```python
if not nit:
    print(f"   ⚠️  No se pudo determinar el NIT para: {nombre_o_nit}")
    # Limpiar vista
    if self._view:
        self._view.show_exposure(outstanding=0.0, total_con_simulacion=None, disponibilidad=None)
        if self._operations_table_model:
            self._operations_table_model.set_operations([])
    return
```

**Caso: Cliente válido seleccionado**
```python
# Actualizar outstanding en la vista
self._current_outstanding = outstanding

if self._view:
    # Solo mostrar Outstanding; NO igualar OutstandingSim aquí
    # OutstandingSim se actualiza únicamente al pulsar "Simular"
    self._view.show_exposure(
        outstanding=outstanding,
        total_con_simulacion=None,  # Dejar en "—" hasta simular
        disponibilidad=None
    )
```

**Cambios clave:**
- ✅ Al seleccionar cliente, solo se actualiza `outstanding`
- ✅ `total_con_simulacion` se pasa como `None` explícitamente
- ✅ NO se iguala "Outstanding + simulación" al "Outstanding"
- ✅ El valor solo se actualiza al pulsar "Simular"

### Fix 3: "Agregar simulación" No Altera Exposición

#### Controlador (`src/controllers/forward_controller.py`)

**Método `add_simulation()` actualizado:**
```python
def add_simulation(self) -> None:
    """Agrega una nueva fila de simulación."""
    print("[ForwardController] add_simulation")
    
    # Verificar que hay un cliente seleccionado
    if not self._current_client_nit:
        print("   ⚠️  No hay cliente seleccionado")
        if self._view:
            self._view.notify("Seleccione primero una contraparte antes de agregar una simulación.", "warning")
        return
    
    # Obtener el nombre del cliente
    cliente_nombre = ""
    if self._data_model:
        # Intentar obtener el nombre del cliente por NIT
        cliente_nombre = self._data_model.get_nombre_by_nit(self._current_client_nit)
        if not cliente_nombre:
            cliente_nombre = self._current_client_nit
    
    print(f"   → Cliente seleccionado: {cliente_nombre}")
    
    # Agregar fila al modelo de tabla Qt
    if self._simulations_table_model:
        self._simulations_table_model.add_row(cliente_nombre=cliente_nombre)
        print("   → Fila agregada a la tabla de simulaciones")
    
    # Emitir señal
    if self._signals:
        self._signals.forward_simulations_changed.emit()
    
    # NO tocar: Outstanding, Outstanding+Sim, Disponibilidad
```

**Cambios clave:**
- ✅ Solo valida cliente y agrega fila a la tabla
- ✅ NO llama a `show_exposure()`
- ✅ NO actualiza ningún label de exposición
- ✅ Comportamiento "silencioso" respecto a los cálculos

### Fix 4: "Simular" Ejecuta Simulación y Actualiza Solo Outstanding+Sim

#### Controlador (`src/controllers/forward_controller.py`)

**Método `simulate_selected_row()` (ya implementado correctamente):**
```python
def simulate_selected_row(self) -> None:
    """
    Simula la exposición crediticia de la fila seleccionada.
    
    Recalcula la exposición total incorporando la operación simulada
    junto con las operaciones vigentes del cliente actual.
    """
    # ... validaciones ...
    
    # Convertir fila simulada a "operación 415-like"
    simulated_op = self._simulation_processor.build_simulated_operation(row, nit, nombre, fc)
    
    # Tomar las vigentes del cliente actual
    vigentes = self._data_model.get_operaciones_por_nit(nit) or []
    
    # Recalcular exposición conjunto
    exp_total = self._simulation_processor.recalc_exposure_with_simulation(vigentes, simulated_op)
    
    # Mostrar: Outstanding queda igual; solo actualizar Outstanding + simulación
    outstanding = self._data_model.get_outstanding_por_nit(nit)
    if self._view:
        self._view.show_exposure(
            outstanding=outstanding,
            total_con_simulacion=exp_total,  # ← AQUÍ se actualiza
            disponibilidad=None
        )
        
        self._view.notify(
            f"Simulación procesada: Exposición total $ {exp_total:,.2f}",
            "info"
        )
```

**Cambios clave:**
- ✅ `outstanding` se vuelve a pasar (no cambia)
- ✅ `total_con_simulacion` recibe el valor calculado
- ✅ Es la ÚNICA función que actualiza "Outstanding + simulación"

## Comportamiento Completo

### Flujo de Uso

```
┌────────────────────────────────────────────────────────────────┐
│ 1. Abrir aplicación                                            │
│    - Combo vacío                                               │
│    - Outstanding: "—"                                          │
│    - Outstanding+Sim: "—"                                      │
│    - Disponibilidad: "—"                                       │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ 2. Cargar archivo 415                                          │
│    - Combo se llena con clientes                               │
│    - Sin selección automática (index = -1)                     │
│    - Outstanding: "—"  (NO CAMBIA)                             │
│    - Outstanding+Sim: "—"  (NO CAMBIA)                         │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ 3. Seleccionar cliente                                         │
│    - Outstanding: $ 350,000.00  (se actualiza)                 │
│    - Outstanding+Sim: "—"  (NO se iguala)                      │
│    - Tabla vigentes se carga                                   │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ 4. Cargar archivo IBR                                          │
│    - Outstanding: $ 350,000.00  (NO CAMBIA)                    │
│    - Outstanding+Sim: "—"  (NO CAMBIA)                         │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ 5. Agregar simulación                                          │
│    - Se agrega fila a tabla                                    │
│    - Outstanding: $ 350,000.00  (NO CAMBIA)                    │
│    - Outstanding+Sim: "—"  (NO CAMBIA)                         │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ 6. Configurar simulación (editar celdas)                       │
│    - Nominal, Spot, Puntos, Fecha Vencimiento                  │
│    - Outstanding: $ 350,000.00  (NO CAMBIA)                    │
│    - Outstanding+Sim: "—"  (NO CAMBIA)                         │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ 7. Pulsar "Simular"                                            │
│    - Outstanding: $ 350,000.00  (NO CAMBIA)                    │
│    - Outstanding+Sim: $ 607,715,956.82  (SE ACTUALIZA)         │
│    - Incorpora vigentes + simulación                           │
└────────────────────────────────────────────────────────────────┘
```

## Ejemplo de Ejecución

### Estado Inicial
```
Combo de clientes: [ vacío ]
Outstanding:            —
Outstanding + sim:      —
Disponibilidad:         —
```

### Después de Cargar 415
```
Combo de clientes: [ Cliente Alfa S.A. | Empresa Beta Ltda. ] ← sin selección
Outstanding:            —
Outstanding + sim:      —
Disponibilidad:         —
```

### Después de Seleccionar Cliente
```
Combo de clientes: [ Cliente Alfa S.A. ✓ | Empresa Beta Ltda. ]
Outstanding:            $ 350,000.00
Outstanding + sim:      —                    ← NO se iguala
Disponibilidad:         —
```

### Después de Cargar IBR
```
Outstanding:            $ 350,000.00         ← NO cambia
Outstanding + sim:      —                    ← NO cambia
Disponibilidad:         —
```

### Después de Agregar Simulación
```
Tabla de simulaciones: [ 1 fila nueva ]
Outstanding:            $ 350,000.00         ← NO cambia
Outstanding + sim:      —                    ← NO cambia
Disponibilidad:         —
```

### Después de Pulsar "Simular"
```
Outstanding:            $ 350,000.00         ← NO cambia
Outstanding + sim:      $ 607,715,956.82     ← SE ACTUALIZA
Disponibilidad:         —
```

**Diferencia:** $ 607,365,956.82 (contribución de la simulación)

## Tests Ejecutados

| # | Test | Descripción | Estado |
|---|------|-------------|--------|
| 1 | Estado inicial | Combo vacío, todos los labels en "—" | ✅ |
| 2 | Cargar 415 | Combo lleno sin selección, labels NO cambian | ✅ |
| 3 | Seleccionar cliente | Solo Outstanding actualizado | ✅ |
| 4 | Cargar IBR | Labels NO cambian | ✅ |
| 5 | Agregar simulación | Labels NO cambian | ✅ |
| 6 | Configurar simulación | Labels NO cambian | ✅ |
| 7 | Pulsar Simular | Solo Outstanding+Sim actualizado | ✅ |

## Criterios de Aceptación Cumplidos

### ✅ Fix 1: Dropdown Sin Valores por Defecto
- [x] Al abrir la app: combo vacío
- [x] `setCurrentIndex(-1)` sin selección
- [x] Tras cargar 415: combo se llena sin selección automática
- [x] `blockSignals()` evita triggers durante actualización

### ✅ Fix 2: Outstanding+Sim NO se Rellena Automáticamente
- [x] Labels inician en "—" no en "$ 0.00"
- [x] Seleccionar cliente: solo actualiza Outstanding
- [x] Outstanding+Sim permanece en "—" hasta simular
- [x] NO se iguala automáticamente al Outstanding

### ✅ Fix 3: Agregar Simulación NO Altera Exposición
- [x] `add_simulation()` solo agrega fila a tabla
- [x] NO llama a `show_exposure()`
- [x] NO actualiza ningún label
- [x] Comportamiento "silencioso"

### ✅ Fix 4: Simular Actualiza Solo Outstanding+Sim
- [x] `simulate_selected_row()` es la única función que actualiza
- [x] Outstanding permanece constante
- [x] Outstanding+Sim recibe valor calculado (vigentes + simulación)
- [x] Notificación al usuario con el valor calculado

## Archivos Modificados

### Vista
- `src/views/forward_view.py`
  - Inicialización de `cmbClientes` vacío
  - Inicialización de labels en "—"
  - Método `set_client_list()` con `blockSignals()` y sin selección
  - Método `show_exposure()` con manejo explícito de None

### Controlador
- `src/controllers/forward_controller.py`
  - Método `select_client()` pasa `total_con_simulacion=None`
  - Método `add_simulation()` NO toca labels
  - Método `simulate_selected_row()` actualiza solo Outstanding+Sim

## Ventajas del Nuevo Comportamiento

1. **🎯 Predecible**: Los valores solo cambian cuando el usuario los solicita explícitamente
2. **🧹 Limpio**: No hay valores "fantasma" o automáticos que confundan
3. **👤 Control del Usuario**: El usuario decide cuándo calcular la exposición con simulación
4. **🔍 Claro**: Es evidente cuándo se ha ejecutado una simulación
5. **🚀 Performante**: No se disparan cálculos innecesarios
6. **🛡️ Robusto**: Bloqueo de señales previene efectos colaterales

## Conclusión

Los 4 fixes implementados mejoran significativamente la experiencia del usuario al:

- ✨ Eliminar comportamientos automáticos no deseados
- 🎯 Hacer el flujo más predecible y controlable
- 🧩 Separar claramente las acciones y sus efectos
- 📊 Mostrar información solo cuando es relevante y solicitada

El sistema ahora tiene un comportamiento "manual" donde cada acción del usuario tiene un efecto claro y único, sin sorpresas ni valores que aparecen "mágicamente".

