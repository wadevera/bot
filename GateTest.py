# -*- coding: utf-8 -*-

from GateConsultas import GateConsultas as Consultas
import json
import socket

c = Consultas()

cantidad = c.ObtenerPosicion("usdt")
print(cantidad)