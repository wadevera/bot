from MargenBot import MargenBot
import time
import logging

# Configurar logging para ver el proceso detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class TestVentaRONINBTC:
    def __init__(self):
        self.bot = MargenBot()
        
        # Mockear las consultas de saldo para la prueba
        self.mock_saldos()
        
    def mock_saldos(self):
        """Configurar saldos iniciales para la prueba"""
        # Mockear los métodos necesarios de FuturosTrading
        self.bot.futuros_ops.futuros.obtener_saldo_futuros = self.mock_obtener_saldo_futuros
        self.bot.futuros_ops.futuros.obtener_posicion = self.mock_obtener_posicion
        
        # Mockear las operaciones reales
        self.bot.futuros_ops.comprar_btc = self.mock_comprar_btc
        self.bot.futuros_ops.vender_ronin = self.mock_vender_ronin
    
    def mock_obtener_saldo_futuros(self, asset):
        """Mock de saldos disponibles"""
        if asset == 'RONIN':
            return 1500.0
        elif asset == 'USDT':
            return 0.0
        return 0.0
    
    def mock_obtener_posicion(self, symbol):
        """Mock de posición en RONIN"""
        if symbol == 'RONINUSDT':
            return {
                'lado': 'LONG',
                'cantidad': '1500.0',
                'entrada': '3.50'
            }
        return None
    
    def mock_vender_ronin(self, porcentaje=1.0, apalancamiento=1):
        """Mock de venta de RONIN"""
        logging.info(f"[MOCK] Vendiendo RONIN: {1500.0 * porcentaje} unidades")
        return {
            'symbol': 'RONINUSDT',
            'side': 'SELL',
            'quantity': 1500.0,
            'price': 3.52
        }
    
    def mock_comprar_btc(self, porcentaje=1.0, apalancamiento=1):
        """Mock de compra de BTC"""
        # Después de vender RONIN, tenemos ~5280 USDT (1500 * 3.52)
        logging.info(f"[MOCK] Comprando BTC con 5280 USDT")
        return {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'quantity': 0.084,
            'price': 62857.14
        }
    
    def ejecutar_prueba(self):
        """Ejecuta la prueba completa"""
        logging.info("=== INICIANDO PRUEBA DE VENTA RONINBTC ===")
        logging.info("Configuración inicial:")
        logging.info(f"- Saldo RONIN: 1500")
        logging.info(f"- Precio RONIN: 3.52 USDT")
        logging.info(f"- Precio BTC: 62857.14 USDT")
        
        # Simular recepción del mensaje desde Flask
        mensaje = "venta roninbtc"
        logging.info(f"Procesando mensaje: '{mensaje}'")
        
        # Ejecutar la operación
        resultado = self.bot.Entrar(mensaje)
        
        # Mostrar resultados
        if resultado:
            logging.info("Prueba exitosa! Operación completada")
        else:
            logging.error("Prueba fallida! Hubo un error en la operación")
        
        logging.info("=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    tester = TestVentaRONINBTC()
    tester.ejecutar_prueba()