import pandas as pd
import numpy as np
from source.data.preprocessing import Data
from source.data.indicators import volatility

#dataPre

if __name__ == "__main__":

    dt = Data()
    vl = volatility()
    df = dt.getExcelInterval(pd.Timestamp("2015-10-26 16:00:00"),pd.Timestamp("2016-03-26 16:00:00"))
    ave,upband,dnband = vl.bollingerBand(df['Close'],30)
    signals = pd.DataFrame()
    print df.loc[30,'Close']
    for i in range(29,len(ave)):
        if df.loc[i,'Close'] > upband[i]:
            signal = ["HSI",df.loc[i,'Date'],df.loc[i,'Close'],"Sell"]
        if df.ix[i,'Close'] < dnband[i]:
            signal = ["HSI",df.loc[i,'Date'],df.loc[i,'Close'],"Buy"]
        signals.append(signal)
    print signals

