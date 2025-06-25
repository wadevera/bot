import math
import time
from MargenConsultas import MargenConsultas
from FuturosConsultas import FuturosConsultas 
from BinanceAPI import BinanceAPI

class MargenBot:
    def __init__(self):
        self.client = BinanceAPI().get_client()
        self.consultas = MargenConsultas()
        self.consultas_futuros = FuturosConsultas()
        self.registro_operaciones = []
    
    def obtener_saldo(self, activo: str) -> float:
        """Obtiene el saldo disponible de un activo en margen"""
        saldos = self.consultas.obtener_saldo_margen()
        return saldos.get(activo, 0.0)
    
    def obtener_precio(self, simbolo: str) -> float:
        """Obtiene el precio actual de un símbolo"""
        return self.consultas.obtener_precio_actual(simbolo)
    def obtener_precision_activo(self, activo: str) -> int:
        """Obtiene la precisión decimal permitida para un activo"""
        # Binance requiere diferentes precisiones para diferentes activos
        precisiones = {
            'BTC': 6,    # 8 decimales pero en trading suelen ser 6
            'ETH': 4,
            'RONIN': 0,  # RONIN solo permite números enteros
            'USDT': 2
        }
        return precisiones.get(activo.upper(), 2)  # Por defecto 2 decimales
    
    def ajustar_cantidad(self, activo: str, cantidad: float) -> float:
        """Ajusta la cantidad a la precisión permitida por el activo"""
        precision = self.obtener_precision_activo(activo)
        
        if activo == 'RONIN':
            # Para RONIN, debe ser un número entero (sin decimales)
            return math.floor(cantidad)
        
        # Para otros activos, redondear a la precisión permitida
        return round(cantidad, precision)
    
    def comprar_mercado(self, simbolo: str, cantidad: float):
        """Coloca una orden de compra a mercado en margen"""
        lado = 'BUY'
        base = simbolo.replace('USDT', '')
        
        # Ajustar cantidad según precisión permitida
        cantidad_ajustada = self.ajustar_cantidad(base, cantidad)
        print(f"Cantidad ajustada para {base}: {cantidad} → {cantidad_ajustada}")
        
        try:
            orden = self.consultas.colocar_orden_margen_mercado(
                symbol=simbolo,
                side=lado,
                quantity=cantidad_ajustada
            )
            self.registro_operaciones.append(('COMPRA', base, cantidad_ajustada, self.obtener_precio(simbolo)))
            return orden
        except Exception as e:
            print(f"Error en compra: {e}")
            return None
    
    def vender_mercado(self, simbolo: str, cantidad: float):
        """Coloca una orden de venta a mercado en margen"""
        lado = 'SELL'
        base = simbolo.replace('USDT', '')
        
        # Ajustar cantidad según precisión permitida
        cantidad_ajustada = self.ajustar_cantidad(base, cantidad)
        print(f"Cantidad ajustada para {base}: {cantidad} → {cantidad_ajustada}")
        
        try:
            orden = self.consultas.colocar_orden_margen_mercado(
                symbol=simbolo,
                side=lado,
                quantity=cantidad_ajustada
            )
            self.registro_operaciones.append(('VENTA', base, cantidad_ajustada, self.obtener_precio(simbolo)))
            return orden
        except Exception as e:
            print(f"Error en venta: {e}")
            return None

    def comprar_ronin_con_btc_futuros(self):
        """Compra RONIN usando BTC en futuros (conversión en dos pasos)"""
        print("\n=== COMPRA FUTUROS RONIN CON BTC ===")
        
        try:
            # 1. Obtener saldo BTC en futuros
            saldo_btc = self.consultas_futuros.obtener_saldo_futuros('BTC')
            if saldo_btc <= 0:
                print("Error: No hay saldo de BTC en futuros")
                return False
            
            # Obtener precio actual de BTC/USDT
            precio_btc_usdt = self.consultas_futuros.obtener_precio_actual('BTCUSDT')
            print(f"Saldo BTC en futuros: {saldo_btc:.6f} | Precio: {precio_btc_usdt:.2f} USDT")
            
            # 2. Vender BTC por USDT en futuros
            print("Vendiendo BTC por USDT en futuros...")
            orden_venta_btc = self.operar_en_mercado(
                simbolo='BTCUSDT',
                accion='vender',
                cantidad=saldo_btc,
                tipo="futuros"
            )
            
            if not orden_venta_btc:
                print("Error al vender BTC en futuros")
                return False
            
            # Esperar y obtener nuevo saldo USDT en futuros
            time.sleep(3)
            saldo_usdt = self.consultas_futuros.obtener_saldo_futuros('USDT')
            print(f"USDT obtenidos en futuros: {saldo_usdt:.2f}")
            
            # 3. Comprar RONIN con USDT en futuros
            print("Comprando RONIN con USDT en futuros...")
            precio_ronin = self.consultas_futuros.obtener_precio_actual('RONINUSDT')
            
            # Calcular cantidad de RONIN (ajustar a enteros)
            cantidad_ronin = math.floor(saldo_usdt / precio_ronin)
            
            orden_compra_ronin = self.operar_en_mercado(
                simbolo='RONINUSDT',
                accion='comprar',
                cantidad=cantidad_ronin,
                tipo="futuros"
            )
            
            if not orden_compra_ronin:
                print("Error al comprar RONIN en futuros")
                return False
            
            # 4. Mostrar resultados
            print("\nResultado de la operación en futuros:")
            print(f"BTC iniciales: {saldo_btc:.6f}")
            print(f"RONIN comprados: {cantidad_ronin:.0f}")
            print(f"Precio promedio RONIN: {precio_ronin:.4f} USDT")
            
            # Registrar operación
            self.registro_operaciones.append((
                'COMPRA FUTUROS', 
                'RONIN', 
                cantidad_ronin, 
                precio_ronin,
                time.time()
            ))
            
            return True
        
        except Exception as e:
            print(f"Error en compra futuros RONIN con BTC: {str(e)}")
            return False   
             
    def comprar_ronin_con_btc(self):
        """Compra RONIN usando BTC a través de USDT (conversión en dos pasos)"""
        print("\n=== COMPRA RONIN CON BTC ===")
        
        # 1. Obtener saldo BTC
        saldo_btc = self.obtener_saldo('BTC')
        if saldo_btc <= 0:
            print("Error: No hay saldo de BTC")
            return False
        
        precio_btc_usdt = self.obtener_precio('BTCUSDT')
        print(f"Saldo BTC: {saldo_btc:.6f} | Precio: {precio_btc_usdt:.2f} USDT")
        
        # 2. Vender BTC por USDT
        print("Vendiendo BTC por USDT...")
        orden_venta_btc = self.vender_mercado('BTCUSDT', saldo_btc)
        if not orden_venta_btc:
            return False
        
        # Esperar y obtener nuevo saldo USDT
        time.sleep(3)
        saldo_usdt = self.obtener_saldo('USDT')
        print(f"USDT obtenidos: {saldo_usdt:.2f}")
        
        # 3. Comprar RONIN con USDT
        print("Comprando RONIN con USDT...")
        precio_ronin = self.obtener_precio('RONINUSDT')
        cantidad_ronin = math.floor(saldo_usdt / precio_ronin)
        
        orden_compra_ronin = self.comprar_mercado('RONINUSDT', cantidad_ronin)
        if not orden_compra_ronin:
            return False
        
        # 4. Mostrar resultados
        print("\nResultado de la operación:")
        print(f"BTC iniciales: {saldo_btc:.6f}")
        print(f"RONIN comprados: {cantidad_ronin:.2f}")
        print(f"Precio promedio RONIN: {precio_ronin:.4f} USDT")
        
        return True
    
    def vender_ronin_por_btc_futuros(self):
        """Vende RONIN y compra BTC en futuros"""
        if not self.consultas_futuros:
            print("Error: Servicio de futuros no disponible")
            return False
            
        print("\n=== VENTA FUTUROS RONIN POR BTC ===")
        
        try:
            # 1. Obtener saldo RONIN en futuros
            saldo_ronin = self.consultas_futuros.obtener_saldo_futuros('RONIN')
            if saldo_ronin <= 0:
                print("Error: No hay saldo de RONIN en futuros")
                return False
            
            # ... (resto de la implementación que ya tenías)
            
        
        
            # 2. Vender RONIN por USDT en futuros
            self.operar_en_mercado('RONINUSDT', 'vender', saldo_ronin, tipo="futuros")
            
            # 3. Obtener nuevo saldo USDT en futuros
            time.sleep(3)
            saldo_usdt = self.consultas_futuros.obtener_saldo_futuros('USDT')
            
            # 4. Comprar BTC con USDT en futuros
            precio_btc = self.consultas_futuros.obtener_precio_actual('BTCUSDT')
            cantidad_btc = saldo_usdt / precio_btc
            self.operar_en_mercado('BTCUSDT', 'comprar', cantidad_btc, tipo="futuros")
                        
            return True

        except Exception as e:
            print(f"Error en venta futuros: {str(e)}")
            return False
        

    def vender_ronin_por_btc(self):
        """Vende RONIN y compra BTC a través de USDT (conversión en dos pasos)"""
        print("\n=== VENTA RONIN POR BTC ===")
        
        # 1. Obtener saldo RONIN
        saldo_ronin = self.obtener_saldo('RONIN')
        if saldo_ronin <= 0:
            print("Error: No hay saldo de RONIN")
            return False
        
        precio_ronin = self.obtener_precio('RONINUSDT')
        print(f"Saldo RONIN: {saldo_ronin:.2f} | Precio: {precio_ronin:.4f} USDT")
        
        # 2. Vender RONIN por USDT
        print("Vendiendo RONIN por USDT...")
        orden_venta_ronin = self.vender_mercado('RONINUSDT', saldo_ronin)
        if not orden_venta_ronin:
            return False
        
        # Esperar y obtener nuevo saldo USDT
        time.sleep(3)
        saldo_usdt = self.obtener_saldo('USDT')
        print(f"USDT obtenidos: {saldo_usdt:.2f}")
        
        # 3. Comprar BTC con USDT
        print("Comprando BTC con USDT...")
        precio_btc = self.obtener_precio('BTCUSDT')
        cantidad_btc = saldo_usdt / precio_btc
        
        orden_compra_btc = self.comprar_mercado('BTCUSDT', cantidad_btc)
        if not orden_compra_btc:
            return False
        
        # 4. Mostrar resultados
        print("\nResultado de la operación:")
        print(f"RONIN vendidos: {saldo_ronin:.2f}")
        print(f"BTC comprados: {cantidad_btc:.6f}")
        print(f"Precio promedio BTC: {precio_btc:.2f} USDT")
        
        return True
    
    def ejecutar_comando(self, comando: str):
        """Ejecuta un comando basado en texto"""
        comando = comando.lower().strip()
        
        if comando in ["comprar ronin", "comprar roninbtc", "buy ronin"]:
            return self.comprar_ronin_con_btc()
        
        elif comando in ["vender ronin", "vender roninbtc", "sell ronin"]:
            return self.vender_ronin_por_btc()
        
        elif "comprar" in comando or "vender" in comando:
            # Manejo de otros pares (implementación básica)
            partes = comando.split()
            if len(partes) < 2:
                print("Comando inválido. Formato: [comprar/vender] [activo]")
                return False
            
            accion = partes[0]
            activo = partes[1].upper()
            
            if "USDT" not in activo:
                activo += "USDT"
            
            saldo = self.obtener_saldo(activo.replace('USDT', ''))
            
            if saldo <= 0 and accion == "vender":
                print(f"No hay saldo de {activo} para vender")
                return False
            
            if accion == "comprar":
                precio = self.obtener_precio(activo)
                saldo_usdt = self.obtener_saldo('USDT')
                cantidad = math.floor(saldo_usdt * 0.99 / precio)
                return self.comprar_mercado(activo, cantidad)
            
            elif accion == "vender":
                return self.vender_mercado(activo, saldo * 0.99)
        
        else:
            print("Comando no reconocido")
            return False
    
    def mostrar_resumen_operaciones(self):
        """Muestra un resumen de todas las operaciones realizadas"""
        if not self.registro_operaciones:
            print("No se han realizado operaciones")
            return
        
        print("\nResumen de operaciones:")
        for idx, op in enumerate(self.registro_operaciones, 1):
            tipo, activo, cantidad, precio = op
            print(f"{idx}. {tipo} {cantidad} {activo} @ {precio} USDT")

    def Entrar(self, mensaje: str):
        """Método principal que procesa todos los tipos de mensajes"""
        # Convertir a minúsculas y eliminar espacios adicionales
        mensaje = mensaje.lower().strip()
        print(f"Procesando comando: '{mensaje}'")
        
        # Determinar el tipo de operación (margen o futuros)
        tipo_operacion = "margen"
        if "btc" in mensaje or "futuros" in mensaje:
            tipo_operacion = "futuros"
        
        # Manejo de mensajes específicos
        if "ronusdt" in mensaje or "roninusdt" in mensaje:
            if "compra" in mensaje or "comprar" in mensaje or "buy" in mensaje:
                return self.operacion_margen_directa('RONINUSDT', 'comprar')
            elif "venta" in mensaje or "vender" in mensaje or "sell" in mensaje:
                return self.operacion_margen_directa('RONINUSDT', 'vender')
        
        elif "roninbtc" in mensaje:
            if "compra" in mensaje or "comprar" in mensaje or "buy" in mensaje:
                if tipo_operacion == "futuros":
                    return self.comprar_ronin_con_btc_futuros()
                else:
                    return self.comprar_ronin_con_btc()
            elif "venta" in mensaje or "vender" in mensaje or "sell" in mensaje:
                if tipo_operacion == "futuros":
                    return self.vender_ronin_por_btc_futuros()
                else:
                    return self.vender_ronin_por_btc()
    
    
    def operacion_margen_directa(self, simbolo: str, accion: str):
        """Maneja operaciones directas en margen"""
        # Normalizar el símbolo
        if "USDT" not in simbolo:
            simbolo = simbolo.upper() + "USDT"
        else:
            simbolo = simbolo.upper()
            
        base = simbolo.replace('USDT', '')
        print(f"Operación directa en margen: {accion} {simbolo}")
        
        if accion == 'comprar':
            precio = self.obtener_precio(simbolo)
            saldo_usdt = self.obtener_saldo('USDT')
            
            if saldo_usdt <= 0:
                print("Error: No hay saldo de USDT para comprar")
                return False
                
            cantidad = math.floor(saldo_usdt * 0.99 / precio)
            return self.comprar_mercado(simbolo, cantidad)
        
        elif accion == 'vender':
            saldo_base = self.obtener_saldo(base)
            
            if saldo_base <= 0:
                print(f"Error: No hay saldo de {base} para vender")
                return False
                
            return self.vender_mercado(simbolo, saldo_base * 0.99)