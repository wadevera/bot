from BinanceAPI import BinanceAPI

class FuturosConsultas:
   # def __init__(self, client=None):
        
    
    def obtener_saldo_futuros(self, activo: str) -> float:
        """Obtiene el saldo disponible de un activo en futuros"""
        try:
            # Obtener balance de futuros
            balance = self.client.futures_account_balance()
            for asset in balance:
                if asset['asset'] == activo:
                    return float(asset['availableBalance'])
            return 0.0
        except Exception as e:
            print(f"Error obteniendo saldo futuros: {e}")
            return 0.0
    
    def obtener_precio_actual(self, simbolo: str) -> float:
        """Obtiene el precio actual de un símbolo en futuros"""
        try:
            ticker = self.client.futures_ticker(symbol=simbolo)
            return float(ticker['lastPrice'])
        except Exception as e:
            print(f"Error obteniendo precio futuros: {e}")
            return 0.0
    
    def colocar_orden_futuros_mercado(self, symbol: str, side: str, quantity: float):
        """Coloca una orden a mercado en futuros"""
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=quantity
            )
            return order
        except Exception as e:
            print(f"Error en orden futuros: {e}")
            return None