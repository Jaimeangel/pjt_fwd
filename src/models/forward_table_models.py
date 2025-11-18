"""
Modelos de tabla Qt para el módulo Forward.
Implementa QAbstractTableModel para operaciones vigentes y simulaciones.
"""

from typing import Any, List, Dict, Optional
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from datetime import date


class OperationsTableModel(QAbstractTableModel):
    """
    Modelo de tabla Qt para operaciones vigentes (solo lectura).
    
    Responsabilidades:
    - Presentar operaciones vigentes del 415 en QTableView
    - Modo solo lectura (no editable)
    - Formatear datos para visualización
    
    Columnas esperadas:
    - ID Operación
    - Fecha Inicio
    - Fecha Vencimiento
    - Punta Cliente
    - Nominal USD
    - Tasa Forward
    - Fair Value
    - Derecho
    - Obligación
    """
    
    # Definición de columnas
    COLUMNS = [
        "ID Operación",
        "Fecha Inicio",
        "Fecha Vencimiento",
        "Punta Cliente",
        "Nominal USD",
        "Tasa Forward",
        "Fair Value",
        "Derecho",
        "Obligación"
    ]
    
    # Mapeo de columnas a campos del diccionario
    COLUMN_KEYS = [
        "id_operacion",
        "fecha_inicio",
        "fecha_vencimiento",
        "punta_cliente",
        "nominal_usd",
        "tasa_forward",
        "fair_value",
        "derecho",
        "obligacion"
    ]
    
    def __init__(self, parent=None):
        """
        Inicializa el modelo de tabla de operaciones.
        
        Args:
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        self._data: List[Dict[str, Any]] = []
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de filas (operaciones).
        
        Args:
            parent: Índice padre (no usado en tablas planas)
            
        Returns:
            Cantidad de operaciones vigentes
        """
        pass
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de columnas.
        
        Args:
            parent: Índice padre (no usado en tablas planas)
            
        Returns:
            Cantidad de columnas (len(COLUMNS))
        """
        pass
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Retorna el dato para una celda específica.
        
        Roles soportados:
        - Qt.DisplayRole: Texto formateado para mostrar
        - Qt.TextAlignmentRole: Alineación (números a la derecha)
        - Qt.ToolTipRole: Tooltip con información adicional
        
        Formateo:
        - Fechas: formato "dd/MM/yyyy"
        - Números: formato con separadores de miles y decimales
        - Punta: "Compra" o "Venta" capitalizado
        
        Args:
            index: Índice de la celda (fila, columna)
            role: Rol de los datos (DisplayRole, etc.)
            
        Returns:
            Dato formateado según el rol, None si índice inválido
        """
        pass
    
    def headerData(self, section: int, orientation: Qt.Orientation, 
                   role: int = Qt.DisplayRole) -> Any:
        """
        Retorna datos del header (encabezados de columnas/filas).
        
        Args:
            section: Número de columna (horizontal) o fila (vertical)
            orientation: Qt.Horizontal o Qt.Vertical
            role: Rol de los datos
            
        Returns:
            - Horizontal + DisplayRole: Nombre de columna
            - Vertical + DisplayRole: Número de fila (1-based)
            - None para otros roles
        """
        pass
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Retorna flags de la celda (capacidades).
        
        Solo lectura: Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        Args:
            index: Índice de la celda
            
        Returns:
            Flags indicando que es seleccionable pero no editable
        """
        pass
    
    def set_operations(self, operations: List[Dict[str, Any]]) -> None:
        """
        Establece las operaciones a mostrar.
        
        Args:
            operations: Lista de operaciones vigentes
            
        Side effects:
            - Actualiza _data
            - Emite señales beginResetModel/endResetModel
        """
        pass
    
    def clear(self) -> None:
        """
        Limpia todas las operaciones.
        
        Side effects:
            - Vacía _data
            - Emite señales de reset
        """
        pass
    
    def get_operation_at_row(self, row: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la operación en una fila específica.
        
        Args:
            row: Índice de fila (0-based)
            
        Returns:
            Diccionario con datos de la operación o None si índice inválido
        """
        pass


