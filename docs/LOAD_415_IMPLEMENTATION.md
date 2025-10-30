# Implementación del Flujo de Carga del Archivo 415

## Resumen Ejecutivo

Se ha implementado el flujo completo de carga del archivo "Informe 415" con validación básica, registro de metadatos, y actualización de la interfaz. El sistema valida la extensión, el separador, y la estructura básica del archivo CSV sin parsear las filas completas.

---

## Componentes Implementados

### 1. ForwardDataModel (`src/models/forward_data_model.py`)

**Nuevos Campos para Metadatos:**

```python
class ForwardDataModel:
    def __init__(self):
        # ...campos existentes...
        
        # Metadatos del archivo 415
        self.ruta_415: Optional[str] = None
        self.nombre_415: Optional[str] = None
        self.tamano_415_kb: float = 0.0
        self.hash_415: Optional[str] = None
        self.timestamp_cargue: Optional[Any] = None  # datetime
```

**Nuevos Métodos:**

#### `set_415_metadata(ruta, nombre, tamano_kb, hash_value, estado)`
Almacena los metadatos del archivo cargado.

**Parámetros:**
- `ruta`: Ruta completa del archivo
- `nombre`: Nombre del archivo
- `tamano_kb`: Tamaño en KB
- `hash_value`: Hash MD5 simple
- `estado`: "valido", "invalido", o "no_cargado"

#### `get_415_metadata() -> dict`
Retorna todos los metadatos del archivo en un diccionario.

#### `clear_415_data()`
Actualizado para limpiar también los metadatos.

---

### 2. ForwardController (`src/controllers/forward_controller.py`)

#### `load_415(file_path: str)`

**Algoritmo de Validación:**

```
1. Validar que el archivo existe
2. Validar extensión .csv
3. Calcular tamaño en KB
4. Leer primera línea y validar:
   - Archivo no vacío
   - Separador ';' presente
   - Al menos 3 columnas en el header
5. Calcular hash MD5 simple (path + tamaño)
6. Guardar metadatos en ForwardDataModel
7. Emitir señal forward_415_loaded
8. Actualizar vista (header + banner)
```

**Validaciones Implementadas:**

✅ Archivo existe  
✅ Extensión `.csv`  
✅ Archivo no vacío  
✅ Separador `;` en la cabecera  
✅ Cabecera con al menos 3 columnas  

**Salida en Consola (Archivo Válido):**

```
[ForwardController] load_415: C:\path\to\file.csv
   ✓ Archivo encontrado: test_415_valido.csv
   ✓ Tamaño: 0.25 KB
   ✓ Separador ';' detectado
   ✓ Headers detectados: 6 columnas
   ✓ Primeras columnas: NIT, CLIENTE, OPERACION
   ✓ Hash: a3f2b4c1
   ✓ Metadatos guardados en ForwardDataModel
   ✅ Archivo 415 validado exitosamente
```

**Salida en Consola (Archivo Inválido):**

```
[ForwardController] load_415: C:\path\to\file.txt
   ❌ Error: Extensión inválida (.txt), se esperaba .csv
```

#### `_handle_invalid_415(file_path, razon)`

Maneja archivos inválidos:
- Guarda metadatos con estado "invalido"
- Emite señal con estado "invalido"
- Actualiza vista con badge rojo
- Muestra notificación de error

---

### 3. ForwardView (`src/views/forward_view.py`)

#### Nuevo Handler: `_on_load_415_button_clicked()`

```python
def _on_load_415_button_clicked(self):
    """Handler interno para el botón Cargar 415."""
    from PySide6.QtWidgets import QFileDialog
    
    # Abrir diálogo de selección de archivo
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Seleccionar archivo 415",
        "",
        "Archivos CSV (*.csv);;Todos los archivos (*.*)"
    )
    
    # Si se seleccionó un archivo, emitir señal
    if file_path:
        self.on_load_415_clicked(file_path)
```

**Características:**
- Abre `QFileDialog` filtrado por archivos `.csv`
- Emite señal `load_415_requested` con la ruta seleccionada

#### `show_basic_info()` - Actualizado

Ahora actualiza también el **badge de estado** con colores:

| Estado | Color | Hex |
|--------|-------|-----|
| "valido" | Verde | #4caf50 |
| "invalido" | Rojo | #f44336 |
| "no_cargado" | Gris | #999 |

#### Nuevo Método: `update_banner_415()`

