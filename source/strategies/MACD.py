import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib as tl
from datetime import timedelta

from talib import MA_Type

from source.strategies.strategy import Strategy
from source.data.preprocessing import Data


class MACD(Strategy):

    def __init__(self):
        self.name = "MACD"

    def analysis(self, df, quantity=100):
        """
        :param df:
        :param quantity:
        :return:
        """

        """ Data """
        float_close = Data.toFloatArray(df['Close'])
        float_high = Data.toFloatArray(df['High'])
        float_low = Data.toFloatArray(df['Low'])
        float_open = Data.toFloatArray(df['Open'])
        stochastic_K , stochastic_D = tl.STOCH(np.array(float_high),np.array(float_low),np.array(float_close),
                                               fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        macd , macdsignal, macdhist = tl.MACD(np.array(float_close), fastperiod=12, slowperiod=26, signalperiod=9)
        sma = tl.SMA(np.array(float_close), timeperiod=10)

        """ Trade Logic """
        signals = []
        flag = 0
        for i in xrange(2 , len(macd) - 1):
            if flag ==0:
                if df.loc[i, 'Close']> sma[i] and macd[i]-macdsignal[i] > 0 and macd[i-1] - macdsignal[i-1] < 0:
                    if stochastic_D[i-2] > 30 and stochastic_D[i-1] < 30 or stochastic_D[i-1] >30 and stochastic_D[i]<30:
                        signal = self.Long('HSI', df, i, quantity, self.name)
                        flag =1
                        signals.append(signal)
                if df.loc[i, 'Close']< sma[i] and macd[i]-macdsignal[i] < 0 and macd[i-1] - macdsignal[i-1] > 0:
                    if stochastic_D[i-2] < 70 and stochastic_D[i-1] > 70 or stochastic_D[i-1] <70 and stochastic_D[i]>30:
                        signal = self.Short('HSI', df, i, quantity, self.name)
                        flag =2
                        signals.append(signal)
            elif flag ==1:
                if df.loc[i, 'Close']>= signal[3]*1.01 or df.loc[i, 'Close']<= signal[3]*0.98 or (df.loc[i, 'Date']-signal[1])>timedelta(days=5):
                    signal = self.SellToCover('HSI', df, i, quantity, self.name)
                    flag = 0
                    signals.append(signal)
            elif flag ==2:
                if df.loc[i, 'Close']<= signal[3]*0.99 or df.loc[i, 'Close']>= signal[3]*1.02 or (df.loc[i, 'Date']-signal[1])>timedelta(days=5):
                    signal = self.BuyToCover('HSI', df, i, quantity, self.name)
                    flag = 0
                    signals.append(signal)

        """ Signal Table """
        sig = pd.DataFrame(signals, columns=['Code', 'Time', 'Action', 'Qnt', 'Price', 'Strategy'])

        """ Simple Profit Calculation """
        profits = []
        for k in range(0,len(signals)/2):
            if sig['Action'][k*2] == "Long":
                profit = sig['Price'][k*2+1] - sig['Price'][k*2]
            else:
                profit = sig['Price'][k*2]- sig['Price'][k*2+1]
            profits.append(profit)

        print "=" * 100
        print self.name, "profit: $", np.sum(profits)
        print(profits)
        print "=" * 100

        """ PLOT """
        longSignals = sig[sig['Action'] == 'Long']
        sellToCoverSignals = sig[sig['Action'] == 'SellToCover']
        shortSignals = sig[sig['Action'] == 'Short']
        buyToCoverSignals = sig[sig['Action'] == 'BuyToCover']

        plt.plot(df['Date'], df['Close'], longSignals['Time'], longSignals['Price'], 'r^',
                 buyToCoverSignals['Time'], buyToCoverSignals['Price'], 'r^',
                 shortSignals['Time'], shortSignals['Price'], 'gv',
                 sellToCoverSignals['Time'], sellToCoverSignals['Price'], 'gv',
                 markersize=10)
        red_patch = mpatches.Patch(color='red', label='Long')
        green_patch = mpatches.Patch(color='green', label='Short')
        plt.legend(handles=[red_patch, green_patch])

        plt.grid()
        plt.savefig("image/MACD.png")

        return sig

"""test MACD
if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan)
    pd.set_option("display.max_rows", 280)
    dt = Data()
    df = dt.getCSVData()
    MACD_Stochastic(df)
"""