

class Strategy:

    def __init__(self):
        self.name = ""

    def Long(self, code, data, tradeId, quantity, strategy, OpenOrClose='Close'):
        signal = [code, data.loc[tradeId, 'Date'], 'Long', quantity, data.loc[tradeId, OpenOrClose], data.loc[tradeId, 'Volume'], strategy]
        return signal

    def Short(self, code, data, tradeId, quantity, strategy, OpenOrClose='Close'):
        signal = [code, data.loc[tradeId, 'Date'], 'Short', quantity, data.loc[tradeId, OpenOrClose], data.loc[tradeId, 'Volume'], strategy]
        return signal

    def SellToCover(self, code, data, tradeId, quantity, strategy, OpenOrClose='Close'):
        signal = [code, data.loc[tradeId, 'Date'], 'SellToCover', quantity, data.loc[tradeId, OpenOrClose], data.loc[tradeId, 'Volume'], strategy]
        return signal

    def BuyToCover(self, code, data, tradeId, quantity, strategy, OpenOrClose='Close'):
        signal = [code, data.loc[tradeId, 'Date'], 'BuyToCover', quantity, data.loc[tradeId, OpenOrClose], data.loc[tradeId, 'Volume'], strategy]
        return signal