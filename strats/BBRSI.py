from strats.TradingStrat import TradingStrat
from ta.volatility import BollingerBands
from ta.volatility import AverageTrueRange as ATR
from ta.momentum import RSIIndicator as RSI
from ta.momentum import StochRSIIndicator as Stoch
import pandas as pd

class BBRSI(TradingStrat):
    def __init__(self, candles):
        super().__init__(candles)

        self.ratio = 5
        self.self.RSI_range_lower =30
        self.self.RSI_range_upper = 70
        self.atr_multiple = 5
        self.self.band_wiggle = 0.05
        
    
    def __indicators(self):
        #add indicators here
        df = self.candles
        indicator_RSI = RSI(close=df['close'], window=14)
        indicator_ATR = ATR(high=df['high'], low=df['low'], close=df['close'], window=14)
        indicator_Stoch = Stoch(close=df['close'], window=14, smooth1=3, smooth2=3)
        indicator_bb = BollingerBands(close=df["close"], window=20, window_dev=2)
        indicator_bb1d = BollingerBands(close=df["close"], window=20, window_dev=1)
        
        df['bb_bbm'] = indicator_bb.bollinger_mavg()
        df['bb_bbh'] = indicator_bb.bollinger_hband()
        df['bb_bbl'] = indicator_bb.bollinger_lband()
        df['bb_bb%'] = indicator_bb.bollinger_pband()
        df['bb_bbw'] = indicator_bb.bollinger_wband()
        df['bb_bbh1d'] = indicator_bb1d.bollinger_hband()
        df['bb_bbl1d'] = indicator_bb1d.bollinger_lband()
        df['rsi'] = indicator_RSI.rsi()
        df['atr'] = indicator_ATR.average_true_range()
        df['stoch_k'] = indicator_Stoch.stochrsi_k()
        df['stoch_d'] = indicator_Stoch.stochrsi_d()

        df['rsioversold'] = df['rsi'] <= 30
        df['rsioverbought'] = df['rsi'] >= 70

        df['green_candle'] = df['close'] > df['open']
        df['red_candle'] = df['close'] < df['open']
        self.candles = df

    
    def __signals(self):
        BBRSI.__indicators()
        df = self.candles
        
        #candle patterns
        lower_band_touch = [df['bb_bb%'].index[-2] < self.band_wiggle,
                            df['bb_bb%'].index[-1] < self.band_wiggle]
        lower_band_touch = pd.Series(lower_band_touch).any()
        upper_band_touch = [df['bb_bb%'].index[-2] > (1-self.band_wiggle),
                            df['bb_bb%'].index[-1] > (1-self.band_wiggle)]
        upper_band_touch = pd.Series(upper_band_touch).any()
        
        

        
        #buy/sell signals
        strong_buy = [df['rsioversold'].index[-2],
                    not df['rsioversold'].index[-1],
                    df['stoch_k'].index[-2] < df['stoch_d'].index[-2],
                    df['stoch_k'].index[-1] > df['stoch_d'].index[-1],
                    lower_band_touch,
                    df['bb_bb%'].index[-1]>0,
                    df['green_candle'].index[-1]]
        strong_buy = pd.Series(strong_buy).all()


        strong_sell = [df['rsioverbought'].index[-2],
                    not df['rsioverbought'].index[-1],
                    df['stoch_k'].index[-2] > df['stoch_d'].index[-2],
                    df['stoch_k'].index[-1] < df['stoch_d'].index[-1],
                    upper_band_touch,
                    df['bb_bb%'].index[-1]<1,
                    df['red_candle'].index[-1]]
        strong_sell = pd.Series(strong_sell).all()


        exit_buy = [lower_band_touch,
                    df['green_candle'].index[-1],
                    df['stoch_k'].index[-2] < df['stoch_d'].index[-2],
                    df['stoch_k'].index[-1] > df['stoch_d'].index[-1],
                    self.RSI_range_lower < df['rsi'].index[-1] < self.RSI_range_upper]
        exit_buy = pd.Series(exit_buy).all()

        exit_sell = [upper_band_touch,
                    df['red_candle'].index[-1],
                    df['stoch_k'].index[-2] > df['stoch_d'].index[-2],
                    df['stoch_k'].index[-1] < df['stoch_d'].index[-1],
                    self.RSI_range_lower < df['rsi'].index[-1] < self.RSI_range_upper]
        exit_sell = pd.Series(exit_sell).all()

        entry_buy = [df['green_candle'].index[-1],
                    df['stoch_k'].index[-2] < df['stoch_d'].index[-2],
                    df['stoch_k'].index[-1] > df['stoch_d'].index[-1],
                    self.RSI_range_lower < df['rsi'].index[-1] < self.RSI_range_upper,
                    lower_band_touch]
                    #df['open'].index[-1] < df['bb_bbm'].index[-1] < df['close'].index[-1]]
        entry_buy = pd.Series(entry_buy).all()

        entry_sell = [df['red_candle'].index[-1],
                    df['stoch_k'].index[-2] > df['stoch_d'].index[-2],
                    df['stoch_k'].index[-1] < df['stoch_d'].index[-1],
                    self.RSI_range_lower < df['rsi'].index[-1] < self.RSI_range_upper,
                    upper_band_touch]
                    #df['open'].index[-1] > df['bb_bbm'].index[-1] > df['close'].index[-1]]
        entry_sell = pd.Series(entry_sell).all()   

        self.buy = strong_buy or entry_buy
        self.sell = strong_sell or entry_sell

