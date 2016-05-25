import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib as tl
from datetime import timedelta
import matplotlib.gridspec as gridspec

from talib import CCI

from source.strategies.strategy import Strategy
from source.dataManager.manager import DataManager as Data

class CCI_Correction(Strategy):

    def __init__(self):
        self.name = "CCI_Correction"

    def dailydata(self,df):
        self.daylist = []
        dhigh, dlow, dclose=[],[],[]
        high,low=[],[]
        for i in df.index:
            dt = df.loc[i,'Date'].date()
            if not dt in self.daylist:
                self.daylist.append(dt)
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
        self.dailyhigh = map(float, dhigh)
        self.dailylow = map(float, dlow)
        self.dailyclose = map(float, dclose)
        #print self.daylist
        #print len(self.daylist), len(self.dailyhigh), len(self.dailylow), len(self.dailyclose)



    def analysis(self, df, quantity=1):
        """
        :param df:
        :param quantity:
        :return:
        """

        self.dailydata(df)

        """ Data """
        float_close = Data.toFloatArray(df['Close'])
        float_high = Data.toFloatArray(df['High'])
        float_low = Data.toFloatArray(df['Low'])

        CCI_5min = CCI(np.array(float_high),np.array(float_low),np.array(float_close), timeperiod=10)
        CCI_day = CCI(np.array(self.dailyhigh),np.array(self.dailylow),np.array(self.dailyclose),timeperiod=10)

        #print CCI_5min, len(CCI_5min)
        #print CCI_day, len(CCI_day)

        """ Trade Logic """
        signals = []
        longshort_flag = 0
        for i in xrange(len(CCI_day)):
            if np.isnan(CCI_day[i]):
                continue
            dt = self.daylist[i]
            if longshort_flag == 0:
                intraCCI = []
                num = []
                if CCI_day[i] > 100:
                    for j in xrange(len(CCI_5min)):
                        if df.loc[j,'Date'].date() == dt:
                            num.append(j)
                            intraCCI.append(CCI_5min[j])
                    for k in xrange(len(intraCCI)):
                        if intraCCI[k] < -100:
                            if k != len(intraCCI)-1:
                                signal = self.Long('HSI', df, num[k], quantity, self.name)
                                longshort_flag = 1
                                signals.append(signal)
                                break
                if CCI_day[i] < -100:
                    dt = self.daylist[i]
                    for j in xrange(len(CCI_5min)):
                        if df.loc[j,'Date'].date() == dt:
                            num.append(j)
                            intraCCI.append(CCI_5min[j])
                    for k in xrange(len(intraCCI)):
                        if intraCCI[k] > 100:
                            if k != len(intraCCI)-1:
                                signal = self.Short('HSI', df, num[k], quantity, self.name)
                                longshort_flag = -1
                                signals.append(signal)
                                break
            if longshort_flag == 1:
                for j in xrange(len(CCI_5min)):
                    if df.loc[j,'Date'] > signal[1] and df.loc[j,'Date'].date() == dt:
                        if df.loc[j,'Open'] >= signal[4]*1.02 or df.loc[j,'Open'] <= signal[4]*0.99:
                            signal = self.SellToCover('HSI', df, j, quantity, self.name)
                            longshort_flag = 0
                            signals.append(signal)
                            break
            if longshort_flag == -1:
                for j in xrange(len(CCI_5min)):
                    if df.loc[j,'Date'] > signal[1] and df.loc[j,'Date'].date() == dt:
                        if df.loc[j,'Open'] <= signal[4]*0.98 or df.loc[j,'Open'] >= signal[4]*1.01:
                            signal = self.BuyToCover('HSI', df, j, quantity, self.name)
                            longshort_flag = 0
                            signals.append(signal)
                            break

        # print signals
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
        fig.set_figheight(6)
        fig.set_figwidth(16)

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
        priceline   = plot1.plot(df['Date'], df['Close'], '#F39C12',lw=2)
        longline    = plot1.plot(longSignals['Time'], longSignals['Price'], '^', markersize=markerSize)
        bcline      = plot1.plot(buyToCoverSignals['Time'], buyToCoverSignals['Price'], '^', markersize=markerSize)
        shortline   = plot1.plot(shortSignals['Time'], shortSignals['Price'], 'v', markersize=markerSize)
        scline      = plot1.plot(sellToCoverSignals['Time'], sellToCoverSignals['Price'], 'v', markersize=markerSize)

        # Set every line
        plt.title("CCI Correction", color='white', fontsize=20)
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



        # Axis
        plot1.set_axis_bgcolor('#1B2631')
        plot1.tick_params(axis='x', colors='white')
        plot1.tick_params(axis='y', colors='white')
        plot1.spines['bottom'].set_color('white')
        plot1.spines['left'].set_color('white')
        plot1.spines['top'].set_color('white')
        plot1.spines['right'].set_color('white')

        plot1.spines['bottom'].set_linewidth(2)
        plot1.spines['left'].set_linewidth(2)
        plot1.spines['top'].set_linewidth(2)
        plot1.spines['right'].set_linewidth(2)

        plt.savefig("strategies/image/CCI_Correction.png", facecolor='#17202A', edgecolor=None)
        plt.close()
        return sig

'''
if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan)
    pd.set_option("display.max_rows", 280)
    dt = Data()
    df = dt.getCSVData()
    CCI_Correction().analysis(df)
'''