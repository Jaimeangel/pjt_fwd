"""
Script de prueba para servicios mock.
Verifica que los cálculos y el flujo funcionen correctamente.
"""

import sys
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.forward_pricing_service import ForwardPricingService
from services.exposure_service import ExposureService
from services.client_service import ClientService


def test_forward_pricing_service():
    """Prueba el servicio de pricing."""
    print("\n" + "="*60)
    print("TEST: ForwardPricingService")
    print("="*60)
    
    service = ForwardPricingService()
    
    # Test 1: Cálculo básico
    result = service.calc_forward(
        spot=4250.0,
        tasa_dom=0.12,
        tasa_ext=0.05,
        plazo_dias=90
    )
    
    print("\nTest 1: Cálculo básico")
    print(f"   Spot: 4250.0")
    print(f"   Tasa doméstica: 12%")
    print(f"   Tasa extranjera: 5%")
    print(f"   Plazo: 90 días")
    print(f"\n   Resultados:")
    print(f"   [OK] Tasa Forward: {result['tasa_fwd']:,.6f}")
    print(f"   [OK] Puntos: {result['puntos']:,.6f}")
    print(f"   [OK] Fair Value: $ {result['fair_value']:,.2f}")
    
    assert result['tasa_fwd'] > result['puntos'], "La tasa forward debe ser mayor que los puntos"
    assert result['puntos'] > 0, "Los puntos deben ser positivos con tasa doméstica mayor"
    
    # Test 2: Cálculo desde simulación
    fila_sim = {
        "spot": 4250.5,
        "tasa_ibr": 0.115,
        "nominal_usd": 100000
    }
    
    result2 = service.calc_forward_from_simulation(fila_sim)
    
    print("\nTest 2: Cálculo desde fila de simulación")
    print(f"   ✓ Tasa Forward: {result2['tasa_fwd']:,.6f}")
    print(f"   ✓ Puntos: {result2['puntos']:,.6f}")
    print(f"   ✓ Fair Value: $ {result2['fair_value']:,.2f}")
    
    print("\n✅ ForwardPricingService: PASADO")


def test_exposure_service():
    """Prueba el servicio de exposición."""
    print("\n" + "="*60)
    print("TEST: ExposureService")
    print("="*60)
    
    service = ExposureService()
    
    # Test 1: Exposición simulada
    fila_sim = {
        "nominal_usd": 100000,
        "spot": 4250.0
    }
    
    exposicion = service.calc_simulated_exposure(fila_sim)
    
    print("\nTest 1: Exposición de simulación")
    print(f"   Nominal USD: $ {fila_sim['nominal_usd']:,.2f}")
    print(f"   Spot: {fila_sim['spot']:,.2f}")
    print(f"   Factor de exposición: 15%")
    print(f"\n   ✓ Exposición: $ {exposicion:,.2f}")
    
    expected = 100000 * 4250.0 * 0.15
    assert abs(exposicion - expected) < 1, "Cálculo de exposición incorrecto"
    
    # Test 2: Disponibilidad
    result = service.calc_disponibilidad(
        outstanding=1000000.0,
        exposicion_simulada=500000.0,
        linea_credito=5000000000.0,
        colchon_pct=0.10
    )
    
    print("\nTest 2: Cálculo de disponibilidad")
    print(f"   Outstanding: $ {result['outstanding']:,.2f}")
    print(f"   Exposición simulada: $ {result['exposicion_simulada']:,.2f}")
    print(f"   Total con simulación: $ {result['total_con_simulacion']:,.2f}")
    print(f"   Límite máximo: $ {result['limite_max']:,.2f}")
    print(f"   Disponibilidad: $ {result['disponibilidad']:,.2f}")
    print(f"   Utilización: {result['utilizacion_pct']:.2f}%")
    
    assert result['total_con_simulacion'] == 1500000.0, "Total mal calculado"
    assert result['limite_max'] == 4500000000.0, "Límite mal calculado"
    assert result['disponibilidad'] > 0, "Disponibilidad debe ser positiva"
    
    print("\n✅ ExposureService: PASADO")


