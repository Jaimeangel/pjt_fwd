# Actualización: Patrimonio Técnico en COP Reales

## Resumen

Se actualizó el campo "Patrimonio Técnico Vigente" en el módulo Configuraciones para que se exprese y guarde en COP completos (valor real), eliminando la representación en millones de COP que se usaba anteriormente.

## Fecha de Implementación

Noviembre 5, 2025

## Problema Identificado

### Antes de la Actualización

❌ **Problema**: El campo "Patrimonio Técnico Vigente" usaba millones de COP:

```python
# ❌ ANTES (en millones)
self.inpPatrimonio = QDoubleSpinBox()
self.inpPatrimonio.setRange(0, 1000000)           # 0 a 1 millón de millones
self.inpPatrimonio.setValue(50000)                # 50,000 millones
self.inpPatrimonio.setSuffix(" mill COP")         # Sufijo indica millones
layout.addRow("Patrimonio Técnico Vigente:", self.inpPatrimonio)
```

**Problemas:**
- Confusión sobre si el valor es en millones o COP reales
- Necesidad de conversión (multiplicar/dividir por 1,000,000) al leer/escribir
- Etiqueta ambigua sin indicar claramente la unidad
- Posible fuente de errores en cálculos

### Después de la Actualización

✅ **Correcto**: El campo ahora usa COP reales:

```python
# ✅ DESPUÉS (en COP reales)
self.inpPatrimonio = QDoubleSpinBox()
self.inpPatrimonio.setDecimals(2)
self.inpPatrimonio.setMaximum(1_000_000_000_000.00)   # 1 billón COP
self.inpPatrimonio.setMinimum(0.00)
self.inpPatrimonio.setSingleStep(1_000_000.00)        # pasos de $1M COP
self.inpPatrimonio.setValue(50_000_000_000.00)        # 50 mil millones COP
self.inpPatrimonio.setSuffix(" COP")
layout.addRow("Patrimonio Técnico Vigente (COP):", self.inpPatrimonio)
```

**Ventajas:**
- ✅ Claridad: El valor es exactamente lo que se ve (COP reales)
- ✅ Sin conversiones: No hay multiplicación/división por 1,000,000
- ✅ Etiqueta explícita: "(COP)" indica la unidad claramente
- ✅ Precisión: 2 decimales para máxima exactitud
- ✅ Consistencia: Mismo formato que TRM y otros valores monetarios

## Cambios Implementados

### 1. Widget de Patrimonio (UI)

**Archivo**: `src/views/settings_view.py` → `_create_parametros_generales()`

#### Configuración del QDoubleSpinBox

| Propiedad | Antes (Millones) | Después (COP Reales) |
|-----------|------------------|----------------------|
| **Valor Default** | 50,000 mill | 50,000,000,000.00 COP |
| **Mínimo** | 0 mill | 0.00 COP |
| **Máximo** | 1,000,000 mill | 1,000,000,000,000.00 COP |
| **Step** | N/A | 1,000,000.00 COP (1 millón) |
| **Decimales** | 2 | 2 |
| **Sufijo** | " mill COP" | " COP" |
| **Separador miles** | ✅ | ✅ |
| **Etiqueta** | "Patrimonio Técnico Vigente:" | "Patrimonio Técnico Vigente (COP):" |

#### Código Actualizado

```python
# Patrimonio Técnico Vigente (COP reales, no millones)
self.inpPatrimonio = QDoubleSpinBox()
self.inpPatrimonio.setDecimals(2)
self.inpPatrimonio.setMaximum(1_000_000_000_000.00)  # 1 billón COP
self.inpPatrimonio.setMinimum(0.00)
self.inpPatrimonio.setSingleStep(1_000_000.00)       # pasos de $1M COP
self.inpPatrimonio.setValue(50_000_000_000.00)       # Default: 50 mil millones COP
self.inpPatrimonio.setSuffix(" COP")
self.inpPatrimonio.setGroupSeparatorShown(True)
layout.addRow("Patrimonio Técnico Vigente (COP):", self.inpPatrimonio)
```

### 2. Métodos de Acceso (Vista)

**Archivo**: `src/views/settings_view.py`

#### load_parametros_generales()

**Antes:**
```python
def load_parametros_generales(self, patrimonio: float, trm: float) -> None:
    """
    Args:
        patrimonio: Patrimonio técnico en millones de COP  # ❌ Millones
    """
    self.inpPatrimonio.setValue(patrimonio)
```

**Después:**
```python
def load_parametros_generales(self, patrimonio_cop: float, trm: float) -> None:
    """
    Args:
        patrimonio_cop: Patrimonio técnico en COP (valor real, no millones)  # ✅ COP reales
    """
    self.inpPatrimonio.setValue(patrimonio_cop)
    print(f"[SettingsView] Parametros generales cargados: Patrimonio={patrimonio_cop:,.2f} COP, TRM={trm}")
```

#### get_parametros_generales()

