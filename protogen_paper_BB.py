# Paper trading version of Protogen Alorithmic Trading Bot

import ccxt
import config
import schedule
import pandas as pd
pd.set_option('display.max_rows', None)
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator, SMAIndicator

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

def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr

def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr

def check_market(df):
    df['50EMA'] = EMAIndicator(df['close'], window=50).ema_indicator()
    # df['uptrend'] = df['bb_bbl'] > df['600EMA']
    # df['downtrend'] = df['bb_bbh'] < df['600EMA']
    # df['range'] = (df['bb_bbh'] > df['600EMA']) & (df['bb_bbl'] < df['600EMA'])
    # df['delta'] = df['bb_bbm'] - df['bb_bbm'].shift()
    # df['vel_SMA'] = SMAIndicator(df['delta'], window=5).sma_indicator()

    df['price_delta'] = df['close'] - df['close'].shift()
    # df['vel_price'] = EMAIndicator(df['price_delta'], window=20).ema_indicator()
    df['vel_price'] = SMAIndicator(df['price_delta'], window=20).sma_indicator()
    df['vel_price2'] = SMAIndicator(df['price_delta'], window=10).sma_indicator()

    # velthreshold = .00073 * df['close'][df.index[-1]]
    velthreshold = 27.5
    rangethreshold = velthreshold
    df['uptrend'] = (df['vel_price'] > velthreshold) & (df['vel_price2'] > df['vel_price'])
    df['downtrend'] = (df['vel_price'] < -velthreshold) & (df['vel_price2'] < df['vel_price'])
    # df['uptrend'] = (df['vel_price'] > velthreshold) | (df['close'] > df['50EMA'])
    # df['downtrend'] = (df['vel_price'] < -velthreshold) | (df['close'] < df['50EMA'])

    df['range'] = (-rangethreshold <= df['vel_price']) & (df['vel_price'] <= rangethreshold)
    df['squeeze'] = df['bb_bbw'] < 1
    
    
    df['green_candle'] = df['close'] > df['open']
    df['red_candle'] = df['close'] < df['open']
    
    
    
    
    return df


def bollingerbands(df):
    indicator_bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    indicator_bb1d = BollingerBands(close=df["close"], window=20, window_dev=1)

    # Add Bollinger Bands features
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()
    df['bb_bb%'] = indicator_bb.bollinger_pband()
    df['bb_bbw'] = indicator_bb.bollinger_wband()
    df['bb_bbh1d'] = indicator_bb1d.bollinger_hband()
    df['bb_bbl1d'] = indicator_bb1d.bollinger_lband()
    # Add Bollinger Band high indicator
    # df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    # df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()
    return df

