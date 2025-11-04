# Funcionalidad IBR Implementada

## ✅ Resumen de Implementación

Se implementó soporte completo para cargar y usar curvas de tasas IBR (Interest Bank Rate) en el sistema de simulaciones Forward.

---

## 🎯 Funcionalidades Implementadas

### 1. **Botón "Cargar IBR" en la UI**

**Ubicación**: Header de ForwardView, junto al botón "Cargar 415"

**Funcionalidad**:
- Abre diálogo de selección de archivo (*.csv)
- Valida extensión y existencia del archivo
- Emite señal `load_ibr_requested` al controller

**Archivo**: `src/views/forward_view.py`
- Botón: `btnLoadIBR`
- Señal: `load_ibr_requested = Signal(str)`
- Handler: `_on_load_ibr_button_clicked()`

### 2. **Loader de Archivos IBR**

**Archivo**: `data/ibr_loader.py`

**Formato esperado del CSV**:
```
30;0.0450
60;0.0468
90;0.0485
120;0.0502
180;0.0535
360;0.0605
```

**Características**:
- Sin headers
- Separador: `;`
- Columna 0: días (int)
- Columna 1: tasa en DECIMAL (0.045 = 4.5%)
- Encoding: UTF-8 con fallback a latin-1
- Limpieza de BOM y espacios

**Función principal**:
```python
def load_ibr_csv(file_path: str) -> Dict[int, float]:
    """
    Retorna: {dias: tasa_decimal}
    Ejemplo: {30: 0.045, 60: 0.0468, ...}
    """
```

**Validación**:
```python
def validate_ibr_curve(curve: Dict[int, float]) -> bool:
    """
    Valida:
    - Curva no vacía
    - Días positivos
    - Tasas en rango 0-1 (decimal)
    """
```

### 3. **Almacenamiento en ForwardDataModel**

**Archivo**: `src/models/forward_data_model.py`

**Atributos agregados**:
```python
self.ibr_curve: Dict[int, float] = {}  # {dias: tasa_decimal}
self.ibr_loaded: bool = False
self.ibr_file_path: Optional[str] = None
```

**Métodos agregados**:

#### `set_ibr_curve(curve, file_path=None)`
Almacena la curva IBR en memoria.

#### `get_ibr_for_days(days: int) -> float`
**Comportamiento**:
- Busca el plazo exacto en la curva
- Si existe: retorna `tasa_decimal * 100` (convierte a %)
- Si NO existe: retorna `0.0`
- **NO interpola** valores intermedios

**Ejemplo**:
```python
model.get_ibr_for_days(30)   # → 4.5  (si existe)
model.get_ibr_for_days(45)   # → 0.0  (si no existe)
model.get_ibr_for_days(360)  # → 6.05 (si existe)
```

#### `get_ibr_status()` 
Retorna estado de carga del IBR.

#### `clear_ibr_data()`
Limpia la curva IBR de memoria.

### 4. **Actualización Automática en Simulaciones**

**Archivo**: `src/models/qt/simulations_table_model.py`

**Flujo de actualización**:

```
Usuario edita "Fecha Vencimiento"
           ↓
Método setData() detecta cambio en col 5
           ↓
Llama _recalculate_plazo(row)
           ↓
1. Calcula: plazo = (fecha_venc - hoy).days
2. Llama ibr_resolver(plazo) → obtiene tasa_ibr_%
3. Actualiza row_data["tasa_ibr"] = tasa_% / 100
4. Emite dataChanged para columna "Plazo"
5. Emite dataChanged para columna "Tasa IBR"
```

**IBR Resolver**:
El modelo recibe un callback (`ibr_resolver`) que es inyectado por el Controller:

```python
def __init__(self, ..., ibr_resolver=None):
    self._ibr_resolver = ibr_resolver
```

El resolver es una función lambda que consulta el ForwardDataModel:
```python
lambda dias: data_model.get_ibr_for_days(dias)
```

