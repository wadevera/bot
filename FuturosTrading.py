from BinanceAPI import BinanceAPI
from binance.enums import *

class FuturosTrading:
    def __init__(self):
        self.client = BinanceAPI().get_client()
        self.leverage_cache = {}  # Cache para apalancamientos
    
    def obtener_saldo_futuros(self, asset='USDT'):
        """Obtiene el saldo disponible en futuros para un activo específico"""
        try:
            balance = self.client.futures_account_balance()
            for item in balance:
                if item['asset'] == asset:
                    return float(item['availableBalance'])
            return 0.0
        except Exception as e:
            print(f"Error al obtener saldo de futuros: {e}")
            return 0.0
    
    def establecer_apalancamiento(self, symbol, leverage):
        """Establece el nivel de apalancamiento para un símbolo"""
        try:
            # Verificar si ya tenemos este apalancamiento en cache
            if symbol in self.leverage_cache and self.leverage_cache[symbol] == leverage:
                return True
                
            response = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            self.leverage_cache[symbol] = leverage
            print(f"Apalancamiento establecido a {leverage}x para {symbol}")
            return True
        except Exception as e:
            print(f"Error al establecer apalancamiento: {e}")
            return False
    
    def obtener_posicion(self, symbol):
        """Obtiene la posición actual para un símbolo"""
        try:
            positions = self.client.futures_position_information()
            for pos in positions:
                if pos['symbol'] == symbol and float(pos['positionAmt']) != 0:
                    return {
                        'symbol': symbol,
                        'cantidad': float(pos['positionAmt']),
                        'entrada': float(pos['entryPrice']),
                        'lado': 'LONG' if float(pos['positionAmt']) > 0 else 'SHORT',
                        'apalancamiento': float(pos['leverage'])
                    }
            return None
        except Exception as e:
            print(f"Error al obtener posición: {e}")
            return None
    
    def colocar_orden_futuros_limit(self, symbol, side, quantity, price, reduce_only=False):
        """Coloca una orden limit en futuros"""
        try:
            # Asegurar el apalancamiento (ej: 10x)
            self.establecer_apalancamiento(symbol, 10)
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=price,
                timeInForce=TIME_IN_FORCE_GTC,
                reduceOnly=reduce_only
            )
            print(f"Orden limit de futuros colocada: {order}")
            return order
        except Exception as e:
            print(f"Error al colocar orden limit en futuros: {e}")
            return None
    
    def colocar_orden_futuros_market(self, symbol, side, quantity, reduce_only=False, leverage=1):
        """Coloca una orden de mercado en futuros"""
        try:
            # Asegurar el apalancamiento
            self.establecer_apalancamiento(symbol, leverage)
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity,
                reduceOnly=reduce_only
            )
            print(f"Orden market de futuros colocada: {order}")
            return order
        except Exception as e:
            print(f"Error al colocar orden market en futuros: {e}")
            return None
    
    def colocar_orden_stop_loss(self, symbol, side, quantity, stop_price, reduce_only=True):
        """Coloca una orden stop loss"""
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=FUTURE_ORDER_TYPE_STOP_MARKET,
                quantity=quantity,
                stopPrice=stop_price,
                reduceOnly=reduce_only
            )
            print(f"Orden stop loss colocada: {order}")
            return order
        except Exception as e:
            print(f"Error al colocar stop loss: {e}")
            return None
    
    def obtener_ordenes_abiertas_futuros(self, symbol=None):
        """Obtiene las órdenes abiertas en futuros"""
        try:
            if symbol:
                open_orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                open_orders = self.client.futures_get_open_orders()
            
            print(f"Órdenes abiertas en futuros ({len(open_orders)}):")
            for order in open_orders:
                print(f"ID: {order['orderId']} {order['side']} {order['origQty']} {order['symbol']} @ {order.get('price', 'MARKET')}")
            return open_orders
        except Exception as e:
            print(f"Error al obtener órdenes abiertas en futuros: {e}")
            return []
    
    def cancelar_orden_futuros(self, symbol, order_id):
        """Cancela una orden específica en futuros"""
        try:
            response = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            print(f"Orden de futuros cancelada: {response}")
            return response
        except Exception as e:
            print(f"Error al cancelar orden de futuros: {e}")
            return None
    
    def cancelar_todas_ordenes_futuros(self, symbol=None):
        """Cancela todas las órdenes abiertas en futuros"""
        try:
            if symbol:
                response = self.client.futures_cancel_all_open_orders(symbol=symbol)
                print(f"Todas las órdenes de futuros canceladas para {symbol}")
            else:
                # Para cancelar todas las órdenes de todos los símbolos
                symbols = set([order['symbol'] for order in self.obtener_ordenes_abiertas_futuros()])
                for sym in symbols:
                    self.client.futures_cancel_all_open_orders(symbol=sym)
                print("Todas las órdenes de futuros canceladas en todos los símbolos")
            return True
        except Exception as e:
            print(f"Error al cancelar todas las órdenes de futuros: {e}")
            return False
    
    def obtener_precio_actual(self, symbol):
        """Obtiene el precio actual de un símbolo en futuros"""
        try:
            ticker = self.client.futures_ticker(symbol=symbol)
            return float(ticker['lastPrice'])
        except Exception as e:
            print(f"Error al obtener precio de {symbol} en futuros: {e}")
            return None
    
    def obtener_minimo_qty(self, symbol):
        """Obtiene la cantidad mínima operable para un símbolo"""
        try:
            info = self.client.futures_exchange_info()
            for s in info['symbols']:
                if s['symbol'] == symbol:
                    for filtro in s['filters']:
                        if filtro['filterType'] == 'LOT_SIZE':
                            return float(filtro['minQty'])
            return 0.001  # Valor por defecto si no se encuentra
        except Exception as e:
            print(f"Error al obtener cantidad mínima: {e}")
            return 0.001