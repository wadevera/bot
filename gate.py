from datetime import datetime
import Configuracion
import requests
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
        self.url = "https://api.gateio.ws"



