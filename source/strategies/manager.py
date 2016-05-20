import pandas as pd
import talib as tl
import numpy as np
from talib import MA_Type
from datetime import timedelta
import matplotlib.pyplot as plt

# import strategies
from source.strategies.MACD import *
from source.strategies.ACOscillator import *
from source.strategies.DM_RSI_ADX import *
from source.strategies.oscillator3_13 import *
from source.strategies.breakouts_swing import *
from source.strategies.CCI_Correction import *

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
        oscillator3 = oscillator3_13()
        breakouts = breakouts_swing()
        CCI_correction = CCI_Correction()

        pool[macd.name] = macd
        pool[dm_rsi_adx.name] = dm_rsi_adx
        pool[acoscillator.name] = acoscillator
        pool[oscillator3.name] = oscillator3
        pool[breakouts.name] = breakouts
        pool[CCI_correction.name] = CCI_correction

        return pool

    def monitorMarket(self, dataSet):
        for strategy in self.strategiesPool:
            self.signals = pd.concat([self.signals, self.strategiesPool[strategy].analysis(dataSet)], axis=0, ignore_index=True)

        print "*" * 80
        print "\t" * 6, "Signal Table for All Strategies"
        print "*" * 80
        print self.signals
        return self.signals

if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan)
    pd.set_option("display.max_rows", 500)
    dt = Data()
    df = dt.getCSVData()
    sm = StrategiesManager()
    sm.monitorMarket(df)