```python
def update_banner_415(
    self,
    nombre: str,
    tamano_kb: float,
    fecha_cargue: Optional[Any],
    estado: str
) -> None:
    """Actualiza el banner con información del archivo 415."""
    # Formatea fecha_cargue a string
    # Actualiza lblArchivo415 con formato:
    # "Archivo: nombre.csv | Tamaño: 1.25 KB | Fecha cargue: 2025-10-28 14:30"
    
    # Muestra el banner (inicialmente oculto)
    # Aplica color de fondo según estado:
    #   - valido: verde claro (#e8f5e9)
    #   - invalido: rojo claro (#ffebee)
    #   - otro: gris claro (#f0f4f8)
```

---

## Flujo Completo

### Escenario 1: Archivo Válido

```
1. Usuario hace clic en "Cargar 415"
   └─> _on_load_415_button_clicked()
       └─> QFileDialog.getOpenFileName()
           └─> Usuario selecciona "test_415_valido.csv"
               
2. ForwardView emite señal: load_415_requested(file_path)

3. ForwardController.load_415(file_path):
   ✓ Validar extensión .csv
   ✓ Validar separador ;
   ✓ Calcular tamaño y hash
   ✓ Guardar metadatos en ForwardDataModel
   ✓ Emitir señal: forward_415_loaded(date.today(), "valido")
   ✓ Actualizar vista

4. ForwardView actualiza UI:
   ✓ lblEstado415: "valido" (badge verde)
   ✓ lblFechaCorte415: "Fecha corte 415: --" (sin parsear todavía)
   ✓ lblArchivo415: "Archivo: test_415_valido.csv | Tamaño: 0.25 KB | ..."
   ✓ Banner visible con fondo verde claro
   ✓ Notificación: "Archivo 415 cargado: test_415_valido.csv (0.25 KB)"
```

### Escenario 2: Archivo Inválido (extensión incorrecta)

```
1. Usuario selecciona "test_415_invalido.txt"

2. ForwardController.load_415(file_path):
   ❌ Extensión != .csv
   └─> _handle_invalid_415(file_path, "Extensión inválida")
       ✓ Guardar metadatos con estado="invalido"
       ✓ Emitir señal: forward_415_loaded(None, "invalido")
       ✓ Actualizar vista

3. ForwardView actualiza UI:
   ✓ lblEstado415: "invalido" (badge rojo)
   ✓ Banner con fondo rojo claro
   ✓ Notificación error: "Archivo 415 inválido: Extensión inválida"
```

### Escenario 3: Archivo Inválido (separador incorrecto)

```
1. Usuario selecciona "test_415_sin_separador.csv"

2. ForwardController.load_415(file_path):
   ✓ Extensión .csv OK
   ✓ Tamaño calculado
   ❌ Separador ';' no encontrado (usa ',')
   └─> _handle_invalid_415(file_path, "Separador inválido")
       ✓ Guardar metadatos con estado="invalido"
       ✓ Actualizar vista

3. ForwardView actualiza UI:
   ✓ Badge rojo: "invalido"
   ✓ Notificación error: "Archivo 415 inválido: Separador inválido"
```

---

## Criterios de Aceptación - CUMPLIDOS

### ✅ Al pulsar "Cargar 415"

- [x] Se abre QFileDialog filtrado por archivos `.csv`
- [x] Usuario puede seleccionar un archivo
- [x] Si cancela, no pasa nada (no rompe la app)

### ✅ Validación Básica

- [x] Valida extensión `.csv`
- [x] Valida separador `;` en la cabecera
- [x] Valida cabecera mínima (al menos 3 columnas)
- [x] Archivo no vacío

### ✅ Registro de Metadatos

- [x] Ruta completa del archivo
- [x] Nombre del archivo
- [x] Tamaño en KB
- [x] Hash MD5 simple (path + tamaño)
- [x] Timestamp de cargue (datetime.now())
- [x] Estado: "valido" o "invalido"

### ✅ Actualización de UI

- [x] Badge de estado (lblEstado415) con color dinámico:
  - Verde: archivo válido
  - Rojo: archivo inválido
  - Gris: no cargado
- [x] Banner (banner415) visible después de cargar, con:
  - Nombre del archivo
  - Tamaño en KB
  - Fecha de cargue formateada
  - Fondo coloreado según estado
- [x] Notificación (notify) con mensaje de éxito o error

### ✅ Sin Parseo de Filas

- [x] No se leen filas de datos (solo cabecera)
- [x] No se llenan tablas
- [x] No se calculan exposiciones
- [x] lblFechaCorte415 muestra "--" (sin fecha de corte todavía)

### ✅ Robustez

