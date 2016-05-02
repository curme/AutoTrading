import pandas as pd
import talib as tl
import numpy as np
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
    for i in xrange(timeperiod - 1, len(middleBand) - 1):
        # Cross Over, Sell
        if df.loc[i, 'Close'] > upperBand[i]:
            signal = Sell('HSI', df, i)
            signals.append(signal)
        # Cross Under, Buy
        if df.loc[i, 'Close'] < lowerBand[i]:
            signal = Buy('HSI', df, i)
            signals.append(signal)

    signals = tradeBook.simpleBook(signals)
    print signals


if __name__ == "__main__":
    dt = Data()
    vl = volatility()
    df = dt.getExcelInterval(pd.Timestamp("2015-10-26 16:00:00"),pd.Timestamp("2016-03-26 16:00:00"))
    BollingerTest(df)
