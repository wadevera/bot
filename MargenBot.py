import math
import time
from MargenConsultas import MargenConsultas
from FuturosConsultas import FuturosConsultas 
from FuturosOperaciones import FuturosOperaciones  
from BinanceAPI import BinanceAPI

class MargenBot:
    def __init__(self):
        self.consultas = MargenConsultas()
        self.consultas_futuros = FuturosConsultas()
        self.registro_operaciones = []
        self.registro_comparacion = []  # Nuevo registro para comparación de precios
        
        # Inicializa FuturosOperaciones
        self.futuros_ops = FuturosOperaciones()
    
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
        """Compra RONIN usando BTC en futuros con medición de precios"""
        print("\n=== COMPRA FUTUROS RONIN CON BTC ===")
        
        try:
            # Registrar hora de inicio
            start_time = time.time()
            
            # 1. Obtener precios de referencia antes de operar
            precio_btc_inicial = self.futuros_ops.futuros.obtener_precio_actual('BTCUSDT')
            precio_ronin_inicial = self.futuros_ops.futuros.obtener_precio_actual('RONINUSDT')
            
            # 2. Vender BTC
            print("Vendiendo BTC por USDT en futuros...")
            orden_venta_btc = self.futuros_ops.vender_btc(porcentaje=1.0)
            if not orden_venta_btc:
                print("Error al vender BTC en futuros")
                return False
            
            # 3. Obtener precio real de venta de BTC
            precio_btc_real = self.obtener_precio_real(orden_venta_btc)
            print(f"Precio referencia BTC: {precio_btc_inicial:.2f} | Precio real: {precio_btc_real:.2f}")
            
            # 4. Esperar y obtener USDT
            time.sleep(3)
            saldo_usdt = self.futuros_ops.futuros.obtener_saldo_futuros('USDT')
            print(f"USDT obtenidos: {saldo_usdt:.2f}")
            
            # 5. Comprar RONIN
            print("Comprando RONIN con USDT en futuros...")
            monto_compra = saldo_usdt - 10
            precio_ronin_antes = self.futuros_ops.futuros.obtener_precio_actual('RONINUSDT')
            cantidad_ronin = math.floor(monto_compra / precio_ronin_antes)
            #orden_compra_ronin = self.futuros_ops.comprar_ronin(porcentaje=1.0)
            # Verificar mínimo 1 RONIN
            if cantidad_ronin < 1:
                print(f"Error: Cantidad RONIN insuficiente: {cantidad_ronin} < 1")
                return False
            
            print(f"Comprando {cantidad_ronin} RONIN con {monto_compra:.2f} USDT (saldo total: {saldo_usdt:.2f} USDT)")
            
            # 4. Comprar cantidad fija de RONIN
            self.futuros_ops.futuros.establecer_apalancamiento('RONINUSDT', 1)
            orden_compra_ronin = self.futuros_ops.comprar_ronin(
                porcentaje=1.0,
                apalancamiento=1,
                cantidad_fija=cantidad_ronin  # Usar cantidad fija
            )


            if not orden_compra_ronin:
                print("Error al comprar RONIN en futuros")
                return False
            
            # 6. Obtener precio real de compra de RONIN
            precio_ronin_real = self.obtener_precio_real(orden_compra_ronin)
            print(f"Precio referencia RONIN: {precio_ronin_antes:.4f} | Precio real: {precio_ronin_real:.4f}")
            
            # 7. Calcular diferencias
            diff_btc = precio_btc_real - precio_btc_inicial
            diff_ronin = precio_ronin_real - precio_ronin_antes
            pct_diff_btc = (diff_btc / precio_btc_inicial) * 100
            pct_diff_ronin = (diff_ronin / precio_ronin_antes) * 100
            
            # 8. Mostrar resultados
            print("\nResultado de la operación en futuros:")
            print(f"BTC vendidos: 0.001 | Precio ref: {precio_btc_inicial:.2f} | Precio real: {precio_btc_real:.2f} | Diff: {diff_btc:.2f} ({pct_diff_btc:.4f}%)")
            print(f"RONIN comprados: {math.floor(saldo_usdt / precio_ronin_real)} | Precio ref: {precio_ronin_antes:.4f} | Precio real: {precio_ronin_real:.4f} | Diff: {diff_ronin:.4f} ({pct_diff_ronin:.4f}%)")
            
            # 9. Registrar comparación
            self.registro_comparacion.append({
                'operacion': 'COMPRA RONIN CON BTC',
                'precio_ref_btc': precio_btc_inicial,
                'precio_real_btc': precio_btc_real,
                'precio_ref_ronin': precio_ronin_antes,
                'precio_real_ronin': precio_ronin_real,
                'diff_btc': diff_btc,
                'diff_ronin': diff_ronin,
                'pct_diff_btc': pct_diff_btc,
                'pct_diff_ronin': pct_diff_ronin,
                'timestamp': time.time(),
                'duracion': time.time() - start_time
            })
            
            return True
        
        except Exception as e:
            print(f"Error en compra futuros RONIN con BTC: {str(e)}")
            return False
    
    def vender_ronin_por_btc_futuros(self):
        """Vende RONIN y compra BTC en futuros con medición de precios"""
        print("\n=== VENTA FUTUROS RONIN POR BTC ===")
        
        try:
            # Registrar hora de inicio
            start_time = time.time()
            
            # 1. Obtener precios de referencia antes de operar
            precio_ronin_inicial = self.futuros_ops.futuros.obtener_precio_actual('RONINUSDT')
            
            # 2. Vender RONIN
            print("Vendiendo RONIN por USDT en futuros...")
            orden_venta_ronin = self.futuros_ops.vender_ronin(porcentaje=1.0)
            if not orden_venta_ronin:
                print("Error al vender RONIN en futuros")
                return False
            
            # 3. Obtener precio real de venta de RONIN
            precio_ronin_real = self.obtener_precio_real(orden_venta_ronin)
            print(f"Precio referencia RONIN: {precio_ronin_inicial:.4f} | Precio real: {precio_ronin_real:.4f}")
            
            # 4. Esperar y obtener USDT
            time.sleep(3)
            saldo_usdt = self.futuros_ops.futuros.obtener_saldo_futuros('USDT')
            print(f"USDT obtenidos: {saldo_usdt:.2f}")
            
            # 5. Comprar BTC
            print("Comprando BTC con USDT en futuros...")
            precio_btc_antes = self.futuros_ops.futuros.obtener_precio_actual('BTCUSDT')
            orden_compra_btc = self.futuros_ops.comprar_btc(porcentaje=1.0)
            if not orden_compra_btc:
                print("Error al comprar BTC en futuros")
                return False
            
            # 6. Obtener precio real de compra de BTC
            precio_btc_real = self.obtener_precio_real(orden_compra_btc)
            print(f"Precio referencia BTC: {precio_btc_antes:.2f} | Precio real: {precio_btc_real:.2f}")
            
            # 7. Calcular diferencias
            diff_ronin = precio_ronin_real - precio_ronin_inicial
            diff_btc = precio_btc_real - precio_btc_antes
            pct_diff_ronin = (diff_ronin / precio_ronin_inicial) * 100
            pct_diff_btc = (diff_btc / precio_btc_antes) * 100
            
            # 8. Mostrar resultados
            print("\nResultado de la operación en futuros:")
            print(f"RONIN vendidos: [cantidad] | Precio ref: {precio_ronin_inicial:.4f} | Precio real: {precio_ronin_real:.4f} | Diff: {diff_ronin:.4f} ({pct_diff_ronin:.4f}%)")
            print(f"BTC comprados: 0.001 | Precio ref: {precio_btc_antes:.2f} | Precio real: {precio_btc_real:.2f} | Diff: {diff_btc:.2f} ({pct_diff_btc:.4f}%)")
            
            # 9. Registrar comparación
            self.registro_comparacion.append({
                'operacion': 'VENTA RONIN POR BTC',
                'precio_ref_ronin': precio_ronin_inicial,
                'precio_real_ronin': precio_ronin_real,
                'precio_ref_btc': precio_btc_antes,
                'precio_real_btc': precio_btc_real,
                'diff_ronin': diff_ronin,
                'diff_btc': diff_btc,
                'pct_diff_ronin': pct_diff_ronin,
                'pct_diff_btc': pct_diff_btc,
                'timestamp': time.time(),
                'duracion': time.time() - start_time
            })
            
            return True
        
        except Exception as e:
            print(f"Error en venta futuros RONIN por BTC: {str(e)}")
            return False
    
    def obtener_precio_real(self, orden):
        """Calcula el precio real de ejecución de una orden"""
        try:
            if 'fills' in orden and orden['fills']:
                # Calcular precio promedio ponderado
                total_quantity = 0
                total_quote = 0
                for fill in orden['fills']:
                    qty = float(fill['qty'])
                    price = float(fill['price'])
                    total_quantity += qty
                    total_quote += qty * price
                
                if total_quantity > 0:
                    return total_quote / total_quantity
            
            # Si no hay fills, usar cummulativeQuoteQty
            if 'cummulativeQuoteQty' in orden and 'executedQty' in orden:
                cum_quote = float(orden['cummulativeQuoteQty'])
                exec_qty = float(orden['executedQty'])
                if exec_qty > 0:
                    return cum_quote / exec_qty
            
            # Si todo falla, devolver precio de mercado actual
            return self.futuros_ops.futuros.obtener_precio_actual(orden['symbol'])
        except:
            return 0.0
    
    def comprar_ronin_futuros(self):
        """Compra RONIN usando USDT en futuros con medición de precios"""
        print("\n=== COMPRA FUTUROS RONIN CON USDT ===")
        
        try:
            # Registrar hora de inicio
            start_time = time.time()
            
            # 1. Obtener precios de referencia antes de operar
            precio_ronin_inicial = self.futuros_ops.futuros.obtener_precio_actual('RONINUSDT')
            
            # 4. Obtener USDT
            saldo_usdt = self.futuros_ops.futuros.obtener_saldo_futuros('USDT')
            print(f"USDT obtenidos: {saldo_usdt:.2f}")

            # 5. Comprar RONIN
            print("Comprando RONIN con USDT en futuros...")
            monto_compra = saldo_usdt - 10
            precio_ronin_antes = self.futuros_ops.futuros.obtener_precio_actual('RONINUSDT')
            cantidad_ronin = math.floor(monto_compra / precio_ronin_antes)
            #orden_compra_ronin = self.futuros_ops.comprar_ronin(porcentaje=1.0)
            # Verificar mínimo 1 RONIN
            if cantidad_ronin < 1:
                print(f"Error: Cantidad RONIN insuficiente: {cantidad_ronin} < 1")
                return False
            
            print(f"Comprando {cantidad_ronin} RONIN con {monto_compra:.2f} USDT (saldo total: {saldo_usdt:.2f} USDT)")
            
            # 4. Comprar cantidad fija de RONIN
            self.futuros_ops.futuros.establecer_apalancamiento('RONINUSDT', 5)
            orden_compra_ronin = self.futuros_ops.comprar_ronin(
                porcentaje=1.0,
                apalancamiento=5,
                cantidad_fija=cantidad_ronin  # Usar cantidad fija
            )


            if not orden_compra_ronin:
                print("Error al comprar RONIN en futuros")
                return False
            
            # 6. Obtener precio real de compra de RONIN
            precio_ronin_real = self.obtener_precio_real(orden_compra_ronin)
            print(f"Precio referencia RONIN: {precio_ronin_antes:.4f} | Precio real: {precio_ronin_real:.4f}")
            
            # 7. Calcular diferencias
            diff_ronin = precio_ronin_real - precio_ronin_antes
            pct_diff_ronin = (diff_ronin / precio_ronin_antes) * 100
            
            # 8. Mostrar resultados
            print("\nResultado de la operación en futuros:")
            print(f"RONIN comprados: {math.floor(saldo_usdt / precio_ronin_real)} | Precio ref: {precio_ronin_antes:.4f} | Precio real: {precio_ronin_real:.4f} | Diff: {diff_ronin:.4f} ({pct_diff_ronin:.4f}%)")
            
            # 9. Registrar comparación
            self.registro_comparacion.append({
                'operacion': 'COMPRA RONIN CON BTC',
                'precio_ref_ronin': precio_ronin_antes,
                'precio_real_ronin': precio_ronin_real,
                'diff_ronin': diff_ronin,
                'pct_diff_ronin': pct_diff_ronin,
                'timestamp': time.time(),
                'duracion': time.time() - start_time
            })
            
            return True
        
        except Exception as e:
            print(f"Error en compra futuros RONIN con USDT: {str(e)}")
            return False

    def vender_ronin_futuros(self):
        """Vende RONIN y compra BTC en futuros con medición de precios"""
        print("\n=== VENTA FUTUROS RONIN POR USDT ===")
        
        try:
            # Registrar hora de inicio
            start_time = time.time()
            
            # 1. Obtener precios de referencia antes de operar
            precio_ronin_inicial = self.futuros_ops.futuros.obtener_precio_actual('RONINUSDT')
            
            # 2. Vender RONIN
            print("Vendiendo RONIN por USDT en futuros...")
            orden_venta_ronin = self.futuros_ops.vender_ronin(porcentaje=1.0)
            if not orden_venta_ronin:
                print("Error al vender RONIN en futuros")
                return False
            
            # 3. Obtener precio real de venta de RONIN
            precio_ronin_real = self.obtener_precio_real(orden_venta_ronin)
            print(f"Precio referencia RONIN: {precio_ronin_inicial:.4f} | Precio real: {precio_ronin_real:.4f}")
            
            # 4. Esperar y obtener USDT
            time.sleep(3)
            saldo_usdt = self.futuros_ops.futuros.obtener_saldo_futuros('USDT')
            print(f"USDT obtenidos: {saldo_usdt:.2f}")
            
            
            # 7. Calcular diferencias
            diff_ronin = precio_ronin_real - precio_ronin_inicial
            pct_diff_ronin = (diff_ronin / precio_ronin_inicial) * 100
            
            # 8. Mostrar resultados
            print("\nResultado de la operación en futuros:")
            print(f"RONIN vendidos: [cantidad] | Precio ref: {precio_ronin_inicial:.4f} | Precio real: {precio_ronin_real:.4f} | Diff: {diff_ronin:.4f} ({pct_diff_ronin:.4f}%)")
            
            # 9. Registrar comparación
            self.registro_comparacion.append({
                'operacion': 'VENTA RONIN POR BTC',
                'precio_ref_ronin': precio_ronin_inicial,
                'precio_real_ronin': precio_ronin_real,
                'diff_ronin': diff_ronin,
                'pct_diff_ronin': pct_diff_ronin,
                'timestamp': time.time(),
                'duracion': time.time() - start_time
            })
            
            return True
        
        except Exception as e:
            print(f"Error en venta futuros RONIN por USDT: {str(e)}")
            return False

    def mostrar_comparacion_precios(self):
        """Muestra un resumen de las diferencias de precios"""
        if not self.registro_comparacion:
            print("No hay datos de comparación")
            return
        
        print("\nResumen de comparación de precios:")
        print("Operación | Asset | Ref vs Real | Diferencia | % Diferencia | Duración")
        print("-" * 80)
        
        for registro in self.registro_comparacion:
            # Para operación de compra (BTC -> RONIN)
            if registro['operacion'] == 'COMPRA RONIN CON BTC':
                print(f"COMPRA RONIN CON BTC | BTC | {registro['precio_ref_btc']:.2f} vs {registro['precio_real_btc']:.2f} | "
                      f"{registro['diff_btc']:.2f} | {registro['pct_diff_btc']:.4f}% | {registro['duracion']:.2f}s")
                print(f"COMPRA RONIN CON BTC | RONIN | {registro['precio_ref_ronin']:.4f} vs {registro['precio_real_ronin']:.4f} | "
                      f"{registro['diff_ronin']:.4f} | {registro['pct_diff_ronin']:.4f}% |")
            
            # Para operación de venta (RONIN -> BTC)
            elif registro['operacion'] == 'VENTA RONIN POR BTC':
                print(f"VENTA RONIN POR BTC | RONIN | {registro['precio_ref_ronin']:.4f} vs {registro['precio_real_ronin']:.4f} | "
                      f"{registro['diff_ronin']:.4f} | {registro['pct_diff_ronin']:.4f}% | {registro['duracion']:.2f}s")
                print(f"VENTA RONIN POR BTC | BTC | {registro['precio_ref_btc']:.2f} vs {registro['precio_real_btc']:.2f} | "
                      f"{registro['diff_btc']:.2f} | {registro['pct_diff_btc']:.4f}% |")
            
            print("-" * 80)

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
                #return self.operacion_margen_directa('RONINUSDT', 'comprar')
                return self.comprar_ronin_futuros()
            elif "venta" in mensaje or "vender" in mensaje or "sell" in mensaje:
                #return self.operacion_margen_directa('RONINUSDT', 'vender')
                return self.vender_ronin_futuros()
        
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