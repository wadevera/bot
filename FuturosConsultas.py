from BinanceAPI import BinanceAPI

import requests

class FuturosConsultas:
    def __init__(self, client=None):
        self.client = client or BinanceAPI().get_futures_client()
    
    def colocar_orden_futuros_mercado(self, symbol: str, side: str, quantity: float):
        """Coloca una orden a mercado en futuros"""
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            return order
        except Exception as e:
            print(f"Error en orden futuros: {e}")
            return None
    
    def obtener_saldo_futuros(self, activo: str) -> float:
        """Obtiene el saldo disponible en futuros"""
        try:
            balances = self.client.futures_account_balance()
            for balance in balances:
                if balance['asset'] == activo:
                    return float(balance['availableBalance'])
            return 0.0
        except Exception as e:
            print(f"Error obteniendo saldo futuros: {e}")
            return 0.0
  



    def ObtenerCuentaGeneral(self) -> dict:
        endpoint = self.url + "/fapi/v2/account"
        parametros = "timestamp=" + str(self.ObtenerFechaServer())
        parametros = self.Firmar(parametros)
        h = self.Encabezados(self.apiKey)
        try:
            response = requests.get(self.url+endpoint, params=parametros, headers=h)
            response.raise_for_status() # genera una excepción si la solicitud no fue exitosa
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error al hacer la solicitud HTTP:", e)
            return None

    def ObtenerPosiciones(self)-> dict:
        ac = self.ObtenerCuentaGeneral()
        if "positions" in ac.keys():
            return ac["positions"]
        return None
    
    def ObtenerPosicion(self, simbolo:str)->dict:
        pos = self.ObtenerPosiciones()
        ticker = simbolo.upper()
        for item in pos:
            if item["symbol"] == ticker:
                return float(item["positionAmt"])
        return 0.0
