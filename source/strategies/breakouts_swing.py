"""
Momentum trading: Using pre-market trading and range breaks out

"""
"""
range break out

Assumption is the market moves in the same direction as pre-market trade when market
moves outside the prior day's range

Short stocks making lower daily lows
Long stocks making high daily highs


Enter signal:
Market open higher that previous day's high(H(1))
When P > H(1)*1.01
    Long P
Stop loss
    When P < P'*0.97
profit taking
    when P > P'*1.03

Market open lower than previous day's low(L(1))
When P < L(1)*1.01
    Short L
Stop Loss
    when P > P'*1.03
profit taking
    when P < P'*0.97
"""


import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib as tl
from datetime import timedelta
import matplotlib.gridspec as gridspec

from source.strategies.strategy import Strategy
from source.dataManager.manager import DataManager as Data

class breakouts_swing(Strategy):

    def __init__(self):
        self.name = "breakouts_swing"

    def dailydata(self,df):
        self.daylist = []
        self.dayid = []
        dopen, dhigh, dlow, dclose=[],[],[],[]
        high,low=[],[]
        for i in df.index:
            dt = df.loc[i,'Date'].date()
            if not dt in self.daylist:
                self.daylist.append(dt)
                self.dayid.append(i)
                dopen.append(df.loc[i,'Open'])
                high,low=[],[]
            high.append(df.loc[i,'High'])
            low.append(df.loc[i,'Low'])
            if i+1 in df.index:
                if df.loc[i+1,'Date'].date() != dt:
                    dhigh.append(max(high))
                    dlow.append(min(low))
                    dclose.append(df.loc[i,'Close'])
                else:
                    continue
            else:
                dhigh.append(max(high))
                dlow.append(min(low))
                dclose.append(df.loc[i,'Close'])
        self.dailyopen = map(float,dopen)
        self.dailyhigh = map(float, dhigh)
        self.dailylow = map(float, dlow)
        self.dailyclose = map(float, dclose)


    def analysis(self, df, quantity=1):
        """
        :param df:
        :param quantity:
        :return:
        """

        """ Data """
        self.dailydata(df)
        #print CCI_5min, len(CCI_5min)
        #print CCI_day, len(CCI_day)

        """ Trade Logic """
        signals = []
        longshort_flag = 0
        for i in xrange(3,len(self.daylist)):
            dt = self.daylist[i]
            if longshort_flag == 0:
                today_open = self.dailyopen[i]
                pre_high = max(self.dailyhigh[i-1], self.dailyhigh[i-2], self.dailyhigh[i-3])
                pre_low = min(self.dailylow[i-1], self.dailylow[i-2], self.dailylow[i-3])
                if today_open > pre_high:
                    signal = self.Long('HSI', df, self.dayid[i], quantity, self.name)
                    longshort_flag = 1
                    signals.append(signal)
                if today_open < pre_low:
                    signal = self.Short('HSI', df, self.dayid[i], quantity, self.name)
                    longshort_flag = -1
                    signals.append(signal)
            if longshort_flag == 1:
                for j in df.index:
                    if df.loc[j,'Date'] > signal[1] and df.loc[j,'Date'].date() == dt:
                        if df.loc[j,'Open'] >= signal[4]*1.02 or df.loc[j,'Open'] <= signal[4]*0.98:
                            signal = self.SellToCover('HSI', df, j, quantity, self.name)
                            longshort_flag = 0
                            signals.append(signal)
                            break
            if longshort_flag == -1:
                for j in df.index:
                    if df.loc[j,'Date'] > signal[1] and df.loc[j,'Date'].date() == dt:
                        if df.loc[j,'Open'] <= signal[4]*0.98 or df.loc[j,'Open'] >= signal[4]*1.02:
                            signal = self.BuyToCover('HSI', df, j, quantity, self.name)
                            longshort_flag = 0
                            signals.append(signal)
                            break

        #print signals
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


        """ Plot """
        fig = plt.figure(1)
        fig.set_figheight(10)
        fig.set_figwidth(15)

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
        plt.title("Breakouts Swing", color='white', fontsize=20)
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

        plt.savefig("strategies/image/breakouts_swing.png", facecolor='#17202A', edgecolor=None)
        plt.close()
        return sig


