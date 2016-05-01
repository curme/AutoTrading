"""
Indicators will be used to trigger strategies
---------------------------------------------------------
Type        |Examples
---------------------------------------------------------
Trend       |Moving Average, MACD, Parabolic SAR
Momentum    |Stochastic, CCI, RSI, EMA
Volatility  |Bollinger Band, Average True Range, Std
Volume      |Chaikin Oscillator, OBV, Rate of Change(ROV)
---------------------------------------------------------
"""

import pandas as pd
import numpy as np

""" trend indicatiors """
class trend:
    def __init__(self):
        pass



""" momentum indicators """
class momentum:
    def __init__(self):
        pass

    def EMA(self,price,length):
        pass

    def movingAverage(self,price,length):
        """
        :param price: price list
        :param length:the days for calculating moving average
        :return:moving average
        """
        ave = pd.stats.moments.rolling_mean(price,length)
        return ave

    def MACD(self):
        pass

""" volatility indicators """
class volatility:
    def __init__(self):
        pass

    def bollingerBand(self,price, length, numsd=2):
        """
        :param price: the price list
        :param length: the days for calculating moving average
        :param numsd: define the upper and lower band
        :return: moving average, upband, lowband
        """
        ave = price.rolling(window=length,center=False).mean()
        sd = price.rolling(window=length,center=False).std()
        upband = ave + (sd*numsd)
        dnband = ave - (sd*numsd)
        return ave , upband,dnband
