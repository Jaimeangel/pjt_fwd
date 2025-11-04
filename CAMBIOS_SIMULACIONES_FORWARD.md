# Cambios Implementados: Simulaciones Forward

## ✅ Resumen de Cambios

Se actualizaron exitosamente tres aspectos clave de la tabla de simulaciones Forward:

1. **Nueva fórmula de cálculo** para Tasa Forward
2. **Nueva columna "Plazo"** con cálculo automático
3. **Distribución visual mejorada** de las columnas

---

## 1. 🔢 Nueva Fórmula de Tasa Forward

### Cambio Realizado

**Fórmula anterior:**
```python
Tasa Forward = Spot + (Puntos / 10000)
```

**Nueva fórmula:**
```python
Tasa Forward = Spot + Puntos
```

### Ejemplos de Cálculo

| Spot    | Puntos | Tasa Forward (Anterior) | Tasa Forward (Nueva) |
|---------|--------|------------------------|---------------------|
| 4100.00 | 50.30  | 4100.00503             | **4150.30** ✅      |
| 4250.00 | 100.00 | 4250.01                | **4350.00** ✅      |
| 4200.00 | 75.50  | 4200.00755             | **4275.50** ✅      |

### Implementación

**Archivo**: `src/models/qt/simulations_table_model.py`

```python
def _recalculate_tasa_fwd(self, row: int) -> None:
    """
    Recalcula la Tasa Forward cuando cambian Spot o Puntos.
    
    Fórmula: Tasa Forward = Spot + Puntos (suma directa)
    """
    if 0 <= row < len(self._rows):
        row_data = self._rows[row]
        spot = float(row_data.get("spot", 0) or 0)
        puntos = float(row_data.get("puntos", 0) or 0)
        
        # Calcular Tasa Forward (nueva fórmula: suma directa)
        tasa_fwd = spot + puntos
        row_data["tasa_fwd"] = tasa_fwd
```

### Verificación

✅ **Test ejecutado**: La nueva fórmula calcula correctamente
- Spot=4100, Puntos=50.30 → Tasa Forward=4150.30 ✓
- Spot=4250, Puntos=100 → Tasa Forward=4350.00 ✓

---

## 2. 📅 Nueva Columna "Plazo"

### Características

- **Ubicación**: Entre "Fec Venc" y "Spot" (columna 6)
- **Cálculo**: Días entre Fecha Vencimiento y fecha actual
- **Actualización**: Automática al cambiar Fecha Vencimiento
- **Edición**: **NO editable** (solo lectura)

### Estructura Actualizada de Columnas

```
0. Cliente
1. Punta Cli
2. Punta Emp
3. Nominal USD
4. Fec Sim
5. Fec Venc
6. Plazo        ← NUEVA COLUMNA
7. Spot
8. Puntos
9. Tasa Fwd
10. Tasa IBR
11. Derecho
12. Obligación
13. Fair Value
```

### Implementación

**Método de cálculo**:

```python
def _recalculate_plazo(self, row: int) -> None:
    """
    Recalcula el Plazo cuando cambia la Fecha de Vencimiento.
    
    Plazo = días entre Fecha Vencimiento y hoy
    """
    from datetime import date, datetime
    
    if 0 <= row < len(self._rows):
        row_data = self._rows[row]
        fecha_venc_str = row_data.get("fec_venc")
        
        if fecha_venc_str:
            # Parsear la fecha
            fecha_venc = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()
            
            # Calcular plazo
            hoy = date.today()
            plazo_dias = (fecha_venc - hoy).days
            
            # Evitar plazos negativos
            row_data["plazo"] = plazo_dias if plazo_dias >= 0 else 0
```

### Formato de Visualización

```python
elif col == 6:  # Plazo
    plazo = row_data.get("plazo")
    if plazo is None:
        return "—"
    return f"{plazo} días"
```

### Ejemplos de Uso

| Fecha Vencimiento | Fecha Actual | Plazo Mostrado |
|-------------------|--------------|----------------|
| 2025-12-02        | 2025-11-02   | 30 días        |
| 2026-01-31        | 2025-11-02   | 90 días        |
| 2025-11-15        | 2025-11-02   | 13 días        |

### Verificación

✅ **Tests ejecutados**:
- Plazo se calcula correctamente (30 días ✓, 90 días ✓)
- Plazo se recalcula al cambiar Fecha Vencimiento ✓
- Plazo es solo lectura (no editable) ✓

---

## 3. 🎨 Distribución Visual Mejorada

### Cambios Aplicados

#### 1. Ancho Uniforme de Columnas

**Archivo**: `src/views/forward_view.py`

```python
# Distribución uniforme de columnas
self.tblSimulaciones.horizontalHeader().setStretchLastSection(True)
self.tblSimulaciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
```

**Resultado**: Todas las columnas tienen el mismo ancho, adaptándose al espacio disponible.

#### 2. Números de Fila Ocultos

```python
# Ocultar números de fila verticales
self.tblSimulaciones.verticalHeader().setVisible(False)
```

