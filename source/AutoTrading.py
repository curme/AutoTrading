import pandas as pd
pd.options.display.max_rows = 999
pd.set_option('expand_frame_repr', False)
import datetime

from source.data.preprocessing import Data
from source.strategies.manager import StrategiesManager
from source.money.account      import AccountManager
from source.order.manager      import OrderManager

class AutoTradeManager:

    def __init__(self):
        self.data       = Data()
        self.strategies = StrategiesManager()
        self.account    = AccountManager(self.strategies.strategiesPool)
        # self.orderAgent = OrderManager()

    # reset system
    def resetSystem(self, capital, margin):

        # reset account
        self.account.setAccount(self.strategies.strategiesPool, capital, margin)

    def run(self, start, end, security, capital=100000000.0, margin=0.3):

        # reset system before run
        self.resetSystem(capital, margin)

        # generate trading signals for specific security
        dataSet = self.data.getCSVData()
        signals = self.strategies.monitorMarket(dataSet)

        # # trade under signals
        # self.orderAgent.handleSignals(self.account, signals)
        for index, row in signals.iterrows():

            if row['Action'] == "Long" or row['Action'] == "Short":
                self.account.execAccount(row['Code'], row['Time'], row['Action'],
                                         self.account.getQuantity(row['Strategy'], dataSet, row['Price'], row['Volume']),
                                         self.account.getQuantity(row['Strategy'], dataSet, row['Price'], row['Volume'])/row['Volume'],
                                         row['Price'], row['Strategy'])

            elif row['Action'] == "BuyToCover":
                Qnt = int(self.account.queryPosition(row['Code'], "Short", row['Strategy'])['CumuQnt'])
                self.account.execAccount(row['Code'], row['Time'], row['Action'],
                                         int(self.account.queryPosition(row['Code'], "Short", row['Strategy'])['CumuQnt']),
                                         Qnt/row['Volume'],
                                         row['Price'], row['Strategy'])

            elif row['Action'] == "SellToCover":
                Qnt = int(self.account.queryPosition(row['Code'], "Long", row['Strategy'])['CumuQnt'])
                self.account.execAccount(row['Code'], row['Time'], row['Action'],
                                         int(self.account.queryPosition(row['Code'], "Long", row['Strategy'])['CumuQnt']),
                                         Qnt/row['Volume'],
                                         row['Price'], row['Strategy'])

        # print history
        self.account.printTradeHistory()

        # query position
        # print self.account.queryPosition('HSI', 'Long', 'ACOscillator')

if __name__ == "__main__":

    atm = AutoTradeManager()
    atm.run(pd.Timestamp("2015-12-31 16:00:00"), pd.Timestamp("2016-02-26 16:00:00"), "HSI")
