# Implementación de Indicador Visual para Archivo IBR

## Resumen

Se ha implementado un indicador visual (banner) para el archivo IBR en el proyecto SimuladorForward, similar al existente para el archivo 415. El banner muestra información completa del archivo cargado incluyendo nombre, tamaño, fecha de cargue y estado de validación.

## Fecha de Implementación

Noviembre 3, 2025

## Cambios Implementados

### 1. Modelo de Datos (`src/models/forward_data_model.py`)

#### Nuevos Atributos

```python
# Metadatos del archivo IBR
self.ibr_nombre: Optional[str] = None
self.ibr_tamano_kb: Optional[float] = None
self.ibr_timestamp: Optional[str] = None
self.ibr_estado: str = "—"
```

#### Nuevos Métodos

**`set_ibr_metadata(nombre, tamano_kb, timestamp, estado)`**
- Guarda los metadatos del archivo IBR en el modelo
- Parámetros:
  - `nombre`: Nombre del archivo
  - `tamano_kb`: Tamaño en KB (float)
  - `timestamp`: Fecha/hora de cargue (string)
  - `estado`: Estado del archivo ("Cargado" o "Inválido")

**Actualización de `clear_ibr_data()`**
- Ahora también limpia los metadatos del IBR
- Restablece todos los campos a sus valores por defecto

### 2. Vista (`src/views/forward_view.py`)

#### Nuevos Widgets

Se agregaron las siguientes referencias en `__init__`:
```python
# Referencias para banner IBR
self.lblArchivoIBR = None
self.lblTamanoIBR = None
self.lblFechaIBR = None
self.lblEstadoIBR = None
self.bannerIBR = None
```

#### Nuevo Banner

**`_create_banner_ibr()`**
- Crea el banner visual para el archivo IBR
- Estructura similar al banner del 415
- Componentes:
  - `lblArchivoIBR`: Muestra el nombre del archivo o "—"
  - `lblTamanoIBR`: Muestra el tamaño en KB con 2 decimales
  - `lblFechaIBR`: Muestra la fecha/hora de cargue (formato: YYYY-MM-DD HH:MM:SS)
  - `lblEstadoIBR`: Badge de estado ("✅ Cargado" o "⛔ Inválido")