**Resultado**: Más espacio para las columnas, interfaz más limpia.

#### 3. Contenido Centrado

**Archivo**: `src/models/qt/simulations_table_model.py`

```python
# TextAlignmentRole: alineación de texto
elif role == Qt.TextAlignmentRole:
    # Centrar todo el contenido para mejor estética
    return Qt.AlignCenter
```

**Resultado**: Todo el contenido (texto y números) está centrado en las celdas.

#### 4. Comportamiento de Selección

```python
self.tblSimulaciones.setSelectionBehavior(QAbstractItemView.SelectRows)
```

**Resultado**: Al hacer clic en una celda, se selecciona toda la fila.

### Aspecto Visual

**Antes**:
- Columnas con anchos variables
- Números de fila visibles
- Contenido alineado a izquierda/derecha
- Selección por celda

**Después**:
- ✅ Columnas con ancho uniforme
- ✅ Sin números de fila
- ✅ Contenido centrado
- ✅ Selección por fila completa

---

## 📊 Columnas Editables

### Columnas que SE PUEDEN editar:

1. **Punta Cli** (dropdown: Compra/Venta)
2. **Nominal USD** (número)
3. **Fec Venc** (date picker)
4. **Spot** (número)
5. **Puntos** (número)

### Columnas que NO se pueden editar (calculadas automáticamente):

- **Cliente** (establecido al crear la fila)
- **Punta Emp** (inversa de Punta Cli)
- **Fec Sim** (fecha actual)
- **Plazo** ← NUEVA (calculada automáticamente)
- **Tasa Fwd** (calculada: Spot + Puntos)
- **Tasa IBR** (pendiente de implementación)
- **Derecho** (pendiente de implementación)
- **Obligación** (pendiente de implementación)
- **Fair Value** (pendiente de implementación)

---

## ✅ Criterios de Aceptación - TODOS CUMPLIDOS

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Nueva fórmula: Tasa Forward = Spot + Puntos | ✅ CUMPLIDO | Test: 4150.30, 4350.00 |
| Distribución uniforme de columnas | ✅ CUMPLIDO | QHeaderView.Stretch |
| Nueva columna "Plazo" agregada | ✅ CUMPLIDO | Índice 6 en headers |
| Plazo muestra días correctamente | ✅ CUMPLIDO | "X días" |
| Plazo se recalcula automáticamente | ✅ CUMPLIDO | Al cambiar Fec Venc |
| Plazo es solo lectura | ✅ CUMPLIDO | No editable |
| Funcionalidades previas funcionan | ✅ CUMPLIDO | Delegates, validaciones |
| Contenido centrado | ✅ CUMPLIDO | Qt.AlignCenter |

---

## 🧪 Tests Ejecutados

### Test 1: Nueva Fórmula

```
Caso 1: Spot=4100, Puntos=50.30
  Tasa Forward calculada: 4150.3
  Esperado: 4150.3
  ✅ CORRECTO

Caso 2: Spot=4250, Puntos=100
  Tasa Forward calculada: 4350.0
  Esperado: 4350.0
  ✅ CORRECTO
```

### Test 2: Columna Plazo

```
Caso 1: Fecha vencimiento en 30 días
  Plazo calculado: 30 días
  ✅ CORRECTO

Caso 2: Fecha vencimiento en 90 días
  Plazo calculado: 90 días
  ✅ CORRECTO

Caso 3: Plazo no editable
  ¿Plazo es editable?: False
  ✅ CORRECTO
```

### Test 3: Estructura Visual

```
✓ Total de columnas: 14
✓ Contenido centrado en todas las celdas
✓ Columnas editables correctas
✓ Distribución uniforme configurada
```

---

## 📝 Archivos Modificados

### 1. `src/models/qt/simulations_table_model.py`

**Cambios**:
- Actualizado `HEADERS` para incluir "Plazo"
- Actualizado `EDITABLE_COLUMNS` con nuevos índices
- Modificado `_recalculate_tasa_fwd()` con nueva fórmula
- Agregado método `_recalculate_plazo()`
- Actualizado `data()` para mostrar "Plazo"
- Actualizado `setData()` para calcular Plazo
- Cambiado alineación a `Qt.AlignCenter`
- Actualizado `add_row()` para incluir campo "plazo"

### 2. `src/views/forward_view.py`

**Cambios**:
- Configurado `QHeaderView.Stretch` para ancho uniforme
- Ocultado números de fila verticales
- Configurado selección por filas

---

## 🚀 Resultado Final

La tabla de simulaciones Forward ahora:

✅ Calcula Tasa Forward con la nueva fórmula (suma directa)  
✅ Muestra el Plazo en días hasta vencimiento  
✅ Tiene distribución visual uniforme y estética  
✅ Mantiene toda la funcionalidad previa (delegates, validaciones)  
✅ Actualiza automáticamente valores calculados  

**Estado**: ✅ **IMPLEMENTADO Y VERIFICADO**

**Fecha**: 2025-11-03

