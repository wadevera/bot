import math
from MargenConsultas import MargenConsultas

def main():
    margen = MargenConsultas()
    

    # Coloca una orden de margen (ajusta los parámetros según sea necesario)
    #margen.colocar_orden_margen('RONINUSDT', 'BUY', 10, 1.8)

    # Consulta las órdenes abiertas
    #open_orders = margen.obtener_ordenes_abiertas('RONINUSDT')

    # Consulta y cancela todas las órdenes abiertas
    #margen.cancelar_todas_las_ordenes_abiertas('RONINUSDT')
    
    # Consulta el saldo de margen
    saldos = margen.obtener_saldo_margen()
    
    # Imprimir la información de saldo
    if saldos:
        print("Saldo de margen:")
        for activo, saldo in saldos.items():
            print(f"Activo: {activo}, Saldo: {saldo}")
    else:
        print("No hay activos con saldo disponible.")
        return  # Salir si no hay saldos disponibles

    # Obtener el saldo disponible en USDT
    saldo_usdt = saldos.get('USDT', 0)

    # Obtener el precio actual de RONINUSDT
    precio_actual = margen.obtener_precio_actual('RONINUSDT')
    
    if precio_actual is not None:
        print(f"El precio actual de RONINUSDT es: {precio_actual} USDT")
        
        # Calcular cuántos RONIN se pueden comprar con todo el saldo de USDT, redondeando hacia abajo
        cantidad_a_comprar = math.floor(saldo_usdt / precio_actual)  # Redondear hacia abajo
        if cantidad_a_comprar > 0:
            print(f"Colocando una orden de compra a precio de mercado para {cantidad_a_comprar} RONIN...")
            #order_id = margen.colocar_orden_margen_mercado('RONINUSDT', 'BUY', cantidad_a_comprar)
            #order_id = margen.colocar_orden_margen_mercado('RONINUSDT', 'BUY', 10)
        else:
            print("No hay suficiente saldo en USDT para comprar RONIN.")
    else:
        print("No se pudo obtener el precio de RONINUSDT.")
    
    # Vender todo el saldo de RONIN (parte entera)
    saldo_ronin = saldos.get('RONIN', 0)
    if saldo_ronin > 0:
        cantidad_a_vender = math.floor(saldo_ronin)  # Redondear hacia abajo
        print(f"Colocando una orden de venta a precio de mercado para {cantidad_a_vender} RONIN...")
        order_id = margen.colocar_orden_margen_mercado('RONINUSDT', 'SELL', cantidad_a_vender)
    else:
        print("No hay saldo de RONIN disponible para vender.")
    
    




if __name__ == "__main__":
    main()


