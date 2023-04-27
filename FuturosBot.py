import json
from FuturosConsultas import FuturosConsultas as Consultas
from FuturosOrdenes import FuturosOrdenes as Ordenes
from Binance import Binance

class FuturosBot(Binance):

    orden = ""
    ticker = ""

    def __init__(self):
        Binance.__init__(self)
    
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
        pos = c.ObtenerPosicion(self.ticker)

        #obtener la cantidad a operar segun el ticker
        cantidad = self.ObtenerCantidad(self.ticker)

        print(self.orden + "->" + self.ticker + " " + str(cantidad) + " Pos actual: " + str(pos))

        o = Ordenes()
        if self.orden == "Comprar":
            if pos < 0:
                try:
                    o.CerrarVentaMarket(self.ticker, abs(pos))
                    self.Log("Cerrando short previo "+ self.ticker + " Cant: " + str(abs(pos)))
                except Exception as e:
                    self.Log("Error en la operación:"+ e)
                    if "code" in str(e):
                        error_json = json.loads(str(e).replace("'", "\""))
                        self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"])    
            try:
                o.ComprarMarket(self.ticker, cantidad)
                self.Log(self.orden + " : " + self.ticker + " Cant: " + str(cantidad))
            except Exception as e:
                print("Error en la operación:", e)
                self.Log("Error en la operación:", e)
                if "code" in str(e):
                    error_json = json.loads(str(e).replace("'", "\""))
                    self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"])
                

        if self.orden == "Vender":
            if pos > 0:
                try:
                    o.CerrarCompraMarket(self.ticker, pos)
                    self.Log("Cerrando long previo "+ self.ticker + " Cant: " + str(abs(pos)))
                except Exception as e:
                        print("Error en la operación:", e)
                        self.Log("Error en la operación:", e)
                        if "code" in str(e):
                            error_json = json.loads(str(e).replace("'", "\""))
                            self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"])
            try:
                o.VenderMarket(self.ticker, cantidad)
                self.Log(self.orden + " : " + self.ticker + " Cant: " + str(cantidad))
            except Exception as e:
                print("Error en la operación:", e)
                self.Log("Error en la operación:", e)
                if "code" in str(e):
                    error_json = json.loads(str(e).replace("'", "\""))
                    self.Log("Código de respuesta:" + error_json["code"] + "\n" + "Mensaje de respuesta:"+ error_json["msg"])


        

