import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib as tl
from datetime import timedelta
from talib import MA_Type

from source.strategies.strategy import Strategy
from source.data.preprocessing import Data
from source.strategies.util import *


class DM_RSI_ADX(Strategy):
    def __init__(self):
        self.name = "DM_RSI_ADX"

    def analysis(self, df, quantity=50):
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

        adx_values = tl.ADX(np.array(float_high), np.array(float_low), np.array(float_close), timeperiod=14)
        dmi = tl.DX(np.array(float_high), np.array(float_low), np.array(float_close), timeperiod=14)
        mdmi = tl.MINUS_DI(np.array(float_high), np.array(float_low), np.array(float_close), timeperiod=14)
        rsi = tl.RSI(np.array(float_close), timeperiod=4)

        """ Trade Logic """
        signals = []
        flag = 0
        for i in xrange(40, len(adx_values) - 2):
            if flag == 0:
                if adx_values[i] > 20 and dmi[i] > mdmi[i] and df.loc[i + 1, 'Open'] > (df.loc[i, 'Close'] + 1.8) and \
                                rsi[i] < 50:
                    signal = self.Long('HSI', df, i + 1, quantity, self.name)
                    flag = 1
                    signals.append(signal)
                if adx_values[i] > 20 and dmi[i] < mdmi[i] and df.loc[i + 1, 'Open'] < (df.loc[i, 'Close'] - 1.8) and \
                                rsi[i] < 50:
                    signal = self.Short('HSI', df, i + 1, quantity, self.name)
                    flag = 2
                    signals.append(signal)
            elif flag == 1:
                if df.loc[i, 'Close'] >= signal[4] * 1.01 or df.loc[i, 'Close'] <= signal[4] * 0.90 or (
                    df.loc[i, 'Date'] - signal[1]) > timedelta(days=5):
                    signal = self.SellToCover('HSI', df, i + 1, quantity, self.name)
                    flag = 0
                    signals.append(signal)
            elif flag == 2:
                if df.loc[i, 'Close'] <= signal[4] * 0.99 or df.loc[i, 'Close'] >= signal[4] * 1.10 or (
                    df.loc[i, 'Date'] - signal[1]) > timedelta(days=5):
                    signal = self.BuyToCover('HSI', df, i + 1, quantity, self.name)
                    flag = 0
                    signals.append(signal)

        """ Signal List """
        sig = pd.DataFrame(signals, columns=['Code', 'Time', 'Action', 'Qnt', 'Price', 'Strategy'])

        """ Simple Profit """
        profits = []
        for k in range(0, len(signals) / 2):
            if sig['Action'][k * 2] == "Long":
                profit = sig['Price'][k * 2 + 1] - sig['Price'][k * 2]
            else:
                profit = sig['Price'][k * 2] - sig['Price'][k * 2 + 1]
            profits.append(profit)

        print "=" * 100
        print self.name, "profit: $", np.sum(profits)
        print(profits)
        print "=" * 100

        """ Plot """
        longSignals = sig[sig['Action'] == 'Long']
        sellToCoverSignals = sig[sig['Action'] == 'SellToCover']
        shortSignals = sig[sig['Action'] == 'Short']
        buyToCoverSignals = sig[sig['Action'] == 'BuyToCover']

        plt.plot(df['Date'], df['Close'], longSignals['Time'], longSignals['Price'], 'r^',
                 buyToCoverSignals['Time'], buyToCoverSignals['Price'], 'r^',
                 shortSignals['Time'], shortSignals['Price'], 'gv',
                 sellToCoverSignals['Time'], sellToCoverSignals['Price'], 'gv',
                 markersize=6)
        red_patch = mpatches.Patch(color='red', label='Long')
        green_patch = mpatches.Patch(color='green', label='Short')
        plt.legend(handles=[red_patch, green_patch])
        plt.grid()

        plt.savefig("image/DM_RSI_ADX.png")
        plt.close()
        return sig

        # # test DM_RSI
        # if __name__ == "__main__":
        #     np.set_printoptions(threshold=np.nan)
        #     pd.set_option("display.max_rows", 280)
        #     dt = Data()
        #     df = dt.getCSVData()
        #
        #     DM_RSI_ADX(df)