**Antes:**
```python
def get_parametros_generales(self) -> Dict[str, float]:
    """
    Returns:
        Diccionario con patrimonio y TRM  # ❌ Nombre ambiguo
    """
    return {
        "patrimonio": self.inpPatrimonio.value(),  # ❌ ¿Millones o COP?
        "trm": self.inpTRM.value()
    }
```

**Después:**
```python
def get_parametros_generales(self) -> Dict[str, float]:
    """
    Returns:
        Diccionario con patrimonio_cop (valor en COP, no millones) y TRM  # ✅ Explícito
    """
    return {
        "patrimonio_cop": self.inpPatrimonio.value(),  # ✅ COP reales
        "trm": self.inpTRM.value()
    }
```

### 3. Referencias en Otros Módulos

#### ForwardView - show_basic_info()

**Archivo**: `src/views/forward_view.py`

```python
def show_basic_info(self, patrimonio: float, trm: float,
                    corte_415: Optional[date], estado_415: str) -> None:
    """
    Args:
        patrimonio: Patrimonio técnico en COP  # ✅ Ya estaba correcto
    """
    # Formatear para display (sin alterar el dato)
    self.lblPatrimonio.setText(f"$ {patrimonio:,.2f}")  # ✅ Sin conversión
```

**Estado**: ✅ **Ya estaba correcto** - No requiere cambios. El método espera COP reales y solo formatea para visualización.

#### ForwardController - load_415()

**Archivo**: `src/controllers/forward_controller.py`

```python
# Valores mock actuales
self._view.show_basic_info(
    patrimonio=0.0,  # Mock value en COP
    trm=4250.0,
    corte_415=None,
    estado_415="valido"
)
```

**Estado**: ✅ **Valores mock en COP** - Los valores 0.0 son temporales y ya están en COP reales (aunque sean 0). Cuando se implemente la integración con SettingsView, los valores vendrán directamente en COP reales sin necesidad de conversión.

## Migración de Datos

### Si se Carga desde Archivo Antiguo (en Millones)

Si existe una configuración guardada en formato antiguo (millones), realizar conversión **una sola vez** al leer:

```python
# Ejemplo: Al cargar config antigua
def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """Carga configuración desde archivo."""
    config = json.load(open(file_path))
    
    # Detectar si el valor está en millones (formato antiguo)
    if "patrimonio_millones" in config:
        # Convertir de millones a COP reales
        patrimonio_cop = config["patrimonio_millones"] * 1_000_000.0
        print(f"[Config] Convirtiendo {config['patrimonio_millones']:,.0f} mill → {patrimonio_cop:,.2f} COP")
    elif "patrimonio" in config and config["patrimonio"] < 1_000_000:
        # Si el valor es menor a 1 millón, probablemente está en millones
        patrimonio_cop = config["patrimonio"] * 1_000_000.0
        print(f"[Config] Convirtiendo {config['patrimonio']:,.0f} mill → {patrimonio_cop:,.2f} COP")
    else:
        # Ya está en COP reales
        patrimonio_cop = config.get("patrimonio_cop", 50_000_000_000.00)
    
    return {
        "patrimonio_cop": patrimonio_cop,
        "trm": config.get("trm", 4200.50)
    }
```

**Importante**: Convertir **solo una vez** al leer. Guardar y trabajar en adelante **solo en COP reales**.

## Integración con Controller (Ejemplo)

### SettingsController (si se implementa)

```python
class SettingsController:
    def __init__(self, view: SettingsView, model: ConfigModel):
        self._view = view
        self._model = model
    
    def load_initial_values(self):
        """Carga valores iniciales desde el modelo."""
        # Obtener valores del modelo (ya en COP reales)
        patrimonio_cop = self._model.get_patrimonio_cop()  # COP reales
        trm = self._model.get_trm()
        
        # Cargar en la vista (sin conversión)
        self._view.load_parametros_generales(
            patrimonio_cop=patrimonio_cop,  # Ya en COP
            trm=trm
        )
    
    def save_values(self):
        """Guarda valores desde la vista al modelo."""
        # Obtener valores de la vista (ya en COP reales)
        params = self._view.get_parametros_generales()
        
        # Guardar en el modelo (sin conversión)
        self._model.set_patrimonio_cop(params["patrimonio_cop"])  # Ya en COP
        self._model.set_trm(params["trm"])
```

**Sin Conversiones**: El flujo completo maneja COP reales sin multiplicar/dividir por 1,000,000.

## Ejemplo de Uso

### Cargar Valor

```python
# Cargar 75 mil millones de COP
settings_view.load_parametros_generales(
    patrimonio_cop=75_000_000_000.00,  # COP reales
    trm=4250.75
)
```

### Obtener Valor

```python
# Obtener valores actuales
params = settings_view.get_parametros_generales()

# params["patrimonio_cop"] = 75_000_000_000.00 (COP reales)
# params["trm"] = 4250.75
```

### Visualización

```python
# Formatear para mostrar en UI
patrimonio_cop = 75_000_000_000.00
label.setText(f"Patrimonio: $ {patrimonio_cop:,.2f} COP")

# Resultado: "Patrimonio: $ 75,000,000,000.00 COP"
```