def test_client_service():
    """Prueba el servicio de clientes."""
    print("\n" + "="*60)
    print("TEST: ClientService")
    print("="*60)
    
    service = ClientService()
    
    # Test 1: Obtener cliente por NIT
    nit = "123456789"
    client = service.get_client_by_nit(nit)
    
    print(f"\nTest 1: Obtener cliente por NIT ({nit})")
    print(f"   ✓ Nombre: {client['nombre']}")
    print(f"   ✓ Línea de crédito: $ {client['linea_credito']:,.2f}")
    print(f"   ✓ Colchón interno: {client['colchon_interno']*100:.1f}%")
    print(f"   ✓ Rating: {client['rating']}")
    
    assert client is not None, "Cliente debe existir"
    assert client['linea_credito'] > 0, "Línea de crédito debe ser positiva"
    
    # Test 2: Obtener límites
    limits = service.get_client_limits(nit)
    
    print(f"\nTest 2: Obtener límites del cliente ({nit})")
    print(f"   ✓ Línea de crédito: $ {limits['linea_credito']:,.2f}")
    print(f"   ✓ Colchón interno: {limits['colchon_pct']:.1f}%")
    print(f"   ✓ Límite máximo: $ {limits['limite_max']:,.2f}")
    
    expected_limite = client['linea_credito'] * (1 - client['colchon_interno'])
    assert abs(limits['limite_max'] - expected_limite) < 1, "Límite máximo mal calculado"
    
    # Test 3: Listar todos los clientes
    all_clients = service.get_all_clients()
    
    print(f"\nTest 3: Listar todos los clientes")
    print(f"   ✓ Total de clientes: {len(all_clients)}")
    
    for c in all_clients:
        print(f"      - {c['nit']}: {c['nombre']}")
    
    assert len(all_clients) == 3, "Debe haber 3 clientes mock"
    
    print("\n✅ ClientService: PASADO")


def test_integration():
    """Prueba integración completa simulando run_simulations()."""
    print("\n" + "="*60)
    print("TEST: Integración Completa (Simular run_simulations)")
    print("="*60)
    
    pricing = ForwardPricingService()
    exposure = ExposureService()
    client_service = ClientService()
    
    # Datos de simulaciones dummy
    simulaciones = [
        {
            "cliente": "Cliente Ejemplo S.A.",
            "nominal_usd": 100000,
            "spot": 4250.5,
            "tasa_ibr": 0.112
        },
        {
            "cliente": "Corporación ABC Ltda.",
            "nominal_usd": 50000,
            "spot": 4250.5,
            "tasa_ibr": 0.115
        },
        {
            "cliente": "Empresa XYZ S.A.S.",
            "nominal_usd": 75000,
            "spot": 4250.5,
            "tasa_ibr": 0.110
        }
    ]
    
    print(f"\n📊 Procesando {len(simulaciones)} simulaciones...\n")
    
    exposicion_total = 0.0
    
    for idx, sim in enumerate(simulaciones, 1):
        print(f"   Simulación {idx}:")
        print(f"      Cliente: {sim['cliente']}")
        print(f"      Nominal: $ {sim['nominal_usd']:,.2f}")
        
        # Calcular pricing
        pricing_result = pricing.calc_forward_from_simulation(sim)
        sim['tasa_fwd'] = pricing_result['tasa_fwd']
        sim['puntos'] = pricing_result['puntos']
        sim['fair_value'] = pricing_result['fair_value']
        
        print(f"      ✓ Tasa Fwd: {sim['tasa_fwd']:,.6f}")
        print(f"      ✓ Puntos: {sim['puntos']:,.6f}")
        print(f"      ✓ Fair Value: $ {sim['fair_value']:,.2f}")
        
        # Calcular exposición
        exp = exposure.calc_simulated_exposure(sim)
        exposicion_total += exp
        
        print(f"      ✓ Exposición: $ {exp:,.2f}\n")
    
    # Calcular disponibilidad
    nit = "123456789"
    limits = client_service.get_client_limits(nit)
    outstanding = 100000.0  # Mock
    
    disp = exposure.calc_disponibilidad(
        outstanding=outstanding,
        exposicion_simulada=exposicion_total,
        linea_credito=limits['linea_credito'],
        colchon_pct=limits['colchon_interno']
    )
    
    print("📈 Métricas Finales:")
    print(f"   Outstanding: $ {disp['outstanding']:,.2f}")
    print(f"   Exposición simulada: $ {disp['exposicion_simulada']:,.2f}")
    print(f"   Total con simulación: $ {disp['total_con_simulacion']:,.2f}")
    print(f"   Límite máximo: $ {disp['limite_max']:,.2f}")
    print(f"   Disponibilidad: $ {disp['disponibilidad']:,.2f}")
    print(f"   Utilización: {disp['utilizacion_pct']:.2f}%")
    
    assert disp['disponibilidad'] > 0, "Debe haber disponibilidad positiva"
    assert disp['utilizacion_pct'] < 100, "Utilización debe ser menor a 100%"
    
    print("\n✅ Integración Completa: PASADO")


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "="*60)
    print("PRUEBAS DE SERVICIOS MOCK")
    print("="*60)
    
    try:
        test_forward_pricing_service()
        test_exposure_service()
        test_client_service()
        test_integration()
        
        print("\n" + "="*60)
        print("TODAS LAS PRUEBAS PASARON")
        print("="*60 + "\n")
        
        return 0
    
    except AssertionError as e:
        print(f"\n❌ PRUEBA FALLIDA: {e}")
        return 1
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

