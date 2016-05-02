"""
Different type of signals: Buy, Sell
"""

def Buy(code, df, i):
    signal = [code, df.loc[i, 'Date'], 'Buy', df.loc[i, 'Close']]
    return signal

def Sell(code, df, i):
    signal = [code, df.loc[i, 'Date'], 'Sell', df.loc[i, 'Close']]
    return signal

def crossOver(i, price, upBand):
    if (price.loc[i,'Close'] > upBand[i] and price.loc[i-1,'Close'] < upBand[i-1]):
        return True
    else:
        return False

def crossDown(i,price, downBand):
    if (price.loc[i,'Close'] < downBand[i] and price.loc[i-1,'Close'] > downBand[i-1]):
        return True
    else:
        return False