## Tests Ejecutados

### Test 1: Configuración del Widget
```
[OK] Valor default: 50,000,000,000.00 COP (50 mil millones)
[OK] Sufijo correcto: ' COP'
[OK] Maximo: 1,000,000,000,000.00 COP (1 billon)
[OK] Minimo: 0.00 COP
[OK] Step: 1,000,000.00 COP (1 millon)
[OK] Decimales: 2
```

### Test 2: NO Usa Millones
```
[OK] Sufijo NO contiene 'mill'
[OK] Valor default NO es 50,000 (millones)
[OK] Valor default ES 50,000,000,000 (COP reales)
```

### Test 3: Métodos de Acceso
```
[OK] Clave: 'patrimonio_cop'
[OK] Valor: 50,000,000,000.00 COP
```

### Test 4: Load/Get
```
[OK] load_parametros_generales() actualiza correctamente
[OK] get_parametros_generales() retorna valor correcto
```

### Test 5: Valores Extremos
```
[OK] Acepta valor minimo: 0.00 COP
[OK] Acepta valor maximo: 1,000,000,000,000.00 COP
[OK] Acepta valores intermedios: 250,500,750,123.45 COP
```

## Comparación: Antes vs. Después

| Aspecto | Antes (Millones) | Después (COP Reales) |
|---------|------------------|----------------------|
| **Valor Default** | 50,000 mill | 50,000,000,000.00 COP |
| **Unidad Display** | " mill COP" | " COP" |
| **Etiqueta** | Ambigua | Explícita "(COP)" |
| **Conversiones** | ✗ Necesarias (×1e6) | ✓ No necesarias |
| **Precisión** | 2 decimales (millones) | 2 decimales (COP) |
| **Claridad** | Media | Alta |
| **Riesgo de error** | Medio | Bajo |
| **Key en dict** | "patrimonio" | "patrimonio_cop" |

## Ventajas del Cambio

### 1. Claridad ✅
- El valor es exactamente lo que se ve en pantalla
- No hay ambigüedad sobre la unidad
- Etiqueta explícita: "(COP)"

### 2. Sin Conversiones ✅
- No se necesita multiplicar/dividir por 1,000,000
- Menos código, menos errores
- Flujo directo: Vista → Modelo → Vista

### 3. Consistencia ✅
- Mismo formato que TRM y otros valores monetarios
- Todos los valores en COP reales
- Formateo uniforme con separadores de miles

### 4. Mantenibilidad ✅
- Código más simple y legible
- Documentación clara en tipos y nombres
- Menos posibilidad de confusión futura

## Criterios de Aceptación Cumplidos

### ✅ UI
- [x] Campo se llama "Patrimonio Técnico Vigente (COP)"
- [x] Input permite valores reales en COP con 2 decimales
- [x] Sin escalado a millones
- [x] Sufijo: " COP"
- [x] Separadores de miles habilitados

### ✅ Modelo/Controller
- [x] Valor se guarda en COP reales
- [x] No hay división/multiplicación por 1,000,000
- [x] Nombre de variable explícito: `patrimonio_cop`

### ✅ Consumo en Otros Módulos
- [x] ForwardView.show_basic_info() ya esperaba COP reales
- [x] No hay suposiciones de millones en código existente
- [x] Visualización usa formateo sin alterar datos

### ✅ Compatibilidad
- [x] No se rompe lógica existente
- [x] TRM, normativos, líneas de crédito funcionan igual
- [x] Migración de datos documentada

## Archivos Modificados

**Actualizados:**
1. ✅ `src/views/settings_view.py`
   - `_create_parametros_generales()`: Widget actualizado
   - `load_parametros_generales()`: Parámetro renombrado a `patrimonio_cop`
   - `get_parametros_generales()`: Key cambiada a `"patrimonio_cop"`

**Sin Cambios Necesarios:**
2. ✅ `src/views/forward_view.py`
   - `show_basic_info()`: Ya esperaba COP reales
3. ✅ `src/controllers/forward_controller.py`
   - Valores mock ya están en COP (0.0)

**Nuevos:**
4. ✅ `docs/PATRIMONIO_COP_REALES.md` - Esta documentación

## Conclusión

La actualización para expresar el Patrimonio Técnico en COP reales (en lugar de millones) ha sido exitosa, cumpliendo con todos los criterios de aceptación:

- ✅ UI actualizada con etiqueta clara "(COP)"
- ✅ Widget configurado para COP reales (0 a 1 billón)
- ✅ Métodos usan `patrimonio_cop` explícito
- ✅ Sin conversiones por 1,000,000
- ✅ Compatibilidad con código existente preservada
- ✅ Migración de datos documentada

### Impacto del Cambio

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **Claridad** | Media | Alta | ⬆️ |
| **Conversiones** | Necesarias | No necesarias | ⬆️ |
| **Riesgo error** | Medio | Bajo | ⬆️ |
| **Mantenibilidad** | Media | Alta | ⬆️ |

✅ **Patrimonio Técnico ahora en COP reales, sin ambigüedad**

