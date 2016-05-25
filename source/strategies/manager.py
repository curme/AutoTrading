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
from source.strategies.pairstrading import *

from source.money.account import *

class StrategiesManager:

    def __init__(self, strategies = []):
        self.signals = pd.DataFrame(columns=["Code", "Time", "Action", "Qnt", "Price", "Strategy"])
        self.strategiesPool = {}
        self.setStrategies(strategies)

    def setStrategies(self, strategies):

        pool = {}
        # new strategies object
        for strategy in strategies:
            if strategy == "ACOscillator"   : s=ACOscillator()  ;   pool[s.name] = s; continue;
            if strategy == "CCI_Correction" : s=CCI_Correction();   pool[s.name] = s; continue;
            if strategy == "DM_RSI_ADX"     : s=DM_RSI_ADX();       pool[s.name] = s; continue;
            if strategy == "MACD"           : s=MACD();             pool[s.name] = s; continue;
            if strategy == "breakouts_swing": s=breakouts_swing();  pool[s.name] = s; continue;
            if strategy == "oscillator3_13" : s=oscillator3_13();   pool[s.name] = s; continue;
            if strategy == "pairstrading"   : s=pairstrading();     pool[s.name] = s; continue;

        for strategySubManager in self.strategiesPool: del strategySubManager
        self.strategiesPool = pool

    def monitorMarket(self, dataSet):
        self.signals = None
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
