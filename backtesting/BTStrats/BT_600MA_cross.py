import backtrader as bt

class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        '''Returns fractional size for cash operation @price'''
        return self.p.leverage * (cash / price)

class BT600MA_Cross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        p=600,   # period for the slow moving average
        target = 0.99,
        rratio = 2,
        stop_multiple = 2,
        atr_p=14)

    def __init__(self):
        self.sma = bt.ind.SMA(period=self.p.p)  #moving average
        self.atr = bt.ind.ATR(period=self.p.atr_p)
        
    def start(self):
        self.val_start = self.broker.get_cash()    

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))

    def next(self):
        
        if self.position.size > 0 and (self.data.close <= self.stoploss or self.data.close >= self.profit_target):  #hit target on long
            self.close()  # close position

        if self.position.size < 0 and (self.data.close >= self.stoploss or self.data.close <= self.profit_target):  #hit target on short
            self.close()  # close position
        
        if not self.position:
            if self.data.close > self.data.close[-1] and self.data.close[-1] > self.sma[-1] and self.data.open[-1] < self.sma[-1]:
                self.order_target_percent(target=self.p.target)  # enter long
                self.stoploss = self.position.price - self.p.stop_multiple*self.atr
                self.profit_target = self.position.price + self.p.rratio*self.p.stop_multiple*self.atr

            if self.data.close < self.data.close[-1] and self.data.close[-1] < self.sma[-1] and self.data.open[-1] > self.sma[-1]:
                self.order_target_percent(target=-self.p.target)  # enter short
                self.stoploss = self.position.price + self.p.stop_multiple*self.atr
                self.profit_target = self.position.price - self.p.rratio*self.p.stop_multiple*self.atr
        
       