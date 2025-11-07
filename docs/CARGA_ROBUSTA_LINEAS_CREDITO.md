# Carga Robusta de Líneas de Crédito - Implementación

## Descripción General

Se actualizó la funcionalidad de **carga de líneas de crédito** para hacerla **robusta** ante variaciones en encabezados, diferencias de codificación y espacios ocultos. El sistema ahora soporta múltiples codificaciones (UTF-8 con BOM, Latin-1), normaliza automáticamente los nombres de columnas y reconoce variaciones en mayúsculas/minúsculas y formato.

## Mejoras Implementadas

### 1. Soporte de Múltiples Codificaciones

**Problema anterior:** Solo se intentaba leer con una codificación, lo que fallaba con archivos que tenían BOM o usaban Latin-1.

**Solución:**
```python
def leer_csv_robusto(path):
    """
    Lee un CSV intentando múltiples codificaciones.
    Soporta UTF-8, UTF-8 con BOM, y Latin-1.
    """
    df = None
    # Intentar con utf-8-sig (maneja BOM automáticamente) y latin1
    for enc in ("utf-8-sig", "latin1"):
        try:
            df = pd.read_csv(
                path,
                sep=";",
                engine="python",
                encoding=enc,
                dtype=str,
                keep_default_na=False  # Evita convertir strings vacíos a NaN
            )
            break
        except Exception:
            df = None
    
    if df is None:
        raise ValueError("No se pudo leer el CSV con ninguna codificación estándar")
    
    return df
```

**Codificaciones soportadas:**
- ✅ **UTF-8** (estándar)
- ✅ **UTF-8 con BOM** (utf-8-sig maneja `\ufeff` automáticamente)
- ✅ **Latin-1** (ISO-8859-1, común en sistemas legacy)

### 2. Normalización de Nombres de Columnas

**Problema anterior:** Caracteres invisibles como BOM, NBSP o espacios múltiples causaban que las validaciones fallaran.

**Solución:**
```python
def normalizar(c):
    """Normaliza un nombre de columna eliminando caracteres especiales."""
    c = c.replace("\ufeff", "")        # Eliminar BOM (Byte Order Mark)
    c = c.replace("\xa0", " ")         # Eliminar NBSP (Non-Breaking Space)
    c = re.sub(r"\s+", " ", c).strip() # Colapsar múltiples espacios en uno
    return c

df.columns = [normalizar(c) for c in df.columns]
```

**Transformaciones aplicadas:**

| Entrada | Salida |
|---------|--------|
| `\ufeffNIT` | `NIT` |
| `  NIT  ` | `NIT` |
| `Grupo  Conectado  de  Contrapartes` | `Grupo Conectado de Contrapartes` |
| `Monto\xa0(COP)` | `Monto (COP)` |

### 3. Reconocimiento de Variaciones en Nombres de Columnas

**Problema anterior:** Si el usuario usaba minúsculas o variaciones menores (como `monto(cop)` sin espacio), la validación fallaba.

**Solución:**
```python
# Sistema de alias (case-insensitive)
alias = {
    "nit": "NIT",
    "contraparte": "Contraparte",
    "grupo conectado de contrapartes": "Grupo Conectado de Contrapartes",
    "monto (cop)": "Monto (COP)",
    "monto(cop)": "Monto (COP)",  # Sin espacio antes del paréntesis
    "monto": "Monto (COP)",        # Solo "Monto"
}

# Mapear columnas según alias (insensible a mayúsculas/minúsculas)
df.rename(columns=lambda c: alias.get(c.lower(), c), inplace=True)
```

**Variaciones reconocidas:**

| Entrada | Salida |
|---------|--------|
| `nit` | `NIT` |
| `NIT` | `NIT` |
| `Nit` | `NIT` |
| `contraparte` | `Contraparte` |
| `CONTRAPARTE` | `Contraparte` |
| `monto (cop)` | `Monto (COP)` |
| `monto(cop)` | `Monto (COP)` |
| `MONTO (COP)` | `Monto (COP)` |
| `Monto` | `Monto (COP)` |

### 4. Mejor Mensaje de Error con Diagnóstico

**Problema anterior:** El mensaje de error no indicaba qué columnas se detectaron, dificultando el diagnóstico.

**Solución:**
```python
faltantes = [col for col in columnas_esperadas if col not in df.columns]
if faltantes:
    QMessageBox.warning(
        self,
        "Error de formato",
        f"El archivo no contiene las columnas requeridas:\n{', '.join(faltantes)}\n\n"
        f"Columnas detectadas: {', '.join(df.columns)}"
    )
    return
```

**Ejemplo de mensaje mejorado:**
```
⚠️ Error de formato

El archivo no contiene las columnas requeridas:
Grupo Conectado de Contrapartes, Monto (COP)

Columnas detectadas: NIT, Contraparte, Grupo, Monto
```

Esto permite al usuario identificar rápidamente qué está mal en su archivo.

## Casos de Prueba Validados