in_position = False
position = ''
balance_usd = 1000 #starting balance USD
balance_pos = .03 #starting position balance
fees = 0
fee = 0.00075
stoploss = 0
trailing_loss = False
size = 0
usd_size = 0
profit_target = 0
risk_reward_ratio = 2.5
ride_trend = False
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
    global trailing_loss
    global size
    global usd_size
    global orders
    global profit_target
    global risk_reward_ratio
    global ride_trend
    print("checking for buy and sell signals")
    print(df.iloc[:, :11].tail(5))
    print(df.iloc[:, 11:].tail(5))
    last_row_index = df.index[-1]
    previous_row_index = last_row_index - 1
    
    #candle patterns
    lower_band_touch = [df['low'][previous_row_index-1] < (df['bb_bbh'][previous_row_index-1] - df['bb_bbl'][previous_row_index-1])*.05+df['bb_bbl'][previous_row_index-1],
                        df['low'][previous_row_index] < (df['bb_bbh'][previous_row_index] - df['bb_bbl'][previous_row_index])*.05+df['bb_bbl'][previous_row_index],
                        df['low'][last_row_index] < (df['bb_bbh'][last_row_index] - df['bb_bbl'][last_row_index])*.05+df['bb_bbl'][last_row_index]]
    lower_band_touch = pd.Series(lower_band_touch).any()
    upper_band_touch = [df['high'][previous_row_index-1] > (df['bb_bbh'][previous_row_index-1] - df['bb_bbl'][previous_row_index-1])*.95+df['bb_bbl'][previous_row_index-1],
                        df['high'][previous_row_index] > (df['bb_bbh'][previous_row_index] - df['bb_bbl'][previous_row_index])*.95+df['bb_bbl'][previous_row_index],
                        df['high'][last_row_index] > (df['bb_bbh'][last_row_index] - df['bb_bbl'][last_row_index])*.95+df['bb_bbl'][last_row_index]]
    upper_band_touch = pd.Series(upper_band_touch).any()
    
    in_uptrend = [df['green_candle'][previous_row_index-1] and df['open'][previous_row_index-1] > df['bb_bbh1d'][previous_row_index-1],
                  df['green_candle'][previous_row_index] and df['open'][previous_row_index] > df['bb_bbh1d'][previous_row_index],
                  df['green_candle'][last_row_index] and df['open'][last_row_index] > df['bb_bbh1d'][last_row_index]]
    in_uptrend = pd.Series(in_uptrend).all()

    in_downtrend = [df['red_candle'][previous_row_index-1] and df['open'][previous_row_index-1] < df['bb_bbl1d'][previous_row_index-1],
                  df['red_candle'][previous_row_index] and df['open'][previous_row_index] < df['bb_bbl1d'][previous_row_index],
                  df['red_candle'][last_row_index] and df['open'][last_row_index] < df['bb_bbh1d'][last_row_index]]
    in_downtrend = pd.Series(in_downtrend).all()


    bullish_engulfing = lower_band_touch and df['close'][last_row_index] > df['open'][previous_row_index] and df['green_candle'][last_row_index] and df['red_candle'][previous_row_index]
    bearish_engulfing = upper_band_touch and df['close'][last_row_index] < df['open'][previous_row_index] and df['red_candle'][last_row_index] and df['green_candle'][previous_row_index]
    two_candles_up = lower_band_touch and df['bb_bb%'][last_row_index]>=0 \
                     and df['green_candle'][previous_row_index] and df['green_candle'][last_row_index]

    two_candles_down = upper_band_touch and df['bb_bb%'][last_row_index]<=1 \
                        and df['red_candle'][previous_row_index] and df['red_candle'][last_row_index]

    # two_candles_up = lower_band_touch and df['close'][last_row_index]>=df['open'][previous_row_index-1] \
    #                  and df['green_candle'][previous_row_index] and df['green_candle'][last_row_index]

    # two_candles_down = upper_band_touch and df['close'][last_row_index]<= df['open'][previous_row_index-1] \
    #                     and df['red_candle'][previous_row_index] and df['red_candle'][last_row_index] 
    
    SDband_cross_up = df['low'][last_row_index] < df['bb_bbh1d'][last_row_index] and df['close'][last_row_index] > df['bb_bbh1d'][last_row_index] and df['green_candle'][last_row_index]
    SDband_cross_down = df['high'][last_row_index] > df['bb_bbl1d'][last_row_index] and df['close'][last_row_index] < df['bb_bbl1d'][last_row_index] and df['red_candle'][last_row_index] 

    



    if not in_position:
        if df['uptrend'][last_row_index]:
            
            if two_candles_up or bullish_engulfing or SDband_cross_up or in_uptrend:
                usd_size = 0.95 * balance_usd
                size = usd_size / df['close'][last_row_index]
                balance_pos += size
                fees += usd_size * fee
                balance_usd -= usd_size
                print(df['timestamp'][last_row_index],"Reversal from lower/middle BB in uptrend, BUY LONG!")
                in_position = True
                position = 'long'
                stoploss = df['low'][-5:].min()
                profit_target = risk_reward_ratio*(df['close'][last_row_index] - stoploss) + df['close'][last_row_index]
                
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

        elif df['downtrend'][last_row_index]:
            
            if two_candles_down or bearish_engulfing or SDband_cross_down or in_downtrend:
                size = 0.95 * balance_pos
                usd_size = size * df['close'][last_row_index]
                balance_usd += usd_size
                
                fees += usd_size * fee
                balance_pos -= size
                print(df['timestamp'][last_row_index], "Reversal from upper/middle BB in downtrend, SELL SHORT!")
                in_position = True
                position = 'short'
                stoploss = df['high'][-5:].max()
                profit_target = risk_reward_ratio*(df['close'][last_row_index] - stoploss) + df['close'][last_row_index]
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

        elif df['range'][last_row_index]:
            
            if (two_candles_up or bullish_engulfing) and (df['bb_bb%'][last_row_index]<0.5):
                usd_size = 0.95 * balance_usd
                size = usd_size / df['close'][last_row_index]
                balance_pos += size
                fees += usd_size * fee
                balance_usd -= usd_size
                print(df['timestamp'][last_row_index],"Reversal from lower BB in range, BUY LONG!")
                in_position = True
                position = 'long'
                stoploss = df['low'][-5:].min()
                profit_target = risk_reward_ratio*(df['close'][last_row_index] - stoploss) + df['close'][last_row_index]
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

            elif (two_candles_down or bearish_engulfing) and (df['bb_bb%'][last_row_index]>0.5):
                size = 0.95 * balance_pos
                usd_size = size * df['close'][last_row_index]
                balance_usd += usd_size
                
                fees += usd_size * fee
                balance_pos -= size
                print(df['timestamp'][last_row_index],"Reversal from upper BB in range, SELL SHORT!")
                in_position = True
                position = 'short'
                stoploss = df['high'][-5:].max()
                profit_target = risk_reward_ratio*(df['close'][last_row_index] - stoploss) + df['close'][last_row_index]
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

            elif (df['bb_bb%'][last_row_index] > 0.95) and df['squeeze'][last_row_index]:
                #squeeze code
                usd_size = 0.95 * balance_usd
                size = usd_size / df['close'][last_row_index]
                balance_pos += size
                fees += usd_size * fee
                balance_usd -= usd_size
                print(df['timestamp'][last_row_index],"Break up From Squeeze, BUY LONG!")
                in_position = True
                position = 'long'
                stoploss = df['bb_bbm'][last_row_index]
                profit_target = risk_reward_ratio*(df['close'][last_row_index] - stoploss) + df['close'][last_row_index]
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

            elif (df['bb_bb%'][last_row_index] < 0.05) and df['squeeze'][last_row_index]:
                size = 0.95 * balance_pos
                usd_size = size * df['close'][last_row_index]
                balance_usd += usd_size
                
                fees += usd_size * fee
                balance_pos -= size
                print(df['timestamp'][last_row_index],"Break down from squeeze, SELL SHORT!")
                in_position = True
                position = 'short'
                stoploss = df['bb_bbm'][last_row_index]
                profit_target = risk_reward_ratio*(df['close'][last_row_index] - stoploss) + df['close'][last_row_index]

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
            
            
            if df['close'][last_row_index]>df['bb_bbh1d'][last_row_index] or trailing_loss:
                if df['uptrend'][last_row_index]:
                    stoploss = df['bb_bbh1d'][last_row_index]
                    trailing_loss = True
                
                               
                else:
                    stoploss = df['bb_bbm'][last_row_index]
                    trailing_loss = True
            
            

            trendbreak = df['red_candle'][last_row_index] and df['bb_bbh1d'][last_row_index] < 0.25*(df['close'][last_row_index] - df['open'][last_row_index])+df['open'][last_row_index]
            if (df['uptrend'][last_row_index] or df['uptrend'][previous_row_index]) and df['close'][last_row_index] > profit_target and not trendbreak:
                ride_trend = True
            else:
                ride_trend = False

            if ((df['close'][last_row_index] < stoploss) or (df['close'][last_row_index] > profit_target)):
                #sell
                usd_size = size * df['close'][last_row_index]
                balance_usd += usd_size
                fees += usd_size * fee
                balance_pos -= size
                print(df['timestamp'][last_row_index],"Price dropped below stop or hit target, SELL LONG POSITION!")
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
            
            


            if (df['close'][last_row_index]<df['bb_bbl1d'][last_row_index]) or trailing_loss:
                if df['downtrend'][last_row_index]:
                    stoploss = df['bb_bbl1d'][last_row_index]
                    trailing_loss = True
                else:
                    stoploss = df['bb_bbm'][last_row_index]
                    trailing_loss = True

            # if df['downtrend'][last_row_index]:
            #     profit_target = 0.25 * (df['bb_bbl'][last_row_index] - df['bb_bbh'][last_row_index]) + df['bb_bbl'][last_row_index]
            
            # else:
            #     profit_target = profit_target

            trendbreak = df['green_candle'][last_row_index] and df['bb_bbl1d'][last_row_index] > 0.25*(df['close'][last_row_index] - df['open'][last_row_index])+df['open'][last_row_index]
            if (df['downtrend'][last_row_index] or df['downtrend'][previous_row_index]) and df['close'][last_row_index] < profit_target and not trendbreak:
                ride_trend = True
            else:
                ride_trend = False

            if ((df['close'][last_row_index] > stoploss) or (df['close'][last_row_index] < profit_target)):
                #buy
                size = usd_size / df['close'][last_row_index]
                balance_pos += size
                fees += usd_size * fee
                balance_usd -= usd_size
                print(df['timestamp'][last_row_index],"Price crossed stop loss or hit target. BUY BACK SHORT SALE!!")
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
    print(orders)


def run_bot():
    try:
        print(f"Fetching new bars for {datetime.now().isoformat()}")
        bars = exchange.fetch_ohlcv('BTC/USD', timeframe='5m', limit=50)
        
        df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        
        # supertrend_data = supertrend(df)
        df = bollingerbands(df)
        df = check_market(df)
    

        
        
        # check_buy_sell_signals_supertrend(supertrend_data)
        check_buy_sell_signals(df)

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
    
    


schedule.every(5).seconds.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)