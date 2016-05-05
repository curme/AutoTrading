import pandas as pd
import talib as tl
import numpy as np
from talib import MA_Type
from datetime import timedelta
import matplotlib.pyplot as plt
from source.strategies.MACD import *
from source.strategies.ACOscillator import *
from source.strategies.DM_RSI_ADX import *
from source.money.account import *

class StrategiesManager:

    def __init__(self):
        self.signals = pd.DataFrame(columns=["Code", "Time", "Action", "Qnt", "Price", "Strategy"])
        self.strategiesPool = self.initStrategies()

    def initStrategies(self):
        pool = {}

        # new strategies object
        macd = MACD()
        dm_rsi_adx = DM_RSI_ADX()
        acoscillator = ACOscillator()

        pool[macd.name] = macd
        pool[dm_rsi_adx.name] = dm_rsi_adx
        pool[acoscillator.name] = acoscillator

        return pool

    def monitorMarket(self, dataSet):
        for strategy in self.strategiesPool:
            self.signals = pd.concat([self.signals, self.strategiesPool[strategy].analysis(dataSet)], axis=0, ignore_index=True)

        print "*" * 70
        print "\t" * 5, "Signal Table for All Strategies"
        print "*" * 70
        print self.signals

if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan)
    pd.set_option("display.max_rows", 500)
    dt = Data()
    df = dt.getCSVData()
    sm = StrategiesManager()
    sm.monitorMarket(df)