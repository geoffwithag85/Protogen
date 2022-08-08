import ccxt
import pandas as pd

class Belter:
    def __init__(self, APIkey, APIsecret):
        self.apikey = APIkey
        self.apisecret = APIsecret
        self.exchange = ccxt.binanceus({
            "apiKey": self.apikey,
            "secret": self.apisecret
        })
        self.switch = True

        self.autobalance()
    

    def orders(self):
        #insert order tracking code here
        pass

    def autobalance(self):
        #insert autobalance account code here
        pass

    def buy(self):
        pass

    def sell(self):
        pass



