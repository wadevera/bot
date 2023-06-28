
# -*- coding: utf-8 -*-
# encoding: utf-8

'''
Provide user specific data and interact with gate.io
'''
import json
import Configuracion
from gateAPI import GateIO

# apiKey APISECRET
apiKey = Configuracion.GATE_API_KEY
secretKey = Configuracion.GATE_SECRET_KEY


# address
btcAddress = '0xa384b30eC47b4346e941F688aE93c98CeA42b918'


# Provide constants

API_QUERY_URL = 'data.gateio.la'
API_TRADE_URL = 'api.gateio.la'

# Create a gate class instance

gate_query = GateIO(API_QUERY_URL, apiKey, secretKey)
gate_trade = GateIO(API_TRADE_URL, apiKey, secretKey)


orden = ""
ticker = ""
    
class GateBot(GateIO):
    
    def ObtenerComando(self, texto:str)->str:
        compra = ["comprar", "compra", "buy", "long"]
        venta = ["vender", "vender", "venda", "sell", "short"]
        if texto.lower() in compra:
            return "Comprar"
        if texto.lower() in venta:
            return "Vender"
        return "nada"

    def ObtenerTicker(self, texto:str)->str:
        ticker = texto.lower()
        if "perp" in ticker:
            ticker = ticker.replace("perp", "")
        if "_usdt" not in ticker:
            if "usdt" in ticker:
                ticker = ticker.replace("usdt", "_usdt")
            else:
                ticker = ticker+"_usdt"
        return ticker

    def Desglozar(self, mensaje:str):
        x = mensaje.split()
        print(x)
        self.orden = self.ObtenerComando(x[0])
        self.ticker = self.ObtenerTicker(x[1])
        print("orden " + self.orden + " \n") 
        print("Desglozar " +self.ticker)

    def ObtenerCantidad(self, ticker:str)->float:
        #obtiene el saldo de usdt / precio del ticker
        balances = json.loads(gate_trade.balances())
        usdt_balance = balances['available']['USDT']
        print(usdt_balance)
        currency_pair = 'ron_usdt'  # Reemplaza 'ron_usdt' con el par de divisas correspondiente

        # Llama a la función ticker para obtener la información del precio actual
        response = gate_trade.ticker(currency_pair)

        # Obtiene el precio actual del par de divisas
        current_price = response['last']
        return usdt_balance / current_price

    def ObtenerPosicion(self, ticker:str)->float:
        #obtiene el saldo del ticker
        balance = gate_trade.balances()
        print(balance)
        balances = json.loads(balance)
        ticker_balance = balances['available'][ticker]
        return ticker_balance

    def Entrar(self, mensaje:str)->bool:
        currency_pair = 'ron_usdt'  # Reemplaza 'ron_usdt' con el par de divisas correspondiente

        # Llama a la función ticker para obtener la información del precio actual
        response = gate_trade.ticker(currency_pair)

        # Obtiene el precio actual del par de divisas
        current_price = response['last']    

        #Desglosar mensaje
        self.Desglozar(mensaje)

        #obtener la posicion actual del ticker
        #print("voy a obtener la posicion " + self.ticker)
        #pos = c.ObtenerPosicion(self.ticker)
        pos = self.ObtenerPosicion("RON")

        #obtener la cantidad a operar segun el ticker
        cantidad = self.ObtenerCantidad("USDT")

        print(self.orden + "->" + self.ticker + " " + str(cantidad))

        if self.orden == "Comprar":
            f = open("salida.txt", "a")
            f.write(self.orden + " -> " + self.ticker + " " + cantidad + "\n")
            f.close()
#   """          try:
#                # Place order buy
#                print(gate_trade.buy(self.ticker, current_price, cantidad))
#                self.Log(self.orden + " : " + self.ticker + " Cant: " + str(cantidad))
#            except Exception as e:
#                print("Error en la operación:", e)
#                self.Log("Error en la operación:", e)
#                if "code" in str(e):
#                    error_json = json.loads(str(e).replace("'", "\""))
#                    self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"]) """
                

        if self.orden == "Vender":
            if pos > 0:
                try:
                    # Realiza la venta al precio actual
                    response = gate_trade.sell(self.ticker, current_price, pos)
                    self.Log("Cerrando long previo "+ self.ticker + " Cant: " + str(abs(pos)))
                except Exception as e:
                        print("Error en la operación:", e)
                        self.Log("Error en la operación:", e)
                        if "code" in str(e):
                            error_json = json.loads(str(e).replace("'", "\""))
                            self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"])