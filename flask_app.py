# A very simple Flask Hello World app for you to get started with...
#from FuturosBot import FuturosBot
from GateBot import GateBot
from MargenBot import MargenBot
from Margen2Bot import Margen2Bot
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
    # Parsear el mensaje de TradingView
    parametro = str(request.data, 'UTF-8').lower()
    
    # Extraer el precio si está presente en el mensaje (formato: "comando @precio")
    #precio_alerta = None
    #if '@' in parametro:
    #    comando, precio_str = parametro.split('@', 1)
    #    try:
    #        precio_alerta = float(precio_str.strip())
    #        parametro = comando.strip()
    #    except ValueError:
    #        print(f"Formato de precio inválido: {precio_str}")
    
    bot = MargenBot()
    # Pasar el precio de alerta al bot si está disponible
    bot.Entrar(parametro)

    #bot.Entrar(parametro, precio_alerta=precio_alerta)

    return 'ok'