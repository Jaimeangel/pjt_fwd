"""
Controlador para el módulo Forward.
"""

from typing import List
from datetime import date


class ForwardController:
    """
    Controlador del módulo Forward.
    
    Responsabilidades:
    - Coordinar entre Model, View y Services
    - Procesar acciones del usuario
    - Validar datos antes de enviar al modelo
    - Actualizar la vista con cambios del modelo
    """
    
    def __init__(self, data_model=None, simulations_model=None, view=None,
                 pricing_service=None, exposure_service=None, signals=None,
                 simulations_table_model=None, operations_table_model=None, client_service=None,
                 simulation_processor=None):
        """
        Inicializa el controlador Forward.
        
        Args:
            data_model: Instancia de ForwardDataModel
            simulations_model: Instancia de SimulationsModel
            view: Instancia de ForwardView
            pricing_service: Instancia de ForwardPricingService
            exposure_service: Instancia de ExposureService
            signals: Instancia de AppSignals (señales globales)
            simulations_table_model: Instancia de SimulationsTableModel (Qt)
            operations_table_model: Instancia de OperationsTableModel (Qt)
            client_service: Instancia de ClientService
            simulation_processor: Instancia de ForwardSimulationProcessor
        """
        self._data_model = data_model
        self._simulations_model = simulations_model
        self._view = view
        self._pricing_service = pricing_service
        self._exposure_service = exposure_service
        self._signals = signals
        self._simulations_table_model = simulations_table_model
        self._operations_table_model = operations_table_model
        self._client_service = client_service
        
        # Procesador de simulaciones
        if simulation_processor:
            self._simulation_processor = simulation_processor
        else:
            # Crear instancia por defecto si no se proporciona
            from src.services.forward_simulation_processor import ForwardSimulationProcessor
            self._simulation_processor = ForwardSimulationProcessor()
        
        # Estado actual
        self._current_client_nit = None
        self._current_outstanding = 100000.0  # Mock: $100,000 COP
        
        # Conectar señales de la vista a métodos del controller
        self._connect_view_signals()
    
    def _connect_view_signals(self):
        """Conecta las señales de la vista a los métodos del controlador."""
        if self._view:
            self._view.load_415_requested.connect(self.load_415)
            self._view.load_ibr_requested.connect(self.load_ibr)
            self._view.client_selected.connect(self.select_client)
            self._view.add_simulation_requested.connect(self.add_simulation)
            self._view.delete_simulations_requested.connect(self.delete_simulations)
            self._view.simulate_selected_requested.connect(self.simulate_selected_row)
            self._view.save_simulations_requested.connect(self.save_simulations)
            print("[ForwardController] Señales de vista conectadas")
        
        # Configurar el resolver de IBR en el modelo de simulaciones
        if self._simulations_table_model and self._data_model:
            self._simulations_table_model.set_ibr_resolver(
                lambda dias: self._data_model.get_ibr_for_days(dias)
            )
            print("[ForwardController] IBR resolver configurado en modelo de simulaciones")
    
    def load_415(self, file_path: str) -> None:
        """
        Carga el archivo 415 con validación básica.
        
        Args:
            file_path: Ruta al archivo CSV formato 415
        """
        print(f"\n[ForwardController] load_415: {file_path}")
        
        try:
            from pathlib import Path
            import hashlib
            
            file_obj = Path(file_path)
            
            # 1. Validar que el archivo existe
            if not file_obj.exists():
                print(f"   ❌ Error: El archivo no existe")
                self._handle_invalid_415(file_path, "Archivo no encontrado")
                return
            
            # 2. Validar extensión .csv
            if file_obj.suffix.lower() != '.csv':
                print(f"   ❌ Error: Extensión inválida ({file_obj.suffix}), se esperaba .csv")
                self._handle_invalid_415(file_path, "Extensión inválida")
                return
            
            # 3. Calcular tamaño en KB
            tamano_bytes = file_obj.stat().st_size
            tamano_kb = tamano_bytes / 1024
            
            print(f"   ✓ Archivo encontrado: {file_obj.name}")
            print(f"   ✓ Tamaño: {tamano_kb:.2f} KB")
            
            # 4. Leer primeras líneas para validar formato
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                primera_linea = f.readline().strip()
                
                # Verificar que hay contenido
                if not primera_linea:
                    print(f"   ❌ Error: Archivo vacío")
                    self._handle_invalid_415(file_path, "Archivo vacío")
                    return
                
                # Verificar que usa separador ;
                if ';' not in primera_linea:
                    print(f"   ❌ Error: Separador ';' no encontrado en la cabecera")
                    self._handle_invalid_415(file_path, "Separador inválido")
                    return
                
                # Verificar que hay headers
                headers = primera_linea.split(';')
                if len(headers) < 3:
                    print(f"   ❌ Error: Cabecera incompleta (menos de 3 columnas)")
                    self._handle_invalid_415(file_path, "Cabecera incompleta")
                    return
                
                print(f"   ✓ Separador ';' detectado")
                print(f"   ✓ Headers detectados: {len(headers)} columnas")
                print(f"   ✓ Primeras columnas: {', '.join(headers[:3])}")
            
            # 5. Calcular hash simple (md5 del path + tamaño)
            hash_input = f"{file_path}_{tamano_bytes}"
            hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
            
            print(f"   ✓ Hash: {hash_value}")
            
            # 6. Guardar metadatos en el modelo
            if self._data_model:
                self._data_model.set_415_metadata(
                    ruta=str(file_path),
                    nombre=file_obj.name,
                    tamano_kb=tamano_kb,
                    hash_value=hash_value,
                    estado="valido"
                )
                print(f"   ✓ Metadatos guardados en ForwardDataModel")
            
            # 7. PROCESAR OPERACIONES VIGENTES
            print(f"\n   📊 Procesando operaciones vigentes...")
            self._process_415_operations(file_path)
            
            # 8. Emitir señal de éxito
            if self._signals:
                self._signals.forward_415_loaded.emit(date.today(), "valido")
            
            # 9. Actualizar vista
            if self._view:
                # Actualizar header
                self._view.show_basic_info(
                    patrimonio=0.0,  # Mock
                    trm=4250.0,      # Mock
                    corte_415=None,   # Sin parsear todavía
                    estado_415="valido"
                )
                
                # Actualizar banner
                metadata = self._data_model.get_415_metadata()
                self._view.update_banner_415(
                    nombre=metadata['nombre'],
                    tamano_kb=metadata['tamano_kb'],
                    fecha_cargue=metadata['timestamp'],
                    estado=metadata['estado']
                )
                
                self._view.notify(
                    f"Archivo 415 cargado: {file_obj.name} ({tamano_kb:.2f} KB)",
                    "info"
                )
            
            print(f"   ✅ Archivo 415 validado y procesado exitosamente")
            
        except Exception as e:
            print(f"   ❌ Error al cargar 415: {e}")
            import traceback
            traceback.print_exc()
            self._handle_invalid_415(file_path, f"Error: {str(e)}")
    
    def _handle_invalid_415(self, file_path: str, razon: str) -> None:
        """
        Maneja un archivo 415 inválido.
        
        Args:
            file_path: Ruta del archivo
            razon: Razón de invalidez
        """
        from pathlib import Path
        
        file_obj = Path(file_path)
        
        # Guardar metadatos con estado inválido
        if self._data_model:
            self._data_model.set_415_metadata(
                ruta=str(file_path),
                nombre=file_obj.name if file_obj.exists() else "archivo_invalido.csv",
                tamano_kb=0.0,
                hash_value="",
                estado="invalido"
            )
        
        # Emitir señal de error
        if self._signals:
            self._signals.forward_415_loaded.emit(None, "invalido")
        
        # Actualizar vista
        if self._view:
            # Actualizar header
            self._view.show_basic_info(
                patrimonio=0.0,
                trm=0.0,
                corte_415=None,
                estado_415="invalido"
            )
            
            # Actualizar banner si el archivo existe
            if file_obj.exists() and self._data_model:
                metadata = self._data_model.get_415_metadata()
                self._view.update_banner_415(
                    nombre=metadata['nombre'],
                    tamano_kb=metadata['tamano_kb'],
                    fecha_cargue=metadata['timestamp'],
                    estado=metadata['estado']
                )
            
            self._view.notify(
                f"Archivo 415 inválido: {razon}",
                "error"
            )
    
    def _process_415_operations(self, file_path: str) -> None:
        """
        Procesa las operaciones del archivo 415.
        
        1. Carga operaciones vigentes con Csv415Loader
        2. Calcula columnas derivadas con Forward415Processor
        3. Agrupa por NIT y calcula exposición crediticia
        4. Guarda resultados en ForwardDataModel
        
        Args:
            file_path: Ruta al archivo CSV 415
        """
        try:
            # Importar servicios necesarios
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "data"))
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from data.csv_415_loader import Csv415Loader
            from services.forward_415_processor import Forward415Processor
            import numpy as np
            
            # 1. Cargar operaciones vigentes
            print(f"      [1/3] Cargando operaciones vigentes...")
            loader = Csv415Loader()
            df_operations = loader.load_operations_from_415(file_path)
            
            if df_operations.empty:
                print(f"      ⚠️  No hay operaciones vigentes en el archivo")
                return
            
            print(f"      ✓ {len(df_operations)} operaciones vigentes cargadas")
            
            # 2. Procesar columnas derivadas
            print(f"      [2/3] Calculando columnas derivadas...")
            processor = Forward415Processor()
            df_enriched = processor.process_operations(df_operations)
            
            # Guardar en el modelo
            if self._data_model:
                self._data_model.dataset_415 = df_enriched
                print(f"      ✓ Dataset guardado en ForwardDataModel")
            
            # 3. Calcular exposición crediticia por NIT
            print(f"      [3/3] Calculando exposición crediticia por cliente...")
            exposure_by_nit = self._calculate_credit_exposure_by_nit(df_enriched)
            
            # Guardar exposiciones y operaciones en el modelo
            if self._data_model:
                # Convertir DataFrame a lista de diccionarios para guardar
                operaciones_list = df_enriched.to_dict('records')
                self._data_model.set_datos_415(operaciones_list, exposure_by_nit)
                
                print(f"      ✓ Exposiciones calculadas para {len(exposure_by_nit)} clientes")
                
                # Mostrar resumen
                total_exposure = sum(exposure_by_nit.values())
                print(f"      ✓ Exposición total: $ {total_exposure:,.2f}")
                
                # Actualizar lista de clientes en la vista (usando NOMBRES)
                if self._view:
                    nombres_clientes = self._data_model.get_client_names()
                    self._view.set_client_list(nombres_clientes)
            
            print(f"      ✅ Procesamiento de operaciones completado")
            
        except Exception as e:
            print(f"      ❌ Error procesando operaciones: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_credit_exposure_by_nit(self, df: 'pd.DataFrame') -> dict:
        """
        Calcula la exposición crediticia por NIT.
        
        Fórmulas:
        - total_vne = sum(vne) por NIT
        - fc = primer fc del NIT
        - total_epfp = abs(total_vne * fc)
        - total_vr = sum(vr) por NIT
        - mgp = min(0.05 + 0.95 * exp(total_vr / (1.9 * total_epfp)), 1)
        - crp = max(total_vr - 0, 0)
        - exp_cred_total = 1.4 * (crp + (mgp * total_epfp))
        
        Args:
            df: DataFrame con operaciones enriquecidas
            
        Returns:
            Diccionario {nit: exp_cred_total}
        """
        import numpy as np
        
        exposure_by_nit = {}
        
        # Agrupar por NIT
        for nit in df['nit'].unique():
            try:
                # Filtrar operaciones del cliente
                ops_cliente = df[df['nit'] == nit]
                
                # Calcular total_vne (suma de vne, excluyendo nulos)
                vne_values = ops_cliente['vne'].dropna()
                total_vne = vne_values.sum() if len(vne_values) > 0 else 0.0
                
                # Obtener primer fc
                fc_values = ops_cliente['fc'].dropna()
                fc = fc_values.iloc[0] if len(fc_values) > 0 else 1.0
                
                # Calcular total_epfp = abs(total_vne * fc)
                total_epfp = abs(total_vne * fc)
                
                # Calcular total_vr (suma de vr)
                vr_values = ops_cliente['vr'].dropna()
                total_vr = vr_values.sum() if len(vr_values) > 0 else 0.0
                
                # Calcular MGP (Market Gap Provision)
                # mgp = min(0.05 + 0.95 * exp((total_vr - 0)/(1.9 * total_epfp)), 1)
                if total_epfp > 0:
                    try:
                        exponent = total_vr / (1.9 * total_epfp)
                        mgp = min(0.05 + 0.95 * np.exp(exponent), 1.0)
                    except (OverflowError, FloatingPointError):
                        # Si hay overflow, usar valor por defecto
                        mgp = 1.0
                else:
                    # Si total_epfp es 0, no hay exposición
                    mgp = 0.0
                
                # Calcular CRP (Credit Risk Premium)
                # crp = max(total_vr - 0, 0)
                crp = max(total_vr, 0.0)
                
                # Calcular exposición crediticia total
                # exp_cred_total = 1.4 * (crp + (mgp * total_epfp))
                exp_cred_total = 1.4 * (crp + (mgp * total_epfp))
                
                # Guardar en diccionario
                exposure_by_nit[nit] = exp_cred_total
                
                # Log detallado
                print(f"         NIT {nit}:")
                print(f"            Operaciones: {len(ops_cliente)}")
                print(f"            Total VNE: $ {total_vne:,.2f}")
                print(f"            FC: {fc:.6f}")
                print(f"            Total EPFp: $ {total_epfp:,.2f}")
                print(f"            Total VR: $ {total_vr:,.2f}")
                print(f"            MGP: {mgp:.6f}")
                print(f"            CRP: $ {crp:,.2f}")
                print(f"            → Exposición Crediticia: $ {exp_cred_total:,.2f}")
                
            except Exception as e:
                print(f"         ⚠️  Error calculando exposición para NIT {nit}: {e}")
                exposure_by_nit[nit] = 0.0
        
        return exposure_by_nit
    
    def load_ibr(self, file_path: str) -> None:
        """
        Carga el archivo IBR (curva de tasas).
        
        Args:
            file_path: Ruta al archivo CSV con la curva IBR
        """
        print(f"\n[ForwardController] load_ibr: {file_path}")
        
        try:
            from pathlib import Path
            from datetime import datetime
            import os
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "data"))
            from data.ibr_loader import load_ibr_csv, validate_ibr_curve
            
            file_obj = Path(file_path)
            
            # 1. Validar que el archivo existe
            if not file_obj.exists():
                print(f"   ❌ Error: El archivo no existe")
                if self._view:
                    self._view.notify(f"Archivo IBR no encontrado", "error")
                    self._view.update_ibr_status(None, "Inválido")
                return
            
            # 2. Validar extensión .csv
            if file_obj.suffix.lower() != '.csv':
                print(f"   ❌ Error: Extensión inválida ({file_obj.suffix}), se esperaba .csv")
                if self._view:
                    self._view.notify(f"Archivo IBR debe ser .csv", "error")
                    self._view.update_ibr_status(None, "Inválido")
                return
            
            print(f"   ✓ Archivo encontrado: {file_obj.name}")
            
            # 3. Cargar curva IBR
            print(f"   📊 Cargando curva IBR...")
            ibr_curve = load_ibr_csv(file_path)
            
            if not ibr_curve:
                print(f"   ❌ Error: Curva IBR vacía")
                if self._view:
                    self._view.notify(f"Archivo IBR vacío o inválido", "error")
                    self._view.update_ibr_status(file_path, "Inválido")
                return
            
            # 4. Validar curva
            if not validate_ibr_curve(ibr_curve):
                print(f"   ❌ Error: Curva IBR inválida")
                if self._view:
                    self._view.notify(f"Curva IBR contiene datos inválidos", "error")
                    self._view.update_ibr_status(file_path, "Inválido")
                return
            
            print(f"   ✓ Curva IBR cargada: {len(ibr_curve)} puntos")
            
            # Mostrar algunos puntos de muestra
            sample_points = sorted(ibr_curve.keys())[:5]
            for dias in sample_points:
                tasa_pct = ibr_curve[dias] * 100
                print(f"      {dias} días → {tasa_pct:.4f}%")
            
            # 5. Calcular metadatos del archivo
            tamano_kb = os.path.getsize(file_path) / 1024.0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nombre_archivo = file_obj.name
            
            # 6. Guardar en el modelo
            if self._data_model:
                self._data_model.set_ibr_curve(ibr_curve, file_path)
                self._data_model.set_ibr_metadata(nombre_archivo, tamano_kb, timestamp, "Cargado")
                print(f"   ✓ Curva IBR guardada en ForwardDataModel")
            
            # 7. Actualizar vista
            if self._view:
                # Actualizar banner con estado
                self._view.update_ibr_status(
                    file_path=file_path,
                    estado="Cargado",
                    tamano_kb=tamano_kb,
                    timestamp=timestamp
                )
                
                # Notificación
                self._view.notify(
                    f"Curva IBR cargada: {nombre_archivo} ({len(ibr_curve)} puntos)",
                    "info"
                )
            
            print(f"   ✅ Archivo IBR cargado exitosamente")
            
        except Exception as e:
            print(f"   ❌ Error al cargar IBR: {e}")
            import traceback
            traceback.print_exc()
            if self._view:
                self._view.notify(f"Error al cargar IBR: {str(e)}", "error")
                self._view.update_ibr_status(None, "Inválido")
    
    def select_client(self, nombre_o_nit: str) -> None:
        """
        Selecciona un cliente por nombre o NIT.
        
        Args:
            nombre_o_nit: Nombre de la contraparte o NIT del cliente
        """
        print(f"[ForwardController] select_client: {nombre_o_nit}")
        
        # Intentar obtener NIT desde el nombre
        nit = None
        if self._data_model:
            # Primero intentar como nombre
            nit = self._data_model.get_nit_by_name(nombre_o_nit)
            # Si no funciona, asumir que es NIT directamente
            if not nit:
                nit = nombre_o_nit
        else:
            nit = nombre_o_nit
        
        if not nit:
            print(f"   ⚠️  No se pudo determinar el NIT para: {nombre_o_nit}")
            # Limpiar vista
            if self._view:
                self._view.show_exposure(outstanding=0.0, total_con_simulacion=None, disponibilidad=None)
                if self._operations_table_model:
                    self._operations_table_model.set_operations([])
            return
        
        print(f"   → NIT determinado: {nit}")
        
        # Guardar cliente actual
        self._current_client_nit = nit
        
        # Actualizar cliente actual en el modelo de datos
        if self._data_model:
            nombre = self._data_model.get_nombre_by_nit(nit)
            self._data_model.set_current_client(nit, nombre)
        
        # Obtener límites del cliente usando ClientService (mock)
        if self._client_service:
            limits = self._client_service.get_client_limits(nit)
            
            print(f"   → Límites del cliente:")
            print(f"      Línea de crédito: $ {limits['linea_credito']:,.2f}")
            print(f"      Colchón interno: {limits['colchon_pct']:.1f}%")
            print(f"      Límite máximo: $ {limits['limite_max']:,.2f}")
            
            # Actualizar vista con límites
            if self._view:
                self._view.show_client_limits(
                    linea=limits['linea_credito'],
                    colchon_pct=limits['colchon_pct'],
                    limite_max=limits['limite_max']
                )
        
        # Obtener exposición crediticia del cliente (outstanding)
        outstanding = 0.0
        if self._data_model:
            outstanding = self._data_model.get_outstanding_por_nit(nit)
            if outstanding > 0:
                print(f"   → Outstanding del cliente: $ {outstanding:,.2f}")
            else:
                print(f"   → Sin operaciones vigentes para este cliente (Outstanding: $ 0.00)")
        
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
        
        # Cargar operaciones vigentes del cliente en la tabla
        if self._data_model and self._operations_table_model:
            operaciones = self._data_model.get_operaciones_por_nit(nit)
            print(f"   → Cargando {len(operaciones)} operaciones del cliente en la tabla")
            self._operations_table_model.set_operations(operaciones)
            
            # Actualizar vista de la tabla
            if self._view:
                self._view.set_operations_table(self._operations_table_model)
        
        # Emitir señal global
        if self._signals:
            self._signals.forward_client_changed.emit(nit)
    
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
    
    def delete_simulations(self, rows: List[int]) -> None:
        """
        Elimina múltiples filas de simulación.
        
        Args:
            rows: Lista de índices de filas a eliminar
        """
        print(f"[ForwardController] delete_simulations: rows={rows}")
        
        # Aquí iría: self._simulations_model.remove(rows)
        # Por ahora, eliminar directamente del modelo de tabla Qt
        if self._simulations_table_model and rows:
            success = self._simulations_table_model.remove_rows(rows)
            if success:
                print(f"   → {len(rows)} fila(s) eliminada(s) de la tabla")
        
        if self._signals:
            self._signals.forward_simulations_changed.emit()
    
    def simulate_selected_row(self) -> None:
        """
        Simula la exposición crediticia de la fila seleccionada.
        
        Recalcula la exposición total incorporando la operación simulada
        junto con las operaciones vigentes del cliente actual.
        """
        print("\n" + "="*60)
        print("[ForwardController] simulate_selected_row - INICIANDO")
        print("="*60)
        
        # 1) Validaciones
        nit = self._data_model.get_current_client_nit() if self._data_model else None
        if not nit:
            print("   ⚠️  No hay contraparte seleccionada")
            if self._view:
                self._view.notify("Seleccione primero una contraparte.", "warning")
            return
        
        # Obtener índice seleccionado
        idx = self._view.get_selected_simulation_index() if self._view else None
        if not idx or not idx.isValid():
            print("   ⚠️  No hay fila de simulación seleccionada")
            if self._view:
                self._view.notify("Seleccione una fila de simulación.", "warning")
            return
        
        row_idx = idx.row()
        row = self._simulations_table_model.get_row_data(row_idx) if self._simulations_table_model else None
        
        if not row:
            print("   ❌ Error: No se pudo obtener datos de la fila")
            return
        
        print(f"   → Fila seleccionada: {row_idx}")
        print(f"   → Cliente: {nit}")
        
        # Verificar insumos mínimos
        required_fields = {
            "punta_cli": "Punta Cliente",
            "nominal_usd": "Nominal USD",
            "spot": "Tasa Spot",
            "puntos": "Puntos Fwd",
            "plazo": "Plazo"
        }
        
        for field_key, field_name in required_fields.items():
            value = row.get(field_key)
            if value is None or value == "":
                print(f"   ❌ Falta el campo: {field_name}")
                if self._view:
                    self._view.notify(f"Complete el campo: {field_name}", "warning")
                return
        
        print("   ✓ Todos los campos requeridos están presentes")
        
        # 2) Resolver nombre y fc
        nombre = self._data_model.get_current_client_name() if self._data_model else ""
        fc = self._data_model.get_fc_for_nit(nit) if self._data_model else 0.0
        
        print(f"   → Nombre: {nombre}")
        print(f"   → FC: {fc}")
        
        # 3) Convertir fila simulada a "operación 415-like"
        print("\n   📊 Convirtiendo simulación a operación 415-like...")
        simulated_op = self._simulation_processor.build_simulated_operation(row, nit, nombre, fc)
        
        print(f"      ✓ Deal: {simulated_op.get('deal')}")
        print(f"      ✓ VNA: {simulated_op.get('vna'):,.2f} USD")
        print(f"      ✓ TRM: {simulated_op.get('trm'):,.2f}")
        print(f"      ✓ VNE: {simulated_op.get('vne'):,.2f}")
        print(f"      ✓ VR: {simulated_op.get('vr'):,.2f}")
        
        # 4) Tomar las vigentes del cliente actual
        vigentes = self._data_model.get_operaciones_por_nit(nit) if self._data_model else []
        print(f"\n   📋 Operaciones vigentes del cliente: {len(vigentes)}")
        
        # 5) Recalcular exposición conjunto
        print("\n   🧮 Recalculando exposición conjunto (vigentes + simulada)...")
        exp_total = self._simulation_processor.recalc_exposure_with_simulation(vigentes, simulated_op)
        
        print(f"      ✓ Exposición total: $ {exp_total:,.2f} COP")
        
        # 6) Mostrar en UI
        outstanding = self._data_model.get_outstanding_por_nit(nit) if self._data_model else 0.0
        
        print(f"\n   📈 Métricas de Exposición:")
        print(f"      Outstanding actual: $ {outstanding:,.2f}")
        print(f"      Total con simulación: $ {exp_total:,.2f}")
        
        if self._view:
            self._view.show_exposure(
                outstanding=outstanding,
                total_con_simulacion=exp_total,
                disponibilidad=None  # Se puede calcular si se tiene línea de crédito
            )
            
            self._view.notify(
                f"Simulación procesada: Exposición total $ {exp_total:,.2f}",
                "info"
            )
        
        # 7) Emitir señales globales
        if self._signals:
            self._signals.forward_simulations_changed.emit()
        
        print("="*60)
        print("[ForwardController] simulate_selected_row - COMPLETADO")
        print("="*60 + "\n")
    
    def save_simulations(self, rows: List[int]) -> None:
        """
        Guarda las simulaciones seleccionadas.
        
        Args:
            rows: Lista de índices de filas a guardar
        """
        print(f"[ForwardController] save_simulations: rows={rows}")
        
        # Aquí iría la lógica de guardado
        # Después de guardar, actualizar exposición
        if self._signals:
            self._signals.forward_exposure_updated.emit(1200000.0, 1200000.0, 800000.0)
