import math
import time
from FuturosConsultas import FuturosConsultas
from MargenConsultas import MargenConsultas
from BinanceAPI import BinanceAPI

class TradingBot:
    def __init__(self):
        self.client = BinanceAPI().get_client()
        self.futures_client = BinanceAPI().get_futures_client()  # Nuevo cliente para futuros
        self.consultas_margen = MargenConsultas()
        self.consultas_futuros = FuturosConsultas()  # Nueva clase para consultas de futuros
        self.registro_operaciones = []
    
    def operar_en_mercado(self, simbolo: str, accion: str, cantidad: float, tipo: str = "margen"):
        """Método unificado para operaciones en diferentes mercados"""
        if tipo == "margen":
            if accion == "comprar":
                return self.consultas_margen.colocar_orden_margen_mercado(
                    symbol=simbolo,
                    side='BUY',
                    quantity=cantidad
                )
            else:  # vender
                return self.consultas_margen.colocar_orden_margen_mercado(
                    symbol=simbolo,
                    side='SELL',
                    quantity=cantidad
                )
        else:  # futuros
            if accion == "comprar":
                return self.consultas_futuros.colocar_orden_futuros_mercado(
                    symbol=simbolo,
                    side='BUY',
                    quantity=cantidad
                )
            else:  # vender
                return self.consultas_futuros.colocar_orden_futuros_mercado(
                    symbol=simbolo,
                    side='SELL',
                    quantity=cantidad
                )