import backtrader as bt

class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        '''Returns fractional size for cash operation @price'''
        return self.p.leverage * (cash / price)

class SmaCross_longshort(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=200,  # period for the fast moving average
        pslow=600,   # period for the slow moving average
        target = 0.98)

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def start(self):
        self.val_start = self.broker.get_cash()


    def next(self):
        if self.position:
            if self.crossover < 0 and self.position.size > 0:  # in the market long & cross to the downside
                self.close() # close long position
                self.order_target_percent(target=-self.p.target)  
            elif self.crossover > 0 and self.position.size < 0:  # in the market short & cross to the downside
                self.close()  # close short position
                self.order_target_percent(target=self.p.target)
        
        elif not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.order_target_percent(target=self.p.target)  # enter long
            elif self.crossover < 0:  
                self.order_target_percent(target=-self.p.target)  # enter short

       

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))