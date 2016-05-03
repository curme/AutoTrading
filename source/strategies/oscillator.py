import pandas as pd
import talib as tl
import numpy as np
from talib import MA_Type
import matplotlib.pyplot as plt

from source.data.preprocessing import Data
from source.order.action import *
from source.order.tradeBook import tradeBook
import matplotlib.patches as mpatches


def oscillator1(df):
    """
    :param data:
    :return:
    """
    float_close = Data.toFloatArray(df['Close'])
    float_high = Data.toFloatArray(df['High'])
    float_low = Data.toFloatArray(df['Low'])
    float_open = Data.toFloatArray(df['Open'])

    adx_values = tl.ADX(np.array(float_high),np.array(float_low),np.array(float_close), timeperiod = 15)

    aco_values = ACOscillator(df)
    aco_values =np.insert(aco_values, 0,0, axis=0)

    signals = []
    flag = 0

    #plt.plot(df['Date'], aco_values, df['Date'], adx_values, df['Date'],df['Close'] )
    #plt.show()
    ddf = pd.concat([df['Date'], pd.DataFrame(aco_values), pd.DataFrame(adx_values), df['Close']], axis=1)
    ddf.to_csv("ddf2.csv")
    for i in xrange(40 , len(adx_values) - 1):
        if flag ==0:
            if adx_values[i]>20  and aco_values[i]>0:
                signal = ['HSI', df.loc[i, 'Date'], 'Long',  df.loc[i, 'Close']]
                flag =1
                signals.append(signal)
            if adx_values[i]>20  and aco_values[i]<0:
                signal = ['HSI', df.loc[i, 'Date'], 'Short',  df.loc[i, 'Close']]
                flag =2
                signals.append(signal)
        elif flag ==1:
            if df.loc[i, 'Close']>= signal[3]*1.01 or df.loc[i, 'Close']<= signal[3]*0.98:
                signal = ['HSI', df.loc[i, 'Date'], 'Short',  df.loc[i, 'Close']]
                flag = 0
                signals.append(signal)
        elif flag ==2:
            if df.loc[i, 'Close']<= signal[3]*0.99 or df.loc[i, 'Close']>= signal[3]*1.02:
                signal = ['HSI', df.loc[i, 'Date'], 'Long',  df.loc[i, 'Close']]
                flag = 0
                signals.append(signal)


    sig = pd.DataFrame(signals, columns=['Code', 'Time', 'Action',  'Price'])
    print sig
    profits = []
    for k in range(0,len(signals)/2):
        if sig['Action'][k*2] == "Long":
            profit = sig['Price'][k*2+1] - sig['Price'][k*2]
        else:
            profit = sig['Price'][k*2]- sig['Price'][k*2+1]
        profits.append(profit)
    print np.sum(profits)
    print(profits)
    ###### PLOT #######
    longSignals = sig[sig['Action'] == 'Long']
    shortSignals = sig[sig['Action'] == 'Short']
    plt.plot(df['Date'], df['Close'], longSignals['Time'], longSignals['Price'], 'r^', shortSignals['Time'],
             shortSignals['Price'], 'gv', markersize=10)
    red_patch = mpatches.Patch(color='red', label='Long')
    green_patch = mpatches.Patch(color='green', label='Short')
    plt.legend(handles=[red_patch, green_patch])
    plt.grid()
    plt.show()
    ###### PLOT #######


def oscillator2(data):
    pass

def oscillator3(data):
    pass

def ACOscillator(df):
    df_mid_points = (df['High'] + df['Low'])/2
    mid_points = Data.toFloatArray(df_mid_points)
    longav = tl.SMA(np.array(mid_points), timeperiod=40)
    shortav = tl.SMA(np.array(mid_points),timeperiod =15)
    A0 = longav - shortav
    Mavg = tl.SMA(A0, timeperiod = 15)
    AcResult = tl.SMA(Mavg - A0, timeperiod = 15)
    signals = np.diff(AcResult)
    return signals

if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan)
    pd.set_option("display.max_rows", 280)
    dt = Data()
    df = dt.getCSVData()
    #ACOscillator(df)
    oscillator1(df)