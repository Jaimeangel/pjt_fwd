# Implementación del Csv415Loader

## Resumen Ejecutivo

Se ha implementado el `Csv415Loader` en `data/csv_415_loader.py` que lee archivos CSV del "Informe 415" con separador `;`, filtra solo las operaciones vigentes (`UCaptura == 1`), mapea las columnas a nombres internos, y retorna un `pandas.DataFrame` limpio y listo para usar.

---

## Características Implementadas

### ✅ Lectura de CSV con Separador `;`
- Usa `pandas.read_csv()` con `sep=';'`
- Múltiples encodings soportados: `utf-8`, `latin-1`, `iso-8859-1`, `cp1252`
- Fallback automático si un encoding falla

### ✅ Filtrado de Operaciones Vigentes
- Filtra solo las filas donde `UCaptura == 1`
- Convierte `UCaptura` a numérico para comparación robusta
- Maneja valores nulos o no numéricos

### ✅ Mapeo de Columnas

| Columna 415 (Original) | Nombre Interno |
|------------------------|----------------|
| `14Nom_Cont` | `contraparte` |
| `13Nro_Cont` | `nit` |
| `04Num_Cont` | `deal` |
| `71Oper` | `tipo_operacion` |
| `49Vlr_DerP` | `vr_derecho` |
| `50Vlr_OblP` | `vr_obligacion` |
| `82FC` | `fc` |
| `23Nomi_Der` | `nomin_der` |
| `25Nomi_Obl` | `nomin_obl` |
| `85TRM` | `trm` |
| `89FVcto` | `fecha_liquidacion` |
| `90FCorte` | `fecha_corte` |
| `UCaptura` | `u_captura` |

**Total:** 13 columnas mapeadas

### ✅ Limpieza de Datos

1. **Strings:** Elimina espacios en blanco (`strip()`)
2. **Numéricos:** Convierte a `float` las columnas de valores monetarios
3. **Fechas:** Convierte a `datetime` las columnas de fechas
4. **Manejo de nulos:** Usa `errors='coerce'` para conversiones seguras

### ✅ Validación
- Verifica existencia de columnas requeridas
- Valida que `UCaptura` exista en el archivo
- Retorna DataFrame vacío si no hay operaciones vigentes

---

## Clase `Csv415Loader`

### Constructor

```python
def __init__(self):
    """Inicializa el cargador de archivos 415."""
    pass
```

### Método Principal: `load_operations_from_415()`

```python
def load_operations_from_415(self, file_path: str) -> pd.DataFrame:
    """
    Carga operaciones vigentes del archivo 415.
    
    Args:
        file_path: Ruta al archivo CSV 415
        
    Returns:
        DataFrame con operaciones vigentes y columnas renombradas
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo tiene formato inválido
    """
```

**Algoritmo:**

```
1. Validar que el archivo existe
2. Intentar leer con múltiples encodings (utf-8, latin-1, etc.)
3. Validar que existe la columna UCaptura
4. Filtrar filas donde UCaptura == 1
5. Mapear columnas a nombres internos
6. Limpiar datos (strip whitespace)
7. Convertir tipos de datos:
   - Numéricos: vr_derecho, vr_obligacion, fc, nomin_der, nomin_obl, trm
   - Fechas: fecha_liquidacion, fecha_corte
8. Retornar DataFrame limpio
```

### Métodos Auxiliares

#### `validate(data: Any) -> bool`
Valida que el DataFrame tiene las columnas mínimas requeridas.

#### `get_column_mapping() -> Dict[str, str]`
Retorna el mapeo completo de columnas 415 → nombres internos.

#### `get_stats(df: pd.DataFrame) -> Dict[str, Any]`
Obtiene estadísticas del DataFrame:
- Total de operaciones
- Clientes únicos (por NIT)
- Tipos de operación únicos
- Columnas disponibles
- Valores nulos por columna

---

## Uso

### Ejemplo Básico

```python
from data.csv_415_loader import Csv415Loader

# Crear instancia del loader
loader = Csv415Loader()

# Cargar operaciones vigentes
df = loader.load_operations_from_415("ruta/al/archivo_415.csv")

# DataFrame contiene solo operaciones vigentes con nombres internos
print(f"Total de operaciones: {len(df)}")
print(f"Columnas: {list(df.columns)}")
```

