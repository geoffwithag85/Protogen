import ccxt
import pandas as pd
from datetime import datetime


exchange = ccxt.binanceus()


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