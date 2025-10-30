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
                 simulations_table_model=None, client_service=None):
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
            client_service: Instancia de ClientService
        """
        self._data_model = data_model
        self._simulations_model = simulations_model
        self._view = view
        self._pricing_service = pricing_service
        self._exposure_service = exposure_service
        self._signals = signals
        self._simulations_table_model = simulations_table_model
        self._client_service = client_service
        
        # Estado actual
        self._current_client_nit = None
        self._current_outstanding = 100000.0  # Mock: $100,000 COP
        
        # Conectar señales de la vista a métodos del controller
        self._connect_view_signals()
    
    def _connect_view_signals(self):
        """Conecta las señales de la vista a los métodos del controlador."""
        if self._view:
            self._view.load_415_requested.connect(self.load_415)
            self._view.client_selected.connect(self.select_client)
            self._view.add_simulation_requested.connect(self.add_simulation)
            self._view.duplicate_simulation_requested.connect(self.duplicate_simulation)
            self._view.delete_simulations_requested.connect(self.delete_simulations)
            self._view.run_simulations_requested.connect(self.run_simulations)
            self._view.save_simulations_requested.connect(self.save_simulations)
            print("[ForwardController] Señales de vista conectadas")
    
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
            
            # Guardar exposiciones en el modelo
            if self._data_model:
                self._data_model.outstanding_por_cliente = exposure_by_nit
                print(f"      ✓ Exposiciones calculadas para {len(exposure_by_nit)} clientes")
                
                # Mostrar resumen
                total_exposure = sum(exposure_by_nit.values())
                print(f"      ✓ Exposición total: $ {total_exposure:,.2f}")
            
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
    
    def select_client(self, nit: str) -> None:
        """
        Selecciona un cliente.
        
        Args:
            nit: NIT del cliente seleccionado
        """
        print(f"[ForwardController] select_client: {nit}")
        
        # Guardar cliente actual
        self._current_client_nit = nit
        
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
        if self._data_model and nit in self._data_model.outstanding_por_cliente:
            outstanding = self._data_model.outstanding_por_cliente[nit]
            print(f"   → Outstanding del cliente: $ {outstanding:,.2f}")
        else:
            print(f"   → Sin operaciones vigentes para este cliente")
        
        # Actualizar outstanding en la vista
        self._current_outstanding = outstanding
        
        if self._view:
            # Calcular total con simulación (por ahora solo outstanding)
            total_con_simulacion = outstanding
            
            # Calcular disponibilidad
            disponibilidad = 0.0
            if self._client_service:
                limits = self._client_service.get_client_limits(nit)
                disponibilidad = limits['limite_max'] - total_con_simulacion
            
            # Actualizar exposición en la vista
            self._view.show_exposure(
                outstanding=outstanding,
                total_con_simulacion=total_con_simulacion,
                disponibilidad=disponibilidad
            )
        
        # Emitir señal global
        if self._signals:
            self._signals.forward_client_changed.emit(nit)
    
    def add_simulation(self) -> None:
        """Agrega una nueva fila de simulación."""
        print("[ForwardController] add_simulation")
        
        # Aquí iría: self._simulations_model.add()
        # Por ahora, agregar directamente al modelo de tabla Qt
        if self._simulations_table_model:
            self._simulations_table_model.add_row()
            print("   → Fila agregada a la tabla de simulaciones")
        
        # Emitir señal
        if self._signals:
            self._signals.forward_simulations_changed.emit()
    
    def duplicate_simulation(self, row: int) -> None:
        """
        Duplica una fila de simulación.
        
        Args:
            row: Índice de la fila a duplicar
        """
        print(f"[ForwardController] duplicate_simulation: row={row}")
        
        # Aquí iría: self._simulations_model.duplicate(row)
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
    
    def run_simulations(self) -> None:
        """Ejecuta los cálculos para todas las simulaciones."""
        print("\n" + "="*60)
        print("[ForwardController] run_simulations - INICIANDO")
        print("="*60)
        
        if not self._simulations_table_model:
            print("   ❌ Error: No hay modelo de tabla de simulaciones")
            return
        
        # Obtener todas las filas de simulaciones
        rows = self._simulations_table_model.get_all_rows()
        
        if not rows:
            print("   ⚠️  No hay simulaciones para procesar")
            if self._view:
                self._view.notify("No hay simulaciones para procesar", "warning")
            return
        
        print(f"\n📊 Procesando {len(rows)} simulaciones...")
        
        # Acumulador de exposición simulada
        exposicion_simulada_total = 0.0
        
        # Iterar cada fila y calcular
        for idx, row_data in enumerate(rows):
            print(f"\n   Simulación {idx + 1}:")
            print(f"      Cliente: {row_data.get('cliente', 'N/A')}")
            print(f"      Nominal USD: {row_data.get('nominal_usd', 0):,.2f}")
            print(f"      Spot: {row_data.get('spot', 0):,.2f}")
            
            # 1. Calcular pricing usando ForwardPricingService
            if self._pricing_service:
                pricing_result = self._pricing_service.calc_forward_from_simulation(row_data)
                
                # Actualizar fila con resultados
                row_data['tasa_fwd'] = pricing_result['tasa_fwd']
                row_data['puntos'] = pricing_result['puntos']
                row_data['fair_value'] = pricing_result['fair_value']
                
                print(f"      ✓ Tasa Fwd calculada: {pricing_result['tasa_fwd']:,.6f}")
                print(f"      ✓ Puntos: {pricing_result['puntos']:,.6f}")
                print(f"      ✓ Fair Value: $ {pricing_result['fair_value']:,.2f}")
            
            # 2. Calcular exposición usando ExposureService
            if self._exposure_service:
                exposicion = self._exposure_service.calc_simulated_exposure(row_data)
                exposicion_simulada_total += exposicion
                
                print(f"      ✓ Exposición: $ {exposicion:,.2f}")
            
            # 3. Actualizar la fila en el modelo de tabla
            self._simulations_table_model.update_row(idx, row_data)
        
        print(f"\n✅ Simulaciones procesadas exitosamente")
        print(f"   Exposición simulada total: $ {exposicion_simulada_total:,.2f}")
        
        # 4. Calcular métricas de exposición
        outstanding = self._current_outstanding  # Mock
        total_con_simulacion = outstanding + exposicion_simulada_total
        
        # Obtener límites del cliente actual
        disponibilidad = 0.0
        limite_max = 0.0
        
        if self._client_service and self._current_client_nit:
            limits = self._client_service.get_client_limits(self._current_client_nit)
            limite_max = limits['limite_max']
            disponibilidad = limite_max - total_con_simulacion
        else:
            # Mock sin cliente seleccionado
            limite_max = 5_000_000_000.0  # $5,000 millones
            disponibilidad = limite_max - total_con_simulacion
        
        print(f"\n📈 Métricas de Exposición:")
        print(f"   Outstanding actual: $ {outstanding:,.2f}")
        print(f"   Total con simulación: $ {total_con_simulacion:,.2f}")
        print(f"   Límite máximo: $ {limite_max:,.2f}")
        print(f"   Disponibilidad: $ {disponibilidad:,.2f}")
        
        # 5. Actualizar vista
        if self._view:
            # Actualizar labels de exposición
            self._view.show_exposure(
                outstanding=outstanding,
                total_con_simulacion=total_con_simulacion,
                disponibilidad=disponibilidad
            )
            
            # Actualizar gráfica (placeholder)
            chart_data = {
                "linea_total": limite_max,
                "consumo_actual": outstanding,
                "consumo_con_simulacion": total_con_simulacion,
                "disponibilidad": disponibilidad
            }
            self._view.update_chart(chart_data)
            
            # Notificar éxito
            self._view.notify(
                f"Simulaciones procesadas: {len(rows)} operaciones",
                "info"
            )
        
        # 6. Emitir señales globales
        if self._signals:
            self._signals.forward_simulations_changed.emit()
            self._signals.forward_exposure_updated.emit()
        
        print("="*60)
        print("[ForwardController] run_simulations - COMPLETADO")
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
