"""
Different type of signals: Buy, Sell
"""
from source.money.account import Account
from numpy import nan


def Long(code, df, i):
    qnt = quantity(df, i)
    signal = [code, df.loc[i, 'Date'], 'Buy', qnt, df.loc[i, 'Close'], Account.capital]
    Account.capital -= df.loc[i, 'Close'] * qnt
    return signal

def Short(code, df, i):
    qnt = quantity(df, i)
    signal = [code, df.loc[i, 'Date'], 'Sell', qnt, df.loc[i, 'Close'], Account.capital]
    Account.capital += df.loc[i, 'Close'] * qnt
    return signal

def quantity(df, i):
    # if Account.capital >= df['Close']:
    qnt = int(Account.capital / df.loc[i, 'Close'])
    return qnt

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
