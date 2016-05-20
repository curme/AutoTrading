import pandas as pd
from source.data.preprocessing import Data
import datetime
import operator
import collections
import copy

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
        if self.orderGenerateType == "TWAP": return self.orderTWAP(signal)
        if self.orderGenerateType == "TVOL": return self.orderTVOL(signal)
        return []

    # generate orders in VWAP type
    def orderVWAP(self, signal):
        # Take the last 7 days transaction data for historical data analysis
        historyDays = 7

        # analysis the signal
        code = signal[0]
        sDate = signal[1]
        action = signal[2]
        expectPrice = signal[3]
        totalTradeSize = signal[4]
        type = signal[5]

        # setup the search start data and end date for searching the historical data
        searchSDate = sDate - datetime.timedelta(days=historyDays+1)
        searchEDate = sDate - datetime.timedelta(days=1)

        # setup the data source and start to search
        dt = Data()
        df = dt.getCSVData()
        dataSet = dt.getInterval(searchSDate, searchEDate)

        # predefined dictionaries
        timeslotVolumes = {}
        timeslotCounts = {}
        timeslotAvgVolumes = {}
        timeslotAvgVolumePercentages = {}

        # find out the total past 7 days trading volumes for each time interval
        for row in dataSet.iterrows():
            tempTime = row[1]['Date']
            tempVolume = row[1]['Volume']
            tempTimeslotStr = str(tempTime.hour)+':'+str(tempTime.minute)+':'+str(tempTime.second)
            tempTimeslot=datetime.datetime.strptime(tempTimeslotStr,"%H:%M:%S").time()
            if not tempTimeslot in timeslotVolumes:
                timeslotVolumes[tempTimeslot] = tempVolume
                timeslotCounts[tempTimeslot] = 1
            else:
                timeslotVolumes[tempTimeslot] += tempVolume
                timeslotCounts[tempTimeslot] += 1

        # find out the average past 7 day trading volumes for each time interval
        totalTimelotAvgVolume = 0
        for timeslot in timeslotVolumes:
            timeslotAvgVolumes[timeslot] = timeslotVolumes[timeslot]/timeslotCounts[timeslot]
            totalTimelotAvgVolume += timeslotVolumes[timeslot]/timeslotCounts[timeslot]

        # find out how many percentage each time interval trading volumes included
        for timeslot in timeslotAvgVolumes:
            timeslotAvgVolumePercentages[timeslot] = timeslotAvgVolumes[timeslot]*1.0 / totalTimelotAvgVolume

        # put the data in a sortable container
        sortedTimeslotAvgVolumePercentages = collections.OrderedDict(sorted(timeslotAvgVolumePercentages.items(), key=operator.itemgetter(0)))

        # ready the iterators to loop all transaction intervals
        stimeStr = str(sDate.hour)+':'+str(sDate.minute)+':'+str(sDate.second)
        sTimeslot=datetime.datetime.strptime(tempTimeslotStr,"%H:%M:%S").time()
        sIndex = sortedTimeslotAvgVolumePercentages.keys().index(sTimeslot)
        timeslotSize = len(sortedTimeslotAvgVolumePercentages)
        loopIndex = sIndex
        tempSearchDate = sDate

        # setup the order List
        orderList = []

        # loop until all expected trading volumes used up
        while totalTradeSize > 0:
            # use the historical volume percentage to calculate how many trading volume should choose in current time interval
            timeInterval = sortedTimeslotAvgVolumePercentages.keys()[loopIndex]
            tempSearchDate = tempSearchDate.replace(hour=timeInterval.hour, minute=timeInterval.minute, second=timeInterval.second)
            dataSet = dt.getInterval(tempSearchDate, tempSearchDate)
            tempVolume = 0
            tempPrice = 0
            for row in dataSet.iterrows():
                tempVolume = row[1]['Volume']
                tempPrice = row[1]['Open']
                break
            print tempVolume
            print sortedTimeslotAvgVolumePercentages.values()[loopIndex]
            tradableVol = round(tempVolume*1.0 * sortedTimeslotAvgVolumePercentages.values()[loopIndex])

            if(totalTradeSize - tradableVol<0):
                orderList.append([code, tempSearchDate.strftime('%Y-%m-%d %H:%M:%S'), action, totalTradeSize, tempPrice])
                totalTradeSize = 0
            else:
                totalTradeSize -= tradableVol
                orderList.append([code, tempSearchDate.strftime('%Y-%m-%d %H:%M:%S'), action, tradableVol, tempPrice])
            loopIndex+=1
            if loopIndex >= timeslotSize:
                loopIndex = 0
                tempSearchDate = tempSearchDate + datetime.timedelta(days=1)

        # return the order list
        print "orderList" , "*" * 100
        print orderList
        return orderList

    # generate orders in TWAP type
    def orderTWAP(self, signal):

        # THIS IS A EXAMPLE WITHOUT GENERATING ORDERS
        return []

    # generate orders in POV type
    def orderPOV(self, signal):
        """
           Code                Time       Action  Qnt    QntPer  Price     PnL    Equity        Strategy
        0   HSI 2016-01-06 14:15:00        Short    0  0.000000  20983          25000000    ACOscillator
        1   HSI 2016-01-07 09:30:00   BuyToCover    0  0.000000  20775       0  25000000    ACOscillator
        2   HSI 2016-01-07 09:45:00         Long    5  0.135135  20628          25000000    ACOscillator
        3   HSI 2016-01-12 10:15:00  SellToCover    5  0.192308  20009   -3095  24996905    ACOscillator
        ...
        16  HSI 2016-02-03 13:00:00        Short  337  0.096094  18926          25023833    ACOscillator
        17  HSI 2016-02-11 09:15:00   BuyToCover  337  0.051592  18400  177262  25201095    ACOscillator
        18  HSI 2016-02-19 09:00:00        Short   41  0.148014  19232          25201095    ACOscillator

        :param signal:
        :return:
        """
        executionBook = pd.DataFrame(columns=["Code", "Time", "Action", "Qnt", "QntPer", "Price", "PnL", "Equity", "Strategy"])
        for index, row in signal.iterrows():
            pass

        # THIS IS A EXAMPLE WITHOUT GENERATING ORDERS
        return []

    # generate orders in TWAP type
    def orderTVOL(self, signal):

        # THIS IS A EXAMPLE WITHOUT GENERATING ORDERS
        return []
