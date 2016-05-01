"""
Indicators will be used to trigger strategies
---------------------------------------------------------
Type        |Examples
---------------------------------------------------------
Trend       |Moving Average, MACD, Parabolic SAR
Momentum    |Stochastic, CCI, RSI
Volatility  |Bollinger Band, Average True Range, Std
Volume      |Chaikin Oscillator, OBV, Rate of Change(ROV)
---------------------------------------------------------
"""

import pandas as pd
import numpy as np

""" momentum indicators """
class momentum:
    def __init__(self):
        pass

    def movingAverage(self):
        pass

    def MACD(self):
        pass

""" volatility indicators """
class volatility:
    def __init__(self):
        pass

    def bollingerBand(self,price, length=30, numsd=2):
        """ returns average, upper band, and lower band"""
        ave = pd.stats.moments.rolling_mean(price,length)
        sd = pd.stats.moments.rolling_std(price,length)
        upband = ave + (sd*numsd)
        dnband = ave - (sd*numsd)
        return np.round(ave,3), np.round(upband,3), np.round(dnband,3)

