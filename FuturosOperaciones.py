from FuturosTrading import FuturosTrading
import math

class FuturosOperaciones:
    def __init__(self):
        self.futuros = FuturosTrading()
    
    def obtener_precision(self, symbol):
        """Obtiene la precisión decimal permitida para un símbolo"""
        try:
            exchange_info = self.futuros.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    for filtro in s['filters']:
                        if filtro['filterType'] == 'LOT_SIZE':
                            step_size = filtro['stepSize']
                            if 'e-' in step_size:
                                return int(step_size.split('e-')[1])
                            else:
                                return len(step_size.split('.')[1].rstrip('0'))
            return 3  # Valor por defecto
        except Exception as e:
            print(f"Error al obtener precisión: {e}")
            return 3
    
    def comprar_btc(self, porcentaje=0.95, apalancamiento=1):
        """Compra BTCUSDT con un porcentaje del saldo disponible"""
        return self._comprar_activo('BTCUSDT', 'USDT', porcentaje, apalancamiento)
    
    def vender_btc(self, porcentaje=1.0, apalancamiento=1):
        """Vende el BTC disponible en futuros"""
        return self._vender_activo('BTCUSDT', 'BTC', porcentaje, apalancamiento)
    
  #  def comprar_ronin(self, porcentaje=0.95, apalancamiento=1):
   #     """Compra RONINUSDT con un porcentaje del saldo disponible"""
  #      return self._comprar_activo('RONINUSDT', 'USDT', porcentaje, apalancamiento)

    def comprar_ronin(self, porcentaje=0.95, apalancamiento=1, cantidad_fija=None):
        """Compra RONIN con opción de cantidad fija"""
        if cantidad_fija:
            return self._comprar_activo_fija('RONINUSDT', 'USDT', cantidad_fija, apalancamiento)
        else:
            return self._comprar_activo('RONINUSDT', 'USDT', porcentaje, apalancamiento)
    
    def _comprar_activo_fija(self, symbol, asset, cantidad, apalancamiento):
        """Función para comprar con cantidad fija"""
        try:
            # Establecer apalancamiento
            self.futuros.establecer_apalancamiento(symbol, apalancamiento)
            
            # Verificar cantidad mínima
            min_qty = self.futuros.obtener_minimo_qty(symbol)
            if cantidad < min_qty:
                print(f"Cantidad insuficiente. Mínimo requerido: {min_qty}")
                return None
            
            print(f"Comprando {cantidad} {symbol.replace('USDT', '')}...")
            
            # Colocar orden
            orden = self.futuros.colocar_orden_futuros_market(
                symbol=symbol,
                side='BUY',
                quantity=cantidad,
                leverage=apalancamiento
            )
            
            return orden
        except Exception as e:
            print(f"Error en la compra de {symbol}: {e}")
            return None
    
    def vender_ronin(self, porcentaje=1.0, apalancamiento=1):
        """Vende el RONIN disponible en futuros"""
        return self._vender_activo('RONINUSDT', 'RONIN', porcentaje, apalancamiento)
    
    def _comprar_activo(self, symbol, asset, porcentaje, apalancamiento):
        """Función genérica para comprar un activo"""
        try:
            # Obtener saldo disponible
            saldo = self.futuros.obtener_saldo_futuros(asset=asset)
            if saldo <= 0:
                print(f"No hay saldo disponible en {asset}")
                return None
            
            # Obtener precio actual
            precio = self.futuros.obtener_precio_actual(symbol)
            if precio is None:
                print(f"Error al obtener precio de {symbol}")
                return None
            
            # Calcular cantidad a comprar
            if asset == 'USDT':
                cantidad = (saldo * porcentaje) / precio
            else:
                cantidad = saldo * porcentaje
            
            # Ajustar precisión
            precision = self.obtener_precision(symbol)
            cantidad = round(cantidad, precision)
            
            # Verificar cantidad mínima
            min_qty = self.futuros.obtener_minimo_qty(symbol)
            if cantidad < min_qty:
                print(f"Cantidad insuficiente. Mínimo requerido: {min_qty}")
                return None
            
            print(f"Comprando {cantidad} {symbol.replace('USDT', '')} con {saldo * porcentaje:.2f} {asset}...")
            
            # Colocar orden
            orden = self.futuros.colocar_orden_futuros_market(
                symbol=symbol,
                side='BUY',
                quantity=cantidad,
                leverage=apalancamiento
            )
            
            return orden
        except Exception as e:
            print(f"Error en la compra de {symbol}: {e}")
            return None
    
    def _vender_activo(self, symbol, asset, porcentaje, apalancamiento):
        """Función genérica para vender un activo"""
        try:
            # Obtener posición
            posicion = self.futuros.obtener_posicion(symbol)
            if not posicion or abs(float(posicion['cantidad'])) == 0:
                print(f"No hay posición de {asset} para vender")
                return None
            
            # Obtener cantidad disponible
            cantidad_disponible = abs(float(posicion['cantidad']))
            
            # Calcular cantidad a vender
            cantidad = cantidad_disponible * porcentaje
            
            # Ajustar precisión
            precision = self.obtener_precision(symbol)
            cantidad = round(cantidad, precision)
            
            # Verificar cantidad mínima
            min_qty = self.futuros.obtener_minimo_qty(symbol)
            if cantidad < min_qty:
                print(f"Cantidad insuficiente. Mínimo requerido: {min_qty}")
                return None
            
            print(f"Vendiendo {cantidad} {asset}...")
            
            # Determinar dirección de venta (inversa a la posición actual)
            side = 'SELL' if posicion['lado'] == 'LONG' else 'BUY'
            
            # Colocar orden
            orden = self.futuros.colocar_orden_futuros_market(
                symbol=symbol,
                side=side,
                quantity=cantidad,
                leverage=apalancamiento,
                reduce_only=True  # Solo para reducir posición
            )
            
            return orden
        except Exception as e:
            print(f"Error en la venta de {symbol}: {e}")
            return None