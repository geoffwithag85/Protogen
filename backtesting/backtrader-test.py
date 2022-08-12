
import backtrader as bt
import pandas as pd
from BTStrats.BT_SmaCross import SmaCross
from BTStrats.BT_SmaCross_longshort import SmaCross_longshort
from BTStrats.BT_600MA_cross import BT600MA_Cross
from BTStrats.BT_buyandhold import BuyHold, CommInfoFractional
import glob



cerebro = bt.Cerebro()
cerebro.broker.set_cash(100000.0)

# cerebro.addstrategy(SmaCross)
# cerebro.addstrategy(BuyHold)
cerebro.addstrategy(BT600MA_Cross)
# cerebro.addstrategy(SmaCross_longshort)

files = glob.glob("./backtesting/data/BTC_5m/*.csv")
files = files[-1:]

# print(files)
df_list = (pd.read_csv(file, header=None) for file in files)
df   = pd.concat(df_list, ignore_index=True)

# df = pd.read_csv('backtesting\data\BTC_5m\BTCUSDT-5m-2021-10.csv', header=None)

df = df.iloc[:,0:6] 
df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
data0 = bt.feeds.PandasData(dataname=df,
                    datetime='timestamp',
                    open='open',
                    high='high',
                    low='low',
                    close='close',
                    volume='volume',
                    openinterest=None,
                    timeframe=bt.TimeFrame.Minutes,
                    compression=5)
# data0 = bt.feeds.PandasData(dataname=yf.download('SPY', '2000-01-01', '2022-08-01'))



cerebro.adddata(data0)
cerebro.broker.addcommissioninfo(CommInfoFractional())
# cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
cerebro.addanalyzer(bt.analyzers.Returns)
cerebro.addanalyzer(bt.analyzers.DrawDown)

thestrats = cerebro.run()
for each in thestrats[0].analyzers:
    each.print()
cerebro.plot()

