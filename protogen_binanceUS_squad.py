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

exchange = ccxt.binanceus({
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET
})

bucher_exchange = ccxt.binanceus({
    "apiKey": config.BUCHER_API_KEY,
    "secret": config.BUCHER_API_SECRET
})

leber_exchange = ccxt.binanceus({
    "apiKey": config.LEBER_API_KEY,
    "secret": config.LEBER_API_SECRET
})

# exchange = ccxt.binanceus()


brown_switch = True
bucher_switch = True
leber_switch = True


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


if brown_switch:
    balances = exchange.fetch_total_balance() 
    in_position = False
    position = ''
    balance_usd = balances['USD'] #starting balance USD
    balance_pos = balances['BTC'] #starting position balance
    fees = 0
    fee = 0.00075
    stoploss = 0
    size = 0
    usd_size = 0
    profit_target = 0
    breakeven = 0
    orders = pd.DataFrame(columns=['Timestamp',
                                'Type',
                                'Position',
                                'Price',
                                'Amount USD', 
                                'Amount BTC',
                                'Balance USD',
                                'Balance BTC',
                                'Total Fees BNB', 
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
                                'Total Fees BNB': '',
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

if bucher_switch:
    bucher_balances = bucher_exchange.fetch_total_balance() 
    bucher_in_position = False
    bucher_position = ''
    bucher_balance_usd = bucher_balances['USD'] #starting balance USD
    bucher_balance_pos = bucher_balances['BTC'] #starting position balance
    bucher_fees = 0
    bucher_fee = 0.00075
    bucher_stoploss = 0
    bucher_size = 0
    bucher_usd_size = 0
    bucher_profit_target = 0
    bucher_breakeven = 0
    bucher_orders = pd.DataFrame(columns=['Timestamp',
                                'Type',
                                'Position',
                                'Price',
                                'Amount USD', 
                                'Amount BTC',
                                'Balance USD',
                                'Balance BTC',
                                'Total Fees BNB', 
                                'USD Gains',
                                'BTC Gains',
                                'Total Gains USD',
                                'Total Gains %'])
    init_time = datetime.utcnow()
                                
    bucher_orders = bucher_orders.append({'Timestamp': init_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'Type': '',
                                'Position': '',
                                'Price': '', 
                                'Amount USD': '', 
                                'Amount BTC': '',
                                'Balance USD': bucher_balance_usd,
                                'Balance BTC': bucher_balance_pos,
                                'Total Fees BNB': '',
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

if leber_switch:
    leber_balances = leber_exchange.fetch_total_balance() 
    leber_in_position = False
    leber_position = ''
    leber_balance_usd = leber_balances['USD'] #starting balance USD
    leber_balance_pos = leber_balances['BTC'] #starting position balance
    leber_fees = 0
    leber_fee = 0.00075
    leber_stoploss = 0
    leber_size = 0
    leber_usd_size = 0
    leber_profit_target = 0
    leber_breakeven = 0
    leber_orders = pd.DataFrame(columns=['Timestamp',
                                'Type',
                                'Position',
                                'Price',
                                'Amount USD', 
                                'Amount BTC',
                                'Balance USD',
                                'Balance BTC',
                                'Total Fees BNB', 
                                'USD Gains',
                                'BTC Gains',
                                'Total Gains USD',
                                'Total Gains %'])
    init_time = datetime.utcnow()
                                
    leber_orders = leber_orders.append({'Timestamp': init_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'Type': '',
                                'Position': '',
                                'Price': '', 
                                'Amount USD': '', 
                                'Amount BTC': '',
                                'Balance USD': leber_balance_usd,
                                'Balance BTC': leber_balance_pos,
                                'Total Fees BNB': '',
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

def check_buy_sell_signals(df):
    if brown_switch:
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

    if bucher_switch:
        global bucher_in_position
        global bucher_balance_usd
        global bucher_balance_pos
        global bucher_fees
        global bucher_position
        global bucher_stoploss
        global bucher_size
        global bucher_usd_size
        global bucher_orders
        global bucher_profit_target
        global bucher_breakeven 
    
    if leber_switch:
        global leber_in_position
        global leber_balance_usd
        global leber_balance_pos
        global leber_fees
        global leber_position
        global leber_stoploss
        global leber_size
        global leber_usd_size
        global leber_orders
        global leber_profit_target
        global leber_breakeven
    # print("checking for buy and sell signals")
    print(df.iloc[:, :11].tail(5))
    print(df.iloc[:, 11:].tail(5))

    
    


    last_row_index = df.index[-1]
    previous_row_index = last_row_index - 1
    
    risk_reward_ratio = 5
    RSI_range_lower = 40
    RSI_range_upper = 60
    atr_multiple = 5
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
                    df['green_candle'][last_row_index],
                    df['stoch_k'][previous_row_index] <= .20]
    strong_buy = pd.Series(strong_buy).all()


    strong_sell = [df['rsioverbought'][previous_row_index],
                    not df['rsioverbought'][last_row_index],
                    df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                    df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index],
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
                RSI_range_lower < df['rsi'][last_row_index] < RSI_range_upper,
                #lower_band_touch]
                df['open'][last_row_index] < df['bb_bbm'][last_row_index] < df['close'][last_row_index]]
                #df['stoch_k'][previous_row_index] <= .20]
    middle_buy = pd.Series(middle_buy).all()

    middle_sell = [df['red_candle'][last_row_index],
                df['stoch_k'][previous_row_index] > df['stoch_d'][previous_row_index],
                df['stoch_k'][last_row_index] < df['stoch_d'][last_row_index],
                RSI_range_lower < df['rsi'][last_row_index] < RSI_range_upper,
                #upper_band_touch]
                df['open'][last_row_index] > df['bb_bbm'][last_row_index] > df['close'][last_row_index]]
                #df['stoch_k'][previous_row_index] >= .80]
    middle_sell = pd.Series(middle_sell).all()

    if brown_switch:
        if not in_position:
            if strong_buy or middle_buy or range_buy:
                
                balances = exchange.fetch_total_balance()
                
                usd_size = 0.95 * balances['USD']
                size = usd_size / df['close'][last_row_index]
                order = exchange.create_market_buy_order('BTC/USD', size)
                #bucher_order = bucher_exchange.create_market_buy_order('BTC/USD', size)
                #leber_order = leber_exchange.create_market_buy_order('BTC/USD', size)

                size = order['amount']
                usd_size = order['cost']
                balance_pos = balances['BTC'] + order['amount']
                fees += order['fee']['cost']
                balance_usd = balances['USD'] - order['cost']
                
                print(df['timestamp'][last_row_index],"Open Long Position")
                in_position = True
                position = 'long'
                stoploss = df['close'][last_row_index] - atr_multiple*df['atr'][last_row_index]
                profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - stoploss)
                breakeven = order['price']
                orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': order['price'], 
                                'Type': position, 
                                'Position': 'Open',
                                'Amount USD': order['cost'], 
                                'Amount BTC': order['amount'],
                                'Balance USD': '',
                                'Balance BTC': '',
                                'Total Fees BNB': fees,
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

            elif strong_sell or middle_sell or range_sell:
                
                balances = exchange.fetch_total_balance()
                #bucher_balances = bucher_exchange.fetch_total_balance()
                #leber_balances = leber_exchange.fetch_total_balance()
                
                
                size = 0.95 * balances['BTC']
                order = exchange.create_market_sell_order('BTC/USD', size)
                #bucher_order = bucher_exchange.create_market_buy_order('BTC/USD', size)
                #leber_order = leber_exchange.create_market_buy_order('BTC/USD', size)
                
                usd_size = order['cost']
                size = order['amount']
                balance_usd = balances['USD'] + order['cost']
                
                fees += order['fee']['cost']
                balance_pos = balances['BTC'] - order['amount']
                print(df['timestamp'][last_row_index], "Open Short Position")
                in_position = True
                position = 'short'
                stoploss = df['close'][last_row_index] + atr_multiple*df['atr'][last_row_index]
                profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - stoploss)
                breakeven = order['price']
                orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': order['price'], 
                                'Type': position,
                                'Position': 'Open', 
                                'Amount USD': order['cost'], 
                                'Amount BTC': order['amount'],
                                'Balance USD': '',
                                'Balance BTC': '',
                                'Total Fees BNB': fees,
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
                    
                
                

                
                        
                if (df['close'][last_row_index] < stoploss):# or strong_sell:
                    #sell

                    
                    order = exchange.create_market_sell_order('BTC/USD', size)
                    #bucher_order = bucher_exchange.create_market_sell_order('BTC/USD', size)
                    #leber_order = leber_exchange.create_market_sell_order('BTC/USD', size)

                    balances = exchange.fetch_total_balance()
                    usd_size = order['cost']
                    balance_usd = balances['USD']
                    fees += order['fee']['cost']
                    balance_pos = balances['BTC']
                    print(df['timestamp'][last_row_index],"CLOSE LONG POSITION!")
                    in_position = False
                    
                    orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': order['price'], 
                                'Type': position,
                                'Position': 'Closed', 
                                'Amount USD': order['cost'], 
                                'Amount BTC': order['amount'],
                                'Balance USD': balance_usd,
                                'Balance BTC': balance_pos,
                                'Total Fees BNB': fees,
                                'USD Gains': (balance_usd - orders['Balance USD'][0])/orders['Balance USD'][0] * 100,
                                'BTC Gains': (balance_pos - orders['Balance BTC'][0])/orders['Balance BTC'][0] * 100,
                                'Total Gains USD': (balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index],
                                'Total Gains %': ((balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index])/(orders['Balance USD'][0] + orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                    ignore_index=True)

            elif position=='short':
                
                
                if df['low'][last_row_index] > profit_target and df['bb_bb%'][last_row_index] <= 0:
                    stoploss = min(breakeven, stoploss, df['bb_bbl1d'][last_row_index])
                
                elif df['low'][last_row_index] < profit_target:
                    stoploss = min(stoploss, profit_target, df['bb_bbl1d'][last_row_index])

                else:
                    pass


                if (df['close'][last_row_index] > stoploss):# or strong_buy:
                    #buy

                    
                    size = usd_size / df['close'][last_row_index]
                    order = exchange.create_market_buy_order('BTC/USD', size)
                    #bucher_order = bucher_exchange.create_market_sell_order('BTC/USD', size)
                    #leber_order = leber_exchange.create_market_sell_order('BTC/USD', size)

                    balances = exchange.fetch_total_balance()
                    size = order['amount']
                    balance_pos = balances['BTC']
                    fees += order['fee']['cost']
                    balance_usd = balances['USD']
                    print(df['timestamp'][last_row_index],"CLOSE SHORT POSITION!")
                    in_position = False
                    
                    orders = orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': df['close'][last_row_index], 
                                'Type': position, 
                                'Position': 'Closed',
                                'Amount USD': order['cost'], 
                                'Amount BTC': order['amount'],
                                'Balance USD': balance_usd,
                                'Balance BTC': balance_pos,
                                'Total Fees BNB': fees,
                                'USD Gains': (balance_usd - orders['Balance USD'][0])/orders['Balance USD'][0] * 100,
                                'BTC Gains': (balance_pos - orders['Balance BTC'][0])/orders['Balance BTC'][0] * 100,
                                'Total Gains USD': (balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index],
                                'Total Gains %': ((balance_usd - orders['Balance USD'][0]) + (balance_pos-orders['Balance BTC'][0])*df['close'][last_row_index])/(orders['Balance USD'][0] + orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                ignore_index=True)
        
        # print('BTC:', balance_pos)
        # print('USD:', balance_usd)
        # print('Total Fees (USD):', fees)
        print('Brown:\n', orders)

    if bucher_switch:
        if not bucher_in_position:
            if strong_buy or middle_buy or range_buy:
                
                bucher_balances = bucher_exchange.fetch_total_balance()
                
                bucher_usd_size = 0.95 * bucher_balances['USD']
                bucher_size = bucher_usd_size / df['close'][last_row_index]
                
                bucher_order = bucher_exchange.create_market_buy_order('BTC/USD', bucher_size)
                

                bucher_size = bucher_order['amount']
                bucher_usd_size = bucher_order['cost']
                bucher_balance_pos = bucher_balances['BTC'] + bucher_order['amount']
                bucher_fees += bucher_order['fee']['cost']
                bucher_balance_usd = bucher_balances['USD'] - bucher_order['cost']
                
                print(df['timestamp'][last_row_index],"Open Long Position")
                bucher_in_position = True
                bucher_position = 'long'
                bucher_stoploss = df['close'][last_row_index] - atr_multiple*df['atr'][last_row_index]
                bucher_profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - bucher_stoploss)
                bucher_breakeven = bucher_order['price']
                bucher_orders = bucher_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': bucher_order['price'], 
                                'Type': bucher_position, 
                                'Position': 'Open',
                                'Amount USD': bucher_order['cost'], 
                                'Amount BTC': bucher_order['amount'],
                                'Balance USD': '',
                                'Balance BTC': '',
                                'Total Fees BNB': bucher_fees,
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

            elif strong_sell or middle_sell or range_sell:
                
                
                bucher_balances = bucher_exchange.fetch_total_balance()
                
                
                
                bucher_size = 0.95 * bucher_balances['BTC']
                bucher_order = bucher_exchange.create_market_sell_order('BTC/USD', bucher_size)
                
                
                bucher_usd_size = bucher_order['cost']
                bucher_size = bucher_order['amount']
                bucher_balance_usd = bucher_balances['USD'] + bucher_order['cost']
                
                bucher_fees += bucher_order['fee']['cost']
                bucher_balance_pos = bucher_balances['BTC'] - bucher_order['amount']
                print(df['timestamp'][last_row_index], "Open Short Position")
                bucher_in_position = True
                bucher_position = 'short'
                bucher_stoploss = df['close'][last_row_index] + atr_multiple*df['atr'][last_row_index]
                bucher_profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - bucher_stoploss)
                bucher_breakeven = order['price']
                bucher_orders = bucher_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': bucher_order['price'], 
                                'Type': bucher_position,
                                'Position': 'Open', 
                                'Amount USD': bucher_order['cost'], 
                                'Amount BTC': bucher_order['amount'],
                                'Balance USD': '',
                                'Balance BTC': '',
                                'Total Fees BNB': bucher_fees,
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

            


        elif bucher_in_position:
            if bucher_position=='long':
                
                
                if df['high'][last_row_index] < bucher_profit_target and df['bb_bb%'][last_row_index] >= 1:
                    bucher_stoploss = max(bucher_breakeven, bucher_stoploss, df['bb_bbh1d'][last_row_index])
                
                elif df['high'][last_row_index] >= bucher_profit_target:
                    bucher_stoploss = max(bucher_stoploss, bucher_profit_target, df['bb_bbh1d'][last_row_index])

                else:
                    pass
                    
                
                

                
                        
                if (df['close'][last_row_index] < bucher_stoploss):# or strong_sell:
                    #sell

                    
                    
                    bucher_order = bucher_exchange.create_market_sell_order('BTC/USD', bucher_size)
                    

                    bucher_balances = bucher_exchange.fetch_total_balance()
                    bucher_usd_size = bucher_order['cost']
                    bucher_balance_usd = bucher_balances['USD']
                    bucher_fees += bucher_order['fee']['cost']
                    bucher_balance_pos = bucher_balances['BTC']
                    print(df['timestamp'][last_row_index],"CLOSE LONG POSITION!")
                    bucher_in_position = False
                    
                    bucher_orders = bucher_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': bucher_order['price'], 
                                'Type': bucher_position,
                                'Position': 'Closed', 
                                'Amount USD': bucher_order['cost'], 
                                'Amount BTC': bucher_order['amount'],
                                'Balance USD': bucher_balance_usd,
                                'Balance BTC': bucher_balance_pos,
                                'Total Fees BNB': bucher_fees,
                                'USD Gains': (bucher_balance_usd - bucher_orders['Balance USD'][0])/bucher_orders['Balance USD'][0] * 100,
                                'BTC Gains': (bucher_balance_pos - bucher_orders['Balance BTC'][0])/bucher_orders['Balance BTC'][0] * 100,
                                'Total Gains USD': (bucher_balance_usd - bucher_orders['Balance USD'][0]) + (bucher_balance_pos-bucher_orders['Balance BTC'][0])*df['close'][last_row_index],
                                'Total Gains %': ((bucher_balance_usd - bucher_orders['Balance USD'][0]) + (bucher_balance_pos-bucher_orders['Balance BTC'][0])*df['close'][last_row_index])/(bucher_orders['Balance USD'][0] + bucher_orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                ignore_index=True)

            elif bucher_position=='short':
                
                
                if df['low'][last_row_index] > bucher_profit_target and df['bb_bb%'][last_row_index] <= 0:
                    bucher_stoploss = min(bucher_breakeven, bucher_stoploss, df['bb_bbl1d'][last_row_index])
                
                elif df['low'][last_row_index] < bucher_profit_target:
                    bucher_stoploss = min(bucher_stoploss, bucher_profit_target, df['bb_bbl1d'][last_row_index])

                else:
                    pass


                if (df['close'][last_row_index] > bucher_stoploss):# or strong_buy:
                    #buy

                    
                    bucher_size = bucher_usd_size / df['close'][last_row_index]
                    
                    bucher_order = bucher_exchange.create_market_buy_order('BTC/USD', bucher_size)
                    

                    bucher_balances = bucher_exchange.fetch_total_balance()
                    bucher_size = bucher_order['amount']
                    bucher_balance_pos = bucher_balances['BTC']
                    bucher_fees += bucher_order['fee']['cost']
                    bucher_balance_usd = bucher_balances['USD']
                    print(df['timestamp'][last_row_index],"CLOSE SHORT POSITION!")
                    bucher_in_position = False
                    
                    bucher_orders = bucher_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': df['close'][last_row_index], 
                                'Type': bucher_position, 
                                'Position': 'Closed',
                                'Amount USD': bucher_order['cost'], 
                                'Amount BTC': bucher_order['amount'],
                                'Balance USD': bucher_balance_usd,
                                'Balance BTC': bucher_balance_pos,
                                'Total Fees BNB': bucher_fees,
                                'USD Gains': (bucher_balance_usd - bucher_orders['Balance USD'][0])/bucher_orders['Balance USD'][0] * 100,
                                'BTC Gains': (bucher_balance_pos - bucher_orders['Balance BTC'][0])/bucher_orders['Balance BTC'][0] * 100,
                                'Total Gains USD': (bucher_balance_usd - bucher_orders['Balance USD'][0]) + (bucher_balance_pos-bucher_orders['Balance BTC'][0])*df['close'][last_row_index],
                                'Total Gains %': ((bucher_balance_usd - bucher_orders['Balance USD'][0]) + (bucher_balance_pos-bucher_orders['Balance BTC'][0])*df['close'][last_row_index])/(bucher_orders['Balance USD'][0] + bucher_orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                ignore_index=True)
        
        # print('BTC:', balance_pos)
        # print('USD:', balance_usd)
        # print('Total Fees (USD):', fees)
        print('Bucher:\n',bucher_orders)

    if leber_switch:
        if not leber_in_position:
            if strong_buy or middle_buy or range_buy:
                
                leber_balances = leber_exchange.fetch_total_balance()
                
                leber_usd_size = 0.95 * leber_balances['USD']
                leber_size = leber_usd_size / df['close'][last_row_index]
                
                leber_order = leber_exchange.create_market_buy_order('BTC/USD', leber_size)
                

                leber_size = leber_order['amount']
                leber_usd_size = leber_order['cost']
                leber_balance_pos = leber_balances['BTC'] + leber_order['amount']
                leber_fees += leber_order['fee']['cost']
                leber_balance_usd = leber_balances['USD'] - leber_order['cost']
                
                print(df['timestamp'][last_row_index],"Open Long Position")
                leber_in_position = True
                leber_position = 'long'
                leber_stoploss = df['close'][last_row_index] - atr_multiple*df['atr'][last_row_index]
                leber_profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - leber_stoploss)
                leber_breakeven = leber_order['price']
                leber_orders = leber_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': leber_order['price'], 
                                'Type': leber_position, 
                                'Position': 'Open',
                                'Amount USD': leber_order['cost'], 
                                'Amount BTC': leber_order['amount'],
                                'Balance USD': '',
                                'Balance BTC': '',
                                'Total Fees BNB': leber_fees,
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

            elif strong_sell or middle_sell or range_sell:
                
                
                leber_balances = leber_exchange.fetch_total_balance()
               
                
                
                leber_size = 0.95 * leber_balances['BTC']
                leber_order = leber_exchange.create_market_sell_order('BTC/USD', leber_size)
                
                
                leber_usd_size = leber_order['cost']
                leber_size = leber_order['amount']
                leber_balance_usd = leber_balances['USD'] + leber_order['cost']
                
                leber_fees += leber_order['fee']['cost']
                leber_balance_pos = leber_balances['BTC'] - leber_order['amount']
                print(df['timestamp'][last_row_index], "Open Short Position")
                leber_in_position = True
                leber_position = 'short'
                leber_stoploss = df['close'][last_row_index] + atr_multiple*df['atr'][last_row_index]
                leber_profit_target = df['close'][last_row_index] + risk_reward_ratio*(df['close'][last_row_index] - leber_stoploss)
                leber_breakeven = order['price']
                leber_orders = leber_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': leber_order['price'], 
                                'Type': leber_position,
                                'Position': 'Open', 
                                'Amount USD': leber_order['cost'], 
                                'Amount BTC': leber_order['amount'],
                                'Balance USD': '',
                                'Balance BTC': '',
                                'Total Fees BNB': leber_fees,
                                'USD Gains': '',
                                'BTC Gains': '',
                                'Total Gains USD': '',
                                'Total Gains %': ''}, ignore_index=True)

            


        elif leber_in_position:
            if leber_position=='long':
                
                
                if df['high'][last_row_index] < leber_profit_target and df['bb_bb%'][last_row_index] >= 1:
                    leber_stoploss = max(leber_breakeven, leber_stoploss, df['bb_bbh1d'][last_row_index])
                
                elif df['high'][last_row_index] >= leber_profit_target:
                    leber_stoploss = max(leber_stoploss, leber_profit_target, df['bb_bbh1d'][last_row_index])

                else:
                    pass
                    
                
                

                
                        
                if (df['close'][last_row_index] < leber_stoploss):# or strong_sell:
                    #sell

                    
                    
                    leber_order = leber_exchange.create_market_sell_order('BTC/USD', leber_size)
                    

                    leber_balances = leber_exchange.fetch_total_balance()
                    leber_usd_size = leber_order['cost']
                    leber_balance_usd = leber_balances['USD']
                    leber_fees += leber_order['fee']['cost']
                    leber_balance_pos = leber_balances['BTC']
                    print(df['timestamp'][last_row_index],"CLOSE LONG POSITION!")
                    leber_in_position = False
                    
                    leber_orders = leber_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': leber_order['price'], 
                                'Type': leber_position,
                                'Position': 'Closed', 
                                'Amount USD': leber_order['cost'], 
                                'Amount BTC': leber_order['amount'],
                                'Balance USD': leber_balance_usd,
                                'Balance BTC': leber_balance_pos,
                                'Total Fees BNB': leber_fees,
                                'USD Gains': (leber_balance_usd - leber_orders['Balance USD'][0])/leber_orders['Balance USD'][0] * 100,
                                'BTC Gains': (leber_balance_pos - leber_orders['Balance BTC'][0])/leber_orders['Balance BTC'][0] * 100,
                                'Total Gains USD': (leber_balance_usd - leber_orders['Balance USD'][0]) + (leber_balance_pos-leber_orders['Balance BTC'][0])*df['close'][last_row_index],
                                'Total Gains %': ((leber_balance_usd - leber_orders['Balance USD'][0]) + (leber_balance_pos-leber_orders['Balance BTC'][0])*df['close'][last_row_index])/(leber_orders['Balance USD'][0] + leber_orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                ignore_index=True)

            elif leber_position=='short':
                
                
                if df['low'][last_row_index] > leber_profit_target and df['bb_bb%'][last_row_index] <= 0:
                    leber_stoploss = min(leber_breakeven, leber_stoploss, df['bb_bbl1d'][last_row_index])
                
                elif df['low'][last_row_index] < leber_profit_target:
                    leber_stoploss = min(leber_stoploss, leber_profit_target, df['bb_bbl1d'][last_row_index])

                else:
                    pass


                if (df['close'][last_row_index] > leber_stoploss):# or strong_buy:
                    #buy

                    
                    leber_size = leber_usd_size / df['close'][last_row_index]
                    
                    leber_order = leber_exchange.create_market_buy_order('BTC/USD', leber_size)
                    

                    leber_balances = leber_exchange.fetch_total_balance()
                    leber_size = leber_order['amount']
                    leber_balance_pos = leber_balances['BTC']
                    leber_fees += leber_order['fee']['cost']
                    leber_balance_usd = leber_balances['USD']
                    print(df['timestamp'][last_row_index],"CLOSE SHORT POSITION!")
                    leber_in_position = False
                    
                    leber_orders = leber_orders.append({'Timestamp': df['timestamp'][last_row_index], 
                                'Price': df['close'][last_row_index], 
                                'Type': leber_position, 
                                'Position': 'Closed',
                                'Amount USD': leber_order['cost'], 
                                'Amount BTC': leber_order['amount'],
                                'Balance USD': leber_balance_usd,
                                'Balance BTC': leber_balance_pos,
                                'Total Fees BNB': leber_fees,
                                'USD Gains': (leber_balance_usd - leber_orders['Balance USD'][0])/leber_orders['Balance USD'][0] * 100,
                                'BTC Gains': (leber_balance_pos - leber_orders['Balance BTC'][0])/leber_orders['Balance BTC'][0] * 100,
                                'Total Gains USD': (leber_balance_usd - leber_orders['Balance USD'][0]) + (leber_balance_pos-leber_orders['Balance BTC'][0])*df['close'][last_row_index],
                                'Total Gains %': ((leber_balance_usd - leber_orders['Balance USD'][0]) + (leber_balance_pos-leber_orders['Balance BTC'][0])*df['close'][last_row_index])/(leber_orders['Balance USD'][0] + leber_orders['Balance BTC'][0]*df['close'][last_row_index])*100},
                                ignore_index=True)
        
        # print('BTC:', balance_pos)
        # print('USD:', balance_usd)
        # print('Total Fees (USD):', fees)
        print('Leber:\n',leber_orders)

def run_bot():
    try:
        print(f"Fetching new bars for {datetime.now().isoformat()}")
        bars = exchange.fetch_ohlcv('BTC/USD', timeframe='5m', limit=50)
        
        df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        
        # supertrend_data = supertrend(df)
        df = indicators(df)
    

        
        
        # check_buy_sell_signals_supertrend(supertrend_data)
        check_buy_sell_signals(df)
       

    except ccxt.NetworkError as e:
        print(exchange.id, 'fetch_order_book failed due to a network error:', str(e))
        # print('Retrying...')
        # retry or whatever
        # check_buy_sell_signals(df)
    except ccxt.ExchangeError as e:
        print(exchange.id, 'fetch_order_book failed due to exchange error:', str(e))
        # print('Retrying...')
        # retry or whatever
        # check_buy_sell_signals(df)
    except Exception as e:
        print(exchange.id, 'fetch_order_book failed with:', str(e))
        # print('Retrying...')
        # retry or whatever
        # check_buy_sell_signals(df)
    
 


schedule.every(5).seconds.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)