### Caso 1: UTF-8 con BOM

**Archivo:** `test_lineas_utf8_bom.csv`
```csv
﻿NIT;Contraparte;Grupo Conectado de Contrapartes;Monto (COP)
900-111-222;BANCO COMERCIAL S.A.;GRUPO BANCARIO;120.5
800-222-333;FINANCIERA XYZ LTDA;GRUPO FINANCIERO;85.75
```

**Resultado:**
```
✓ BOM eliminado correctamente de los encabezados
✓ Lectura exitosa con utf-8-sig
```

### Caso 2: Columnas en Minúsculas

**Archivo:** `test_lineas_lowercase.csv`
```csv
nit;contraparte;grupo conectado de contrapartes;monto (cop)
900-333-444;CORPORACIÓN ABC S.A.S.;GRUPO INDUSTRIAL;65.25
700-444-555;INVERSIONES DEF S.A.;GRUPO COMERCIAL;95.0
```

**Resultado:**
```
→ Columnas originales: ['nit', 'contraparte', 'grupo conectado de contrapartes', 'monto (cop)']
→ Columnas después de mapeo: ['NIT', 'Contraparte', 'Grupo Conectado de Contrapartes', 'Monto (COP)']
✓ Columnas mapeadas correctamente (case-insensitive)
```

### Caso 3: Espacios Extras y Variaciones

**Archivo:** `test_lineas_espacios.csv`
```csv
  NIT  ;  Contraparte  ;  Grupo  Conectado  de  Contrapartes  ;  Monto(COP)  
600-555-666;COMPAÑÍA GHI LTDA;GRUPO TECNOLÓGICO;55.5
500-666-777;EMPRESA JKL S.A.;GRUPO SERVICIOS;75.25
```

**Resultado:**
```
→ Columnas después de normalización: ['NIT', 'Contraparte', 'Grupo Conectado de Contrapartes', 'Monto(COP)']
→ Columnas después de mapeo: ['NIT', 'Contraparte', 'Grupo Conectado de Contrapartes', 'Monto (COP)']
✓ Espacios extras eliminados correctamente
✓ 'Monto(COP)' mapeado correctamente a 'Monto (COP)'
```

## Flujo de Carga Robusto

```
1. Usuario selecciona archivo CSV
   ↓
2. Intentar lectura con UTF-8-sig
   ├─ ✓ Éxito → Continuar
   └─ ✗ Error → Intentar con Latin-1
       ├─ ✓ Éxito → Continuar
       └─ ✗ Error → Mostrar mensaje de error
   ↓
3. Normalizar nombres de columnas
   - Eliminar BOM (\ufeff)
   - Eliminar NBSP (\xa0)
   - Colapsar espacios múltiples
   ↓
4. Aplicar alias (case-insensitive)
   - "nit" → "NIT"
   - "monto(cop)" → "Monto (COP)"
   - etc.
   ↓
5. Validar columnas requeridas
   ├─ ✓ Todas presentes → Continuar
   └─ ✗ Faltantes → Mostrar mensaje con diagnóstico
   ↓
6. Transformar datos
   - Normalizar NITs (eliminar guiones)
   - Convertir montos (×1,000,000,000)
   - Eliminar filas sin NIT o Contraparte
   ↓
7. Mostrar en tabla
   ↓
8. Mensaje de éxito
```

## Logging Detallado

El método ahora genera logs completos para facilitar el diagnóstico:

```
[SettingsView] Cargando archivo: C:\...\lineas_credito.csv
      Intentando con codificación: utf-8-sig
      ✓ Lectura exitosa con utf-8-sig
      ✓ Columnas normalizadas: ['NIT', 'Contraparte', 'Grupo Conectado de Contrapartes', 'Monto (COP)']
   ✓ Columnas después de mapeo: ['NIT', 'Contraparte', 'Grupo Conectado de Contrapartes', 'Monto (COP)']
   ✓ Columnas validadas correctamente
   → Filas leídas: 4
   ✓ NITs normalizados (guiones eliminados)
   ✓ Montos convertidos (miles de millones → COP reales)
   ✓ DataFrame guardado en memoria (4 filas)
[SettingsView] Mostrando 4 líneas de crédito en la tabla...
   ✓ Tabla actualizada con 4 filas
   ✅ Carga completada exitosamente
```

## Configuración de pandas

**Parámetros clave usados:**

```python
df = pd.read_csv(
    path,
    sep=";",                    # Delimitador punto y coma
    engine="python",            # Motor flexible para separadores complejos
    encoding=enc,               # utf-8-sig o latin1
    dtype=str,                  # Leer todo como string inicialmente
    keep_default_na=False       # No convertir strings vacíos a NaN
)
```

**Ventajas:**
- `engine="python"`: Más flexible que el motor C por defecto
- `dtype=str`: Evita conversiones automáticas incorrectas
- `keep_default_na=False`: Preserva strings vacíos como strings (no NaN)

## Manejo de Errores

### Error 1: Codificación no soportada

