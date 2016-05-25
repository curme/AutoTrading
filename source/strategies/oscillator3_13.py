import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib as tl
from datetime import timedelta

from talib import MA_Type
import matplotlib.gridspec as gridspec

from source.strategies.strategy import Strategy
from source.dataManager.manager import DataManager as Data


class oscillator3_13(Strategy):

    def __init__(self):
        self.name = "oscillator3_13"

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
                    if macd[i]<0 and macd[i-1]<0 and macd[i]>macd[i-1] and sma[i] > 0 and sma[i-1]>0 and sma[i-2]>0 and df.loc[i, 'Close']<df.loc[i+1, 'Open']:
                            signal = self.Long('HSI', df, i+1, quantity, self.name)
                            flag =1
                            signals.append(signal)
                    if macd[i]>0 and macd[i-1]>0 and macd[i]<macd[i-1] and sma[i] < 0 and sma[i-1]<0 and sma[i-2]<0 and df.loc[i, 'Close']>df.loc[i+1, 'Open']:
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
        fig.set_figwidth(26)

        gs = gridspec.GridSpec(20, 10)

        rect = fig.patch
        rect.set_facecolor('#1B2631')
        plot1 = plt.subplot(gs[0:20, :])
        # plot2 = plt.subplot(gs[13:20, :])
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
        plt.title("Oscillator3_13", color='white', fontsize=20)
        plt.xlabel("Time", color='white')
        plt.ylabel("Price", color='white')
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

        plt.savefig("strategies/image/oscillator3_13.png", facecolor='#17202A', edgecolor=None)

        return sig