### Ejemplo con Validación

```python
loader = Csv415Loader()

try:
    # Cargar archivo
    df = loader.load_operations_from_415("archivo_415.csv")
    
    # Validar
    if loader.validate(df):
        print("✓ DataFrame válido")
        
        # Obtener estadísticas
        stats = loader.get_stats(df)
        print(f"Total operaciones: {stats['total_operaciones']}")
        print(f"Clientes únicos: {stats['clientes_unicos']}")
        print(f"Tipos de operación: {stats['tipos_operacion']}")
    
except FileNotFoundError:
    print("❌ Archivo no encontrado")
except ValueError as e:
    print(f"❌ Archivo inválido: {e}")
```

---

## Salida en Consola (Ejemplo)

```
[Csv415Loader] Cargando archivo: informe_415.csv
   Intentando encoding: utf-8
   ✓ Archivo leído exitosamente con encoding utf-8
   ✓ Total de filas leídas: 5
   ✓ Total de columnas: 13
   ✓ Primeras 5 columnas: ['14Nom_Cont', '13Nro_Cont', '04Num_Cont', '71Oper', '49Vlr_DerP']

   Filtrando operaciones vigentes (UCaptura == 1)...
   ✓ Operaciones vigentes encontradas: 3

   Mapeando columnas a nombres internos...
   ✓ Columnas disponibles para mapear: 13/13
   ✓ Columnas mapeadas exitosamente
   ✓ Columnas finales: ['contraparte', 'nit', 'deal', 'tipo_operacion', 'vr_derecho', 'vr_obligacion', 'fc', 'nomin_der', 'nomin_obl', 'trm', 'fecha_liquidacion', 'fecha_corte', 'u_captura']

   Limpiando datos...
   ✓ Datos limpios

   Convirtiendo tipos de datos...
   ✓ Tipos de datos convertidos

✅ Carga completada:
   Total de operaciones vigentes: 3
   Columnas disponibles: 13
```

---

## Estructura del DataFrame Resultante

### Ejemplo de Fila

```python
{
    'contraparte': 'Cliente Ejemplo S.A.',
    'nit': '123456789',
    'deal': 'FWD001',
    'tipo_operacion': 'FWD',
    'vr_derecho': 425050000.0,
    'vr_obligacion': 427625000.0,
    'fc': 1.006,
    'nomin_der': 100000.0,
    'nomin_obl': 100000.0,
    'trm': 4250.5,
    'fecha_liquidacion': Timestamp('2025-12-15 00:00:00'),
    'fecha_corte': Timestamp('2025-10-28 00:00:00'),
    'u_captura': 1.0
}
```

### Tipos de Datos

| Columna | Tipo |
|---------|------|
| `contraparte` | `str` |
| `nit` | `str` |
| `deal` | `str` |
| `tipo_operacion` | `str` |
| `vr_derecho` | `float64` |
| `vr_obligacion` | `float64` |
| `fc` | `float64` |
| `nomin_der` | `float64` |
| `nomin_obl` | `float64` |
| `trm` | `float64` |
| `fecha_liquidacion` | `datetime64` |
| `fecha_corte` | `datetime64` |
| `u_captura` | `float64` |

---

## Manejo de Errores

### Archivo No Encontrado

```python
try:
    df = loader.load_operations_from_415("no_existe.csv")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

**Salida:** `FileNotFoundError: Archivo no encontrado: no_existe.csv`

### Columna UCaptura Faltante

```python
try:
    df = loader.load_operations_from_415("archivo_sin_ucaptura.csv")
except ValueError as e:
    print(f"Error: {e}")
```

**Salida:** `ValueError: Columna 'UCaptura' no encontrada. Columnas disponibles: [...]`

### Encoding Inválido

Si ninguno de los encodings funciona, se levanta un `ValueError`:

```
ValueError: No se pudo leer el archivo con los encodings probados: ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
```

---

## Pruebas Automatizadas

### Script de Prueba: `test_csv_415_loader.py`

**Resultados:**

```
============================================================
RESUMEN: 3/3 pruebas pasadas
============================================================

