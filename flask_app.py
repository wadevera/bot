# A very simple Flask Hello World app for you to get started with...
#from FuturosBot import FuturosBot
from gateBot import GateBot
from datetime import datetime

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
    f = open("salida.txt", "a")
    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " -> " + parametro + "\n")
    f.close()

    bot = GateBot()
    bot.Entrar(parametro)

    return 'ok'