- Estilo:
  - QFrame con `StyledPanel`
  - Fondo verde claro (#e8f5e9) para estado "Cargado"
  - Fondo rojo claro (#ffebee) para estado "Inválido"
  - Badge con colores contrastantes (verde #4caf50 o rojo #f44336)
- Inicialmente oculto, se muestra al cargar un archivo

#### Nuevo Método Público

**`update_ibr_status(file_path, estado, tamano_kb, timestamp)`**
- Actualiza el banner con la información del archivo IBR
- Parámetros:
  - `file_path`: Ruta del archivo (None si inválido)
  - `estado`: Estado del archivo ("Cargado" o "Inválido")
  - `tamano_kb`: Tamaño en KB (opcional)
  - `timestamp`: Fecha/hora de cargue (opcional)
- Comportamiento:
  - Extrae el nombre del archivo de la ruta
  - Actualiza todos los labels del banner
  - Aplica el estilo correspondiente según el estado
  - Muestra el banner (lo hace visible)

### 3. Controlador (`src/controllers/forward_controller.py`)

#### Actualización del método `load_ibr()`

Se agregó la lógica para calcular metadatos y actualizar la vista:

**Nuevas importaciones:**
```python
from datetime import datetime
import os
```

**Cálculo de metadatos:**
```python
# Calcular metadatos del archivo
tamano_kb = os.path.getsize(file_path) / 1024.0
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
nombre_archivo = file_obj.name
```

**Actualización del modelo:**
```python
# Guardar metadatos en el modelo
self._data_model.set_ibr_metadata(nombre_archivo, tamano_kb, timestamp, "Cargado")
```

**Actualización de la vista:**
```python
# Actualizar banner con estado
self._view.update_ibr_status(
    file_path=file_path,
    estado="Cargado",
    tamano_kb=tamano_kb,
    timestamp=timestamp
)
```

**Manejo de errores:**
- Todos los casos de error (archivo no existe, extensión incorrecta, curva vacía o inválida) ahora llaman a `update_ibr_status(None, "Inválido")`
- El banner muestra el estado "⛔ Inválido" en estos casos

### 4. Módulo de Carga IBR (`data/ibr_loader.py`)

No se realizaron cambios en este módulo, ya existía de implementaciones anteriores.

## Ubicación en la UI

El banner IBR se encuentra:
- En el layout principal de ForwardView
- Después del banner del 415
- Antes del panel superior con las 3 columnas
- Ocupa todo el ancho disponible

## Criterios de Aceptación Verificados

✅ **Al cargar un CSV IBR válido, la UI muestra:**
- Nombre del archivo ✓
- Tamaño en KB con 2 decimales ✓
- Fecha/hora de cargue ✓
- Estado: "✅ Cargado" ✓

✅ **Si el archivo es inválido o lectura falla:**
- Estado: "⛔ Inválido" ✓
- Los demás campos quedan en "—" ✓

✅ **El banner IBR queda visualmente alineado con el banner 415** ✓

✅ **No se rompe la actualización automática de Tasa IBR al cambiar Plazo** ✓

## Casos de Uso Probados

1. **Carga de archivo IBR válido:**
   - El banner se muestra correctamente
   - Toda la información es precisa
   - El estado es "✅ Cargado"
   - El color de fondo es verde claro

2. **Carga de archivo inexistente:**
   - El banner muestra estado "⛔ Inválido"
   - Los campos de información muestran "—"
   - El color de fondo es rojo claro

3. **Carga de archivo con extensión incorrecta:**
   - El banner muestra estado "⛔ Inválido"
   - El sistema rechaza el archivo antes de intentar leerlo

4. **Integración con tabla de simulaciones:**
   - La actualización automática de "Tasa IBR" sigue funcionando correctamente
   - El banner se actualiza independientemente del orden de carga (415/IBR)

## Formato de Salida

### Banner IBR - Estado Cargado
```
┌─────────────────────────────────────────────────────────────────────────┐
│ Archivo: test_ibr_valido.csv  │  Tamaño: 0.08 KB  │  Fecha: 2025-11-03 │
│ 18:53:15                                           │  [✅ Cargado]      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Banner IBR - Estado Inválido
```
┌─────────────────────────────────────────────────────────────────────────┐
│ Archivo: —  │  Tamaño: —  │  Fecha: —           │  [⛔ Inválido]      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Compatibilidad

- ✅ Compatible con funcionalidad existente del IBR
- ✅ No interfiere con el banner del 415
- ✅ Funciona independiente del orden de carga (415/IBR)
- ✅ No rompe la actualización automática de "Tasa IBR"

## Archivos Modificados

1. `src/models/forward_data_model.py`
2. `src/views/forward_view.py`
3. `src/controllers/forward_controller.py`

## Archivos de Prueba

- `test_ibr_valido.csv`: Archivo de prueba con curva IBR válida (7 puntos)
- Tests ejecutados exitosamente verificando toda la funcionalidad

## Notas Técnicas

1. **Formato de tamaño:**
   - Se calcula usando `os.path.getsize(file_path) / 1024.0`
   - Se muestra con 2 decimales: `{tamano_kb:.2f} KB`

2. **Formato de timestamp:**
   - Se genera usando `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
   - Formato: YYYY-MM-DD HH:MM:SS

3. **Sincronización modelo-vista:**
   - Los metadatos se guardan primero en el modelo
   - Luego se actualiza la vista con los mismos datos
   - Esto mantiene consistencia entre modelo y vista

4. **Visibilidad del banner:**
   - Inicialmente está oculto (`banner.setVisible(False)`)
   - Se hace visible solo cuando se intenta cargar un archivo
   - Permanece visible una vez que se muestra por primera vez

## Conclusión

La implementación del indicador visual para el archivo IBR está completa y funcional. Todos los criterios de aceptación fueron verificados exitosamente mediante tests automatizados. El banner proporciona retroalimentación clara y consistente al usuario sobre el estado del archivo IBR cargado, manteniendo la coherencia visual con el banner del archivo 415.

