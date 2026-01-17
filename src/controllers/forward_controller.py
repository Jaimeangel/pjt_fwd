"""
Controlador para el módulo Forward.
"""

from typing import List, Optional
from datetime import date

import pandas as pd

from src.services.exposure_service import calculate_exposure_from_operations
from src.utils.ids import normalize_nit


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
                 simulation_processor=None, settings_model=None):
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
            settings_model: Instancia de SettingsModel (configuración compartida)
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
        self._settings_model = settings_model
        
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
        
        # Kill-switch para evitar reentrancia en select_client
        self._updating_client = False
        
        # Conectar señales de la vista a métodos del controller
        self._connect_view_signals()
        
        # Conectar señales del SettingsModel para actualización automática de TRM
        self._connect_settings_signals()
        
        # Conectar señales del modelo de simulaciones para habilitar/deshabilitar botón
        self._connect_simulations_model_signals()
        
        # Cargar catálogo inicial de contrapartes desde Settings
        self._reload_counterparties_from_settings()
    
    def _connect_view_signals(self):
        """Conecta las señales de la vista a los métodos del controlador."""
        if self._view:
            # Desconectar primero (si estaban conectadas) para evitar dobles conexiones
            try:
                self._view.load_415_requested.disconnect(self.load_415)
            except (TypeError, RuntimeError):
                pass
            try:
                self._view.load_ibr_requested.disconnect(self.load_ibr)
            except (TypeError, RuntimeError):
                pass
            # NOTA: Ya NO usamos client_selected (obsoleto)
            # try:
            #     self._view.client_selected.disconnect(self.select_client)
            # except (TypeError, RuntimeError):
            #     pass
            try:
                self._view.add_simulation_requested.disconnect(self.add_simulation)
            except (TypeError, RuntimeError):
                pass
            try:
                self._view.delete_simulations_requested.disconnect(self.delete_simulations)
            except (TypeError, RuntimeError):
                pass
            try:
                self._view.simulate_selected_requested.disconnect(self.simulate_selected_row)
            except (TypeError, RuntimeError):
                pass
            try:
                self._view.save_simulations_requested.disconnect(self.save_simulations)
            except (TypeError, RuntimeError):
                pass
            
            # Ahora conectar
            self._view.load_415_requested.connect(self.load_415)
            self._view.load_ibr_requested.connect(self.load_ibr)
            # NOTA: Ya NO conectamos client_selected (obsoleto, usaba nombres desde 415)
            # Ahora usamos currentIndexChanged conectado a _on_client_combo_changed
            # self._view.client_selected.connect(self.select_client)
            self._view.add_simulation_requested.connect(self.add_simulation)
            self._view.delete_simulations_requested.connect(self.delete_simulations)
            self._view.simulate_selected_requested.connect(self.simulate_selected_row)
            self._view.save_simulations_requested.connect(self.save_simulations)
            
            # Conectar combo de clientes por índice (no por texto)
            if hasattr(self._view, 'cmbClientes') and self._view.cmbClientes:
                try:
                    self._view.cmbClientes.currentIndexChanged.disconnect(self._on_client_combo_changed)
                except (TypeError, RuntimeError):
                    pass
                self._view.cmbClientes.currentIndexChanged.connect(self._on_client_combo_changed)
            
            print("[ForwardController] Señales de vista conectadas (sin duplicados)")
        
        # Configurar el resolver de IBR en el modelo de simulaciones
        if self._simulations_table_model and self._data_model:
            self._simulations_table_model.set_ibr_resolver(
                lambda dias: self._data_model.get_ibr_for_days(dias)
            )
            print("[ForwardController] IBR resolver configurado en modelo de simulaciones")
    
    def _connect_settings_signals(self):
        """Conecta señales del SettingsModel para actualización automática de TRM, patrimonio y contrapartes."""
        if self._settings_model:
            try:
                self._settings_model.trm_cop_usdChanged.disconnect(self._refresh_info_basica)
            except (TypeError, RuntimeError):
                pass
            try:
                self._settings_model.trm_cop_eurChanged.disconnect(self._refresh_info_basica)
            except (TypeError, RuntimeError):
                pass
            try:
                self._settings_model.patrimonioTecCopChanged.disconnect(self._refresh_info_basica)
            except (TypeError, RuntimeError):
                pass
            try:
                self._settings_model.colchonSeguridadChanged.disconnect(self.refresh_exposure_block)
            except (TypeError, RuntimeError):
                pass
            try:
                self._settings_model.lineasCreditoChanged.disconnect(self.refresh_exposure_block)
            except (TypeError, RuntimeError):
                pass
            
            # Conectar señales
            self._settings_model.trm_cop_usdChanged.connect(self._refresh_info_basica)
            self._settings_model.trm_cop_eurChanged.connect(self._refresh_info_basica)
            self._settings_model.patrimonioTecCopChanged.connect(self._refresh_info_basica)
            self._settings_model.patrimonioTecCopChanged.connect(self.refresh_exposure_block)  # Actualizar LLL al cambiar patrimonio
            self._settings_model.colchonSeguridadChanged.connect(self.refresh_exposure_block)  # Actualizar LLL al cambiar colchón
            self._settings_model.lineasCreditoChanged.connect(self.refresh_exposure_block)
            
            # Conectar señal de cambios en catálogo de contrapartes
            try:
                self._settings_model.counterpartiesChanged.disconnect(self._reload_counterparties_from_settings)
            except (TypeError, RuntimeError):
                pass
            self._settings_model.counterpartiesChanged.connect(self._reload_counterparties_from_settings)
            
        print("[ForwardController] Señales de SettingsModel conectadas para actualización automática de TRM, patrimonio, colchón y contrapartes")
    
    def _connect_simulations_model_signals(self):
        """Conecta señales del modelo de simulaciones para habilitar/deshabilitar el botón 'Simular'."""
        if self._simulations_table_model and self._view:
            # Conectar rowsInserted para habilitar botón cuando se agreguen filas
            try:
                self._simulations_table_model.rowsInserted.disconnect(self._update_simulate_button_state)
            except (TypeError, RuntimeError):
                pass
            
            try:
                self._simulations_table_model.rowsRemoved.disconnect(self._update_simulate_button_state)
            except (TypeError, RuntimeError):
                pass
            
            try:
                self._simulations_table_model.modelReset.disconnect(self._update_simulate_button_state)
            except (TypeError, RuntimeError):
                pass
            
            # Conectar señales
            self._simulations_table_model.rowsInserted.connect(self._update_simulate_button_state)
            self._simulations_table_model.rowsRemoved.connect(self._update_simulate_button_state)
            self._simulations_table_model.modelReset.connect(self._update_simulate_button_state)
            
            print("[ForwardController] Señales de SimulationsTableModel conectadas para actualizar estado del botón 'Simular'")
    
    def _update_simulate_button_state(self, *args):
        """
        Actualiza el estado del botón 'Simular' según si hay filas en la tabla de simulaciones.
        
        Este método se ejecuta automáticamente cuando:
        - Se agregan filas (rowsInserted)
        - Se eliminan filas (rowsRemoved)
        - Se limpia la tabla (modelReset)
        """
        if self._view:
            has_rows = self._view.has_simulation_rows()
            self._view.set_simulate_button_enabled(has_rows)
    
    def _reload_counterparties_from_settings(self):
        """
        Recarga el combo de contrapartes desde el catálogo de Información de contrapartes (Settings).
        
        Este método se ejecuta automáticamente cuando:
        - Se carga/actualiza el CSV de Información de contrapartes en Configuraciones
        - Cambia el catálogo de contrapartes
        """
        if not self._view or not self._settings_model:
            return
        
        catalog = self._settings_model.get_counterparties()
        self._view.populate_counterparties(catalog)
        
        # Si no hay catálogo, solo deshabilitar el combo (sin pop-up)
        if not catalog:
            print("[ForwardController] ⚠️ No hay contrapartes cargadas. Combo deshabilitado.")
        else:
            print(f"[ForwardController] Combo de contrapartes actualizado: {len(catalog)} opciones")

    def _get_lll_cop(self) -> float:
        """
        Devuelve el valor de LLL en COP que ya está calculado y mostrado
        en el bloque 'Parámetros de crédito' como 'Límite máximo permitido (LLL)(25%)'.
        
        Este valor ya incluye el 25% del patrimonio y el ajuste del 10% de colchón de seguridad.
        En lugar de recalcular desde patrimonio técnico, usa el mismo valor que ve el usuario en la UI.
        
        Returns:
            LLL en COP reales (el mismo que se muestra en UI)
        """
        if not self._data_model:
            return 0.0
        return self._data_model.get_lll_limit_cop()
    
    def _on_client_combo_changed(self, idx: int):
        """
        Manejador cuando cambia la selección del combo de contrapartes.
        
        Args:
            idx: Índice de la selección en el combo
        """
        if idx < 0:
            # No hay selección válida
            self._show_empty_exposure()
            return
        
        # Obtener NIT desde itemData
        nit_raw = self._view.cmbClientes.itemData(idx) if self._view else None
        
        if not nit_raw:
            print("[ForwardController] ⚠️ No se pudo obtener NIT de la selección")
            self._show_empty_exposure()
            return
        
        nit = normalize_nit(str(nit_raw))
        if not nit:
            print("[ForwardController] ⚠️ NIT inválido en la selección")
            self._show_empty_exposure()
            return
        
        nombre = self._view.cmbClientes.itemText(idx) if self._view else ""
        
        print(f"[ForwardController] Contraparte seleccionada: {nombre} (NIT: {nit})")
        
        # 1) Limpiar simulaciones previas
        print("   → Limpiando simulaciones previas...")
        if self._view:
            self._view.clear_simulations_table()
            self._view.set_simulate_button_enabled(False)
        
        if self._data_model:
            self._data_model.reset_simulation_state()
        
        # Identificar grupo conectado y miembros desde Settings
        group_name = None
        group_members = []
        has_real_group = False
        
        if self._settings_model:
            members_list = self._settings_model.get_group_members_by_nit(nit)
            if members_list and len(members_list) > 1:
                # Grupo real (más de una contraparte)
                has_real_group = True
                group_name = members_list[0].get("grupo", "")
                group_members = [m["nit"] for m in members_list]
                print(f"   → Grupo detectado: '{group_name}' con {len(group_members)} contrapartes")
            else:
                print(f"   → Sin grupo o grupo con solo 1 contraparte")
        
        # 2) LCA no viene de Configuraciones (solo catálogo de contrapartes)
        lca_real = None
        
        # 3) Buscar datos en 415 por NIT normalizado y calcular exposiciones
        # IMPORTANTE: Siempre calcular exposiciones, incluso si no hay operaciones (outstanding = 0)
        outstanding = 0.0
        group_outstanding = 0.0
        ops_list = []
        
        if self._data_model:
            ops_list = self._data_model.get_operaciones_por_nit(nit)
            if ops_list:
                print(f"   → {len(ops_list)} operaciones vigentes desde 415")
            else:
                print(f"   → Sin operaciones vigentes en 415 (outstanding = 0)")
            
            self._data_model.set_current_client(nit, nombre)
            self._data_model.set_current_group(group_name, group_members)
            
            # Calcular exposición de contraparte (siempre)
            df_cte = self._data_model.get_operations_df_for_nit(nit)
            exposure_cte = calculate_exposure_from_operations(df_cte)
            outstanding = exposure_cte.get("outstanding", 0.0)
            
            print(f"   → Outstanding Contraparte: $ {outstanding:,.0f}")
            
            # Calcular exposición de grupo SOLO si has_real_group == True
            group_outstanding = 0.0
            if has_real_group:
                df_group = self._data_model.get_operations_df_for_nits(group_members)
                exposure_group = calculate_exposure_from_operations(df_group)
                group_outstanding = exposure_group.get("outstanding", 0.0)
                print(f"   → Outstanding Grupo: $ {group_outstanding:,.0f}")
            else:
                print(f"   → Sin grupo real, exposición grupo = 0")
            
            # Setear exposiciones base (sin simulación)
            self._data_model.set_exposure_counterparty(outstanding, outstanding)
            self._data_model.set_exposure_group(group_outstanding, group_outstanding)
            
            # 🔹 CRÍTICO: Calcular disponibilidades LLL SIEMPRE, incluso si outstanding = 0
            lll_cop = self._get_lll_cop()
            print(f"   → LLL base para disponibilidad: $ {lll_cop:,.0f}")
            
            disp_cte_cop = lll_cop - outstanding
            disp_grp_cop = lll_cop - group_outstanding
            disp_cte_pct = (disp_cte_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
            disp_grp_pct = (disp_grp_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
            
            print(f"   → Disponibilidad Contraparte: $ {disp_cte_cop:,.0f} ({disp_cte_pct:.2f}%)")
            print(f"   → Disponibilidad Grupo: $ {disp_grp_cop:,.0f} ({disp_grp_pct:.2f}%)")
            
            self._data_model.set_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
            
            self._data_model.set_outstanding_cop(outstanding)
            self._data_model.set_outstanding_with_sim_cop(outstanding)
        
        # 4) Actualizar tabla de operaciones
        if self._view and self._operations_table_model:
            self._operations_table_model.set_operations(ops_list)
            self._view.set_operations_table(self._operations_table_model)
        
        # 5) Actualizar parámetros de crédito (LCA y LLL)
        if self._view and self._settings_model:
            # LCA
            linea_display = f"$ {lca_real:,.0f}" if lca_real else "—"
            
            # LLL global (25% del Patrimonio técnico vigente con colchón)
            lll_global = self._settings_model.lll_cop()
            limite_display = f"$ {lll_global:,.0f}" if lll_global else "—"
            
            # Guardar los límites en el modelo para uso posterior
            if self._data_model:
                self._data_model.set_credit_limits(
                    linea_credito_aprobada_cop=lca_real or 0.0,
                    lll_cop=lll_global or 0.0
                )
            
            self._view.set_credit_params(linea=linea_display, limite=limite_display)
        
        # Actualizar UI de grupo (tags bajo el bloque Cliente)
        if self._view:
            members_for_ui = []
            if has_real_group and self._settings_model:
                members_for_ui = self._settings_model.get_group_members_by_nit(nit)
            self._view.update_group_members(group_name, members_for_ui)
        
        # 6) Recalcular exposición sin simulación
        self._refresh_exposure(lca_real, outstanding, outstanding)
        
        # 7) Actualizar información básica
        self._refresh_info_basica()
    
    def _show_empty_exposure(self):
        """
        Muestra estado vacío cuando no hay contraparte seleccionada o no hay datos.
        """
        if self._view:
            self._view.update_exposure_values(0.0, 0.0, 0.0, 0.0)
            self._view.update_lll_availability(0.0, 0.0, 0.0, 0.0)
            
            self._view.update_consumo_dual_chart(0.0, 0.0, 0.0)
            
            if self._operations_table_model:
                self._operations_table_model.set_operations([])
    
    def _refresh_exposure(self, lca_real: float | None, outstanding: float, outstanding_with_sim: float):
        """
        Actualiza el bloque de exposición y la gráfica con los valores actuales.
        
        IMPORTANTE: También actualiza las disponibilidades LLL desde el modelo.
        """
        out_cte = outstanding or 0.0
        out_cte_sim = outstanding_with_sim if outstanding_with_sim is not None else out_cte
        out_grp = out_cte
        out_grp_sim = out_cte_sim
        
        if self._data_model:
            out_cte, out_cte_sim = self._data_model.get_exposure_counterparty()
            out_grp, out_grp_sim = self._data_model.get_exposure_group()
            out_cte = out_cte or 0.0
            out_cte_sim = out_cte_sim if out_cte_sim is not None else out_cte
            out_grp = out_grp or 0.0
            out_grp_sim = out_grp_sim if out_grp_sim is not None else out_grp
        
        if self._view:
            # Actualizar valores de exposición
            self._view.update_exposure_values(out_cte, out_cte_sim, out_grp, out_grp_sim)
            
            # 🔹 CORRECCIÓN: También actualizar disponibilidades LLL desde el modelo
            if self._data_model:
                disp_cte_cop, disp_cte_pct = self._data_model.get_lll_availability_counterparty()
                disp_grp_cop, disp_grp_pct = self._data_model.get_lll_availability_group()
                self._view.update_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
                print(f"   [_refresh_exposure] Disponibilidad LLL actualizada:")
                print(f"      Contraparte: $ {disp_cte_cop:,.0f} ({disp_cte_pct:.2f}%)")
                print(f"      Grupo: $ {disp_grp_cop:,.0f} ({disp_grp_pct:.2f}%)")
            
            self._view.update_consumo_dual_chart(
                lca_total=lca_real or 0.0,
                outstanding=out_cte,
                outstanding_with_sim=out_cte_sim
            )
    
    def _refresh_info_basica(self, _=None):
        """
        Actualiza la información básica (Patrimonio técnico y TRMs) en la vista cuando cambian en Configuraciones.
        Usa el valor global de Patrimonio técnico desde SettingsModel (no por contraparte).
        """
        if not self._view or not self._settings_model:
            return
        
        # Obtener Patrimonio técnico global (en COP reales)
        patrimonio = self._settings_model.patrimonio_tec_cop()
        patrimonio_str = f"{patrimonio:,.0f}" if isinstance(patrimonio, (int, float)) else "—"
        
        # Obtener TRM actuales
        trm_cop_usd = self._settings_model.trm_cop_usd()
        trm_cop_eur = self._settings_model.trm_cop_eur()
        
        # Formatear
        trm_usd_str = f"{trm_cop_usd:,.2f}" if trm_cop_usd else "—"
        trm_eur_str = f"{trm_cop_eur:,.2f}" if trm_cop_eur else "—"
        
        # Actualizar vista
        self._view.update_info_basica(patrimonio_str, trm_usd_str, trm_eur_str)
        print(f"[ForwardController] Información básica actualizada: Patrimonio={patrimonio_str}, TRM COP/USD={trm_usd_str}, TRM COP/EUR={trm_eur_str}")
    
    def refresh_exposure_block(self):
        """
        Actualiza el bloque de exposición (contraparte y grupo) y la gráfica de consumo.
        """
        if not self._view or not self._data_model or not self._settings_model:
            return
        
        # Obtener NIT del cliente actual
        nit = self._data_model.current_client_nit()
        # Valores por defecto (no hay LCA en el catálogo de contrapartes)
        LCA = 0.0
        
        # Obtener LLL GLOBAL (25% del Patrimonio técnico vigente con colchón de seguridad)
        LLL = self._settings_model.lll_cop()
        
        # 🔹 Actualizar el límite máximo permitido (LLL) en "Parámetros de crédito"
        # Esto se actualiza aquí para reflejar cambios en Patrimonio o Colchón automáticamente
        # También guardar en el modelo para que se use en cálculos de disponibilidad
        if self._data_model:
            # Obtener LCA actual del modelo (o 0 si no está definido)
            lca_actual = self._data_model.get_lca_limit_cop()
            self._data_model.set_credit_limits(
                linea_credito_aprobada_cop=lca_actual,
                lll_cop=LLL or 0.0
            )
        
        if self._view:
            limite_display = f"$ {LLL:,.0f}" if LLL else "—"
            self._view.lblLimiteMax.setText(limite_display)
        
        out_cte, out_cte_sim = self._data_model.get_exposure_counterparty()
        out_grp, out_grp_sim = self._data_model.get_exposure_group()
        out_cte = out_cte or 0.0
        out_cte_sim = out_cte_sim if out_cte_sim is not None else out_cte
        out_grp = out_grp or out_cte
        out_grp_sim = out_grp_sim if out_grp_sim is not None else out_grp
        
        self._view.update_exposure_values(out_cte, out_cte_sim, out_grp, out_grp_sim)
        disp_cte_cop, disp_cte_pct = self._data_model.get_lll_availability_counterparty()
        disp_grp_cop, disp_grp_pct = self._data_model.get_lll_availability_group()
        self._view.update_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
        disp_cte_cop, disp_cte_pct = self._data_model.get_lll_availability_counterparty()
        disp_grp_cop, disp_grp_pct = self._data_model.get_lll_availability_group()
        self._view.update_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
        
        # Actualizar gráfica de consumo de línea (LCA + consumo apilado)
        self._view.update_consumo_dual_chart(
            lca_total=LCA,
            outstanding=out_cte,
            outstanding_with_sim=out_cte_sim
        )
        
        print(f"[ForwardController] Bloque de exposición actualizado:")
        print(f"   Contraparte: $ {out_cte:,.0f} → $ {out_cte_sim:,.0f}")
        print(f"   Grupo: $ {out_grp:,.0f} → $ {out_grp_sim:,.0f}")
    
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
                
                # NOTA: Ya no actualizamos el combo desde el 415
            # El combo se puebla únicamente desde Settings (Información de contrapartes)
                # El 415 solo proporciona Outstanding y operaciones para join
                # if self._view:
                #     nombres_clientes = self._data_model.get_client_names()
                #     self._view.set_client_list(nombres_clientes)
            
            print(f"      ✅ Procesamiento de operaciones completado (combo NO actualizado desde 415)")
            
        except Exception as e:
            print(f"      ❌ Error procesando operaciones: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_credit_exposure_by_nit(self, df: 'pd.DataFrame') -> dict:
        """
        Calcula la exposición crediticia por NIT utilizando la función genérica.
        """
        exposure_by_nit = {}
        if df is None or df.empty or 'nit' not in df.columns:
            return exposure_by_nit
        
        for nit, ops_cliente in df.groupby('nit'):
            try:
                result = calculate_exposure_from_operations(ops_cliente)
                exposure_by_nit[nit] = result.get("outstanding", 0.0)
                
                print(f"         NIT {nit}:")
                print(f"            Operaciones: {result.get('operations_count', 0)}")
                print(f"            Total VNE: $ {result.get('total_vne', 0.0):,.2f}")
                print(f"            FC: {result.get('fc', 0.0):.6f}")
                print(f"            Total EPFp: $ {result.get('epfp_total', 0.0):,.2f}")
                print(f"            Total VR: $ {result.get('total_vr', 0.0):,.2f}")
                print(f"            MGP: {result.get('mgp', 0.0):.6f}")
                print(f"            CRP: $ {result.get('crp', 0.0):,.2f}")
                print(f"            → Exposición Crediticia: $ {result.get('outstanding', 0.0):,.2f}")
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
        Este es el ÚNICO lugar donde se calculan y setean los valores de línea/colchón/límite.
        
        Args:
            nombre_o_nit: Nombre de la contraparte o NIT del cliente
        """
        # Kill-switch: evitar reentrancia si ya estamos procesando
        if self._updating_client:
            print(f"[ForwardController] select_client: BLOQUEADO (ya procesando)")
            return
        
        self._updating_client = True
        try:
            print(f"[ForwardController] select_client: {nombre_o_nit}")
            
            # 🔹 PASO 1: Limpiar simulaciones previas al cambiar de contraparte
            print("   → Limpiando simulaciones previas...")
            if self._view:
                self._view.clear_simulations_table()
                self._view.set_simulate_button_enabled(False)
            
            if self._data_model:
                self._data_model.reset_simulation_state()
            
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
                if self._data_model:
                    self._data_model.set_current_group(None, [])
                return
            
            nit_norm = normalize_nit(nit)
            if not nit_norm:
                print(f"   ⚠️  NIT inválido o vacío para: {nombre_o_nit}")
                if self._view:
                    self._view.show_exposure(outstanding=0.0, total_con_simulacion=None, disponibilidad=None)
                if self._operations_table_model:
                    self._operations_table_model.set_operations([])
                if self._data_model:
                    self._data_model.set_current_group(None, [])
                return
            
            nit = nit_norm
            print(f"   → NIT determinado: {nit}")
            
            # Guardar cliente actual
            self._current_client_nit = nit
            
            # Actualizar cliente actual en el modelo de datos
            if self._data_model:
                nombre = self._data_model.get_nombre_by_nit(nit)
                self._data_model.set_current_client(nit, nombre)
            
            # Determinar grupo conectado y miembros relacionados
            group_name = None
            group_members = [nit]
            if self._settings_model and not self._settings_model.lineas_credito_df.empty:
                group_name = self._settings_model.get_group_for_nit(nit)
                if group_name:
                    members_info = self._settings_model.get_counterparties_by_group(group_name)
                    extracted = [
                        normalize_nit(member.get("nit"))
                        for member in (members_info or [])
                        if member.get("nit")
                    ]
                    extracted = [m for m in extracted if m]
                    if extracted:
                        group_members = extracted
                        if nit not in group_members:
                            group_members.append(nit)
            if self._data_model:
                self._data_model.set_current_group(group_name, group_members)
            
            # 🔹 Buscar cliente en contrapartes (SettingsModel) - SIN valores por defecto
            if self._settings_model:
                # Validar que hay contrapartes cargadas
                if self._settings_model.lineas_credito_df.empty:
                    print(f"   ⚠️  No hay contrapartes cargadas en SettingsModel")
                    # Resetear límites en el modelo
                    if self._data_model:
                        self._data_model.set_credit_limits(
                            linea_credito_aprobada_cop=0.0,
                            lll_cop=0.0
                        )
                    if self._view:
                        self._view.set_credit_params(linea="—", limite="—")
                        self._view.notify("Cargue primero 'Información de contrapartes' en Configuraciones.", "warning")
                    return  # No continuar con operaciones si no hay contrapartes
                
                cliente_info = self._settings_model.get_linea_credito_por_nit(nit)
                
                if cliente_info:
                    # Cliente encontrado en contrapartes
                    print(f"   → Datos del cliente (desde SettingsModel):")
                    
                    # 🔹 Obtener LLL GLOBAL (25% del Patrimonio técnico vigente)
                    lll_global = self._settings_model.lll_cop()
                    if lll_global:
                        print(f"      LLL global (25% PT): $ {lll_global:,.0f}")
                    
                    # 🔹 Guardar límites en el modelo para uso posterior
                    if self._data_model:
                        self._data_model.set_credit_limits(
                            linea_credito_aprobada_cop=0.0,
                            lll_cop=lll_global or 0.0
                        )
                    
                    # 🔹 Actualizar vista con LLL global (sin LCA)
                    if self._view:
                        limite_display = f"$ {lll_global:,.0f}" if lll_global else "—"
                        self._view.set_credit_params(
                            linea="—",
                            limite=limite_display
                        )
                else:
                    # Cliente NO encontrado en contrapartes
                    print(f"   ⚠️  Cliente con NIT {nit} no encontrado en contrapartes.")
                    
                    # 🔹 Obtener LLL GLOBAL (independiente de si se encontró el cliente)
                    lll_global = self._settings_model.lll_cop()
                    if lll_global:
                        print(f"      LLL global (25% PT): $ {lll_global:,.0f}")
                    
                    # 🔹 Guardar LLL en el modelo (LCA = 0 porque no se encontró)
                    if self._data_model:
                        self._data_model.set_credit_limits(
                            linea_credito_aprobada_cop=0.0,
                            lll_cop=lll_global or 0.0
                        )
                    
                    if self._view:
                        limite_display = f"$ {lll_global:,.0f}" if lll_global else "—"
                        self._view.set_credit_params(linea="—", limite=limite_display)
            else:
                print(f"   ⚠️  SettingsModel no disponible, no se pueden cargar límites del cliente.")
                # Resetear límites en el modelo
                if self._data_model:
                    self._data_model.set_credit_limits(
                        linea_credito_aprobada_cop=0.0,
                        lll_cop=0.0
                    )
                if self._view:
                    self._view.set_credit_params(linea="—", limite="—")
            
            # Calcular exposiciones y disponibilidades LLL
            outstanding = 0.0
            group_outstanding = 0.0
            if self._data_model:
                df_cte = self._data_model.get_operations_df_for_nit(nit)
                df_group = self._data_model.get_operations_df_for_nits(group_members)
                exposure_cte = calculate_exposure_from_operations(df_cte)
                exposure_group = calculate_exposure_from_operations(df_group)
                outstanding = exposure_cte.get("outstanding", 0.0)
                group_outstanding = exposure_group.get("outstanding", 0.0)
                
                self._data_model.set_exposure_counterparty(outstanding, outstanding)
                self._data_model.set_exposure_group(group_outstanding, group_outstanding)
                
                lll_cop = self._get_lll_cop()
                disp_cte_cop = lll_cop - outstanding
                disp_grp_cop = lll_cop - group_outstanding
                disp_cte_pct = (disp_cte_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
                disp_grp_pct = (disp_grp_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
                self._data_model.set_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
                self._data_model.set_outstanding_cop(outstanding)
                self._data_model.set_outstanding_with_sim_cop(outstanding)
            
            # Cargar operaciones vigentes del cliente en la tabla
            if self._data_model and self._operations_table_model:
                operaciones = self._data_model.get_operaciones_por_nit(nit)
                print(f"   → Cargando {len(operaciones)} operaciones del cliente en la tabla")
                self._operations_table_model.set_operations(operaciones)
                
                # Actualizar vista de la tabla
                if self._view:
                    self._view.set_operations_table(self._operations_table_model)
            
            # 🔹 Actualizar bloque de exposición completo (Outstanding, Disp LCA, Disp LLL)
            self.refresh_exposure_block()
            
            # 🔹 Actualizar información básica (Patrimonio técnico global y TRMs)
            self._refresh_info_basica()
            
            # Emitir señal global
            if self._signals:
                self._signals.forward_client_changed.emit(nit)
        except Exception as e:
            print(f"[ForwardController] Error en select_client cerca de outstanding: {e}")
        finally:
            # Liberar kill-switch
            self._updating_client = False
    
    def add_simulation(self) -> None:
        """
        Agrega una nueva fila de simulación.
        
        IMPORTANTE: Este método NO debe modificar los valores de exposición
        (Outstanding, Outstanding+Sim). Solo agrega una fila vacía a la tabla.
        """
        from datetime import date
        
        print("[ForwardController] add_simulation")
        
        # Validar que hay un cliente seleccionado
        nit = self._data_model.get_current_client_nit() if self._data_model else None
        nombre = self._data_model.get_current_client_name() if self._data_model else None
        
        if not nit:
            print("   ⚠️  No hay cliente seleccionado")
            if self._view:
                self._view.notify("Seleccione primero una contraparte.", "warning")
            return
        
        print(f"   → Cliente seleccionado: {nombre}")
        
        # Crear una nueva fila vacía (sin modificar exposición)
        if self._simulations_table_model:
            self._simulations_table_model.add_row({
                "cliente": nombre,
                "nit": nit,
                "punta_cli": "Compra",
                "punta_emp": "Venta",
                "nominal_usd": 0.0,
                "fec_sim": date.today().strftime("%Y-%m-%d"),
                "fec_venc": None,
                "plazo": None,
                "spot": 0.0,
                "puntos": 0.0,
                "tasa_fwd": 0.0,
                "tasa_ibr": None,
                "derecho": None,
                "obligacion": None,
                "fair_value": None
            })
            print("   → Fila agregada a la tabla de simulaciones")
        
        # 🔒 Importante: NO tocar los labels de exposición aquí.
        # No llamar show_exposure ni modificar lblOutstanding ni lblOutstandingSim.
        # Solo el botón "Simular" actualiza Outstanding + simulación.
    
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
        
        # Limpiar Outstanding + simulación (ya no hay simulaciones activas)
        if self._data_model:
            self._data_model.set_outstanding_with_sim_cop(None)
        
        # 🔹 Actualizar bloque de exposición (vuelve a mostrar solo Outstanding)
        self.refresh_exposure_block()
        
        if self._signals:
            self._signals.forward_simulations_changed.emit()
    
    def simulate_selected_row(self) -> None:
        """
        Simula la exposición crediticia de una o múltiples filas seleccionadas.
        Permite selección múltiple con Ctrl o Shift.
        
        Recalcula la exposición total incorporando todas las operaciones simuladas
        junto con las operaciones vigentes del cliente actual.
        """
        print("\n" + "="*60)
        print("[ForwardController] simulate_selected_row - INICIANDO")
        print("="*60)
        
        # 1) Validaciones básicas
        nit = self._data_model.get_current_client_nit() if self._data_model else None
        if not nit:
            print("   ⚠️  No hay contraparte seleccionada")
            if self._view:
                self._view.notify("Seleccione primero una contraparte.", "warning")
            return
        
        # Obtener todas las filas seleccionadas (soporte para múltiple selección)
        selected_rows = self._view.get_selected_simulation_rows() if self._view else []
        
        if not selected_rows:
            print("   ⚠️  No hay filas de simulación seleccionadas")
            if self._view:
                self._view.notify("Seleccione al menos una operación para simular (Ctrl o Shift para múltiple).", "warning")
            return
        
        print(f"   → Filas seleccionadas: {len(selected_rows)} ({selected_rows})")
        print(f"   → Cliente: {nit}")
        
        # Deshabilitar botón durante el cálculo
        if self._view and hasattr(self._view, 'btnRun'):
            self._view.btnRun.setEnabled(False)
        
        # 2) Validar y construir lista de operaciones simuladas
        required_fields = {
            "punta_cli": "Punta Cliente",
            "nominal_usd": "Nominal USD",
            "spot": "Tasa Spot",
            "puntos": "Puntos Fwd",
            "plazo": "Plazo"
        }
        
        simulated_ops = []
        nombre = self._data_model.get_current_client_name() if self._data_model else ""
        fc = self._data_model.get_fc_for_nit(nit) if self._data_model else 0.0
        
        print(f"   → Nombre: {nombre}")
        print(f"   → FC: {fc}")
        
        # Validar cada fila seleccionada
        for row_idx in selected_rows:
            row = self._simulations_table_model.get_row_data(row_idx) if self._simulations_table_model else None
            
            if not row:
                print(f"   ❌ Error: No se pudo obtener datos de la fila {row_idx}")
                if self._view and hasattr(self._view, 'btnRun'):
                    self._view.btnRun.setEnabled(True)
                return
            
            # Verificar insumos mínimos
            for field_key, field_name in required_fields.items():
                value = row.get(field_key)
                if value is None or value == "":
                    print(f"   ❌ Fila {row_idx}: Falta el campo: {field_name}")
                    if self._view:
                        self._view.notify(f"Fila {row_idx + 1}: Complete el campo '{field_name}'", "warning")
                        if hasattr(self._view, 'btnRun'):
                            self._view.btnRun.setEnabled(True)
                    return
            
            # Convertir fila a operación 415-like
            simulated_op = self._simulation_processor.build_simulated_operation(row, nit, nombre, fc)
            simulated_ops.append(simulated_op)
            
            print(f"   ✓ Fila {row_idx}: Deal={simulated_op.get('deal')}, VNA={simulated_op.get('vna'):,.2f} USD")
        
        print(f"\n   ✓ Todas las filas ({len(simulated_ops)}) validadas y convertidas")
        
        # 3) Obtener operaciones vigentes del cliente
        vigentes = self._data_model.get_operaciones_por_nit(nit) if self._data_model else []
        print(f"\n   📋 Operaciones vigentes del cliente: {len(vigentes)}")
        
        group_members = self._data_model.current_group_members_nits() if self._data_model else []
        if not group_members:
            group_members = [nit]
        
        df_cte = self._data_model.get_operations_df_for_nit(nit) if self._data_model else pd.DataFrame()
        df_group = self._data_model.get_operations_df_for_nits(group_members) if self._data_model else pd.DataFrame()
        df_simulated_ops = pd.DataFrame(simulated_ops) if simulated_ops else pd.DataFrame()
        
        df_cte_sim = pd.concat([df_cte, df_simulated_ops], ignore_index=True) if not df_simulated_ops.empty else df_cte.copy()
        df_group_sim = pd.concat([df_group, df_simulated_ops], ignore_index=True) if not df_simulated_ops.empty else df_group.copy()
        
        exposure_cte_base = calculate_exposure_from_operations(df_cte)
        exposure_group_base = calculate_exposure_from_operations(df_group)
        exposure_cte_sim = calculate_exposure_from_operations(df_cte_sim)
        exposure_group_sim = calculate_exposure_from_operations(df_group_sim)
        
        outstanding = exposure_cte_base.get("outstanding", 0.0)
        outstanding_with_sim = exposure_cte_sim.get("outstanding", 0.0)
        group_outstanding = exposure_group_base.get("outstanding", 0.0)
        group_outstanding_sim = exposure_group_sim.get("outstanding", 0.0)
        lll_cop = self._get_lll_cop()
        disp_cte_cop = lll_cop - outstanding_with_sim
        disp_grp_cop = lll_cop - group_outstanding_sim
        disp_cte_pct = (disp_cte_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
        disp_grp_pct = (disp_grp_cop / lll_cop * 100.0) if lll_cop > 0 else 0.0
        
        print(f"\n   📈 Métricas de Exposición:")
        print(f"      Outstanding actual: $ {outstanding:,.2f}")
        print(f"      Outstanding grupo: $ {group_outstanding:,.2f}")
        print(f"      Total con simulación ({len(simulated_ops)} ops): $ {outstanding_with_sim:,.2f}")
        print(f"      Total grupo con simulación: $ {group_outstanding_sim:,.2f}")
        
        # Guardar en el modelo
        if self._data_model:
            self._data_model.set_exposure_counterparty(outstanding, outstanding_with_sim)
            self._data_model.set_exposure_group(group_outstanding, group_outstanding_sim)
            self._data_model.set_lll_availability(disp_cte_cop, disp_cte_pct, disp_grp_cop, disp_grp_pct)
            self._data_model.set_outstanding_cop(outstanding)
            self._data_model.set_outstanding_with_sim_cop(outstanding_with_sim)
        
        # 🔹 Actualizar bloque de exposición completo
        self.refresh_exposure_block()
        
        if self._view:
            # Mensaje diferenciado según cantidad de operaciones
            if len(simulated_ops) == 1:
                mensaje = f"Simulación procesada: Exposición total $ {outstanding_with_sim:,.2f}"
            else:
                mensaje = f"{len(simulated_ops)} simulaciones procesadas: Exposición total $ {outstanding_with_sim:,.2f}"
            
            self._view.notify(mensaje, "info")
        
        # Rehabilitar botón
        if self._view and hasattr(self._view, 'btnRun'):
            self._view.btnRun.setEnabled(True)
        
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
