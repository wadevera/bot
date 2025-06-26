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

class TestVentaReal:
    def __init__(self):
        self.bot = MargenBot()
        self.validar_ambiente()
        
    def validar_ambiente(self):
        """Verifica que estamos en producción y con confirmación del usuario"""
        logging.warning("ADVERTENCIA: ESTE TEST EJECUTARÁ OPERACIONES REALES EN TU CUENTA DE BINANCE")
        logging.warning("ESTÁS UTILIZANDO FONDOS REALES - PROCEDE CON PRECAUCIÓN")
        logging.warning("Se ejecutará la operación: VENTA RONINBTC (venta de RONIN y compra de BTC en futuros)")
        
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
    
    def ejecutar_prueba(self):
        """Ejecuta la prueba con operaciones reales"""
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
                return
            
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
            else:
                logging.warning("Resultados inesperados. Verificar manualmente las transacciones")
            
        except Exception as e:
            logging.exception(f"Error durante la prueba: {str(e)}")
        finally:
            logging.info("=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    tester = TestVentaReal()
    tester.ejecutar_prueba()