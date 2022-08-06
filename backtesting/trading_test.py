from datetime import datetime
import backtrader as bt

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=20), bt.ind.SMA(period=50)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

cerebro = bt.Cerebro()
cerebro.broker.set_cash(10000)

cerebro.addstrategy(SmaCross)

data0 = bt.feeds.YahooFinanceData(dataname='SPY', fromdate=datetime(2015, 1, 1),
                                  todate=datetime(2021, 4, 8))
cerebro.adddata(data0)

cerebro.run()
cerebro.plot()