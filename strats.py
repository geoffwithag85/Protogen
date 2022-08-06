from dataclasses import dataclass


class TradingStrat:
    def __init__(self, candles, type):

        self.candles = candles
        self.type = type