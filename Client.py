
# -*- coding: utf-8 -*-
# encoding: utf-8

'''
Provide user specific data and interact with gate.io
'''
import json
import Configuracion
from gateAPI import GateIO
from GateBot import GateBot

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


# Trading Pairs
#print(gate_query.pairs())


# Below, use general methods that query the exchange

#  Market Info
# print(gate_query.marketinfo())

# Market Details
# print(gate_query.marketlist())

# Tickers
# print(gate_query.tickers())
# Depth
# print(gate_query.orderBooks())

# orders
print(gate_query.openOrders())


# Below, use methods that make use of the users keys

# Ticker
print(gate_query.ticker('ron_usdt'))

# Market depth of pair
# print(gate_query.orderBook('btc_usdt'))

# Trade History
#print(gate_query.tradeHistory('ron_usdt'))

# Get account fund balances
#print(gate_trade.balances())

# get new address
# print(gate_trade.depositAddres('btc'))

# get deposit withdrawal history
# print(gate_trade.depositsWithdrawals('1469092370', '1569092370'))

# Place order buy
#print(gate_trade.buy('ron_usdt', '0.9', '5'))

# Place order sell
# print(gate_trade.sell('etc_btc', '0.001', '123'))

# Cancel order
#print(gate_trade.cancelOrder('364536690245', 'ron_usdt'))

# Cancel all orders
#print(gate_trade.cancelAllOrders('0', 'ron_usdt'))

# Get order status
#print(gate_trade.getOrder('323498291104', 'eth_usdt'))

# Get my last 24h trades
#print(gate_trade.mytradeHistory('ron_usdt', '267040896'))

# withdraw
# print(gate_trade.withdraw('btc', '88', btcAddress))

###
#currency_pair = 'ron_usdt'  # Reemplaza 'ron_usdt' con el par de divisas correspondiente

# Llama a la función ticker para obtener la información del precio actual
#response = gate_trade.ticker(currency_pair)

# Obtiene el precio actual del par de divisas
#current_price = response['last']
#print(current_price)
###

#precio_rebajado = float(current_price) - 0.001 

# Imprime el precio actual
#print(f"Precio actual de {currency_pair}: {current_price}")

# Obtén el saldo de la criptomoneda 'ron' en tu cuenta
#balances = json.loads(gate_trade.balances())
#ron_balance = balances['available']['RON']
#print(ron_balance)

#print(balances)


# Calcula la cantidad a vender como el total del saldo de 'ron'
#amount_to_sell = ron_balance



# Realiza la venta al precio actual
#response = gate_trade.sell(currency_pair, current_price, amount_to_sell)

# Realiza la venta utilizando una orden de mercado
#response = gate_trade.sell(currency_pair, precio_rebajado, amount_to_sell)


# Imprime la respuesta
#print(response)

##################
#simular flask
##################
parametro = "Comprar RONUSDT"
api_trade_url = Configuracion.API_TRADE_URL


# Tomar los valores de configuración del archivo Configuracion.py

api_key = Configuracion.GATE_API_KEY
secret_key = Configuracion.GATE_SECRET_KEY

# Modificación en la creación de la instancia de GateBot
bot = GateBot(api_trade_url, api_key, secret_key)

bot.Entrar(parametro)
print(gate_query.openOrders())
print(gate_trade.balances())
