from BinanceAPI import BinanceAPI
from binance.enums import *

class SpotTrading:
    def __init__(self):
        self.client = BinanceAPI().get_client()
    
    def obtener_saldo_spot(self):
        """Obtiene saldos spot >0 en formato {activo: saldo}"""
        try:
            account_info = self.client.get_account()
            activos_con_saldo = {}
            for balance in account_info['balances']:
                saldo = float(balance['free'])
                if saldo > 0:
                    activos_con_saldo[balance['asset']] = saldo
            return activos_con_saldo
        except Exception as e:
            print(f"Error al obtener saldo spot: {e}")
            return {}

    def colocar_orden_spot_limit(self, symbol, side, quantity, price):
        """Orden limit spot estándar"""
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=price,
                timeInForce=TIME_IN_FORCE_GTC
            )
            print("Orden spot LIMIT colocada:", order)
            return order
        except Exception as e:
            print(f"Error al colocar orden spot limit: {e}")

    def colocar_orden_spot_market(self, symbol, side, quantity=None, quote_quantity=None):
        """Orden market spot (2 modos de cantidad)"""
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': ORDER_TYPE_MARKET
            }
            
            # Binance acepta 2 modos:
            if quantity:
                params['quantity'] = quantity
            elif quote_quantity:
                params['quoteOrderQty'] = quote_quantity  # Ej: comprar por $50 USDT de BTC
            
            order = self.client.create_order(**params)
            print("Orden spot MARKET colocada:", order)
            return order
        except Exception as e:
            print(f"Error al colocar orden spot market: {e}")

    def obtener_ordenes_abiertas_spot(self, symbol=None):
        """Obtiene órdenes abiertas (todas o por símbolo)"""
        try:
            open_orders = self.client.get_open_orders(symbol=symbol) if symbol else self.client.get_open_orders()
            print(f"Órdenes spot abiertas ({len(open_orders)}):")
            for order in open_orders:
                print(f"ID: {order['orderId']} {order['side']} {order['origQty']} {order['symbol']} @ {order.get('price', 'MARKET')}")
            return open_orders
        except Exception as e:
            print(f"Error al obtener órdenes spot abiertas: {e}")
            return []

    # Métodos REUTILIZABLES desde MargenConsultas:
    def obtener_precio_actual(self, symbol):
        """Mismo método que en margen (compartible)"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"Error al obtener precio de {symbol}: {e}")
            return None

    def cancelar_orden_spot(self, symbol, order_id):
        try:
            response = self.client.cancel_order(symbol=symbol, orderId=order_id)
            print("Orden spot cancelada:", response)
            return response
        except Exception as e:
            print(f"Error al cancelar orden spot: {e}")

    def cancelar_todas_ordenes_spot(self, symbol=None):
        try:
            orders = self.obtener_ordenes_abiertas_spot(symbol)
            for order in orders:
                self.cancelar_orden_spot(order['symbol'], order['orderId'])
            print(f"Todas las órdenes spot canceladas ({len(orders)} órdenes)")
        except Exception as e:
            print(f"Error al cancelar todas las órdenes spot: {e}")