- [x] No rompe la app con archivos inválidos
- [x] Manejo de excepciones con try/except
- [x] Mensajes claros en consola
- [x] Traceback completo en caso de error inesperado

---

## Archivos de Prueba Creados

### `test_415_valido.csv`
```csv
NIT;CLIENTE;OPERACION;NOMINAL;VENCIMIENTO;ESTADO
123456789;Cliente Ejemplo S.A.;FWD001;100000;2025-12-15;VIGENTE
987654321;Corporación ABC Ltda.;FWD002;250000;2025-11-30;VIGENTE
555444333;Empresa XYZ S.A.S.;FWD003;75000;2026-01-20;VIGENTE
```

**Resultado esperado:** ✅ Cargado (badge verde)

### `test_415_invalido.txt`
Archivo de texto plano, no CSV.

**Resultado esperado:** ⛔ Inválido (extensión incorrecta)

### `test_415_sin_separador.csv`
```csv
NIT,CLIENTE,OPERACION,NOMINAL,VENCIMIENTO,ESTADO
123456789,Cliente Ejemplo S.A.,FWD001,100000,2025-12-15,VIGENTE
```

**Resultado esperado:** ⛔ Inválido (separador `,` en lugar de `;`)

---

## Pruebas Manuales

### 1. Cargar Archivo Válido

```bash
python main.py
```

1. Hacer clic en "Cargar 415"
2. Seleccionar `test_415_valido.csv`
3. Verificar que:
   - Badge cambia a verde "valido"
   - Banner muestra: "Archivo: test_415_valido.csv | Tamaño: 0.25 KB | Fecha cargue: ..."
   - Banner tiene fondo verde claro
   - Notificación: "Archivo 415 cargado: test_415_valido.csv (0.25 KB)"
   - Consola muestra log detallado con ✓

### 2. Cargar Archivo con Extensión Inválida

1. Hacer clic en "Cargar 415"
2. Cambiar filtro a "Todos los archivos (*.*)"
3. Seleccionar `test_415_invalido.txt`
4. Verificar que:
   - Badge cambia a rojo "invalido"
   - Banner tiene fondo rojo claro (si archivo existe)
   - Notificación error: "Archivo 415 inválido: Extensión inválida"
   - Consola muestra: `❌ Error: Extensión inválida (.txt), se esperaba .csv`

### 3. Cargar Archivo con Separador Incorrecto

1. Hacer clic en "Cargar 415"
2. Seleccionar `test_415_sin_separador.csv`
3. Verificar que:
   - Badge cambia a rojo "invalido"
   - Notificación error: "Archivo 415 inválido: Separador inválido"
   - Consola muestra: `❌ Error: Separador ';' no encontrado en la cabecera`

---

## Próximos Pasos Sugeridos

1. **Parseo Completo del Archivo:**
   - Implementar `Csv415Loader.load(file_path)` con pandas
   - Validar columnas esperadas (headers específicos)
   - Cargar todas las filas en `ForwardDataModel.dataset_415`

2. **Llenar Tabla de Operaciones Vigentes:**
   - Procesar filas del 415
   - Agrupar por cliente (NIT)
   - Actualizar `OperationsTableModel` con datos reales
   - Mostrar operaciones en la tabla

3. **Calcular Exposiciones Reales:**
   - Calcular outstanding por cliente desde el 415
   - Actualizar labels de exposición con valores reales
   - Reemplazar mock de `_current_outstanding`

4. **Persistencia en BD (Opcional):**
   - Implementar `SQLiteRepository.save_415_metadata(metadata)`
   - Guardar histórico de archivos cargados
   - Consultar último archivo cargado al iniciar la app

5. **Validaciones Avanzadas:**
   - Validar columnas esperadas por nombre
   - Validar tipos de datos (fechas, números)
   - Validar valores (NITs válidos, fechas futuras)
   - Mostrar diálogo con reporte de validación

---

## Conclusión

✅ **Flujo de carga del archivo 415 implementado exitosamente**

El sistema ahora puede:
- Seleccionar archivos CSV mediante QFileDialog
- Validar extensión, separador y estructura básica
- Registrar metadatos (ruta, nombre, tamaño, hash, timestamp)
- Actualizar la UI con badges y banners coloreados
- Manejar archivos inválidos sin romper la aplicación

**Sin parsear filas ni llenar tablas todavía**, el sistema está listo para la siguiente etapa: parseo completo y carga de datos.

**Estado:** ✅ Completado  
**Fecha:** 2025-10-28  
**Archivos modificados:** 3  
**Archivos de prueba creados:** 3

