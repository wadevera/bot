from BinanceAPI import BinanceAPI
from binance.client import Client

class MarketConsultas:
    def __init__(self):
        self.binance_api = BinanceAPI()

    def consultar_balance(self):
        account_info = self.binance_api.get_account_info()
        balances = account_info['balances']
        for balance in balances:
            if float(balance['free']) > 0:
                print(f"{balance['asset']}: {balance['free']}")

    
    def consultar_posiciones_margen(self, symbol=None):
        """Consulta todas las posiciones de margen, o las de un símbolo específico.

        Args:
            symbol (str, optional): El símbolo del par de trading. Si se omite, se consultan todas las posiciones.
        """
        all_orders = self.binance_api.get_all_orders(symbol=symbol)
        if all_orders:
            # Filtrar las posiciones de margen (puedes ajustar la lógica según tus necesidades)
            #posiciones_margen = [order for order in all_orders if order['isMarginTrade']]
            posiciones_margen = [order for order in all_orders if 'isMarginTrade' in order and order['isMarginTrade']]

            return posiciones_margen
        else:
            print("No se encontraron posiciones de margen.")

    def comprar(self, symbol, quantity):
        order = self.binance_api.client.create_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print(order)