class TradingStrat:
    def __init__(self, candles):
        self.candles = candles
        self.buy = False
        self.sell = False

    def buysellsignals(self):

        return [self.buy, self.sell]