import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib as tl
from datetime import timedelta
import matplotlib.gridspec as gridspec
import matplotlib.finance as mf

from talib import MA_Type

from source.strategies.strategy import Strategy
from source.data.preprocessing import Data


class MACD(Strategy):

    def __init__(self):
        self.name = "MACD"

    def analysis(self, df, quantity=1):
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
        macd, macdsignal, macdhist = tl.MACD(np.array(float_close), fastperiod=12, slowperiod=26, signalperiod=9)
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
                if df.loc[i, 'Close']>= signal[4]*1.01 or df.loc[i, 'Close']<= signal[4]*0.98 or (df.loc[i, 'Date']-signal[1])>timedelta(days=5):
                    signal = self.SellToCover('HSI', df, i, quantity, self.name)
                    flag = 0
                    signals.append(signal)
            elif flag ==2:
                if df.loc[i, 'Close']<= signal[4]*0.99 or df.loc[i, 'Close']>= signal[4]*1.02 or (df.loc[i, 'Date']-signal[1])>timedelta(days=5):
                    signal = self.BuyToCover('HSI', df, i, quantity, self.name)
                    flag = 0
                    signals.append(signal)

        """ Signal Table """
        sig = pd.DataFrame(signals, columns=['Code', 'Time', 'Action', 'Qnt', 'Price', 'Volume', 'Strategy'])

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
        fig = plt.figure(1)
        fig.set_figheight(10)
        fig.set_figwidth(15)

        gs = gridspec.GridSpec(20, 10)

        rect = fig.patch
        rect.set_facecolor('#1B2631')
        plot1 = plt.subplot(gs[0:12, :])
        plot2 = plt.subplot(gs[13:20, :])
        # plot3 = plt.subplot(gs[16:20, :])

        longSignals = sig[sig['Action'] == 'Long']
        sellToCoverSignals = sig[sig['Action'] == 'SellToCover']
        shortSignals = sig[sig['Action'] == 'Short']
        buyToCoverSignals = sig[sig['Action'] == 'BuyToCover']


        ## Plot 1

        markerSize = 15
        priceline   = plot1.plot(df['Date'], df['Close'], '#F39C12')
        longline    = plot1.plot(longSignals['Time'], longSignals['Price'], '^', markersize=markerSize)
        bcline      = plot1.plot(buyToCoverSignals['Time'], buyToCoverSignals['Price'], '^', markersize=markerSize)
        shortline   = plot1.plot(shortSignals['Time'], shortSignals['Price'], 'v', markersize=markerSize)
        scline      = plot1.plot(sellToCoverSignals['Time'], sellToCoverSignals['Price'], 'v', markersize=markerSize)

        # Set every line
        plt.setp(longline, color='#E74C3C', markeredgecolor='#E74C3C')
        plt.setp(bcline, color='#E74C3C', markeredgecolor='#E74C3C')
        plt.setp(shortline, color='#27AE60', markeredgecolor='#27AE60')
        plt.setp(scline, color='#27AE60', markeredgecolor='#27AE60')

        # Legend and grid
        red_patch = mpatches.Patch(color='#E74C3C', label='Long')
        green_patch = mpatches.Patch(color='#27AE60', label='Short')
        plot1.legend(handles=[red_patch, green_patch])
        plot1.grid(True, color='white')


        # Axis
        plot1.set_axis_bgcolor('#1B2631')
        plot1.tick_params(axis='x', colors='white')
        plot1.tick_params(axis='y', colors='white')
        plot1.spines['bottom'].set_color('white')
        plot1.spines['left'].set_color('white')
        plot1.spines['top'].set_color('white')
        plot1.spines['right'].set_color('white')


        ### Plot 2
        bar1 = plot2.plot(df['Date'], macdhist, color='#F39C12')
        plot2.plot(df['Date'], macd, linewidth=2)
        plot2.plot(df['Date'], macdsignal, linewidth=2)

        plot2.set_axis_bgcolor('#1B2631')
        plot2.tick_params(axis='x', colors='white')
        plot2.tick_params(axis='y', colors='white')
        plot2.spines['bottom'].set_color('white')
        plot2.spines['left'].set_color('white')
        plot2.spines['top'].set_color('white')
        plot2.spines['right'].set_color('white')
        plot2.xaxis.set_ticklabels([])


        plt.savefig("strategies/image/MACD.png", facecolor='#17202A', edgecolor=None)
        plt.close()
        return sig

"""test MACD
if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan)
    pd.set_option("display.max_rows", 280)
    dt = Data()
    df = dt.getCSVData()
    MACD_Stochastic(df)
"""