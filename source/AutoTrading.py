import pandas as pd

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
        dataSet = self.data.getInterval(start, end) # entry security code
        signals = self.strategies.monitorMarket(dataSet)

        # # trade under signals
        # self.orderAgent.handleSignals(self.account, signals)
        for index, row in signals.iterrows():
            self.account.execAccount(row['Code'], row['Time'], row['Action'], row['Qnt'], row['Price'], row['Strategy'])

        # print history
        self.account.printTradeHistory()


if __name__ == "__main__":

    atm = AutoTradeManager()
    atm.run(pd.Timestamp("2015-12-31 16:00:00"), pd.Timestamp("2016-02-26 16:00:00"), "HSI")