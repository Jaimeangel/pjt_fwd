"""
Modelo de tabla Qt para operaciones vigentes (solo lectura).
"""

from typing import Any, List, Dict, Optional
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


class OperationsTableModel(QAbstractTableModel):
    """
    Modelo de tabla Qt para operaciones vigentes (solo lectura).
    
    Responsabilidades:
    - Presentar operaciones vigentes del 415 en QTableView
    - Modo solo lectura (no editable)
    - Formatear datos para visualización
    """
    
    # Headers de columnas
    HEADERS = [
        "ID",
        "NIT",
        "Cliente",
        "Divisa",
        "Nominal",
        "Vencimiento",
        "Exposición"
    ]
    
    def __init__(self, parent=None):
        """
        Inicializa el modelo de tabla de operaciones.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Datos dummy para testing
        self._rows = [
            {
                "id": "FWD-2025-001",
                "nit": "123456789",
                "cliente": "Cliente Ejemplo S.A.",
                "divisa": "USD",
                "nominal": 100000.0,
                "vencimiento": "2025-12-15",
                "exposicion": 420500000.0
            },
            {
                "id": "FWD-2025-002",
                "nit": "987654321",
                "cliente": "Corporación ABC Ltda.",
                "divisa": "USD",
                "nominal": 250000.0,
                "vencimiento": "2025-11-30",
                "exposicion": 1051250000.0
            },
            {
                "id": "FWD-2025-003",
                "nit": "555444333",
                "cliente": "Empresa XYZ S.A.S.",
                "divisa": "USD",
                "nominal": 75000.0,
                "vencimiento": "2026-01-20",
                "exposicion": 315375000.0
            },
            {
                "id": "FWD-2025-004",
                "nit": "123456789",
                "cliente": "Cliente Ejemplo S.A.",
                "divisa": "USD",
                "nominal": 150000.0,
                "vencimiento": "2025-12-31",
                "exposicion": 630750000.0
            },
            {
                "id": "FWD-2025-005",
                "nit": "987654321",
                "cliente": "Corporación ABC Ltda.",
                "divisa": "USD",
                "nominal": 50000.0,
                "vencimiento": "2026-02-10",
                "exposicion": 210250000.0
            }
        ]
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de filas (operaciones).
        
        Args:
            parent: Índice padre
            
        Returns:
            Cantidad de operaciones
        """
        if parent.isValid():
            return 0
        return len(self._rows)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de columnas.
        
        Args:
            parent: Índice padre
            
        Returns:
            Cantidad de columnas
        """
        if parent.isValid():
            return 0
        return len(self.HEADERS)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Retorna el dato para una celda específica.
        
        Args:
            index: Índice de la celda
            role: Rol de los datos
            
        Returns:
            Dato formateado según el rol
        """
        if not index.isValid():
            return None
        
        if index.row() >= len(self._rows) or index.row() < 0:
            return None
        
        if index.column() >= len(self.HEADERS) or index.column() < 0:
            return None
        
        row_data = self._rows[index.row()]
        
        # DisplayRole: texto a mostrar
        if role == Qt.DisplayRole:
            col = index.column()
            
            if col == 0:  # ID
                return row_data.get("id", "")
            elif col == 1:  # NIT
                return row_data.get("nit", "")
            elif col == 2:  # Cliente
                return row_data.get("cliente", "")
            elif col == 3:  # Divisa
                return row_data.get("divisa", "")
            elif col == 4:  # Nominal
                nominal = row_data.get("nominal", 0.0)
                return f"{nominal:,.2f}"
            elif col == 5:  # Vencimiento
                return row_data.get("vencimiento", "")
            elif col == 6:  # Exposición
                exposicion = row_data.get("exposicion", 0.0)
                return f"$ {exposicion:,.2f}"
        
        # TextAlignmentRole: alineación de texto
        elif role == Qt.TextAlignmentRole:
            col = index.column()
            # Alinear números a la derecha
            if col in [4, 6]:  # Nominal, Exposición
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        
        return None
    
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
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if 0 <= section < len(self.HEADERS):
                    return self.HEADERS[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)  # Número de fila (1-based)
        
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Retorna flags de la celda (solo lectura).
        
        Args:
            index: Índice de la celda
            
        Returns:
            Flags indicando seleccionable pero no editable
        """
        if not index.isValid():
            return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def set_operations(self, operations: List[Dict[str, Any]]) -> None:
        """
        Establece las operaciones a mostrar.
        
        Args:
            operations: Lista de operaciones vigentes
        """
        self.beginResetModel()
        self._rows = operations if operations else []
        self.endResetModel()
    
    def get_operation_at_row(self, row: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la operación en una fila específica.
        
        Args:
            row: Índice de fila (0-based)
            
        Returns:
            Diccionario con datos de la operación o None
        """
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None
