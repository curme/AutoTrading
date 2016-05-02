import pandas as pd
import talib as tl
import numpy as np
import matplotlib.pyplot as plt
from talib import MA_Type

from source.data.indicators import volatility
from source.data.preprocessing import Data
from source.order.action import *
from source.order.tradeBook import tradeBook

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
    for i in xrange(timeperiod , len(middleBand) - 1):
        if (crossOver(i , df, upperBand)):
            signal = Sell('HSI', df, i)
            signals.append(signal)
        if (crossDown(i, df, lowerBand)):
            signal = Buy('HSI', df, i)
            signals.append(signal)

    signals = tradeBook.simpleBook(signals)
    pd.set_option("display.max_rows", 280)
    print signals
    plt.plot(df['Date'], df['Close'], df['Date'], df['Close'], 'ro', df['Date'], upperBand,df['Date'], lowerBand)
    plt.show()



if __name__ == "__main__":
    dt = Data()
    vl = volatility()
    df = dt.getExcelInterval(pd.Timestamp("2016-02-20 16:00:00"),pd.Timestamp("2016-02-26 16:00:00"))
    BollingerTest(df)
