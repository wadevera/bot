from Gate import Gate
import requests

class GateConsultas(Gate):
    def __init__(self):
        Gate.__init__(self)

    def ObtenerPosicion(self, simbolo:str)->dict:
        
        ticker = simbolo.upper()
        endpoint = '/api/v4/accounts'
        # Define el cuerpo de la solicitud
        parametros = {
            "currency": "usdt"
        }
        h=self.GateEncabezados(self, self.apiKey, parametros)

        response = requests.get(self.url+endpoint, params=parametros, headers=h)
        # Imprime la respuesta
        print(response.json())
