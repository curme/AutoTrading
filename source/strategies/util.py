from source.data.preprocessing import Data
import statistics as stat


def crossOver(i, price, upBand):
    if (price.loc[i,'Close'] > upBand[i] and price.loc[i-1,'Close'] < upBand[i-1]):
        return True
    else:
        return False

def crossDown(i, price, downBand):
    if (price.loc[i,'Close'] < downBand[i] and price.loc[i-1,'Close'] > downBand[i-1]):
        return True
    else:
        return False

def maxDrawDown(df):
    price = df['Close'].tolist()
    mdd = 0
    peak = price[0]
    for p in price:
        if p > peak : peak = p
        dd = (peak - p)
        if dd > mdd : mdd = dd
    return mdd

def volatility(df):
    price = df['Close'].tolist()
    vol = stat.stdev(price)
    return vol


if __name__ == "__main__":
    dt = Data()
    df = dt.getCSVData()
    print df
    mdd = maxDrawDown(df)
    print mdd