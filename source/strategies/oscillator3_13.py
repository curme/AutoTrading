import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib as tl
from datetime import timedelta

from talib import MA_Type

from source.strategies.strategy import Strategy
from source.data.preprocessing import Data


class oscillator3_13(Strategy):

    def __init__(self):
        self.name = "oscillator3_13"

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
        macd , macdsignal, macdhist = tl.MACD(np.array(float_close), fastperiod=4, slowperiod=15, signalperiod=9)
        sma = tl.SMA(np.array(macd), timeperiod=20)
        adx_values = tl.ADX(np.array(float_high), np.array(float_low), np.array(float_close), timeperiod=20)
        stochastic_K , stochastic_D = tl.STOCH(np.array(float_high),np.array(float_low),np.array(float_close),
                                               fastk_period=4, slowk_period=15, slowk_matype=0, slowd_period=3, slowd_matype=0)
        ddf = pd.concat([df['Date'], pd.DataFrame(adx_values), pd.DataFrame(macd), pd.DataFrame(sma), df['Close']], axis=1)
        ddf.to_csv("ddf5.csv")
        """ Trade Logic """
        signals = []
        flag = 0
        for i in xrange(3 , len(macd) - 1):
            if flag ==0:
                if adx_values[i]>30:
                    if macd[i]<0 and macd[i-1]<0 and macd[i]>macd[i-1] and sma[i] > 0 and sma[i-1]>0 and sma[i-2]>0:
                            signal = self.Long('HSI', df, i+1, quantity, self.name)
                            flag =1
                            signals.append(signal)
                    if macd[i]>0 and macd[i-1]>0 and macd[i]<macd[i-1] and sma[i] < 0 and sma[i-1]<0 and sma[i-2]<0:
                            signal = self.Short('HSI', df, i+1, quantity, self.name)
                            flag =2
                            signals.append(signal)
                if adx_values[i]<30:
                    if stochastic_K[i] > 75:
                            signal = self.Short('HSI', df, i+1, quantity, self.name)
                            flag =2
                            signals.append(signal)
                    if stochastic_K[i] < 25:
                            signal = self.Long('HSI', df, i+1, quantity, self.name)
                            flag =1
                            signals.append(signal)
            elif flag ==1:
                if df.loc[i, 'Close']>= signal[4]*1.02 or df.loc[i, 'Close']<= signal[4]*0.98 or (df.loc[i, 'Date']-signal[1])>timedelta(days=5):
                    signal = self.SellToCover('HSI', df, i+1, quantity, self.name)
                    flag = 0
                    signals.append(signal)
            elif flag ==2:
                if df.loc[i, 'Close']<= signal[4]*0.98 or df.loc[i, 'Close']>= signal[4]*1.02 or (df.loc[i, 'Date']-signal[1])>timedelta(days=5):
                    signal = self.BuyToCover('HSI', df, i+1, quantity, self.name)
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
        plt.savefig("image/oscillator3_13.png")

        return sig

