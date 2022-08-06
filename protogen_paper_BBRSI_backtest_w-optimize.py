# Paper trading version of Protogen Alorithmic Trading Bot

import ccxt
import config
import schedule
import pandas as pd
pd.set_option('display.max_rows', None)
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator, SMAIndicator
from ta.volatility import AverageTrueRange as ATR
from ta.momentum import RSIIndicator as RSI
from ta.momentum import StochRSIIndicator as Stoch

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

from scipy.optimize import minimize, Bounds
from scipy import optimize


# exchange = ccxt.binanceus({
#     "apiKey": config.BINANCE_API_KEY,
#     "secret": config.BINANCE_SECRET_KEY
# })

exchange = ccxt.binanceus()



def indicators(df):
    indicator_RSI = RSI(close=df['close'], window=14)
    indicator_ATR = ATR(high=df['high'], low=df['low'], close=df['close'], window=14)
    indicator_Stoch = Stoch(close=df['close'], window=14, smooth1=3, smooth2=3)
    indicator_bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    indicator_bb1d = BollingerBands(close=df["close"], window=20, window_dev=1)

    df['50ema'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
    df['10ema'] = EMAIndicator(close=df['close'], window=10).ema_indicator()
    
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
    
    df['uptrend'] = df['close'] > df['10ema']
    
    
    return df





def check_buy_sell_signals(dfinit, p):
    in_position = False
    position = ''
    balance_usd = 1000 #starting balance USD
    balance_pos = 0.025 #starting position balance
    fees = 0
    fee = 0.00075
    stoploss = 0
    size = 0
    usd_size = 0
    profit_target = 0
    breakeven = 0
    trailing_loss = False
    orders = pd.DataFrame(columns=['Timestamp',
                                'Type',
                                'Position',
                                'Price',
                                'Amount USD', 
                                'Amount BTC',
                                'Balance USD',
                                'Balance BTC',
                                'Total Fees', 
                                'USD Gains',
                                'BTC Gains',
                                'Total Gains USD',
                                'Total Gains %'])
    init_time = datetime.utcnow()                              
    orders = orders.append({'Timestamp': init_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'Type': '',
                                'Position': '',
                                'Price': '', 
                                'Amount USD': '', 
                                'Amount BTC': '',
                                'Balance USD': balance_usd,
                                'Balance BTC': balance_pos,
                                'Total Fees': '',
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)
    # print("checking for buy and sell signals")
    # print(df.iloc[:, :11].tail(5))
    # print(df.iloc[:, 11:].tail(5))

    dfsize = 55
    # x =  range(dfsize, dfinit.index[-1])
    x =  range(dfsize, len(dfinit))
    for i in x:
            
        df = dfinit.iloc[(i-dfsize):(i+1)]
        
        last_row_index = df.index[-1]
        previous_row_index = last_row_index - 1
        
        risk_reward_ratio = p[0]
        RSI_range_lower = p[1]
        RSI_range_upper = p[2]
        atr_multiple = p[3]
        band_wiggle = p[4]


        #candle patterns
        lower_band_touch = [df['bb_bb%'][previous_row_index-1] < band_wiggle,
                            df['bb_bb%'][previous_row_index] < band_wiggle,
                            df['bb_bb%'][last_row_index] < band_wiggle]
        lower_band_touch = pd.Series(lower_band_touch).any()
        upper_band_touch = [df['bb_bb%'][previous_row_index-1] > (1-band_wiggle),
                            df['bb_bb%'][previous_row_index] > (1-band_wiggle),
                            df['bb_bb%'][last_row_index] > (1-band_wiggle)]
        upper_band_touch = pd.Series(upper_band_touch).any()
        
        

        
        #buy/sell signals
        strong_buy = [df['rsioversold'][previous_row_index],
                      not df['rsioversold'][last_row_index],
                      df['stoch_k'][previous_row_index] < df['stoch_d'][previous_row_index] or df['stoch_k'][previous_row_index-1] < df['stoch_d'][previous_row_index-1],
                      df['stoch_k'][last_row_index] > df['stoch_d'][last_row_index] or df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                      lower_band_touch,
                      df['bb_bb%'][last_row_index]>0,
                      df['green_candle'][last_row_index],
                      df['stoch_k'][previous_row_index] <= .20]
        strong_buy = pd.Series(strong_buy).all()


        strong_sell = [df['rsioverbought'][previous_row_index],
                       not df['rsioverbought'][last_row_index],
                       df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index] or df['stoch_k'][previous_row_index -1] > df['stoch_d'][previous_row_index-1],
                       df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index] or df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                       upper_band_touch,
                       df['bb_bb%'][last_row_index]<1,
                       df['red_candle'][last_row_index],
                       df['stoch_k'][previous_row_index] >= .80]
        strong_sell = pd.Series(strong_sell).all()


        range_buy = [lower_band_touch,
                    df['green_candle'][last_row_index],
                    df['stoch_k'][previous_row_index] < df['stoch_d'][previous_row_index],
                    df['stoch_k'][last_row_index] > df['stoch_d'][last_row_index],
                    df['bb_bb%'][last_row_index] > 0,
                    df['stoch_k'][previous_row_index] <= .20]
        range_buy = pd.Series(range_buy).all()

        range_sell = [upper_band_touch,
                    df['red_candle'][last_row_index],
                    df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                    df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index],
                    df['bb_bb%'][last_row_index] < 1,
                    df['stoch_k'][previous_row_index] >= .80]
        range_sell = pd.Series(range_sell).all()

        middle_buy = [df['green_candle'][last_row_index],
                    df['stoch_k'][previous_row_index] < df['stoch_d'][previous_row_index],
                    df['stoch_k'][last_row_index] > df['stoch_d'][last_row_index],
                    RSI_range_upper < df['rsi'][last_row_index] < 70,
                    # df['rsi'][last_row_index] > df['rsi'][previous_row_index],
                    #lower_band_touch]
                    df['open'][last_row_index] < df['bb_bbh1d'][last_row_index] < df['close'][last_row_index]]
                    #df['stoch_k'][previous_row_index] <= .20]
        middle_buy = pd.Series(middle_buy).all()

        middle_sell = [df['red_candle'][last_row_index],
                    df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                    df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index],
                    30 < df['rsi'][last_row_index] < RSI_range_lower,
                    # df['rsi'][last_row_index] < df['rsi'][previous_row_index],
                    #upper_band_touch]
                    df['open'][last_row_index] > df['bb_bbl1d'][last_row_index] > df['close'][last_row_index]]
                    #df['stoch_k'][previous_row_index] >= .80]
        middle_sell = pd.Series(middle_sell).all()

        double_MA_cross_up = [df['open'][last_row_index] < df['10ema'][last_row_index] < df['close'][last_row_index],
                              (df['open'][last_row_index] < df['50ema'][last_row_index] < df['close'][last_row_index]) or (df['open'][last_row_index] < df['bb_bbm'][last_row_index] < df['close'][last_row_index])]
        double_MA_cross_up = pd.Series(double_MA_cross_up).all()

        double_MA_cross_down = [df['open'][last_row_index] > df['10ema'][last_row_index] > df['close'][last_row_index],
                              (df['open'][last_row_index] > df['50ema'][last_row_index] > df['close'][last_row_index]) or (df['open'][last_row_index] > df['bb_bbm'][last_row_index] > df['close'][last_row_index])]
        double_MA_cross_down = pd.Series(double_MA_cross_down).all()

        for k in range(2):
            if not in_position:
                
                

                if (strong_buy or range_buy or middle_buy):
                    
                    
                    usd_size = 0.95 * balance_usd
                    size = usd_size / df['close'][last_row_index]
                    balance_pos += size
                    fees += usd_size * fee
                    balance_usd -= usd_size
                    #print(df['timestamp'][last_row_index],"Reversal from lower BB, BUY LONG!")
                    in_position = True
                    position = 'long'
                    trailing_loss = False
                    stoploss = df['close'][last_row_index] - atr_multiple*df['atr'][last_row_index]
                    profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - stoploss)
                    breakeven = df['close'][last_row_index]
                    orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                    'Price': df['close'][last_row_index], 
                                    'Type': position, 
                                    'Position': 'Open',
                                    'Amount USD': usd_size, 
                                    'Amount BTC': size,
                                    'Balance USD': '',
                                    'Balance BTC': '',
                                    'Total Fees': fees,
                                    'USD Gains': '',
                                    'BTC Gains': '',
                                    'Total Gains USD': '',
                                    'Total Gains %': ''}, ignore_index=True)
                
                
                elif (strong_sell or range_sell or middle_sell):
                    
                    
                    size = 0.95 * balance_pos
                    usd_size = size * df['close'][last_row_index]
                    balance_usd += usd_size
                    
                    fees += usd_size * fee
                    balance_pos -= size
                    #print(df['timestamp'][last_row_index], "Reversal from upper BB, SELL SHORT!")
                    in_position = True
                    position = 'short'
                    trailing_loss = False
                    stoploss = df['close'][last_row_index] + atr_multiple*df['atr'][last_row_index]
                    profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - stoploss)
                    breakeven = df['close'][last_row_index]
                    orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                    'Price': df['close'][last_row_index], 
                                    'Type': position,
                                    'Position': 'Open', 
                                    'Amount USD': usd_size, 
                                    'Amount BTC': size,
                                    'Balance USD': '',
                                    'Balance BTC': '',
                                    'Total Fees': fees,
                                    'USD Gains': '',
                                    'BTC Gains': '',
                                    'Total Gains USD': '',
                                    'Total Gains %': ''}, ignore_index=True)

                


            elif in_position:
                if position=='long':
                    
                    
                    if (df['high'][last_row_index] < profit_target and df['bb_bb%'][last_row_index] >= 1):# or trailing_loss:
                        stoploss = max(breakeven, stoploss, df['bb_bbh1d'][last_row_index])
                        trailing_loss = True
                    
                    elif df['high'][last_row_index] >= profit_target:
                        stoploss = max(stoploss, profit_target, df['bb_bbh1d'][last_row_index])

                    else:
                        pass
                        
                    
                    

                    
                            
                    if (df['close'][last_row_index] < stoploss):
                        #sell
                        usd_size = size * df['close'][last_row_index]
                        balance_usd += usd_size
                        fees += usd_size * fee
                        balance_pos -= size
                        #print(df['timestamp'][last_row_index],"CLOSE LONG POSITION!")
                        in_position = False
                        
                        orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                    'Price': df['close'][last_row_index], 
                                    'Type': position,
                                    'Position': 'Closed', 
                                    'Amount USD': usd_size, 
                                    'Amount BTC': size,
                                    'Balance USD': balance_usd,
                                    'Balance BTC': balance_pos,
                                    'Total Fees': fees,
                                    'USD Gains': (balance_usd - orders['Balance USD'][0])/orders['Balance USD'][0] * 100,
                                    'BTC Gains': (balance_pos - orders['Balance BTC'][0])/orders['Balance BTC'][0] * 100,
                                    'Total Gains USD': (balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index] - fees,
                                    'Total Gains %': ((balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index] - fees)/(orders['Balance USD'][0] + orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                        ignore_index=True)

                elif position=='short':
                    
                    
                    if (df['low'][last_row_index] > profit_target and df['bb_bb%'][last_row_index] <= 0):# or trailing_loss:
                        stoploss = min(breakeven, stoploss, df['bb_bbl1d'][previous_row_index])
                        trailing_loss = True

                    elif df['low'][last_row_index] < profit_target:
                        stoploss = min(stoploss, profit_target, df['bb_bbl1d'][last_row_index])

                    else:
                        pass


                    if (df['close'][last_row_index] > stoploss):
                        #buy
                        size = usd_size / df['close'][last_row_index]
                        balance_pos += size
                        fees += usd_size * fee
                        balance_usd -= usd_size
                        #print(df['timestamp'][last_row_index],"CLOSE SHORT POSITION!")
                        in_position = False
                        
                        orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                    'Price': df['close'][last_row_index], 
                                    'Type': position, 
                                    'Position': 'Closed',
                                    'Amount USD': usd_size, 
                                    'Amount BTC': size,
                                    'Balance USD': balance_usd,
                                    'Balance BTC': balance_pos,
                                    'Total Fees': fees,
                                    'USD Gains': (balance_usd - orders['Balance USD'][0])/orders['Balance USD'][0] * 100,
                                    'BTC Gains': (balance_pos - orders['Balance BTC'][0])/orders['Balance BTC'][0] * 100,
                                    'Total Gains USD': (balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index] - fees,
                                    'Total Gains %': ((balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index] - fees)/(orders['Balance USD'][0] + orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                        ignore_index=True)
            
            # print('BTC:', balance_pos)
            # print('USD:', balance_usd)
            # print('Total Fees (USD):', fees)
            # print(orders)
    print(df)        
    return orders

