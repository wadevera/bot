from MargenBot import MargenBot
import time
import logging
import os
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class TestOperacionesReal:
    def __init__(self):
        self.bot = MargenBot()
        self.operacion = None
        self.validar_ambiente()
        
    def validar_ambiente(self):
        """Verifica que estamos en producción y con confirmación del usuario"""
        logging.warning("ADVERTENCIA: ESTE TEST EJECUTARÁ OPERACIONES REALES EN TU CUENTA DE BINANCE")
        logging.warning("ESTÁS UTILIZANDO FONDOS REALES - PROCEDE CON PRECAUCIÓN")
        
        print("\nSeleccione la operación a probar:")
        print("1. VENTA RONINBTC (vender RONIN y comprar BTC)")
        print("2. COMPRA RONINBTC (vender BTC y comprar RONIN)")
        
        opcion = input("Ingrese el número de la operación (1-2): ").strip()
        
        if opcion == "1":
            self.operacion = "venta"
            mensaje = "VENTA RONINBTC (venta de RONIN y compra de BTC en futuros)"
        elif opcion == "2":
            self.operacion = "compra"
            mensaje = "COMPRA RONINBTC (venta de BTC y compra de RONIN en futuros)"
        else:
            logging.error("Opción no válida")
            sys.exit(1)
        
        logging.warning(f"Se ejecutará la operación: {mensaje}")
        
        confirmacion = input("¿Estás seguro de continuar? (escribe 'SI' para confirmar): ")
        if confirmacion != "SI":
            logging.info("Prueba cancelada por el usuario")
            sys.exit(0)
    
    def obtener_saldos_futuros(self):
        """Obtiene saldos actuales en futuros usando la API"""
        try:
            # Usar el cliente de futuros directamente
            client = self.bot.futuros_ops.futuros.client
            balance = client.futures_account_balance()
            
            saldos = {}
            for asset in balance:
                if asset['asset'] in ['BTC', 'RONIN', 'USDT']:
                    saldos[asset['asset']] = float(asset['availableBalance'])
            
            return saldos
        except Exception as e:
            logging.error(f"Error al obtener saldos: {e}")
            return {}
    
    def obtener_posicion(self, simbolo):
        """Obtiene la posición actual para un símbolo"""
        try:
            client = self.bot.futuros_ops.futuros.client
            positions = client.futures_position_information()
            
            for position in positions:
                if position['symbol'] == simbolo and float(position['positionAmt']) != 0:
                    return {
                        'lado': 'LONG' if float(position['positionAmt']) > 0 else 'SHORT',
                        'cantidad': abs(float(position['positionAmt'])),
                        'entrada': float(position['entryPrice'])
                    }
            return None
        except Exception as e:
            logging.error(f"Error al obtener posición: {e}")
            return None
    
    def ejecutar_prueba_venta(self):
        """Ejecuta la prueba de venta RONIN por BTC"""
        try:
            # 1. Obtener estado inicial
            logging.info("=== OBTENIENDO ESTADO INICIAL ===")
            saldos_iniciales = self.obtener_saldos_futuros()
            pos_ronin_inicial = self.obtener_posicion('RONINUSDT')
            
            logging.info(f"Saldo RONIN disponible: {saldos_iniciales.get('RONIN', 0)}")
            logging.info(f"Saldo BTC disponible: {saldos_iniciales.get('BTC', 0)}")
            logging.info(f"Saldo USDT disponible: {saldos_iniciales.get('USDT', 0)}")
            
            if pos_ronin_inicial:
                logging.info(f"Posición RONIN: {pos_ronin_inicial['cantidad']} ({pos_ronin_inicial['lado']})")
            else:
                logging.info("No hay posición abierta en RONINUSDT")
            
            # 2. Ejecutar la operación
            logging.info("\n=== EJECUTANDO OPERACIÓN 'venta roninbtc' ===")
            resultado = self.bot.Entrar("venta roninbtc")
            
            if not resultado:
                logging.error("La operación falló")
                return False
            
            # 3. Esperar y obtener estado final
            time.sleep(10)  # Esperar para que se completen las operaciones
            logging.info("\n=== OBTENIENDO ESTADO FINAL ===")
            saldos_finales = self.obtener_saldos_futuros()
            pos_ronin_final = self.obtener_posicion('RONINUSDT')
            pos_btc_final = self.obtener_posicion('BTCUSDT')
            
            # 4. Mostrar resultados
            logging.info("\n=== RESULTADOS ===")
            logging.info(f"Saldo RONIN final: {saldos_finales.get('RONIN', 0)}")
            logging.info(f"Saldo BTC final: {saldos_finales.get('BTC', 0)}")
            logging.info(f"Saldo USDT final: {saldos_finales.get('USDT', 0)}")
            
            if pos_ronin_final:
                logging.info(f"Posición RONIN final: {pos_ronin_final['cantidad']} ({pos_ronin_final['lado']})")
            else:
                logging.info("No hay posición abierta en RONINUSDT")
            
            if pos_btc_final:
                logging.info(f"Posición BTC final: {pos_btc_final['cantidad']} ({pos_btc_final['lado']})")
            
            # 5. Verificar operación
            if (saldos_finales.get('RONIN', 0) < saldos_iniciales.get('RONIN', 1) and 
                (saldos_finales.get('BTC', 0) > saldos_iniciales.get('BTC', 0) or pos_btc_final)):
                logging.info("Prueba exitosa! La operación se completó correctamente")
                return True
            else:
                logging.warning("Resultados inesperados. Verificar manualmente las transacciones")
                return False
            
        except Exception as e:
            logging.exception(f"Error durante la prueba: {str(e)}")
            return False
    
    def ejecutar_prueba_compra(self):
        """Ejecuta la prueba de compra de RONIN con BTC"""
        try:
            # 1. Obtener estado inicial
            logging.info("=== OBTENIENDO ESTADO INICIAL ===")
            saldos_iniciales = self.obtener_saldos_futuros()
            pos_btc_inicial = self.obtener_posicion('BTCUSDT')
            
            logging.info(f"Saldo RONIN disponible: {saldos_iniciales.get('RONIN', 0)}")
            logging.info(f"Saldo BTC disponible: {saldos_iniciales.get('BTC', 0)}")
            logging.info(f"Saldo USDT disponible: {saldos_iniciales.get('USDT', 0)}")
            
            if pos_btc_inicial:
                logging.info(f"Posición BTC: {pos_btc_inicial['cantidad']} ({pos_btc_inicial['lado']})")
            else:
                logging.info("No hay posición abierta en BTCUSDT")
            
            # 2. Ejecutar la operación
            logging.info("\n=== EJECUTANDO OPERACIÓN 'comprar roninbtc' ===")
            resultado = self.bot.Entrar("comprar roninbtc")
            
            if not resultado:
                logging.error("La operación falló")
                return False
            
            # 3. Esperar y obtener estado final
            time.sleep(10)  # Esperar para que se completen las operaciones
            logging.info("\n=== OBTENIENDO ESTADO FINAL ===")
            saldos_finales = self.obtener_saldos_futuros()
            pos_btc_final = self.obtener_posicion('BTCUSDT')
            pos_ronin_final = self.obtener_posicion('RONINUSDT')
            
            # 4. Mostrar resultados
            logging.info("\n=== RESULTADOS ===")
            logging.info(f"Saldo RONIN final: {saldos_finales.get('RONIN', 0)}")
            logging.info(f"Saldo BTC final: {saldos_finales.get('BTC', 0)}")
            logging.info(f"Saldo USDT final: {saldos_finales.get('USDT', 0)}")
            
            if pos_btc_final:
                logging.info(f"Posición BTC final: {pos_btc_final['cantidad']} ({pos_btc_final['lado']})")
            else:
                logging.info("No hay posición abierta en BTCUSDT")
            
            if pos_ronin_final:
                logging.info(f"Posición RONIN final: {pos_ronin_final['cantidad']} ({pos_ronin_final['lado']})")
            
            # 5. Verificar operación
            if (saldos_finales.get('BTC', 0) < saldos_iniciales.get('BTC', 1) and 
                (saldos_finales.get('RONIN', 0) > saldos_iniciales.get('RONIN', 0) or pos_ronin_final)):
                logging.info("Prueba exitosa! La operación se completó correctamente")
                return True
            else:
                logging.warning("Resultados inesperados. Verificar manualmente las transacciones")
                return False
            
        except Exception as e:
            logging.exception(f"Error durante la prueba: {str(e)}")
            return False
    
    def ejecutar_prueba(self):
        """Ejecuta la prueba según la operación seleccionada"""
        try:
            if self.operacion == "venta":
                return self.ejecutar_prueba_venta()
            elif self.operacion == "compra":
                return self.ejecutar_prueba_compra()
            else:
                logging.error("Operación no definida")
                return False
        except Exception as e:
            logging.exception(f"Error durante la prueba: {str(e)}")
            return False
        finally:
            logging.info("=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    tester = TestOperacionesReal()
    resultado = tester.ejecutar_prueba()
    
    if resultado:
        logging.info("¡Prueba completada con éxito!")
    else:
        logging.error("¡La prueba encontró errores!")
    
    # Mostrar comparación de precios si está disponible
    try:
        tester.bot.mostrar_comparacion_precios()
    except AttributeError:
        logging.warning("La función de comparación de precios no está disponible")