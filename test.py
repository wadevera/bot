# -*- coding: utf-8 -*-

#from FuturosConsultas import FuturosConsultas as Consultas
#from FuturosOrdenes import FuturosOrdenes as Ordenes
#from FuturosBot import FuturosBot
import json
import socket

import requests

def obtener_ip_publica():
    response = requests.get('https://api.ipify.org?format=json')
    ip = response.json().get('ip')
    return ip

ip_publica = obtener_ip_publica()
print(f"La IP pública de este servidor es: {ip_publica}")



#ip_address = socket.gethostbyname(socket.gethostname())
#print(ip_address)
#print("\n hola mundo")
#print(operaciones)



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