class SimulationsTableModel(QAbstractTableModel):
    """
    Modelo de tabla Qt para simulaciones (editable).
    
    Responsabilidades:
    - Presentar simulaciones en QTableView
    - Permitir edición de celdas
    - Validar datos editados
    - Sincronizar con SimulationsModel
    
    Columnas esperadas:
    - NIT
    - Punta Cliente
    - Punta Empresa
    - Nominal USD
    - Fecha Simulación
    - Fecha Vencimiento
    - Spot
    - Puntos
    - Tasa Forward
    - Tasa IBR
    - Derecho
    - Obligación
    - Fair Value
    """
    
    # Definición de columnas
    COLUMNS = [
        "NIT",
        "Punta Cliente",
        "Punta BNP",
        "Nominal USD",
        "Fecha Sim",
        "Fecha Venc",
        "Spot",
        "Puntos",
        "Tasa Fwd",
        "Tasa IBR",
        "Derecho",
        "Obligación",
        "Fair Value"
    ]
    
    # Mapeo de columnas a campos
    COLUMN_KEYS = [
        "nit",
        "punta_cliente",
        "punta_empresa",
        "nominal_usd",
        "fecha_sim",
        "fecha_venc",
        "spot",
        "puntos",
        "tasa_fwd",
        "tasa_ibr",
        "derecho",
        "obligacion",
        "fair_value"
    ]
    
    # Columnas editables (True) vs calculadas (False)
    EDITABLE_COLUMNS = [
        True,   # NIT
        True,   # Punta Cliente
        False,  # Punta Empresa (calculado automáticamente)
        True,   # Nominal USD
        True,   # Fecha Sim
        True,   # Fecha Venc
        True,   # Spot
        False,  # Puntos (calculado)
        False,  # Tasa Fwd (calculado)
        True,   # Tasa IBR
        False,  # Derecho (calculado)
        False,  # Obligación (calculado)
        False   # Fair Value (calculado)
    ]
    
    def __init__(self, simulations_model=None, parent=None):
        """
        Inicializa el modelo de tabla de simulaciones.
        
        Args:
            simulations_model: Instancia de SimulationsModel (modelo de datos)
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        self._simulations_model = simulations_model
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de filas (simulaciones).
        
        Args:
            parent: Índice padre (no usado)
            
        Returns:
            Cantidad de simulaciones
        """
        pass
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de columnas.
        
        Args:
            parent: Índice padre (no usado)
            
        Returns:
            Cantidad de columnas (len(COLUMNS))
        """
        pass
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Retorna el dato para una celda específica.
        
        Roles soportados:
        - Qt.DisplayRole: Texto formateado
        - Qt.EditRole: Valor crudo para edición
        - Qt.BackgroundRole: Color de fondo (amarillo si incompleta)
        - Qt.ForegroundRole: Color de texto
        - Qt.TextAlignmentRole: Alineación
        - Qt.ToolTipRole: Tooltip con errores de validación
        
        Args:
            index: Índice de la celda
            role: Rol de los datos
            
        Returns:
            Dato según el rol, None si índice inválido
        """
        pass
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """
        Establece el valor de una celda (edición).
        
        Validaciones:
        - NIT: no vacío
        - Nominal USD: float > 0
        - Fechas: formato válido
        - Spot: float > 0
        - Tasa IBR: float >= 0
        - Punta Cliente: 'compra' o 'venta'
        
        Side effects:
        - Actualiza SimulationsModel
        - Emite dataChanged
        - Si cambio afecta cálculos, recalcula y actualiza otras columnas
        
        Args:
            index: Índice de la celda
            value: Nuevo valor
            role: Rol (típicamente EditRole)
            
        Returns:
            True si se actualizó correctamente, False si validación falla
        """
        pass
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """
        Retorna datos del header.
        
        Args:
            section: Número de columna/fila
            orientation: Horizontal o Vertical
            role: Rol de los datos
            
        Returns:
            Nombre de columna o número de fila
        """
        pass
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Retorna flags de la celda.
        
        Columnas editables: Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        Columnas calculadas: Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        Args:
            index: Índice de la celda
            
        Returns:
            Flags según si la columna es editable
        """
        pass
    
    def set_simulations_model(self, simulations_model) -> None:
        """
        Establece el modelo de datos de simulaciones.
        
        Args:
            simulations_model: Instancia de SimulationsModel
            
        Side effects:
            - Actualiza _simulations_model
            - Emite reset
        """
        pass
    
    def refresh(self) -> None:
        """
        Refresca toda la tabla desde el modelo de datos.
        
        Side effects:
            - Emite beginResetModel/endResetModel
        """
        pass
    
    def get_simulation_at_row(self, row: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la simulación en una fila específica.
        
        Args:
            row: Índice de fila (0-based)
            
        Returns:
            Diccionario con datos de la simulación o None
        """
        pass
    
    def insert_row(self, row: int = -1) -> bool:
        """
        Inserta una nueva fila vacía.
        
        Args:
            row: Posición donde insertar (-1 = al final)
            
        Returns:
            True si se insertó correctamente
            
        Side effects:
            - Llama a SimulationsModel.add()
            - Emite beginInsertRows/endInsertRows
        """
        pass
    
    def remove_rows(self, rows: List[int]) -> bool:
        """
        Elimina múltiples filas.
        
        Args:
            rows: Lista de índices de filas a eliminar
            
        Returns:
            True si se eliminó al menos una
            
        Side effects:
            - Llama a SimulationsModel.remove()
            - Emite beginRemoveRows/endRemoveRows
        """
        pass

