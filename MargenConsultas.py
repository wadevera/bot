from BinanceAPI import BinanceAPI
from binance.enums import *

class MargenConsultas:
    def __init__(self):
        self.client = BinanceAPI().get_client()

    # def obtener_saldo_margen(self):
    #     try:
    #         margen_info = self.client.get_margin_account()
    #         activos_con_saldo = []
    #         for asset in margen_info['userAssets']:
    #             saldo = float(asset['free'])
    #             if saldo > 0:  # Solo activos con saldo distinto de 0
    #                 activos_con_saldo.append({
    #                     'activo': asset['asset'],
    #                     'saldo': asset['free'],
    #                     'prestado': asset['borrowed']
    #                 })
    #         return activos_con_saldo  # Retorna la lista de activos
    #     except Exception as e:
    #         print(f"Error al obtener el saldo de margen: {e}")
    #         return []

    def obtener_saldo_margen(self):
        try:
            margen_info = self.client.get_margin_account()
            activos_con_saldo = {}
            for asset in margen_info['userAssets']:
                saldo = float(asset['free'])
                if saldo > 0:
                    activos_con_saldo[asset['asset']] = saldo  # Guardar saldo en un diccionario
            return activos_con_saldo  # Retorna un diccionario de activos y sus saldos
        except Exception as e:
            print(f"Error al obtener el saldo de margen: {e}")
            return {}

    def colocar_orden_margen(self, symbol, side, quantity, price):
        try:
            order = self.client.create_margin_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=price,
                isIsolated=False,  # Cambiar a True si prefieres usar margen aislado
                timeInForce=TIME_IN_FORCE_GTC
            )
            print("Orden de margen colocada:", order)
        except Exception as e:
            print(f"Error al colocar la orden de margen: {e}")
    
    def colocar_orden_margen_mercado(self, symbol, side, quantity):
        try:
            order = self.client.create_margin_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity,
                isIsolated=False  # Para margen cruzado
            )
            print("Orden de margen a precio de mercado colocada:", order)
            return order['orderId']  # Retorna el ID de la orden
        except Exception as e:
            print(f"Error al colocar la orden de margen a precio de mercado: {e}")


    def obtener_ordenes_abiertas(self, symbol):
        try:
            open_orders = self.client.get_open_margin_orders(symbol=symbol)
            print("Órdenes abiertas:")
            for order in open_orders:
                print(f"ID de Orden: {order['orderId']}, Tipo: {order['side']}, Cantidad: {order['origQty']}, Precio: {order['price']}, Estado: {order['status']}")
            return open_orders
        except Exception as e:
            print(f"Error al obtener órdenes abiertas: {e}")

    def obtener_precio_actual(self, symbol):
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])  # Retornar solo el precio
        except Exception as e:
            print(f"Error al obtener el precio de {symbol}: {e}")
            return None
    
    def cancelar_orden_margen(self, symbol, order_id):
        try:
            response = self.client.cancel_margin_order(symbol=symbol, orderId=order_id)
            print("Orden cancelada:", response)
        except Exception as e:
            print(f"Error al cancelar la orden de margen: {e}")
    
    def cancelar_todas_las_ordenes_abiertas(self, symbol):
        open_orders = self.obtener_ordenes_abiertas(symbol)
        if open_orders:
            print("Cancelando todas las órdenes abiertas...")
            for order in open_orders:
                self.cancelar_orden_margen(symbol, order['orderId'])
        else:
            print("No hay órdenes abiertas para cancelar.")