import numpy as np
import pandas as pd
from datetime import timedelta
from source.strategies.strategy import Strategy
from source.dataManager.manager import DataManager as Data
from sklearn import datasets, linear_model, preprocessing
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class pairstrading(Strategy):

    def __init__(self):
        self.name = "pairstrading"

    def analysis(self,dfs):
        """
        :param df:
        :param quantity:
        :return:
        """

        d = Data()
        dfs = d.getMultipelDataframe("hsi_stocks")

        signals = []
        pairs = self.getPairsByCorrelation(dfs, 0.95)
        pair = pairs[0]
        p1 = dfs[pair[0]]
        p2 = dfs[pair[1]]
        regr = linear_model.LinearRegression()
        p1_close = p1['Close'].reshape(len(p1['Close']), 1)
        p2_close = p2['Close'].reshape(len(p2['Close']), 1)
        regr.fit(p1_close, p2_close)
        b = round(int(regr.coef_), 2)
        dff = preprocessing.scale(p1_close - b * p2_close)
        avr_dff = pd.rolling_mean(dff, 7)
        flag = 0
        for i in xrange(7, len(dff)):
            if dff[i] > 1.0 and dff[i] < avr_dff[i] and flag == 0:
                signal1 = self.Short(pair[0], p1, i + 1, 1, self.name)
                signals.append(signal1)
                signal2 = self.Long(pair[1], p2, i + 1, b, self.name)
                signals.append(signal2)
                flag = 1
            elif dff[i] < -1.0 and dff[i] > avr_dff[i] and flag == 0:
                signal1 = self.Long(pair[0], p1, i + 1, 1, self.name)
                signals.append(signal1)
                signal2 = self.Short(pair[1], p2, i + 1, b, self.name)
                signals.append(signal2)
                flag = 2
            elif (dff[i] < 0.2 or dff[i] > 3) and flag == 1:
                signal1 = self.BuyToCover(pair[0], p1, i + 1, 1, self.name)
                signal2 = self.SellToCover(pair[1], p2, i + 1, b, self.name)
                signals.append(signal1)
                signals.append(signal2)
                flag = 0
            elif (dff[i] > -0.2 or dff[i] < -3) and flag == 2:
                signal1 = self.SellToCover(pair[0], p1, i + 1, 1, self.name)
                signal2 = self.BuyToCover(pair[1], p2, i + 1, b, self.name)
                signals.append(signal1)
                signals.append(signal2)
                flag = 0

        sig = pd.DataFrame(signals, columns=['Code', 'Time', 'Action', 'Qnt', 'Price', 'Volume', 'Strategy'])

        """ PLOT """
        fig = plt.figure(1)
        fig.set_figheight(6)
        fig.set_figwidth(16)

        gs = gridspec.GridSpec(20, 10)

        rect = fig.patch
        rect.set_facecolor('#1B2631')
        plot1 = plt.subplot(gs[0:20, :])
        # plot3 = plt.subplot(gs[16:20, :])

        longSignals = sig[sig['Action'] == 'Long']
        sellToCoverSignals = sig[sig['Action'] == 'SellToCover']
        shortSignals = sig[sig['Action'] == 'Short']
        buyToCoverSignals = sig[sig['Action'] == 'BuyToCover']


        ## Plot 1

        markerSize = 15
        priceline1   = plot1.plot(p1['Date'], p1['Close'], '#F39C12', lw=2)
        priceline2   = plot1.plot(p2['Date'], p2['Close'], '#F39C12', lw=2)
        longline1    = plot1.plot(longSignals['Time'], longSignals['Price'], '^', markersize=markerSize)
        bcline1      = plot1.plot(buyToCoverSignals['Time'], buyToCoverSignals['Price'], '^', markersize=markerSize)
        shortline1   = plot1.plot(shortSignals['Time'], shortSignals['Price'], 'v', markersize=markerSize)
        scline1      = plot1.plot(sellToCoverSignals['Time'], sellToCoverSignals['Price'], 'v', markersize=markerSize)

        # priceline2   = plot2.plot(p2['Date'], p2['Close'], '#F39C12', lw=2)
        # longline2    = plot2.plot(longSignals['Time'], longSignals['Price'], '^', markersize=markerSize)
        # bcline2      = plot2.plot(buyToCoverSignals['Time'], buyToCoverSignals['Price'], '^', markersize=markerSize)
        # shortline2   = plot2.plot(shortSignals['Time'], shortSignals['Price'], 'v', markersize=markerSize)
        # scline2      = plot2.plot(sellToCoverSignals['Time'], sellToCoverSignals['Price'], 'v', markersize=markerSize)

        # Set every line
        plt.title("Pairs Trading", color='white', fontsize=20)
        plt.xlabel("Time", color='white')
        plt.ylabel("Price", color='white')
        plt.setp(longline1, color='#E74C3C', markeredgecolor='#E74C3C')
        plt.setp(bcline1, color='#E74C3C', markeredgecolor='#E74C3C')
        plt.setp(shortline1, color='#27AE60', markeredgecolor='#27AE60')
        plt.setp(scline1, color='#27AE60', markeredgecolor='#27AE60')

        # plt.setp(longline2, color='#E74C3C', markeredgecolor='#E74C3C')
        # plt.setp(bcline2, color='#E74C3C', markeredgecolor='#E74C3C')
        # plt.setp(shortline2, color='#27AE60', markeredgecolor='#27AE60')
        # plt.setp(scline2, color='#27AE60', markeredgecolor='#27AE60')

        # Legend and grid
        red_patch = mpatches.Patch(color='#E74C3C', label='Long')
        green_patch = mpatches.Patch(color='#27AE60', label='Short')
        plot1.legend(handles=[red_patch, green_patch])
        # plot1.grid(True, color='white')


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


        # ### Plot 2
        # bar1 = plot2.plot(df['Date'], macdhist, color='#F39C12')
        # plot2.plot(df['Date'], macd, linewidth=2)
        # plot2.plot(df['Date'], macdsignal, linewidth=2)
        #
        # plot2.set_axis_bgcolor('#1B2631')
        # plot2.tick_params(axis='x', colors='white')
        # plot2.tick_params(axis='y', colors='white')
        # plot2.spines['bottom'].set_color('white')
        # plot2.spines['left'].set_color('white')
        # plot2.spines['top'].set_color('white')
        # plot2.spines['right'].set_color('white')
        # plot2.xaxis.set_ticklabels([])


        plt.savefig("strategies/image/pairstrading.png", facecolor='#17202A', edgecolor=None)
        plt.close()


        return sig

    def getPairsByCorrelation(self,dfs, cov):
        pairs =[]
        for df1 in dfs:
            for df2 in dfs:
                if df1 != df2:
                    cor = np.corrcoef(Data.toFloatArray(dfs[df1]['Close']), Data.toFloatArray(dfs[df2]['Close']))
                    if cor[0,1] > cov:
                        if (df1,df2) not in pairs:
                            pairs.append((df1,df2))
        return pairs

