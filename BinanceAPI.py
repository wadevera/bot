from datetime import datetime
import Configuracion
import requests
import json
import hmac
import hashlib
from binance.client import Client
from Configuracion import API_KEY, SECRET_KEY



class BinanceAPI:
    def __init__(self):
        self.client = Client(API_KEY, SECRET_KEY)

    def get_account_info(self):
        try:
            return self.client.get_account()
        except Exception as e:
            print(f"Error al obtener información de la cuenta: {e}")
            return None

    def get_client(self):
        return self.client
    
    def get_futures_client(self):
        """Cliente específico para futuros"""
        return Client(api_key=self.api_key, api_secret=self.api_secret, testnet=False)
    
    def Log(self, texto:str):
        f = open("ordenes.log", "a")
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " -> " + texto + "\n")
        f.close()

