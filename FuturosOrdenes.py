import requests
from Binance import Binance

class FuturosOrdenes(Binance):
    def __init__(self):
        Binance.__init__(self)

    def ComprarMarket(self, simbolo:str, cantidad:float)-> dict:
        endpoint = self.url + "/fapi/v1/order"
        parametros = "timestamp=" + str(self.ObtenerFechaServer())
        parametros += "&symbol=" + simbolo.upper()
        parametros += "&side=BUY"
        parametros += "&type=MARKET"
        parametros += "&quantity=" + str(cantidad)
        parametros = self.Firmar(parametros)

        h = self.Encabezados(self.apiKey)

        r = requests.post(endpoint, params=parametros, headers=h)
        print(r.json())
        return r.json()

    def CerrarCompraMarket(self, simbolo:str, cantidad:float)-> dict:
        endpoint = self.url + "/fapi/v1/order"
        parametros = "timestamp=" + str(self.ObtenerFechaServer())
        parametros += "&symbol=" + simbolo.upper()
        parametros += "&side=SELL"
        parametros += "&type=MARKET"
        parametros += "&quantity=" + str(cantidad)
        parametros += "&reduceOnly=true"

        parametros = self.Firmar(parametros)

        h = self.Encabezados(self.apiKey)

        r = requests.post(endpoint, params=parametros, headers=h)
        print(r.json())
        return r.json()

    def VenderMarket(self, simbolo:str, cantidad:float)-> dict:
        endpoint = self.url + "/fapi/v1/order"
        parametros = "timestamp=" + str(self.ObtenerFechaServer())
        parametros += "&symbol=" + simbolo.upper()
        parametros += "&side=SELL"
        parametros += "&type=MARKET"
        parametros += "&quantity=" + str(cantidad)
        parametros = self.Firmar(parametros)

        h = self.Encabezados(self.apiKey)

        r = requests.post(endpoint, params=parametros, headers=h)
        print(r.json())
        return r.json()

    def CerrarVentaMarket(self, simbolo:str, cantidad:float)-> dict:
        endpoint = self.url + "/fapi/v1/order"
        parametros = "timestamp=" + str(self.ObtenerFechaServer())
        parametros += "&symbol=" + simbolo.upper()
        parametros += "&side=BUY"
        parametros += "&type=MARKET"
        parametros += "&quantity=" + str(cantidad)
        parametros += "&reduceOnly=true"
        
        parametros = self.Firmar(parametros)

        h = self.Encabezados(self.apiKey)

        r = requests.post(endpoint, params=parametros, headers=h)
        print(r.json())
        return r.json()
