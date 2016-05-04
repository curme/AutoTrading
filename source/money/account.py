"""
Account
"""

import pandas as pd

# account manager
class Account:

    def __init__(self, strategies, capital=100000000.0, margin=0.3):
        self.capital   = capital
        self.position  = PositionManager(strategies, self.capital)
        self.tradeBook = TradeBook()
        self.margin    = margin

    # return trade history
    def getTradeHistory(self):
        return self.tradeBook.getTallies()

    # print trade history of the account
    def printTradeHistory(self):
        return self.tradeBook.printHistory()

    # record the trade
    def recordTrade(self, code, time, action, qnt, price, pnl, strategy):
        self.position.updatePosition(strategy, code, qnt, price, action)
        self.tradeBook.recordTally([code, time, action, qnt, price, pnl])

    # print positions for selected strategies
    def printPosition(self, strategies = []):
        self.position.printPosition(strategies)

# the recorder to record trade history
class TradeBook :

    def __init__(self):
        self.tallies = pd.DataFrame(columns=["Code", "Time", "Action", "Qnt", "Price", "PnL"])

    # insert a tally
    def recordTally(self, tally):
        self.tallies.loc[self.tallies["Code"].count()] = tally

    # return the whole trade book
    def getTallies(self):
        return self.tallies

    # print trade history
    def printHistory(self):
        print "History " + "/" * 40
        print self.tallies

# the manager to manage account positions
class PositionManager :

    def __init__(self, strategies, capital):
        self.strategies = strategies
        self.capital    = capital
        self.subManagers= {}
        for strategy in self.strategies:
            self.subManagers[strategy] = self.SubManager(strategy, self.capital/float(len(self.strategies)))

    # update position
    def updatePosition(self, strategy, code, qnt, price, action):
        self.subManagers[strategy].updatePosition(code, action, price, qnt)

    # print the positions of selected strategies
    def printPosition(self, strategies):
        # when the no strategies entry in, that means print positions for all strategies
        if len(strategies) == 0: strategies = self.strategies
        for strategy in strategies:
            self.subManagers[strategy].printPosition()

    # the manager to manage the positions for each strategy
    class SubManager:

        def __init__(self, strategy, capital):
            self.strategy = strategy
            self.capital  = capital
            self.positions= pd.DataFrame(columns=["Code", "Position", "Price", "Qnt", "PxQ"])

        # update position of self strategy
        def updatePosition(self, code, action, price, qnt):

            # init the positions for current Code
            if code not in self.positions["Code"].tolist():
                self.positions.loc[self.positions["Code"].count()] = [code, "Long",  0, 0, 0]
                self.positions.loc[self.positions["Code"].count()] = [code, "Short", 0, 0, 0]

            # make sure which position need to modify
            pos = ""
            if action == "Long"  or action == "SellToCover": pos = "Long"
            if action == "Short" or action == "BuyToCover" : pos = "Short"

            # when do long/short action, add Qnt up; when buy/sell to cover, minus Qnt down
            if action == "SellToCover" or action == "BuyToCover": qnt *= -1

            # query the responding record
            index = self.positions.loc[self.positions.Code==code].loc[self.positions.Position==pos].index

            # update price, quantity and PxQ
            self.positions.loc[index, "Price"] = price
            self.positions.loc[index, "Qnt"]  += qnt
            newQnt = self.positions.loc[index, "Qnt"]
            self.positions.loc[index, "PxQ"] = newQnt * price

        # print positions of self strategy
        def printPosition(self):
            print self.strategy + " " + "/" * 30
            print self.positions


if __name__ == "__main__":

    strategies = ["ANG", "BRA"]
    capital    = 100000000.0
    ac = Account(strategies, capital)

    # code, time, action, qnt, price, pnl, strategy
    ac.recordTrade("HSI", "2015/1/2", "Long",       10, 20000, 10, "ANG")
    ac.recordTrade("HSI", "2015/1/3", "Short",      20, 20000, 11, "ANG")
    ac.recordTrade("HSI", "2015/1/4", "BuyToCover", 5,  20000, 20, "ANG")
    ac.recordTrade("HSI", "2015/1/5", "SellToCover",5,  20000, 21, "ANG")
    ac.recordTrade("GOO", "2015/1/6", "Long",       10, 20000, 10, "ANG")
    ac.recordTrade("GOO", "2015/1/7", "Short",      20, 20000, 11, "ANG")
    ac.recordTrade("GOO", "2015/1/8", "BuyToCover", 5,  20000, 20, "ANG")
    ac.recordTrade("APP", "2015/1/9", "Long",       10, 20000, 10, "ANG")
    ac.recordTrade("HSI", "2015/1/2", "Long",       50, 20000, 10, "BRA")
    ac.recordTrade("HSI", "2015/1/3", "Short",      100,20100, 11, "BRA")
    ac.recordTrade("HSI", "2015/1/4", "BuyToCover", 25, 20200, 20, "BRA")
    ac.recordTrade("HSI", "2015/1/5", "SellToCover",10, 20300, 21, "BRA")
    ac.recordTrade("FBI", "2015/1/6", "Long",       10, 20400, 10, "BRA")
    ac.recordTrade("FBI", "2015/1/7", "Short",      20, 20500, 11, "BRA")
    ac.recordTrade("FBI", "2015/1/8", "BuyToCover", 5,  20600, 20, "BRA")
    ac.recordTrade("FBI", "2015/1/9", "Long",       10, 20700, 10, "BRA")

    # print positions of all strategies
    ac.printPosition()
    # print trade history
    ac.printTradeHistory()

    # print the positions of specific strategy
    print
    ac.printPosition(["ANG"])