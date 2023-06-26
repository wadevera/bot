from datetime import datetime
import Configuracion
import time
import json
import hmac
import hashlib

class Gate:
    apiKey = ""
    secretKey = ""
    url = ""

    def __init__(self):
        self.apiKey = Configuracion.GATE_API_KEY
        self.secretKey = Configuracion.GATE_SECRET_KEY
        self.url = "api.gateio.ws"

    def ObtenerHora(self) -> str:
        # Define el nonce (número único utilizado en cada solicitud)
        nonce = str(int(time.time() * 1000))
        return nonce

    
    def Firmar(self, parametros: dict) -> str:
        # Convierte el cuerpo de la solicitud en una cadena JSON y lo codifica en UTF-8
        parametros_json = json.dumps(parametros).encode('utf-8')

        # Calcula la firma HMAC
        signature = hmac.new(self.secretKey.encode('utf-8'), parametros_json, hashlib.sha512).hexdigest()
        
        return signature

    def GateEncabezados(self, api_key, parametros: dict) -> dict:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        nonce = self.ObtenerHora()
        print(nonce)
        signature = self.Firmar(parametros)
                
        # Define los encabezados de la solicitud
        headers = {
            'KEY': api_key,
            'Timestamp': nonce,
            'SIGN': signature,
            'Content-Type': 'application/json'
        }
        return headers

    


        

