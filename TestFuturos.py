from FuturosOperaciones import FuturosOperaciones
from SpotTrading import SpotTrading
import time
import math

class TestFuturos:
    def __init__(self):
        self.operador = FuturosOperaciones()
        self.spot = SpotTrading()
        self.pares = ['BTCUSDT', 'RONINUSDT']
        self.futuros = self.operador.futuros
        self.registro_operaciones = []
    
    def obtener_saldos_y_posiciones(self):
        resultados = {}
        saldo_usdt = self.futuros.obtener_saldo_futuros(asset='USDT')
        resultados['USDT'] = {'saldo_disponible': saldo_usdt}
        
        for par in self.pares:
            resultados[par] = {}
            precio = self.futuros.obtener_precio_actual(par)
            resultados[par]['precio_actual'] = precio
            
            posicion = self.futuros.obtener_posicion(par)
            resultados[par]['posicion'] = posicion
            
            if posicion and precio and 'cantidad' in posicion and 'entrada' in posicion:
                cantidad = abs(float(posicion['cantidad']))
                valor_posicion = cantidad * precio
                resultados[par]['valor_posicion_usdt'] = valor_posicion
                
                entrada = posicion['entrada']
                if posicion['lado'] == 'LONG':
                    pnl = (precio - entrada) * cantidad
                else:
                    pnl = (entrada - precio) * cantidad
                resultados[par]['pnl_aproximado'] = pnl
            else:
                resultados[par]['valor_posicion_usdt'] = None
                resultados[par]['pnl_aproximado'] = None
            
            ordenes = self.futuros.obtener_ordenes_abiertas_futuros(symbol=par)
            resultados[par]['ordenes_abiertas'] = ordenes
        
        return resultados
    
    def imprimir_resumen(self):
        datos = self.obtener_saldos_y_posiciones()
        
        print("\n" + "="*60)
        print("RESUMEN DE FUTUROS")
        print("="*60)
        
        usdt_info = datos['USDT']
        print(f"\nSaldo disponible en USDT: {usdt_info['saldo_disponible']:.2f}")
        
        for par in self.pares:
            print("\n" + "-"*60)
            print(f"PAR: {par}")
            print("-"*60)
            
            par_info = datos[par]
            precio = par_info.get('precio_actual', 'N/A')
            print(f"Precio actual: {precio}")
            
            posicion = par_info.get('posicion', {})
            if posicion and 'lado' in posicion and 'cantidad' in posicion and abs(float(posicion['cantidad'])) > 0:
                print(f"\nPOSICIÓN ABIERTA:")
                print(f"Lado: {posicion['lado']}")
                print(f"Cantidad: {abs(float(posicion['cantidad']))}")
                if 'entrada' in posicion:
                    print(f"Precio entrada: {posicion['entrada']}")
                if par_info.get('valor_posicion_usdt') is not None:
                    print(f"Valor posición: ${par_info['valor_posicion_usdt']:.2f} USDT")
                if par_info.get('pnl_aproximado') is not None:
                    print(f"P&L aproximado: ${par_info['pnl_aproximado']:.2f}")
                if 'apalancamiento' in posicion:
                    print(f"Apalancamiento: {posicion['apalancamiento']}x")
            else:
                print("\nSIN POSICIÓN ABIERTA")
            
            ordenes = par_info.get('ordenes_abiertas', [])
            print(f"\nÓRDENES ABIERTAS ({len(ordenes)}):")
            for orden in ordenes:
                tipo = orden.get('type', 'MARKET').capitalize()
                lado = orden.get('side', 'N/A')
                cantidad = orden.get('origQty', 'N/A')
                precio = orden.get('price', 'MARKET')
                print(f"→ {tipo} {lado} {cantidad} @ {precio}")
    
    def ejecutar_operacion(self, operacion, porcentaje=1.0, apalancamiento=1):
        if operacion == 'comprar_btc':
            return self.operador.comprar_btc(porcentaje, apalancamiento)
        elif operacion == 'vender_btc':
            return self.operador.vender_btc(porcentaje, apalancamiento)
        elif operacion == 'comprar_ronin':
            return self.operador.comprar_ronin(porcentaje, apalancamiento)
        elif operacion == 'vender_ronin':
            return self.operador.vender_ronin(porcentaje, apalancamiento)
        else:
            print(f"Operación no reconocida: {operacion}")
            return None
    
    def obtener_saldo_disponible_usdt(self):
        """Obtiene el saldo disponible en USDT considerando el margen utilizado"""
        try:
            account_info = self.futuros.client.futures_account()
            for asset in account_info['assets']:
                if asset['asset'] == 'USDT':
                    return float(asset['availableBalance'])
            return 0.0
        except Exception as e:
            print(f"Error al obtener saldo disponible: {e}")
            return 0.0
    
    def realizar_prueba_conversion_btc_a_ronin(self):
        """Realiza la prueba de conversión BTC -> RONIN"""
        # 1. Obtener posición actual de BTC
        pos_btc = self.futuros.obtener_posicion('BTCUSDT')
        if not pos_btc or abs(float(pos_btc.get('cantidad', 0))) == 0:
            print("Error: No tienes posición de BTC para comenzar la prueba")
            return False
        
        saldo_btc = abs(float(pos_btc['cantidad']))
        precio_compra_btc = float(pos_btc['entrada']) if 'entrada' in pos_btc else 0.0
        self.registro_operaciones.append(('POSICION INICIAL', 'BTC', saldo_btc, precio_compra_btc))
        print(f"BTC iniciales: {saldo_btc:.8f} comprados a {precio_compra_btc:.2f} USDT")
        
        # 2. Obtener precio spot RONIN/BTC
        print("\n=== PASO 1: OBTENER PRECIO SPOT RONIN/BTC ===")
        try:
            precio_spot_ronin_btc = self.spot.obtener_precio_actual('RONINBTC')
        except:
            precio_spot_ronin_btc = None
            
        if not precio_spot_ronin_btc:
            print("Error al obtener precio spot RONIN/BTC")
            return False
        
        # Calcular RONIN teóricos que se podrían comprar
        ronin_teorico = saldo_btc / precio_spot_ronin_btc
        print(f"Precio spot RONIN/BTC: {precio_spot_ronin_btc:.8f}")
        print(f"RONIN teóricos (spot): {ronin_teorico:.2f}")
        self.registro_operaciones.append(('CALCULO TEORICO', 'RONIN', ronin_teorico, precio_spot_ronin_btc))
        
        # 3. Vender BTC a USDT
        print("\n=== PASO 2: VENDER BTC POR USDT ===")
        orden_venta_btc = self.ejecutar_operacion('vender_btc', 1.0, 1)
        if not orden_venta_btc:
            print("Error al vender BTC")
            return False
        
        # Esperar y obtener nuevo saldo USDT
        time.sleep(5)
        saldo_usdt = self.obtener_saldo_disponible_usdt()
        try:
            precio_venta_btc = self.futuros.obtener_precio_actual('BTCUSDT')
        except:
            precio_venta_btc = 0.0
        self.registro_operaciones.append(('VENTA BTC', 'USDT', saldo_usdt, precio_venta_btc))
        print(f"USDT después de vender BTC: {saldo_usdt:.2f}")
        
        # 4. Comprar RONIN con márgenes de seguridad
        print("\n=== PASO 3: COMPRAR RONIN ===")
        porcentajes_intento = [0.98, 0.95, 0.90, 0.85]
        orden_compra_ronin = None
        
        for porcentaje in porcentajes_intento:
            print(f"Intentando comprar con {porcentaje*100:.0f}% del saldo...")
            orden_compra_ronin = self.ejecutar_operacion('comprar_ronin', porcentaje, 1)
            if orden_compra_ronin:
                break
            time.sleep(1)
        
        if not orden_compra_ronin:
            print("Error al comprar RONIN después de múltiples intentos")
            return False
        
        # Esperar y obtener posición RONIN
        time.sleep(5)
        pos_ronin = self.futuros.obtener_posicion('RONINUSDT')
        if not pos_ronin or abs(float(pos_ronin.get('cantidad', 0))) == 0:
            print("Error: No se obtuvo posición de RONIN después de comprar")
            return False
        
        saldo_ronin = abs(float(pos_ronin['cantidad']))
        precio_compra_ronin = float(pos_ronin['entrada']) if 'entrada' in pos_ronin else 0.0
        self.registro_operaciones.append(('COMPRA RONIN', 'RONIN', saldo_ronin, precio_compra_ronin))
        print(f"RONIN comprados: {saldo_ronin:.2f} a {precio_compra_ronin:.4f} USDT")
        
        # 5. Calcular resultados
        print("\n=== RESULTADOS DE LA PRUEBA ===")
        self.calcular_resultados_btc_a_ronin(ronin_teorico, saldo_ronin, precio_compra_ronin)
        
        return True
    
    def calcular_resultados_btc_a_ronin(self, ronin_teorico, ronin_real, precio_ronin_final):
        """Calcula y muestra los resultados de la prueba BTC->RONIN"""
        # 1. Calcular pérdida por conversión
        diferencia_ronin = ronin_teorico - ronin_real
        porcentaje_perdida = (diferencia_ronin / ronin_teorico) * 100 if ronin_teorico != 0 else 0
        
        print(f"\nRONIN teóricos (spot): {ronin_teorico:.2f}")
        print(f"RONIN reales (futuros): {ronin_real:.2f}")
        print(f"Diferencia: {diferencia_ronin:.2f} RONIN ({porcentaje_perdida:.2f}%)")
        
        # 2. Calcular pérdida en USDT
        valor_teorico_usdt = ronin_teorico * precio_ronin_final
        valor_real_usdt = ronin_real * precio_ronin_final
        diferencia_usdt = valor_teorico_usdt - valor_real_usdt
        
        print(f"\nValor teórico (USDT): ${valor_teorico_usdt:.2f}")
        print(f"Valor real (USDT): ${valor_real_usdt:.2f}")
        print(f"Diferencia: ${diferencia_usdt:.2f}")
        
        # 3. Calcular eficiencia de la conversión
        eficiencia = (ronin_real / ronin_teorico) * 100 if ronin_teorico != 0 else 0
        print(f"\nEficiencia de conversión: {eficiencia:.2f}%")
        
        # 4. Registrar saldo final
        saldo_final_usdt = self.obtener_saldo_disponible_usdt()
        self.registro_operaciones.append(('FINAL', 'USDT', saldo_final_usdt, None))
        print(f"\nSaldo final USDT: ${saldo_final_usdt:.2f}")
        
        # 5. Mostrar resumen de operaciones
        print("\nResumen de operaciones:")
        for op in self.registro_operaciones:
            if op[0] in ['INICIO', 'FINAL']:
                print(f"- {op[0]}: {op[2]:.2f} {op[1]}")
            elif op[0] == 'CALCULO TEORICO':
                print(f"- {op[0]}: {op[2]:.2f} {op[1]} @ {op[3]:.8f} BTC")
            else:
                if op[3] is None:
                    print(f"- {op[0]}: {op[2]:.2f} {op[1]}")
                else:
                    print(f"- {op[0]}: {op[2]:.2f} {op[1]} @ {op[3]:.8f} USDT")
    
    def realizar_prueba_conversion_ronin_a_btc(self):
        """Realiza la prueba de conversión RONIN -> BTC"""
        # 1. Obtener posición actual de RONIN
        pos_ronin = self.futuros.obtener_posicion('RONINUSDT')
        if not pos_ronin or abs(float(pos_ronin.get('cantidad', 0))) == 0:
            print("Error: No tienes posición de RONIN para comenzar la prueba")
            return False
        
        saldo_ronin = abs(float(pos_ronin['cantidad']))
        precio_compra_ronin = float(pos_ronin['entrada']) if 'entrada' in pos_ronin else 0.0
        self.registro_operaciones.append(('POSICION INICIAL', 'RONIN', saldo_ronin, precio_compra_ronin))
        print(f"RONIN iniciales: {saldo_ronin:.2f} comprados a {precio_compra_ronin:.4f} USDT")
        
        # 2. Obtener precio spot RONIN/BTC
        print("\n=== PASO 1: OBTENER PRECIO SPOT RONIN/BTC ===")
        try:
            precio_spot_ronin_btc = self.spot.obtener_precio_actual('RONINBTC')
        except:
            precio_spot_ronin_btc = None
            
        if not precio_spot_ronin_btc:
            print("Error al obtener precio spot RONIN/BTC")
            return False
        
        # Calcular BTC teóricos que se podrían comprar
        btc_teorico = saldo_ronin * precio_spot_ronin_btc
        print(f"Precio spot RONIN/BTC: {precio_spot_ronin_btc:.8f}")
        print(f"BTC teóricos (spot): {btc_teorico:.8f}")
        self.registro_operaciones.append(('CALCULO TEORICO', 'BTC', btc_teorico, precio_spot_ronin_btc))
        
        # 3. Vender RONIN a USDT
        print("\n=== PASO 2: VENDER RONIN POR USDT ===")
        orden_venta_ronin = self.ejecutar_operacion('vender_ronin', 1.0, 1)
        if not orden_venta_ronin:
            print("Error al vender RONIN")
            return False
        
        # Esperar y obtener nuevo saldo USDT
        time.sleep(5)
        saldo_usdt = self.obtener_saldo_disponible_usdt()
        try:
            precio_venta_ronin = self.futuros.obtener_precio_actual('RONINUSDT')
        except:
            precio_venta_ronin = 0.0
        self.registro_operaciones.append(('VENTA RONIN', 'USDT', saldo_usdt, precio_venta_ronin))
        print(f"USDT después de vender RONIN: {saldo_usdt:.2f}")
        
        # 4. Comprar BTC con márgenes de seguridad
        print("\n=== PASO 3: COMPRAR BTC ===")
        porcentajes_intento = [0.98, 0.95, 0.90, 0.85]
        orden_compra_btc = None
        
        for porcentaje in porcentajes_intento:
            print(f"Intentando comprar con {porcentaje*100:.0f}% del saldo...")
            orden_compra_btc = self.ejecutar_operacion('comprar_btc', porcentaje, 1)
            if orden_compra_btc:
                break
            time.sleep(1)
        
        if not orden_compra_btc:
            print("Error al comprar BTC después de múltiples intentos")
            return False
        
        # Esperar y obtener posición BTC
        time.sleep(5)
        pos_btc = self.futuros.obtener_posicion('BTCUSDT')
        if not pos_btc or abs(float(pos_btc.get('cantidad', 0))) == 0:
            print("Error: No se obtuvo posición de BTC después de comprar")
            return False
        
        saldo_btc = abs(float(pos_btc['cantidad']))
        precio_compra_btc = float(pos_btc['entrada']) if 'entrada' in pos_btc else 0.0
        self.registro_operaciones.append(('COMPRA BTC', 'BTC', saldo_btc, precio_compra_btc))
        print(f"BTC comprados: {saldo_btc:.8f} a {precio_compra_btc:.2f} USDT")
        
        # 5. Calcular resultados
        print("\n=== RESULTADOS DE LA PRUEBA ===")
        self.calcular_resultados_ronin_a_btc(btc_teorico, saldo_btc, precio_compra_btc)
        
        return True
    
    def calcular_resultados_ronin_a_btc(self, btc_teorico, btc_real, precio_btc_final):
        """Calcula y muestra los resultados de la prueba RONIN->BTC"""
        # 1. Calcular pérdida por conversión
        diferencia_btc = btc_teorico - btc_real
        porcentaje_perdida = (diferencia_btc / btc_teorico) * 100 if btc_teorico != 0 else 0
        
        print(f"\nBTC teóricos (spot): {btc_teorico:.8f}")
        print(f"BTC reales (futuros): {btc_real:.8f}")
        print(f"Diferencia: {diferencia_btc:.8f} BTC ({porcentaje_perdida:.2f}%)")
        
        # 2. Calcular pérdida en USDT
        valor_teorico_usdt = btc_teorico * precio_btc_final
        valor_real_usdt = btc_real * precio_btc_final
        diferencia_usdt = valor_teorico_usdt - valor_real_usdt
        
        print(f"\nValor teórico (USDT): ${valor_teorico_usdt:.2f}")
        print(f"Valor real (USDT): ${valor_real_usdt:.2f}")
        print(f"Diferencia: ${diferencia_usdt:.2f}")
        
        # 3. Calcular eficiencia de la conversión
        eficiencia = (btc_real / btc_teorico) * 100 if btc_teorico != 0 else 0
        print(f"\nEficiencia de conversión: {eficiencia:.2f}%")
        
        # 4. Registrar saldo final
        saldo_final_usdt = self.obtener_saldo_disponible_usdt()
        self.registro_operaciones.append(('FINAL', 'USDT', saldo_final_usdt, None))
        print(f"\nSaldo final USDT: ${saldo_final_usdt:.2f}")
        
        # 5. Mostrar resumen de operaciones
        print("\nResumen de operaciones:")
        for op in self.registro_operaciones:
            if op[0] in ['INICIO', 'FINAL']:
                print(f"- {op[0]}: {op[2]:.2f} {op[1]}")
            elif op[0] == 'CALCULO TEORICO':
                print(f"- {op[0]}: {op[2]:.8f} {op[1]} @ {op[3]:.8f} (precio spot)")
            else:
                if op[3] is None:
                    print(f"- {op[0]}: {op[2]:.2f} {op[1]}")
                else:
                    print(f"- {op[0]}: {op[2]:.2f} {op[1]} @ {op[3]:.8f} USDT")
    
    def menu_interactivo(self):
        """Menú interactivo para operaciones manuales"""
        while True:
            print("\n" + "="*60)
            print("MENÚ PRINCIPAL - FUTUROS TRADING")
            print("="*60)
            print("1. Ver resumen de cuenta")
            print("2. Realizar prueba de conversión BTC->RONIN")
            print("3. Realizar prueba de conversión RONIN->BTC")
            print("4. Comprar BTC")
            print("5. Vender BTC")
            print("6. Comprar RONIN")
            print("7. Vender RONIN")
            print("8. Salir")
            
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == '1':
                self.imprimir_resumen()
            elif opcion == '2':
                self.registro_operaciones = []
                print("\n=== INICIANDO PRUEBA DE CONVERSIÓN BTC->RONIN ===")
                if self.realizar_prueba_conversion_btc_a_ronin():
                    print("\nPrueba completada con éxito!")
                    print("Resumen final:")
                    self.imprimir_resumen()
                else:
                    print("\nError durante la prueba")
            elif opcion == '3':
                self.registro_operaciones = []
                print("\n=== INICIANDO PRUEBA DE CONVERSIÓN RONIN->BTC ===")
                if self.realizar_prueba_conversion_ronin_a_btc():
                    print("\nPrueba completada con éxito!")
                    print("Resumen final:")
                    self.imprimir_resumen()
                else:
                    print("\nError durante la prueba")
            elif opcion in ['4', '5', '6', '7']:
                operaciones = {
                    '4': ('comprar_btc', 'BTC'),
                    '5': ('vender_btc', 'BTC'),
                    '6': ('comprar_ronin', 'RONIN'),
                    '7': ('vender_ronin', 'RONIN')
                }
                operacion, activo = operaciones[opcion]
                
                if operacion.startswith('comprar'):
                    default_porcentaje = 0.95
                    porcentaje_prompt = f"Porcentaje de saldo a usar (0-1, default: 0.95): "
                else:
                    default_porcentaje = 1.0
                    porcentaje_prompt = f"Porcentaje de posición a operar (0-1, default: 1.0): "
                
                porcentaje_input = input(porcentaje_prompt).strip()
                porcentaje = float(porcentaje_input) if porcentaje_input else default_porcentaje
                
                apalancamiento_input = input("Apalancamiento (default: 1): ").strip()
                apalancamiento = int(apalancamiento_input) if apalancamiento_input else 1
                
                print(f"\nIniciando operación: {operacion.replace('_', ' ')} {activo}...")
                orden = self.ejecutar_operacion(operacion, porcentaje, apalancamiento)
                
                if orden:
                    print("\nOperación exitosa! Resumen actualizado:")
                    self.imprimir_resumen()
            elif opcion == '8':
                print("Saliendo del programa...")
                break
            else:
                print("Opción no válida, por favor intente nuevamente")

if __name__ == "__main__":
    tester = TestFuturos()
    tester.menu_interactivo()