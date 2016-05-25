import pandas as pd
from source.dataManager.manager import DataManager
from datetime import datetime
import datetime
import operator
import collections
import copy


class OrderManager:
    def __init__(self, orderGenerateType="Simple"):
        self.setManager(orderGenerateType)
        print "Create an order manager."

    def setManager(self, orderGenerateType):
        self.orderGenerateType = orderGenerateType

    # convert the trading signal to trading orders
    def handleSignals(self, account, signals):
        """
           Code                Time       Action  Qnt    QntPer  Price   Equity        Strategy
        0   HSI 2016-01-06 14:15:00        Short    0  0.000000  20983  25000000    ACOscillator
        1   HSI 2016-01-07 09:30:00   BuyToCover    0  0.000000  20775  25000000    ACOscillator
        2   HSI 2016-01-07 09:45:00         Long    5  0.135135  20628  25000000    ACOscillator
        3   HSI 2016-01-12 10:15:00  SellToCover    5  0.192308  20009  24996905    ACOscillator
        ...
        16  HSI 2016-02-03 13:00:00        Short  337  0.096094  18926  25023833    ACOscillator
        17  HSI 2016-02-11 09:15:00   BuyToCover  337  0.051592  18400  25201095    ACOscillator
        18  HSI 2016-02-19 09:00:00        Short   41  0.148014  19232  25201095    ACOscillator

        :param account:
        :param signals:
        :return:
        """
        # signals
        for index, row in signals.iterrows():
            if row['Action'] == "Long" or row['Action'] == "Short":
                eachTrade = [row['Code'],
                             row['Time'],
                             row['Action'],
                             account.getQuantity(row['Strategy'], row['Price'], row['Volume']),
                             float(account.getQuantity(row['Strategy'], row['Price'], row['Volume'])) / float(row['Volume']),
                             row['Price'],
                             account.queryCapital(row['Strategy']),
                             row['Strategy']
                             ]

            elif row['Action'] == "BuyToCover":
                Qnt = int(account.queryPosition(row['Code'], "Short", row['Strategy'])['CumuQnt'])
                eachTrade = [row['Code'],
                             row['Time'],
                             row['Action'],
                             int(account.queryPosition(row['Code'], "Short", row['Strategy'])['CumuQnt']),
                             float(Qnt) / float(row['Volume']),
                             row['Price'],
                             account.queryCapital(row['Strategy']),
                             row['Strategy']
                             ]

            elif row['Action'] == "SellToCover":
                Qnt = int(account.queryPosition(row['Code'], "Long", row['Strategy'])['CumuQnt'])
                eachTrade = [row['Code'],
                             row['Time'],
                             row['Action'],
                             int(account.queryPosition(row['Code'], "Long", row['Strategy'])['CumuQnt']),
                             float(Qnt) / float(row['Volume']),
                             row['Price'],
                             account.queryCapital(row['Strategy']),
                             row['Strategy']
                             ]

            # generate orders
            # signal = [Code, Time, Action, Qnt, QntPer, Price, Equity, Strategy]
            orders = self.generateOrders(eachTrade)

            # execute orders
            self.executeOrders(account, orders)

    # execute orders
    def executeOrders(self, account, orders):

        for order in orders:
            # Code, Time, Action, Qnt, QntPer, Price, Equity, Strategy = signal
            Code, Time, Action, Qnt, QntPer, Price, Equity, Strategy = order
            account.execAccount(Code, Time, Action, Qnt, QntPer, Price, Strategy)

    # generate orders in different types
    def generateOrders(self, signal):
        if self.orderGenerateType == "VWAP"   : return self.orderVWAP(signal)
        if self.orderGenerateType == "TWAP"   : return self.orderTWAP(signal)
        # if self.orderGenerateType == "POV"    : return self.orderPOV(signal)
        # if self.orderGenerateType == "Simple" : return self.orderTWAP(signal)
        if self.orderGenerateType == "Default": return self.orderDefault(signal)

        return []

    # generate orders in VWAP type
    """
    def orderVWAP(self, signal):
        # Take the last 7 days transaction data for historical data analysis
        historyDays = 7

        # analysis the signal
        code, sDate, action, totalTradeSize, QntPer, expectPrice, Equity, type = signal
        # code = signal[0]
        # sDate = signal[1]
        # action = signal[2]
        # totalTradeSize = signal[3]
        # expectPrice = signal[5]
        # qntPer = signal[6]
        # type = signal[5]

        # setup the search start data and end date for searching the historical data
        searchSDate = sDate - datetime.timedelta(days=historyDays + 1)
        searchEDate = sDate - datetime.timedelta(days=1)

        # setup the data source and start to search
        dt = DataManager()
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
            tempTimeslotStr = str(tempTime.hour) + ':' + str(tempTime.minute) + ':' + str(tempTime.second)
            tempTimeslot = datetime.datetime.strptime(tempTimeslotStr, "%H:%M:%S").time()
            if not tempTimeslot in timeslotVolumes:
                timeslotVolumes[tempTimeslot] = tempVolume
                timeslotCounts[tempTimeslot] = 1
            else:
                timeslotVolumes[tempTimeslot] += tempVolume
                timeslotCounts[tempTimeslot] += 1

        # find out the average past 7 day trading volumes for each time interval
        totalTimelotAvgVolume = 0
        for timeslot in timeslotVolumes:
            timeslotAvgVolumes[timeslot] = timeslotVolumes[timeslot] / timeslotCounts[timeslot]
            totalTimelotAvgVolume += timeslotVolumes[timeslot] / timeslotCounts[timeslot]

        # find out how many percentage each time interval trading volumes included
        for timeslot in timeslotAvgVolumes:
            timeslotAvgVolumePercentages[timeslot] = timeslotAvgVolumes[timeslot] * 1.0 / totalTimelotAvgVolume

        # put the data in a sortable container
        sortedTimeslotAvgVolumePercentages = collections.OrderedDict(
            sorted(timeslotAvgVolumePercentages.items(), key=operator.itemgetter(0)))

        # ready the iterators to loop all transaction intervals
        stimeStr = str(sDate.hour) + ':' + str(sDate.minute) + ':' + str(sDate.second)
        sTimeslot = datetime.datetime.strptime(tempTimeslotStr, "%H:%M:%S").time()
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
            tempSearchDate = tempSearchDate.replace(hour=timeInterval.hour, minute=timeInterval.minute,
                                                    second=timeInterval.second)
            dataSet = dt.getInterval(tempSearchDate, tempSearchDate)
            tempVolume = 0
            tempPrice = 0
            for row in dataSet.iterrows():
                tempVolume = row[1]['Volume']
                tempPrice = row[1]['Open']
                break
            print tempVolume
            print sortedTimeslotAvgVolumePercentages.values()[loopIndex]
            tradableVol = round(tempVolume * 1.0 * sortedTimeslotAvgVolumePercentages.values()[loopIndex])

            if (totalTradeSize - tradableVol < 0):
                orderList.append(
                        [code, tempSearchDate.strftime('%Y-%m-%d %H:%M:%S'), action, totalTradeSize, QntPer, tempPrice, Equity, type])
                totalTradeSize = 0
            else:
                totalTradeSize -= tradableVol
                orderList.append([code, tempSearchDate.strftime('%Y-%m-%d %H:%M:%S'), action, totalTradeSize, QntPer, tempPrice, Equity, type])
            loopIndex += 1
            if loopIndex >= timeslotSize:
                loopIndex = 0
                tempSearchDate = tempSearchDate + datetime.timedelta(days=1)

        # return the order list
        print "orderList", "*" * 100
        print orderList
        return orderList
    """

    # generate orders in TWAP type
    """
    def orderTWAP(self, signal):

        # Take the last 7 days transaction data for historical data analysis
        historyDays = 7

        # analysis the signal
        code, sDate, action, totalTradeSize, QntPer, expectPrice, Equity, type = signal


        # setup the search start data and end date for searching the historical data
        searchSDate = sDate - datetime.timedelta(days=historyDays + 1)
        searchEDate = sDate - datetime.timedelta(days=1)

        # setup the data source and start to search
        dt = DataManager()
        df = dt.getCSVData()
        dataSet = dt.getInterval(searchSDate, searchEDate)

        # predefined dictionaries
        timeslotPrice = {}
        timeslotCounts = {}
        timeslotAvgPrice = {}
        timeslotVolumes = {}

        # find out the total past 7 days closing price for each time interval
        for row in dataSet.iterrows():
            tempTime = row[1]['Date']
            tempPrice = row[1]['Close']
            tempTimeslotStr = str(tempTime.hour) + ':' + str(tempTime.minute) + ':' + str(tempTime.second)
            tempTimeslot = datetime.datetime.strptime(tempTimeslotStr, "%H:%M:%S").time()
            if not tempTimeslot in timeslotVolumes:
                timeslotPrice[tempTimeslot] = tempPrice
                timeslotCounts[tempTimeslot] = 1
            else:
                timeslotPrice[tempTimeslot] += tempPrice
                timeslotCounts[tempTimeslot] += 1

		# find out the average past 7 day trading price for each time interval
        totalTimeslotAvgPrice = 0
        for timeslot in timeslotPrice:
            timeslotAvgPrice[timeslot] = timeslotPrice[timeslot] / timeslotCounts[timeslot]
            totalTimeslotAvgPrice += timeslotPrice[timeslot] / timeslotCounts[timeslot]

        print totalTradeSize
        print timeslotCounts
        order_size = totalTradeSize / timeslotCounts
        order=[]

        while totalTradeSize > 0:
        	if totalTradeSize>=order_size:
				order.append([code, sDate, action, order_size, QntPer, totalTimeslotAvgPrice, Equity, type])
				totalTradeSize-=order_size
        	else:
				order.append([code, sDate, action, totalTradeSize, QntPer, totalTimeslotAvgPrice, Equity, type])
				totalTradeSize=0
        return order
    """

    # generate orders in POV type
    def orderPOV(self, signal):
        # Q(t + deltaT) - Q(t) = -min[gamma(V(t) - V(t - deltaT)), Q(t)]
        # Take the last 7 days transaction data for historical data analysis
        historyDays = 7
        participationRatio = 0.1
        # analysis the signal
        # signal = [Code, Time, Action, Qnt, QntPer, Price, Equity, Strategy]
        code, sDate, action, totalTradeSize, QntPer, expectPrice, Equity, type = signal
        
        # code = signal[0]
        # sDate = signal[1]
        # action = signal[2]
        # totalTradeSize = signal[3]
        # #percentageQuantity = signal[4]
        # price = signal[5]
        # #equity = signal[6]
        # #strategy = signal[7]
        
        # setup the data source and start to search
        dt = DataManager()
        df = dt.getCSVData()
        #dataSet = dt.getInterval(searchSDate, searchEDate)
        tempSearchDate = sDate
        dataSet = dt.getInterval(tempSearchDate, tempSearchDate)
        stimeStr = str(sDate.hour) + ':' + str(sDate.minute) + ':' + str(sDate.second)
        sTimeslot = datetime.datetime.strptime(stimeStr, "%H:%M:%S").time()
        curTimeslot = sTimeslot
        
        # setup the order List
        orderList = []
        
        # loop until all expected trading volumes used up
        while totalTradeSize > 0:
            
            dataSet = dt.getInterval(tempSearchDate, tempSearchDate)
            for row in dataSet.iterrows():
                tempTime = row[1]['Date']
                tempVolume = row[1]['Volume']
                tempPrice = row[1]['Open']
                #tempTimeslotStr = str(tempTime.hour) + ':' + str(tempTime.minute) + ':' + str(tempTime.second)
                #tempTimeslot = datetime.datetime.strptime(tempTimeslotStr, "%H:%M:%S").time()
                if tempTime < curTimeslot:
                    continue
                else:
                    break
        
            #print tempVolume

            tradableVol = participationRatio * tempVolume
            
            if (totalTradeSize - tradableVol < 0):
                orderList.append([code, tempSearchDate.strftime('%Y-%m-%d %H:%M:%S'), action, totalTradeSize, QntPer, tempPrice, Equity, type])
                totalTradeSize = 0
            else:
                totalTradeSize -= tradableVol
                orderList.append([code, tempSearchDate.strftime('%Y-%m-%d %H:%M:%S'), action, tradableVol, QntPer, tempPrice, Equity, type])
            
            curTimeslot = tempTime + datetime.timedelta(minutes=1)
            
            if curTimeslot.day > tempSearchDate.day:
                tempSearchDate = tempSearchDate + datetime.timedelta(days=1)

        # return the order list
        print "orderList", "*" * 100
        print orderList
        return orderList
        # THIS IS A EXAMPLE WITHOUT GENERATING ORDERS
        #return []

    # generate orders in POV type
    def orderTWAP(self, signal):
        """
           Code                Time       Action  Qnt    QntPer  Price   Equity        Strategy
        0   HSI 2016-01-06 14:15:00        Short    0  0.000000  20983  25000000    ACOscillator
        1   HSI 2016-01-07 09:30:00   BuyToCover    0  0.000000  20775  25000000    ACOscillator
        2   HSI 2016-01-07 09:45:00         Long    5  0.135135  20628  25000000    ACOscillator
        3   HSI 2016-01-12 10:15:00  SellToCover    5  0.192308  20009  24996905    ACOscillator
        ...
        16  HSI 2016-02-03 13:00:00        Short  337  0.096094  18926  25023833    ACOscillator
        17  HSI 2016-02-11 09:15:00   BuyToCover  337  0.051592  18400  25201095    ACOscillator
        18  HSI 2016-02-19 09:00:00        Short   41  0.148014  19232  25201095    ACOscillator

        """
        slippage = 0.001
        splite   = 3
        Code, Time, Action, Qnt, QntPer, Price, Equity, Strategy = signal
        QntPerMax = 0.05
        realOrder = []

        if Qnt < 3      : return [signal]
        if QntPer < QntPerMax : return [signal]
        if QntPer >= QntPerMax:
            #initiate order data
            remainQnt = Qnt
            remainQntPer = QntPer
            eachQnt     = int(Qnt * QntPerMax / QntPer)
            #handle boundary condition
            if(eachQnt < 1):
                eachQnt = 1
            eachQntPer  = (eachQnt * 1.0 / Qnt) * QntPer
            remainQntPer = remainQntPer - eachQntPer
            remainQnt   = remainQnt - eachQnt

            #generate the first order
            eachSignal = [Code, Time, Action, eachQnt, eachQntPer, Price, Equity, Strategy]
            realOrder.append(eachSignal)

            #generate the following orders
            while remainQntPer >= QntPerMax :
                eachQnt     = int(Qnt * QntPerMax / QntPer)
                #handle boundary condition
                if(eachQnt <1):
                    eachQnt = 1
                eachQntPer  = (eachQnt*1.0 / Qnt) * QntPer
                remainQnt   = remainQnt - eachQnt
                remainQntPer = remainQntPer - eachQntPer
                Time = Time + datetime.timedelta(minutes=5)
                if (Action == 'Short' or Action == 'SellToCover'):
                    Price = Price * (1 - slippage)
                    eachSignal = [Code, Time, Action, eachQnt, eachQntPer,Price,Equity, Strategy]
                    realOrder.append(eachSignal)
                if (Action == 'Buy' or Action == 'BuyToCover'):
                    Price = Price * (1 + slippage)
                    eachSignal = [Code, Time, Action, eachQnt, eachQntPer,Price,Equity, Strategy]
                    realOrder.append(eachSignal)

            #generate the last order
            Time = Time + datetime.timedelta(minutes=5)
            if (Action == 'Short' or Action == 'SellToCover'):
                Price = Price * (1 - slippage)
            if (Action == 'Buy' or Action == 'BuyToCover'):
                Price = Price * (1 + slippage)
            eachSignal = [Code, Time, Action, remainQnt, remainQntPer,Price,Equity, Strategy]
            realOrder.append(eachSignal)
            return realOrder

    def orderDefault(self, signal):

        # THIS IS A EXAMPLE WITHOUT GENERATING ORDERS
        return [signal]
