import sys
from PyQt5.QtWidgets import QApplication
from interface.widgets import MainWindow

import pandas as pd
'''from source.data.preprocessing import Data
from source.strategies.manager import StrategiesManager
from source.money.account      import AccountManager
from source.order.manager      import OrderManager'''

class AutoTradeManager:

    def __init__(self):
        self.app        = QApplication(sys.argv)
        self.mainWindow = MainWindow()
        '''self.data       = Data()
        self.strategies = StrategiesManager()
        self.account    = AccountManager()
        self.orderAgent = OrderManager()'''
        sys.exit(self.app.exec_())

    # reset system
    def resetSystem(self, capital, margin):

        # reset account
        self.account.setAccount(self.strategies.getList(), capital, margin)

    '''def run(self, start, end, security, capital=100000000.0, margin=0.3):

        # reset system before run
        self.resetSystem(capital, margin)

        # generate trading signals for specific security
        dataSet = self.data.getInterval(security, start, end) # entry security code
        signals = self.strategies.monitorMarket(dataSet)

        # trade under signals
        self.orderAgent.handleSignals(self.account, signals)

        # print history
        self.account.printTradeHistory()'''


if __name__ == "__main__":

    atm = AutoTradeManager()
    #atm.run(pd.Timestamp("2016-02-10 16:00:00"), pd.Timestamp("2016-02-26 16:00:00"), "HSI")