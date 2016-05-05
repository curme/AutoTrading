"""
Account
"""

import pandas as pd

# account manager
class AccountManager:

    def __init__(self, strategies=[], capital=100000000.0, margin=0.3):
        self.setAccount(strategies, capital, margin)
        print "Create an empty account."

    def setAccount(self, strategies, capital, margin):
        self.capital    = capital
        self.position   = PositionManager(strategies, self.capital)
        self.tradeBook  = TradeBook()
        self.margin     = margin

    # refresh Account data
    def execAccount(self, code, time, action, qnt, price, strategy):
        pnl = self.position.updatePosition(strategy, code, qnt, price, action)
        self.tradeBook.recordTally([code, time, action, qnt, price, pnl])

    # return trade history
    def queryTradeHistory(self):
        return self.tradeBook.getTallies()

    # print trade history of the account
    def printTradeHistory(self):
        return self.tradeBook.printHistory()

    # print positions for selected strategies
    def printPosition(self, strategies = []):
        self.position.printPosition(strategies)

    # cal qnt
    def calQnt(self, code, action, strategy, proportion = 1):
        if proportion < 0: proportion = 0
        if proportion > 1: proportion = 1
        result = int(proportion * float(self.position.queryPosition(code, action, strategy)["CumuQnt"]))
        if result == "NO RECORD": # while there is no such position record
            print "Account.calQnt() ERROR: ", result
            return 0
        return result


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
        return self.subManagers[strategy].updatePosition(code, action, price, qnt)

    # print the positions of selected strategies
    def printPosition(self, strategies):
        # when the no strategies entry in, that means print positions for all strategies
        if len(strategies) == 0: strategies = self.strategies
        for strategy in strategies:
            self.subManagers[strategy].printPosition()

    # query one position record of selected strategy
    def queryPosition(self, code, action, strategy):
        return self.subManagers[strategy].queryPosition(code, action)

    # the manager to manage the positions for each strategy
    class SubManager:

        def __init__(self, strategy, capital):
            self.strategy = strategy
            self.capital  = capital
            self.positions= pd.DataFrame(columns=["Code", "Position", "LPrice", "CumuQnt", "PxQ", "Base", "AvePrice"])

        # update position of self strategy
        def updatePosition(self, code, action, price, qnt):

            # init the positions for current Code
            if code not in self.positions["Code"].tolist():
                self.positions.loc[self.positions["Code"].count()] = [code, "Long",  0, 0, 0, 0, 0]
                self.positions.loc[self.positions["Code"].count()] = [code, "Short", 0, 0, 0, 0, 0]

            # query the responding record index
            index = self.queryPosition(code, action).index

            # update price, quantity, PxQ
            # when do long/short action, add Qnt up; when buy/sell to cover, minus Qnt down
            signedQnt = qnt
            if action == "SellToCover" or action == "BuyToCover": signedQnt *= -1
            self.positions.loc[index, "LPrice"]  = price
            self.positions.loc[index, "CumuQnt"]+= signedQnt
            self.positions.loc[index, "PxQ"]     = price * self.positions.loc[index, "CumuQnt"]

            # calculate PnL
            # when after position update, the function will return a PnL
            pnl = ""
            if action == "SellToCover" : pnl = qnt * (price - float(self.positions.loc[index, "AvePrice"]))
            if action == "BuyToCover"  : pnl = qnt * (float(self.positions.loc[index, "AvePrice"] - price))

            # update Base and AvePrice
            # init AvePrice if needed
            if float(self.positions.loc[index, "Base"]) == 0: self.positions.loc[index, "AvePrice"] = price
            if action == "SellToCover" or action == "BuyToCover": self.positions.loc[index, "Base"]-= qnt * self.positions.loc[index, "AvePrice"]
            if action == "Long"        or action == "Short"     : self.positions.loc[index, "Base"]+= qnt * price
            self.positions.loc[index, "AvePrice"]= self.positions.loc[index, "Base"]/float(self.positions.loc[index, "CumuQnt"])

            return pnl

        # print positions of self strategy
        def printPosition(self):
            print self.strategy + " " + "/" * 30
            print self.positions

        # query one position record of self strategy
        def queryPosition(self, code, action):
            pos = ""
            if action == "Long" or action == "SellToCover": pos = "Long"
            if action == "Short" or action == "BuyToCover": pos = "Short"
            record = self.positions.loc[self.positions.Code == code].loc[self.positions.Position == pos]
            if len(record) == 0 : return "NO RECORD" # while there is no such position record
            return record


if __name__ == "__main__":

    strategies = ["ANG", "BRA"]
    capital    = 100000000.0
    ac = AccountManager(strategies, capital)

    # code, time, action, qnt, price, strategy
    ac.execAccount("HSI", "2015/1/2", "Long",       60, 20000, "ANG")
    ac.execAccount("HSI", "2015/1/2", "Long",       40, 21000, "ANG")
    ac.execAccount("HSI", "2015/1/2", "Long",       70, 21500, "ANG")
    ac.execAccount("HSI", "2015/1/2", "SellToCover",100,22000, "ANG")
    ac.execAccount("HSI", "2015/1/2", "Long",       120,21900, "ANG")
    ac.execAccount("HSI", "2015/1/2", "SellToCover",120,22200, "ANG")
    ac.execAccount("HSI", "2015/1/2", "Long",       80, 22000, "ANG")
    ac.execAccount("HSI", "2015/1/2", "Long",       100,21500, "ANG")
    ac.execAccount("HSI", "2015/1/2", "SellToCover",150,22000, "ANG")
    ac.execAccount("HSI", "2015/1/2", "SellToCover",50, 22100, "ANG")
    ac.execAccount("HSI", "2015/1/2", "Long",       10, 22000, "ANG")
    ac.execAccount("HSI", "2015/1/2", "SellToCover",60, 21900, "ANG")
    ac.execAccount("HSI", "2015/1/3", "Short",      20, 20000, "ANG")
    ac.execAccount("HSI", "2015/1/4", "BuyToCover", 5,  20000, "ANG")
    ac.execAccount("GOO", "2015/1/6", "Long",       10, 20000, "ANG")
    ac.execAccount("GOO", "2015/1/7", "Short",      20, 20000, "ANG")
    ac.execAccount("GOO", "2015/1/8", "BuyToCover", 5,  20000, "ANG")
    ac.execAccount("APP", "2015/1/9", "Long",       10, 20000, "ANG")
    ac.execAccount("HSI", "2015/1/2", "Long",       50, 20000, "BRA")
    ac.execAccount("HSI", "2015/1/3", "Short",      100,20100, "BRA")
    ac.execAccount("HSI", "2015/1/4", "BuyToCover", 25, 20200, "BRA")
    ac.execAccount("HSI", "2015/1/5", "SellToCover",10, 20300, "BRA")
    ac.execAccount("FBI", "2015/1/6", "Long",       10, 20400, "BRA")
    ac.execAccount("FBI", "2015/1/7", "Short",      20, 20500, "BRA")
    ac.execAccount("FBI", "2015/1/8", "BuyToCover", 5,  20600, "BRA")
    ac.execAccount("FBI", "2015/1/9", "Long",       10, 20700, "BRA")

    # print positions of all strategies
    ac.printPosition()
    # print trade history
    ac.printTradeHistory()