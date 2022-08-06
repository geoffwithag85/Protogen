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
    
    
    
    
    return df




in_position = False
position = ''
balance_usd = 1000 #starting balance USD
balance_pos = .03 #starting position balance
fees = 0
fee = 0.00075
stoploss = 0
size = 0
usd_size = 0
profit_target = 0
breakeven = 0
orders = None
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
def check_buy_sell_signals(df):
    global in_position
    global balance_usd
    global balance_pos
    global fees
    global position
    global stoploss
    global size
    global usd_size
    global orders
    global profit_target
    global breakeven 
    # print("checking for buy and sell signals")
    # print(df.iloc[:, :11].tail(5))
    # print(df.iloc[:, 11:].tail(5))
    last_row_index = df.index[-1]
    previous_row_index = last_row_index - 1
    
    risk_reward_ratio = 4
    RSI_range_lower = 30
    RSI_range_upper = 70
    atr_multiple = 4
    band_wiggle = 0.05

    #candle patterns
    lower_band_touch = [df['bb_bb%'][previous_row_index] < band_wiggle,
                        df['bb_bb%'][last_row_index] < band_wiggle]
    lower_band_touch = pd.Series(lower_band_touch).any()
    upper_band_touch = [df['bb_bb%'][previous_row_index] > (1-band_wiggle),
                        df['bb_bb%'][last_row_index] > (1-band_wiggle)]
    upper_band_touch = pd.Series(upper_band_touch).any()
    
    

    
    #buy/sell signals
    strong_buy = [df['rsioversold'][previous_row_index],
                  not df['rsioversold'][last_row_index],
                  df['stoch_k'][previous_row_index] < df['stoch_d'][previous_row_index],
                  df['stoch_k'][last_row_index] > df['stoch_d'][last_row_index],
                  lower_band_touch,
                  df['bb_bb%'][last_row_index]>0,
                  df['green_candle'][last_row_index]]
    strong_buy = pd.Series(strong_buy).all()


    strong_sell = [df['rsioverbought'][previous_row_index],
                   not df['rsioverbought'][last_row_index],
                   df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                   df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index],
                   upper_band_touch,
                   df['bb_bb%'][last_row_index]<1,
                   df['red_candle'][last_row_index]]
    strong_sell = pd.Series(strong_sell).all()


    exit_buy = [lower_band_touch,
                df['green_candle'][last_row_index],
                df['stoch_k'][previous_row_index] < df['stoch_d'][previous_row_index],
                df['stoch_k'][last_row_index] > df['stoch_d'][last_row_index],
                RSI_range_lower < df['rsi'][last_row_index] < RSI_range_upper]
    exit_buy = pd.Series(exit_buy).all()

    exit_sell = [upper_band_touch,
                df['red_candle'][last_row_index],
                df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index],
                RSI_range_lower < df['rsi'][last_row_index] < RSI_range_upper]
    exit_sell = pd.Series(exit_sell).all()

    entry_buy = [df['green_candle'][last_row_index],
                df['stoch_k'][previous_row_index] < df['stoch_d'][previous_row_index],
                df['stoch_k'][last_row_index] > df['stoch_d'][last_row_index],
                RSI_range_lower < df['rsi'][last_row_index] < RSI_range_upper,
                lower_band_touch]
                #df['open'][last_row_index] < df['bb_bbm'][last_row_index] < df['close'][last_row_index]]
    entry_buy = pd.Series(entry_buy).all()

    entry_sell = [df['red_candle'][last_row_index],
                df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index],
                RSI_range_lower < df['rsi'][last_row_index] < RSI_range_upper,
                upper_band_touch]
                #df['open'][last_row_index] > df['bb_bbm'][last_row_index] > df['close'][last_row_index]]
    entry_sell = pd.Series(entry_sell).all()


    if not in_position:
        if strong_buy or entry_buy:
            
            
            usd_size = 0.95 * balance_usd
            size = usd_size / df['close'][last_row_index]
            balance_pos += size
            fees += usd_size * fee
            balance_usd -= usd_size
            print(df['timestamp'][last_row_index],"Reversal from lower BB, BUY LONG!")
            in_position = True
            position = 'long'
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

        elif strong_sell or entry_sell:
            
            
            size = 0.95 * balance_pos
            usd_size = size * df['close'][last_row_index]
            balance_usd += usd_size
            
            fees += usd_size * fee
            balance_pos -= size
            print(df['timestamp'][last_row_index], "Reversal from upper BB, SELL SHORT!")
            in_position = True
            position = 'short'
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
            
            
            if df['high'][last_row_index] < profit_target and df['bb_bb%'][last_row_index] >= 1:
                stoploss = max(breakeven, stoploss, df['bb_bbh1d'][last_row_index])
            
            elif df['high'][last_row_index] >= profit_target:
                stoploss = max(stoploss, profit_target, df['bb_bbh1d'][last_row_index])

            else:
                pass
                
            
            

            
                    
            if strong_sell or (df['close'][last_row_index] < stoploss) or exit_sell:
                #sell
                usd_size = size * df['close'][last_row_index]
                balance_usd += usd_size
                fees += usd_size * fee
                balance_pos -= size
                print(df['timestamp'][last_row_index],"CLOSE LONG POSITION!")
                in_position = False
                trailing_loss = False
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
            
            
            if df['low'][last_row_index] > profit_target and df['bb_bb%'][last_row_index] <= 0:
                stoploss = min(breakeven, stoploss, df['bb_bbl1d'][last_row_index])
            
            elif df['low'][last_row_index] < profit_target:
                stoploss = min(stoploss, profit_target, df['bb_bbl1d'][last_row_index])

            else:
                pass


            if strong_buy or (df['close'][last_row_index] > stoploss) or exit_buy:
                #buy
                size = usd_size / df['close'][last_row_index]
                balance_pos += size
                fees += usd_size * fee
                balance_usd -= usd_size
                print(df['timestamp'][last_row_index],"CLOSE SHORT POSITION!")
                in_position = False
                trailing_loss = False
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


def run_bot():
    global orders
    try:
        print(f"Fetching new bars for {datetime.now().isoformat()}")
        bars = exchange.fetch_ohlcv('BTC/USD', timeframe='5m', limit=2000)
        
        dfinit = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        dfinit['timestamp'] = pd.to_datetime(dfinit['timestamp'], unit='ms')
        # print(dfinit)
        dfsize = 35
        x =  range(dfsize, dfinit.index[-1])
        for i in x:
            
            df = dfinit.iloc[i-dfsize:i+1]
            # print(df)
            # supertrend_data = supertrend(df)
            
            df = indicators(df)


            
            
            # check_buy_sell_signals_supertrend(supertrend_data)
            check_buy_sell_signals(df)
            check_buy_sell_signals(df)
            
        print(orders)
        print(len(dfinit.index))
        
    except ccxt.NetworkError as e:
        print(exchange.id, 'fetch_order_book failed due to a network error:', str(e))
        # retry or whatever
        # ...
    except ccxt.ExchangeError as e:
        print(exchange.id, 'fetch_order_book failed due to exchange error:', str(e))
        # retry or whatever
        # ...
    except Exception as e:
        print(exchange.id, 'fetch_order_book failed with:', str(e))
        # retry or whatever
        # ...
    
    
    gains = orders['USD Gains'][orders.index[-1]], orders['BTC Gains'][orders.index[-1]]
    return gains


gains = run_bot()
print(gains)
# schedule.every(5).seconds.do(run_bot)


# while True:
#     schedule.run_pending()
#     time.sleep(1)