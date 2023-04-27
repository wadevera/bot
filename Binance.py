from datetime import datetime
import Configuracion
import requests
import json
import hmac
import hashlib

class Binance:
    apiKey = ""
    secretKey = ""
    url = ""

    def __init__(self):
        self.apiKey = Configuracion.API_KEY
        self.secretKey = Configuracion.SECRET_KEY
        self.url = "https://fapi.binance.com"

    def ObtenerFechaServer(self) -> int:
        endpoint = self.url + "/fapi/v1/time"
        r = requests.get(endpoint)
        resp = r.json()
        return resp["serverTime"]

    def Firmar(self, parametros: str) -> str:
        m = hmac.new(self.secretKey.encode('utf-8'), parametros.encode('utf-8'), hashlib.sha256)
        return parametros + "&signature=" + m.hexdigest()


    def Encabezados(self, api_key="") -> dict:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        if api_key:
            headers['X-MBX-APIKEY'] = api_key
        return headers
    
    def Log(self, texto:str):
        f = open("ordenes.log", "a")
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " -> " + texto + "\n")
        f.close()