**Escenario:** Archivo con codificación rara (ej. UTF-16)

**Resultado:**
```
❌ Error al cargar
No se pudo leer el CSV con ninguna codificación estándar (utf-8-sig o latin1).
```

### Error 2: Columnas faltantes

**Escenario:** CSV sin columna "Grupo Conectado de Contrapartes"

**Resultado:**
```
⚠️ Error de formato
El archivo no contiene las columnas requeridas:
Grupo Conectado de Contrapartes

Columnas detectadas: NIT, Contraparte, Monto (COP)
```

### Error 3: Archivo corrupto

**Escenario:** Archivo no es un CSV válido

**Resultado:**
```
❌ Error al cargar
Ocurrió un error al leer el archivo:
[Detalles del error de pandas]
```

## Comparación: Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| Codificaciones | Solo UTF-8 | UTF-8, UTF-8-BOM, Latin-1 |
| BOM | ❌ Causaba errores | ✅ Eliminado automáticamente |
| NBSP | ❌ Causaba errores | ✅ Reemplazado por espacio normal |
| Espacios múltiples | ❌ Causaba errores | ✅ Colapsados a uno |
| Case sensitivity | ❌ "nit" ≠ "NIT" | ✅ "nit" = "NIT" |
| Variaciones | ❌ "monto(cop)" fallaba | ✅ Reconoce "monto(cop)" |
| Mensajes de error | ⚠️ Genéricos | ✅ Diagnóstico detallado |

## Tests Automatizados

Se creó `test_carga_robusta.py` que valida:

1. ✅ Lectura con UTF-8 con BOM
2. ✅ Normalización de BOM, NBSP y espacios extras
3. ✅ Reconocimiento de columnas en minúsculas (case-insensitive)
4. ✅ Mapeo de variaciones: 'monto(cop)' → 'Monto (COP)'
5. ✅ Normalización de NITs (eliminación de guiones)
6. ✅ Conversión de montos (×1,000,000,000)
7. ✅ Detección de columnas faltantes con mensaje detallado
8. ✅ Visualización en tabla con formato apropiado

**Resultado del test:**
```
✅ TODOS LOS TESTS PASARON EXITOSAMENTE
```

## Criterios de Aceptación

| # | Criterio | Estado |
|---|----------|--------|
| 1 | El lector soporta UTF-8, UTF-8 con BOM o Latin-1 | ✅ |
| 2 | Se eliminan espacios ocultos, BOM y NBSP en encabezados | ✅ |
| 3 | Se reconocen encabezados con diferencias menores de formato o capitalización | ✅ |
| 4 | Se eliminan guiones en el campo NIT | ✅ |
| 5 | Los valores de Monto (COP) se convierten correctamente (×1,000,000,000) | ✅ |
| 6 | Los datos se muestran en la tabla con columnas uniformes | ✅ |
| 7 | Mensaje de "Carga exitosa" al finalizar | ✅ |
| 8 | Si falta alguna columna, se muestra mensaje con columnas detectadas y faltantes | ✅ |

## Archivos Modificados

```
src/views/settings_view.py
  ~ cargar_csv_lineas_credito() → Versión robusta con:
    + Función interna leer_csv_robusto()
    + Normalización de columnas
    + Sistema de alias case-insensitive
    + Mejor mensaje de error con diagnóstico
```

## Archivos de Prueba (Temporales)

```
test_lineas_utf8_bom.csv    → CSV con BOM
test_lineas_lowercase.csv   → CSV con columnas en minúsculas
test_lineas_espacios.csv    → CSV con espacios extras y "Monto(COP)"
test_carga_robusta.py       → Test automatizado
```

## Ventajas de la Implementación

### 1. Robustez
- Maneja múltiples codificaciones automáticamente
- Tolera variaciones comunes en archivos CSV

### 2. Flexibilidad
- Reconoce variaciones en nombres de columnas
- No requiere formato exacto

### 3. Diagnóstico
- Mensajes de error informativos
- Logs detallados en consola

### 4. Mantenibilidad
- Código bien documentado
- Sistema de alias fácil de extender

### 5. Usabilidad
- El usuario no necesita preocuparse por formato exacto
- Archivos de diferentes fuentes funcionan sin modificación

## Conclusión

La implementación de **carga robusta** de líneas de crédito fue exitosa y cumple todos los criterios de aceptación. La funcionalidad ahora es:

- ✅ **Robusta**: Maneja múltiples codificaciones y variaciones
- ✅ **Flexible**: Reconoce diferentes formatos de columnas
- ✅ **Informativa**: Mensajes de error con diagnóstico detallado
- ✅ **Confiable**: Tests automatizados validan todos los casos

Esta mejora hace que el sistema sea **más fácil de usar** y **más tolerante a errores**, reduciendo la fricción con archivos de diferentes fuentes y formatos.

---

**Fecha de implementación:** 2025-11-06  
**Autor:** Asistente AI  
**Versión:** 2.0 (Robusta)

