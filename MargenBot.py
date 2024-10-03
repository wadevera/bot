import json
import math
from MargenConsultas import MargenConsultas as Consultas
#from FuturosOrdenes import FuturosOrdenes as Ordenes
from BinanceAPI import BinanceAPI

class MargenBot:

    orden = ""
    ticker = ""

    def __init__(self):
        self.client = BinanceAPI().get_client()
    
    def ObtenerComando(self, texto:str)->str:
        compra = ["comprar", "compra", "buy", "long"]
        venta = ["vender", "vender", "venda", "sell", "short"]
        if texto.lower() in compra:
            return "Comprar"
        if texto.lower() in venta:
            return "Vender"
        return "nada"

    def ObtenerTicker(self, texto:str)->str:
        ticker = texto.upper()
        if "PERP" in ticker:
            ticker = ticker.replace("PERP", "")
        if "USDT" not in ticker:
            ticker = ticker+"USDT"
        return ticker

    def Desglozar(self, mensaje:str):
        x = mensaje.split()
        self.orden = self.ObtenerComando(x[0])
        self.ticker = self.ObtenerTicker(x[1])
        print("Desglozar " +self.ticker)

    def ObtenerCantidad(self, ticker:str)->float:
        #reemplazar por la cantidad pasada desde TView
        f = open("Cantidades.json", "r")
        cantidades = json.load(f)
        f.close
        if ticker in cantidades:
            return cantidades[ticker]
        return 0.0

    def Entrar(self, mensaje:str)->bool:
        c = Consultas()
        

        #Desglosar mensaje
        self.Desglozar(mensaje)

        #obtener la posicion actual del ticker
        print("voy a obtener la posicion " + self.ticker)
        #pos = c.ObtenerPosicion(self.ticker)
        saldos = c.obtener_saldo_margen()
        # Obtener el saldo disponible en USDT
        saldo_usdt = saldos.get('USDT', 0)
        saldo_ronin = saldos.get('RONIN', 0)
        # Obtener el precio actual de RONINUSDT
        precio_actual = c.obtener_precio_actual('RONINUSDT')
    
        if precio_actual is not None:
            print(f"El precio actual de RONINUSDT es: {precio_actual} USDT")
        
        # Calcular cuántos RONIN se pueden comprar con todo el saldo de USDT, redondeando hacia abajo
        cantidad_a_comprar = math.floor(saldo_usdt / precio_actual)  # Redondear hacia abajo
        

        #obtener la cantidad a operar segun el ticker
        cantidad = self.ObtenerCantidad(self.ticker)

        print(self.orden + "->" + self.ticker + " " + str(saldo_usdt) + " Pos actual: " + str(saldo_ronin))

        #o = Ordenes()
        if self.orden == "Comprar" and cantidad_a_comprar > 0:
            
            try:
                print(f"Colocando una orden de compra a precio de mercado para {cantidad_a_comprar} RONIN...")
                #order_id = c.colocar_orden_margen_mercado('RONINUSDT', 'BUY', cantidad_a_comprar)

                #o.ComprarMarket(self.ticker, cantidad)
                self.Log(self.orden + " : " + self.ticker + " Cant: " + str(cantidad_a_comprar))
            except Exception as e:
                print("Error en la operación:", e)
                self.Log("Error en la operación:", e)
                if "code" in str(e):
                    error_json = json.loads(str(e).replace("'", "\""))
                    self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"])
                

        if self.orden == "Vender":
            if saldo_ronin > 0:
                try:
                    cantidad_a_vender = math.floor(saldo_ronin)  # Redondear hacia abajo
                    print(f"Colocando una orden de venta a precio de mercado para {cantidad_a_vender} RONIN...")
                    #order_id = c.colocar_orden_margen_mercado('RONINUSDT', 'SELL', cantidad_a_vender)

                    self.Log("Vendiendo "+ self.ticker + " Cant: " + str(abs(saldo_ronin)) + " a " + str(abs(precio_actual)) + " por " + str(abs(cantidad_a_vender)))
                except Exception as e:
                        print("Error en la operación:", e)
                        self.Log("Error en la operación:", e)
                        if "code" in str(e):
                            error_json = json.loads(str(e).replace("'", "\""))
                            self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"])
            

        

