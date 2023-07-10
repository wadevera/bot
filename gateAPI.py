
# -*- coding: utf-8 -*-

'''
Provide the GateIO class to abstract web interaction
'''

from datetime import datetime
from HttpUtil2 import getSign, httpGet, httpPost

class GateIO:
    def __init__(self, url, apiKey, secretKey):
        self.__url = url
        self.__apiKey = apiKey
        self.__secretKey = secretKey

    ## General methods that query the exchange

    def pairs(self):
        URL = "/api2/1/pairs"
        params=''
        return httpGet(self.__url, URL, params)
    
    def coins_info(self):
        URL = "/api2/1/coininfo"
        params = ''
        return httpGet(self.__url, URL, params)

    def marketinfo(self):
        URL = "/api2/1/marketinfo"
        params=''
        return httpGet(self.__url, URL, params)

    def marketlist(self):
        URL = "/api2/1/marketlist"
        params=''
        return httpGet(self.__url, URL, params)

    def tickers(self):
        URL = "/api2/1/tickers"
        params=''
        return httpGet(self.__url, URL, params)

    def orderBooks(self):
        URL = "/api2/1/orderBooks"
        param=''
        return httpGet(self.__url, URL, param)

    def ticker(self, param):
        URL = "/api2/1/ticker"
        return httpGet(self.__url, URL, param)
#        return httpGet('api.gateio.ws', URL, param)

    def orderBook(self, param):
        URL = "/api2/1/orderBook"
        return httpGet(self.__url, URL, param)

    def tradeHistory(self, param):
        URL = "/api2/1/tradeHistory"
        return httpGet(self.__url, URL, param)

    ## Methods that make use of the users keys

    def balances(self):
        URL = "/api2/1/private/balances"
        param = {}
        return httpPost(self.__url, URL, param, self.__apiKey, self.__secretKey)

    def depositAddres(self,param):
        URL = "/api2/1/private/depositAddress"
        params = {'currency':param}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def depositsWithdrawals(self, start,end):
        URL = "/api2/1/private/depositsWithdrawals"
        params = {'start': start,'end':end}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def buy(self, currencyPair,rate, amount):
        URL = "/api2/1/private/buy"
        params = {'currencyPair': currencyPair,'rate':rate, 'amount':amount}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def sell(self, currencyPair, rate, amount):
        URL = "/api2/1/private/sell"
        params = {'currencyPair': currencyPair, 'rate': rate, 'amount': amount}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def cancelOrder(self, orderNumber, currencyPair):
        URL = "/api2/1/private/cancelOrder"
        params = {'orderNumber': orderNumber, 'currencyPair': currencyPair}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def cancelAllOrders(self, type, currencyPair):
        URL = "/api2/1/private/cancelAllOrders"
        params = {'type': type, 'currencyPair': currencyPair}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def getOrder(self, orderNumber, currencyPair):
        URL = "/api2/1/private/getOrder"
        params = {'orderNumber': orderNumber, 'currencyPair': currencyPair}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def openOrders(self):
        URL = "/api2/1/private/openOrders"
        params = {}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def mytradeHistory(self, currencyPair, orderNumber):
        URL = "/api2/1/private/tradeHistory"
        params = {'currencyPair': currencyPair, 'orderNumber': orderNumber}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)

    def withdraw(self, currency, amount, address):
        URL = "/api2/1/private/withdraw"
        params = {'currency': currency, 'amount': amount,'address':address}
        return httpPost(self.__url, URL, params, self.__apiKey, self.__secretKey)
    
    def Log(self, texto:str):
        f = open("ordenes.log", "a")
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " -> " + texto + "\n")
        f.close()