import pandas as pd
import talib as tl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from talib import MA_Type

from source.data.preprocessing import Data
from source.order.action import *
from source.order.tradeBook import tradeBook
from source.money.account import Account

def BollingerTest(df, timeperiod=30, nbdevup=2, nbdevdn=2, matype=0):
    """
    :param df           : input data
    :param timeperiod   : time period of BBANDS
    :param nbdevup      : upper stdev
    :param nbdevdn      : lower stdev
    :param matype       : matheod type (see ..data/indicators/BBANDS)
    :return             : a signal book
    """
    # Preprocess data
    float_array = Data.toFloatArray(df['Close'])
    # BBANDS
    upperBand, middleBand, lowerBand = tl.BBANDS(np.array(float_array), timeperiod, nbdevup, nbdevdn, matype)
    signals = []
    for i in xrange(timeperiod, len(middleBand) - 1):
        if (crossOver(i , df, upperBand)):
            signalShort = Short('HSI', df, i)
            for sig in signalShort:
                signals.append(sig)

        if (crossDown(i, df, lowerBand)):
            signalLong = Long('HSI', df, i)
            for sig in signalLong:
                signals.append(sig)

    signals = tradeBook.simpleBook(signals)
    pd.set_option("display.max_rows", 280)
    print signals


    ###### PLOT #######
    longSignals = signals[signals['Action'] == 'Long']
    shortSignals = signals[signals['Action'] == 'Short']
    plt.plot(df['Date'], df['Close'], longSignals['Time'], longSignals['Price'], 'r^', shortSignals['Time'],
             shortSignals['Price'], 'gv', df['Date'], upperBand, df['Date'], lowerBand, markersize=10)
    red_patch = mpatches.Patch(color='red', label='Long')
    green_patch = mpatches.Patch(color='green', label='Short')
    plt.legend(handles=[red_patch, green_patch])
    plt.grid()
    plt.show()
    ###### PLOT #######


if __name__ == "__main__":
    ac = Account()
    dt = Data()
    df = dt.getExcelInterval(pd.Timestamp("2016-02-10 16:00:00"), pd.Timestamp("2016-02-26 16:00:00"))
    BollingerTest(df)
    print Account.position
