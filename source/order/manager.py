
class OrderManager:

    def __init__(self, orderGenerateType="VWAP"):
        self.setManager(orderGenerateType)
        print "Create a order manager."

    def setManager(self, orderGenerateType):
        self.orderGenerateType = orderGenerateType

    # convert the trading signal to trading orders
    def handleSignals(self, account, signals):

        # 5.4 20:00 the format of signal [Strategy, Code, Time, Action, Price, QoP, Type]
        for signal in signals:

            strategy, code, time, action, expect_price, qop, type = signal

            # cal trade qnt
            qnt = 0
            if action == "Long"        or action == "Short"     : qnt = qop
            if action == "SellToCover" or action == "BuyToCover": qnt = account.calQnt(code, action, strategy, qop)

            # generate orders
            orders = self.generateOrders([code, time, action, expect_price, qnt, type])

            # execute orders
            self.executeOrders(account, orders, strategy)

    # execute orders
    def executeOrders(self, account, orders, strategy):

        for order in orders:
            account.execAccount(order + [strategy])


    # generate orders in different types
    def generateOrders(self, signal):
        if self.orderGenerateType == "VWAP": return self.orderVWAP(signal)
        if self.orderGenerateType == "TVAP": return self.orderTWAP(signal)
        if self.orderGenerateType == "TVOL": return self.orderTVOL(signal)
        return []

    # generate orders in VWAP type
    def orderVWAP(self, signal):

        # THIS IS A EXAMPLE ORDER POOL WITH ONLY ONE ORDER INSIDE
        code, time, action, expect_price, qnt, type = signal
        actual_price   = expect_price
        orders_example = [[code, time, action, qnt, actual_price]]
        return orders_example

    # generate orders in TWAP type
    def orderTWAP(self, signal):

        # THIS IS A EXAMPLE WITHOUT GENERATING ORDERS
        return []

    # generate orders in TWAP type
    def orderTVOL(self, signal):

        # THIS IS A EXAMPLE WITHOUT GENERATING ORDERS
        return []