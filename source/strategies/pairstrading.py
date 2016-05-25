import numpy as np
import pandas as pd
from datetime import timedelta
from source.strategies.strategy import Strategy
from source.dataManager.manager import DataManager as Data
from sklearn import datasets, linear_model, preprocessing

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

