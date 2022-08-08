from strats.TradingStrat import TradingStrat
from ta.trend import EMAIndicator 
import pandas as pd

class MA600_cross(TradingStrat):
    def __init__(self, candles):
        super().__init__(candles)
        self.signals = self.__signals()
        

    

    def __indicators(self):
        df = self.candles
        df['green_candle'] = df['close'] > df['open']
        df['red_candle'] = df['close'] < df['open']

        
        df['600MA'] = EMAIndicator(window=600, close=df['close']).ema_indicator()
        self.candles = df
        
        
    def __signals(self):
        self.__indicators()
        df = self.candles
        

        crossover = [df['green_candle'].index[-2],
                     df['green_candle'].index[-1],
                     df['open'].index[-2] < df['600MA'].index[-2],
                     df['close'].index[-2] > df['600MA'].index[-2]]
        crossover = pd.Series(crossover).all()

        crossunder = [df['red_candle'].index[-2],
                     df['red_candle'].index[-1],
                     df['open'].index[-2] > df['600MA'].index[-2],
                     df['close'].index[-2] < df['600MA'].index[-2]]
        crossunder = pd.Series(crossunder).all()

        buy = crossover
        sell = crossunder
        return[buy, sell]