def run_bot(p):
    
    print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv('BTC/USD', timeframe='5m', limit=1000)
    
    
        
    
        
    
    dfinit = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    dfinit['timestamp'] = pd.to_datetime(dfinit['timestamp'], unit='ms')
    
    df = indicators(dfinit)
    # print(df)
    orders = check_buy_sell_signals(df, p)
    print(orders)
    print('Number of Candles: ', len(bars))
        
        
    
    if not orders['Total Gains USD'][orders.index[-1]]:
        gain = float(orders['Total Gains USD'][orders.index[-2]])
        
    else:
        gain = float(orders['Total Gains USD'][orders.index[-1]])
        
    gains = np.array([1/gain])
    # print(gains)
    return gains

p0 = np.array([5, #risk_reward_ratio
      40,  #RSI_range_lower
      60,  #RSI_range_upper
      5,    #atr_multiple
      0.05])   #band_wiggle


# p0 = np.array([2, #risk_reward_ratio
#       2])   #atr_multiple
     


# bounds = [(0.1, 10), (30, 50), (50, 70), (0.1, 10), (0,0.1)]
# bounds = Bounds([0.1, 0.1], [10, 10])
gains = run_bot(p0)
# print(gains)



# schedule.every(5).seconds.do(run_bot)

# con = [{"type" : "ineq", "fun" : run_bot}]
# res = minimize(run_bot, p0, constraints=con,
#                options={'disp': True})

# print(res)


# res = optimize.shgo(run_bot, bounds)

# print(res)

# while True:
#     schedule.run_pending()
#     time.sleep(1)