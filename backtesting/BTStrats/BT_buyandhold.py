import backtrader as bt

class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        '''Returns fractional size for cash operation @price'''
        return self.p.leverage * (cash / price)

class BuyHold(bt.Strategy):
    # list of parameters which are configurable for the strategy
    

    def __init__(self):
        self.target = 1
        
    def start(self):
        self.val_start = self.broker.get_cash()

    def next(self):
        if not self.position:
            self.order_target_percent(target=self.target)  # enter long
        
    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))

        