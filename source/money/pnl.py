"""
Create Profit and Loss (PnL) Report
"""
import pandas as pd
import numpy as np
from source.strategies.util import maxDrawDown


class pnlCalculator:
    def __init__(self, money, tradehistory):
        self.capital = money
        self.tradebook = tradehistory
        self.rate = 1.37 / 100

    def departStrategy(self):
        self.strategy = []
        for i in self.tradebook.index:
            if not self.tradebook.loc[i, 'Strategy'] in self.strategy:
                self.strategy.append(self.tradebook.loc[i, 'Strategy'])
                # print "strategy: ", self.strategy

    def GetrealizedPnL(self):
        self.realizedpnl = []
        for s in self.strategy:
            sum = 0
            for i in self.tradebook.index:
                if self.tradebook.loc[i, 'Strategy'] == s:
                    if self.tradebook.loc[i, 'Action'] == "BuyToCover" or self.tradebook.loc[
                        i, 'Action'] == "SellToCover":
                        sum = sum + float(self.tradebook.loc[i, 'PnL'])
            self.realizedpnl.append(sum)
            # print "pnl: ", self.realizedpnl

    def Getactualreturn(self):
        self.actualreturn = [pnl / (0.15 * self.capital) for pnl in self.realizedpnl]
        # print "return: ", self.actualreturn

    def Getannualizedeturn(self):
        self.annualizedreturn = [(1 + r) ** 4 - 1 for r in self.actualreturn]
        # print "annual return: ", self.annualizedreturn

    def Getvol(self):
        self.volatility = []
        self.meanreturn = []
        for s in self.strategy:
            returnlist = []
            for i in self.tradebook.index:
                if self.tradebook.loc[i, 'Strategy'] == s:
                    if self.tradebook.loc[i, 'Action'] == "BuyToCover" or self.tradebook.loc[
                        i, 'Action'] == "SellToCover":
                        if self.tradebook.loc[i, 'Qnt'] != 0:
                            r = float(self.tradebook.loc[i, 'PnL']) / (0.15 * self.capital)
                            # day_count = float(self.tradebook.loc[i,'Time'].day - self.tradebook.loc[i-1,'Time'].day)
                            # if day_count == 0:
                            #    day_count = 1
                            returnlist.append((1 + r) ** 4 - 1)
            self.volatility.append(np.std(np.array(returnlist)))
            self.meanreturn.append(np.mean(returnlist))

    def GetSharperatio(self):
        # self.Sharpratio = [(self.meanreturn[i]-self.rate)/self.volatility[i] for i in xrange(len(self.strategy))]
        self.Sharpratio = [(self.actualreturn[i] - self.rate) / self.volatility[i] for i in xrange(len(self.strategy))]

    def Getmdd(self):
        self.mdd = []
        for s in self.strategy:
            pnllist = []
            for i in self.tradebook.index:
                if self.tradebook.loc[i, 'Strategy'] == s:
                    if self.tradebook.loc[i, 'Action'] == "BuyToCover" or self.tradebook.loc[
                        i, 'Action'] == "SellToCover":
                        if self.tradebook.loc[i, 'Qnt'] != 0:
                            pnllist.append(float(self.tradebook.loc[i, 'PnL']))

            self.mdd.append(maxDrawDown(pd.DataFrame(pnllist, columns=["Close"])))
            # print "mdd: ", self.mdd

    def run(self):
        self.departStrategy()
        self.GetrealizedPnL()
        self.Getactualreturn()
        self.Getannualizedeturn()
        self.Getvol()
        self.GetSharperatio()
        self.Getmdd()
        performance = []
        for i in xrange(len(self.strategy)):
            performance.append([self.strategy[i], self.realizedpnl[i], self.actualreturn[i], self.annualizedreturn[i],
                                self.volatility[i], self.Sharpratio[i], self.mdd[i]])
        report = pd.DataFrame(performance,
                              columns=["Strategy", "realized PnL", "Return", "Annualized Return", "Volatility",
                                       "Sharpe Ratio", "MDD"])
        print "Report " + "/" * 100
        print report