✅ Test 1: Mapeo de columnas - PASADO
✅ Test 2: Cargar archivo completo - PASADO
✅ Test 3: Validación y estadísticas - PASADO
```

### Archivo de Prueba: `test_415_completo.csv`

```csv
14Nom_Cont;13Nro_Cont;04Num_Cont;71Oper;49Vlr_DerP;50Vlr_OblP;82FC;23Nomi_Der;25Nomi_Obl;85TRM;89FVcto;90FCorte;UCaptura
Cliente Ejemplo S.A.;123456789;FWD001;FWD;425050000;427625000;1.006;100000;100000;4250.50;2025-12-15;2025-10-28;1
Corporación ABC Ltda.;987654321;FWD002;FWD;1051250000;1064400000;1.012;250000;250000;4250.50;2025-11-30;2025-10-28;1
Empresa XYZ S.A.S.;555444333;FWD003;FWD;315375000;319931250;1.014;75000;75000;4250.50;2026-01-20;2025-10-28;1
Cliente Ejemplo S.A.;123456789;FWD004;FWD;630750000;637687500;1.011;150000;150000;4250.50;2025-12-31;2025-10-28;0
Corporación ABC Ltda.;987654321;FWD005;FWD;210250000;212525000;1.011;50000;50000;4250.50;2026-02-10;2025-10-28;0
```

**Resultado:**
- Total de filas: 5
- Operaciones vigentes (UCaptura=1): 3
- Operaciones no vigentes (UCaptura=0): 2 (excluidas)

---

## Integración con el Resto del Sistema

### En ForwardController

```python
from data.csv_415_loader import Csv415Loader

class ForwardController:
    def load_415(self, file_path: str) -> None:
        # ... validación básica ...
        
        # Cargar operaciones vigentes
        loader = Csv415Loader()
        df_operations = loader.load_operations_from_415(file_path)
        
        # Guardar en el modelo
        self._data_model.dataset_415 = df_operations
        
        # Procesar por cliente
        self._process_operations_by_client(df_operations)
        
        # Actualizar tabla de operaciones vigentes
        self._update_operations_table(df_operations)
```

### En ForwardDataModel

```python
class ForwardDataModel:
    def set_415_data(self, df: pd.DataFrame) -> None:
        """Almacena el DataFrame de operaciones vigentes."""
        self.dataset_415 = df
        
        # Agrupar por cliente
        for nit in df['nit'].unique():
            ops_cliente = df[df['nit'] == nit]
            self.ops_vigentes_por_cliente[nit] = ops_cliente.to_dict('records')
            
            # Calcular outstanding
            outstanding = ops_cliente['vr_derecho'].sum()
            self.outstanding_por_cliente[nit] = outstanding
```

---

## Requisitos de Sistema

### Dependencias

```
pandas>=2.3.0
numpy>=2.3.0
```

**Instalación:**

```bash
pip install pandas numpy
```

---

## Próximos Pasos Sugeridos

1. **Validaciones Avanzadas:**
   - Validar rangos de valores (montos positivos, fechas futuras)
   - Validar formato de NITs
   - Validar tipos de operación permitidos

2. **Cálculos Derivados:**
   - Calcular plazo en días (fecha_liquidacion - fecha_corte)
   - Calcular fair value desde vr_derecho y vr_obligacion
   - Calcular exposición por operación

3. **Agrupación por Cliente:**
   - Método `group_by_client()` que retorne dict[nit → list[operations]]
   - Cálculo de outstanding total por cliente

4. **Cache:**
   - Implementar cache del DataFrame para evitar recargar el mismo archivo
   - Hash del archivo para detectar cambios

5. **Exportación:**
   - Método `to_excel()` para exportar operaciones filtradas
   - Método `to_json()` para API o persistencia

---

## Conclusión

✅ **Csv415Loader implementado exitosamente**

El sistema ahora puede:
- Leer archivos CSV formato 415 con separador `;`
- Filtrar solo operaciones vigentes (`UCaptura == 1`)
- Mapear 13 columnas a nombres internos
- Limpiar y convertir tipos de datos
- Manejar múltiples encodings
- Validar estructura y retornar estadísticas

**Datos listos y limpios** en formato `pandas.DataFrame` para:
- Llenar tabla de operaciones vigentes
- Calcular exposiciones por cliente
- Análisis y reportes

**Estado:** ✅ Completado  
**Fecha:** 2025-10-28  
**Archivos creados:** 2  
**Pruebas:** 3/3 pasadas

