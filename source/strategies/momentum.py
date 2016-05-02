"""
Momentum Strategy (2-3 Strategies)
"""
from source.data.indicators import volatility, momentum
from source.data.preprocessing import Data

def momentum1(data):
    """
    stochastic & average true range
    :param data: high, low, close
    :return: Buy/Sell
    """
    vl = volatility()
    mo = momentum()
    df = data.getExcelInterval(pd.Timestamp("2015-10-26 16:00:00"),pd.Timestamp("2016-03-26 16:00:00"))
    highprice, lowprice, lastprice = df['High'].values, df['Low'].values, df['Close'].values

    [slowk, slowd] = mo.Stochastic(highprice, lowprice, lastprice, 14,3,3)
    vol = vl.ATR(highprice, lowprice, lastprice, 14)

    signals = []
    for i in df.index:
    	if slowd[i] > 80 and vol[i] > 5:
    		signal = ["HSI",df.loc[i,'Date'], df.loc[i,'Close'],"Sell"]
    	if slowd[i] < 20 and vol[i] < 3:
    		signal = ["HSI",df.loc[i,'Date'], df.loc[i,'Close'],"Buy"]
    	signals.append(signal)
    signals = pd.DataFrame(signals)

    print signals


def momentum2(data):
    pass

def momentum3(data):
    pass


dt = Data()
momentum1(dt)