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


class ACOscillator(Strategy):
    def __init__(self):
        self.name = "ACOscillator"

    def analysis(self, df, quantity=1):
        """
        :param data:
        :return:
        """

        """ Data """
        float_close = Data.toFloatArray(df['Close'])
        float_high = Data.toFloatArray(df['High'])
        float_low = Data.toFloatArray(df['Low'])
        float_open = Data.toFloatArray(df['Open'])

        adx_values = tl.ADX(np.array(float_high), np.array(float_low), np.array(float_close), timeperiod=14)

        aco_values = self.ACO(df)
        aco_values = np.insert(aco_values, 0, 0, axis=0)


        """ Trade Logic """
        signals = []
        flag = 0

        # plt.plot(df['Date'], aco_values, df['Date'], adx_values, df['Date'],df['Close'] )
        # plt.show()
        # ddf = pd.concat([df['Date'], pd.DataFrame(aco_values), pd.DataFrame(adx_values), df['Close']], axis=1)
        # ddf.to_csv("ddf2.csv")
        for i in xrange(40, len(adx_values) - 2):
            if flag == 0:
                if adx_values[i] > 20 and aco_values[i] > 0 and df.loc[i + 1, 'Open'] > (df.loc[i, 'Close'] + 18):
                    signal = self.Long('HSI', df, i + 1, quantity, self.name, 'Open')
                    flag = 1
                    signals.append(signal)
                if adx_values[i] > 20 and aco_values[i] < 0 and df.loc[i + 1, 'Open'] < (df.loc[i, 'Close'] - 18):
                    signal = self.Short('HSI', df, i + 1, quantity, self.name, 'Open')
                    flag = 2
                    signals.append(signal)
            elif flag == 1:
                if df.loc[i, 'Close'] >= signal[4] * 1.01 or df.loc[i, 'Close'] <= signal[4] * 0.90 or (
                    df.loc[i, 'Date'] - signal[1]) > timedelta(days=5):
                    signal = self.SellToCover('HSI', df, i + 1, quantity, self.name, 'Open')
                    flag = 0
                    signals.append(signal)
            elif flag == 2:
                if df.loc[i, 'Close'] <= signal[4] * 0.99 or df.loc[i, 'Close'] >= signal[4] * 1.10 or (
                    df.loc[i, 'Date'] - signal[1]) > timedelta(days=5):
                    signal = self.BuyToCover('HSI', df, i + 1, quantity, self.name, 'Open')
                    flag = 0
                    signals.append(signal)

        """ Signal List """
        sig = pd.DataFrame(signals, columns=['Code', 'Time', 'Action', 'Qnt', 'Price', 'Strategy'])

        """ Simple Profit """
        profits = []
        # print sig
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
        fig1 = plt.figure(1)
        fig1.set_figheight(8)
        fig1.set_figwidth(15)

        rect = fig1.patch
        rect.set_facecolor('red')
        ax = fig1.add_subplot(1, 1, 1)

        longSignals = sig[sig['Action'] == 'Long']
        sellToCoverSignals = sig[sig['Action'] == 'SellToCover']
        shortSignals = sig[sig['Action'] == 'Short']
        buyToCoverSignals = sig[sig['Action'] == 'BuyToCover']

        ax.plot(df['Date'], df['Close'], longSignals['Time'], longSignals['Price'], 'r^',
                 buyToCoverSignals['Time'], buyToCoverSignals['Price'], 'r^',
                 shortSignals['Time'], shortSignals['Price'], 'gv',
                 sellToCoverSignals['Time'], sellToCoverSignals['Price'], 'gv',
                 markersize=10)
        red_patch = mpatches.Patch(color='red', label='Long')
        green_patch = mpatches.Patch(color='green', label='Short')
        plt.legend(handles=[red_patch, green_patch])
        plt.grid()
        plt.savefig("strategies/image/ACOscillator.png")
        plt.close()
        return sig

    def ACO(self, df):
        """
        Helper indicator
        :param df:
        :return:
        """
        df_mid_points = (df['High'] + df['Low']) / 2
        mid_points = Data.toFloatArray(df_mid_points)
        longav = tl.SMA(np.array(mid_points), timeperiod=40)
        shortav = tl.SMA(np.array(mid_points), timeperiod=15)
        A0 = longav - shortav
        Mavg = tl.SMA(A0, timeperiod=15)
        AcResult = tl.SMA(Mavg - A0, timeperiod=15)
        signals = np.diff(AcResult)
        return signals

        # if __name__ == "__main__":
        #     np.set_printoptions(threshold=np.nan)
        #     pd.set_option("display.max_rows", 280)
        #     dt = Data()
        #     df = dt.getCSVData()
        #     #ACOscillator(df)
        #     ACOscillator(df)
