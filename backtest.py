import pandas as pd
from strats.MA600_cross import MA600_cross
import warnings
warnings.filterwarnings('ignore')



def run_bot():

    bars = pd.read_csv('backtesting\data\BTC_5m\BTCUSDT-5m-2022-07.csv')

    dfinit = bars.iloc[:,0:6] 
    dfinit.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    dfinit['timestamp'] = pd.to_datetime(dfinit['timestamp'], unit='ms')

    dfsize = 650
    x =  range(dfsize, dfinit.index[-1])
    for i in x:
        
        df = dfinit.iloc[i-dfsize:i+1]
        # print(df)
        
        
        strat = MA600_cross(df)
        print(i, strat.signals)

    #gains = orders['USD Gains'][orders.index[-1]], orders['BTC Gains'][orders.index[-1]]
    #return gains

gains = run_bot()
print(gains)