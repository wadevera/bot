# A very simple Flask Hello World app for you to get started with...
#from FuturosBot import FuturosBot
from GateBot import GateBot
from datetime import datetime
import Configuracion

from flask import request
from flask import Flask
import socket

app = Flask(__name__)

@app.route('/')
def hello_world():
    ip_address = socket.gethostbyname(socket.gethostname())
    print(ip_address)
    return ip_address





@app.route('/bot1', methods=['POST'])
def bot():
    parametro = str(request.data, 'UTF-8').lower()
    api_trade_url = Configuracion.API_TRADE_URL
#    f = open("salida.txt", "a")
#    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " -> " + parametro + " api:" + api_trade_url + "\n")
#    f.close()

    # Tomar los valores de configuración del archivo Configuracion.py
    
    api_key = Configuracion.GATE_API_KEY
    secret_key = Configuracion.GATE_SECRET_KEY

    # Modificación en la creación de la instancia de GateBot
    bot = GateBot(api_trade_url, api_key, secret_key)

    bot.Entrar(parametro)

    return 'ok'