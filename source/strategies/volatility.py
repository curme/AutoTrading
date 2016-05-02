import pandas as pd
import talib as tl
import numpy as np
from talib import MA_Type

from source.data.indicators import volatility
from source.data.preprocessing import Data

#dataPre

if __name__ == "__main__":

    dt = Data()
    vl = volatility()
    df = dt.getExcelInterval(pd.Timestamp("2015-10-26 16:00:00"),pd.Timestamp("2016-03-26 16:00:00"))

    ave,upband,dnband = vl.bollingerBand(df['Close'],30)

    #print type(df['Close'].values)
    #print list( df['Close'].values)
    dt_array = list( df['Close'].values)
    float_array = [float(x) for x in dt_array]
    upband1,ave1, dnband1 = tl.BBANDS(np.array(float_array), timeperiod=30,  nbdevup=2, nbdevdn=2, matype=0)
    # print upband[50],ave[100], dnband[150]
    # print "---------------------------"
    # print upband1[50],ave1[100], dnband1[150]

    signals = []
    # print df.loc[3452,]
    # print len(ave)
    # print len(upband)
    # print len(dnband)
    for i in range(29,len(ave)-1):
        if df.loc[i,'Close'] > upband1[i]:
            signal = ["HSI",df.loc[i,'Date'],df.loc[i,'Close'],"Sell"]
            signals.append(signal)
        if df.loc[i,'Close'] < dnband1[i]:
            signal = ["HSI",df.loc[i,'Date'],df.loc[i,'Close'],"Buy"]
            signals.append(signal)
    signals = pd.DataFrame(signals)
    print signals