**Método key**:
```python
def _recalculate_plazo(self, row: int) -> None:
    """
    1. Parsea fecha_venc
    2. Calcula plazo en días
    3. Consulta IBR usando resolver
    4. Actualiza tasa_ibr en la fila
    5. Emite señales de cambio
    """
```

### 5. **Integración en el Controller**

**Archivo**: `src/controllers/forward_controller.py`

**Nuevo método**:
```python
def load_ibr(self, file_path: str) -> None:
    """
    1. Valida archivo (existencia, extensión)
    2. Carga curva con load_ibr_csv()
    3. Valida curva
    4. Guarda en data_model.set_ibr_curve()
    5. Notifica a la vista
    """
```

**Configuración del resolver**:
En `_connect_view_signals()`:
```python
if self._simulations_table_model and self._data_model:
    self._simulations_table_model.set_ibr_resolver(
        lambda dias: self._data_model.get_ibr_for_days(dias)
    )
```

Esto conecta el modelo de simulaciones con el modelo de datos.

---

## 📊 Flujo Completo de Uso

### Escenario 1: Cargar IBR antes de crear simulaciones

```
1. Usuario hace clic en "Cargar IBR"
2. Selecciona archivo CSV
3. Controller carga curva → ForwardDataModel
4. Usuario carga 415
5. Usuario selecciona cliente
6. Usuario hace clic en "Agregar fila"
7. Usuario edita "Fecha Vencimiento" → Plazo se calcula
8. ¡Tasa IBR se actualiza automáticamente!
```

### Escenario 2: Cargar IBR después de crear simulaciones

```
1. Usuario carga 415
2. Usuario crea simulaciones (Tasa IBR = 0 porque no hay curva)
3. Usuario hace clic en "Cargar IBR"
4. Controller carga curva → ForwardDataModel
5. Usuario edita cualquier "Fecha Vencimiento"
6. ¡Tasa IBR se actualiza automáticamente para esa fila!
```

### Escenario 3: Plazo no existe en curva

```
Usuario establece fecha vencimiento a 45 días
    ↓
Plazo = 45 días
    ↓
get_ibr_for_days(45) → retorna 0.0
    ↓
Tasa IBR = 0.00%
```

---

## 🧪 Tests Ejecutados

### Test 1: IBR Loader
```
✅ Carga archivo CSV sin headers
✅ Parsea correctamente días y tasas
✅ Maneja encoding UTF-8 y latin-1
✅ Valida formato de curva
```

### Test 2: ForwardDataModel
```
✅ Almacena curva IBR
✅ get_ibr_for_days retorna % correctos
✅ get_ibr_for_days retorna 0 para plazos no existentes
✅ get_ibr_status funciona correctamente
```

### Test 3: SimulationsTableModel
```
✅ Resolver de IBR se configura correctamente
✅ Plazo se calcula al cambiar fecha
✅ Tasa IBR se actualiza automáticamente
✅ Tasa IBR = 0 para plazos no existentes
✅ Tasa IBR se recalcula al cambiar fecha
```

**Resultados de tests**:
```
30 días → 4.5000%  ✓
60 días → 4.6800%  ✓
90 días → 4.8500%  ✓
45 días → 0.0000%  ✓ (no existe, correcto)
```

---

## 📝 Reglas de Negocio Implementadas

1. ✅ **Archivo IBR se carga diariamente** (igual que 415)
   
2. ✅ **Formato CSV sin headers, separador `;`, encoding flexible**

3. ✅ **Tasa IBR solo se actualiza al cambiar Fecha Vencimiento**
   - Cambio de fecha → recalcula Plazo → consulta IBR → actualiza Tasa IBR

4. ✅ **Si plazo no existe en curva → Tasa IBR = 0**
   - **NO se interpola**
   - Búsqueda exacta en diccionario

5. ✅ **Conversión decimal → porcentaje**
   - Archivo: `0.045` (decimal)
   - Almacenamiento interno: `0.045`
   - Display en tabla: `4.50%`

