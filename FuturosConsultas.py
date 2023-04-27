from Binance import Binance
import requests

class FuturosConsultas(Binance):
    def __init__(self):
        Binance.__init__(self)

    def ObtenerOperaciones(self, simbolo:str, limite:int=500):
        endpoint = self.url + "/fapi/v1/trades"
        parametro = "&symbol=" + simbolo.upper()
        if limite !=500 and limite <= 1000 and limite>0:
            parametro += "&limit=" + str(limite)
        r = requests.get(endpoint, parametro)
        return r.json()
        
    def ObtenerBalance(self):
        endpoint = self.url + "/fapi/v2/balance"
        parametros = "timestamp=" + str(self.ObtenerFechaServer())
        parametros = self.Firmar(parametros)
        h = self.Encabezados(self.apiKey)
        try:
            response = requests.get(endpoint, params=parametros, headers=h)
            response.raise_for_status() # genera una excepción si la solicitud no fue exitosa
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error al hacer la solicitud HTTP:", e)
            return None

    def ObtenerCuentaGeneral(self) -> dict:
        endpoint = self.url + "/fapi/v2/account"
        parametros = "timestamp=" + str(self.ObtenerFechaServer())
        parametros = self.Firmar(parametros)
        h = self.Encabezados(self.apiKey)
        try:
            response = requests.get(endpoint, params=parametros, headers=h)
            response.raise_for_status() # genera una excepción si la solicitud no fue exitosa
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error al hacer la solicitud HTTP:", e)
            return None

    def ObtenerPosiciones(self)-> dict:
        ac = self.ObtenerCuentaGeneral()
        if "positions" in ac.keys():
            return ac["positions"]
        return None
    
    def ObtenerPosicion(self, simbolo:str)->dict:
        pos = self.ObtenerPosiciones()
        ticker = simbolo.upper()
        for item in pos:
            if item["symbol"] == ticker:
                return float(item["positionAmt"])
        return 0.0
