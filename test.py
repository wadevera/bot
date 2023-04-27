# -*- coding: utf-8 -*-

from FuturosConsultas import FuturosConsultas as Consultas
from FuturosOrdenes import FuturosOrdenes as Ordenes
from FuturosBot import FuturosBot
import json
import socket

c = Consultas()
o = Ordenes()
bot = FuturosBot()

#operaciones = c.ObtenerOperaciones("BTCUSDT")
#balance = c.ObtenerBalance()

#cantidad = c.ObtenerPosicion("ETHUSDT")

#print(cantidad)
ip_address = socket.gethostbyname(socket.gethostname())
print(ip_address)

#bot.Entrar("Compra   eth")

#o.CerrarCompraMarket("ETHUSDT", cantidad)

""" try:
    o.ComprarMarket("ETHUSDT", 0.005)
except Exception as e:
    print("Error en la operación:", e)
    if "code" in str(e):
        error_json = json.loads(str(e).replace("'", "\""))
        print("Código de respuesta:", error_json["code"])
        print("Mensaje de respuesta:", error_json["msg"])

 """