6. ✅ **Tasa IBR es solo lectura**
   - No editable manualmente
   - Se actualiza automáticamente por el sistema

7. ✅ **Funciona aunque IBR se cargue antes o después de 415**
   - Sin IBR: Tasa IBR = 0
   - Con IBR: Tasa IBR se actualiza al editar fechas

---

## 🔧 Archivos Creados/Modificados

### Archivos Creados:
1. **`data/ibr_loader.py`** - Loader de archivos IBR
2. **`test_ibr_curva.csv`** - Archivo de prueba

### Archivos Modificados:

1. **`src/models/forward_data_model.py`**
   - Atributos: `ibr_curve`, `ibr_loaded`, `ibr_file_path`
   - Métodos: `set_ibr_curve()`, `get_ibr_for_days()`, `get_ibr_status()`, `clear_ibr_data()`

2. **`src/models/qt/simulations_table_model.py`**
   - Constructor acepta `ibr_resolver` callback
   - `_recalculate_plazo()` actualiza Tasa IBR
   - Método `set_ibr_resolver()`

3. **`src/controllers/forward_controller.py`**
   - Método `load_ibr()`
   - Configuración de IBR resolver en `_connect_view_signals()`
   - Conexión de señal `load_ibr_requested`

4. **`src/views/forward_view.py`**
   - Señal: `load_ibr_requested`
   - Botón: `btnLoadIBR`
   - Handler: `_on_load_ibr_button_clicked()`
   - Método: `on_load_ibr_clicked()`

---

## ✅ Criterios de Aceptación - TODOS CUMPLIDOS

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Botón "Cargar IBR" funcional | ✅ CUMPLIDO | Vista actualizada |
| Loader CSV sin headers con `;` | ✅ CUMPLIDO | `ibr_loader.py` |
| Encoding UTF-8/latin-1 | ✅ CUMPLIDO | Fallback implementado |
| Curva almacenada en memoria | ✅ CUMPLIDO | `ForwardDataModel` |
| get_ibr_for_days retorna % | ✅ CUMPLIDO | Test: 4.50%, 4.68% |
| Plazo no existente → 0 | ✅ CUMPLIDO | Test: 45 días → 0.00% |
| Actualización automática | ✅ CUMPLIDO | Al cambiar Fec Venc |
| Tasa IBR solo lectura | ✅ CUMPLIDO | flags() sin ItemIsEditable |
| Funciona sin IBR cargado | ✅ CUMPLIDO | Tasa IBR = 0 |
| No rompe funcionalidad previa | ✅ CUMPLIDO | Tests pasaron |

---

## 📖 Ejemplo de Uso

### Archivo IBR (test_ibr_curva.csv):
```csv
30;0.0450
60;0.0468
90;0.0485
120;0.0502
180;0.0535
360;0.0605
```

### En la aplicación:
1. Hacer clic en "Cargar IBR" → seleccionar `test_ibr_curva.csv`
2. Cargar archivo 415
3. Seleccionar cliente
4. Agregar simulación
5. Editar "Fecha Vencimiento" a 30 días desde hoy
6. **Resultado**: Plazo = 30 días, Tasa IBR = 4.50%

7. Cambiar "Fecha Vencimiento" a 90 días desde hoy
8. **Resultado**: Plazo = 90 días, Tasa IBR = 4.85%

9. Cambiar "Fecha Vencimiento" a 45 días desde hoy
10. **Resultado**: Plazo = 45 días, Tasa IBR = 0.00% (no existe en curva)

---

## 🚀 Estado Final

✅ **FUNCIONALIDAD COMPLETA IMPLEMENTADA Y VERIFICADA**

- Botón UI funcional
- Loader robusto
- Almacenamiento en modelo
- Actualización automática
- Manejo de casos edge (plazos no existentes)
- Sin romper funcionalidad existente
- Tests exitosos

**Fecha**: 2025-11-03

