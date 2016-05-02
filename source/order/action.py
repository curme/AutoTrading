"""
Different type of signals: Buy, Sell
"""
from source.money.account import Account
from numpy import nan


def Long(code, df, i):
    signal = []
    # cover the short position first
    if len(Account.position) != 0 and Account.position[0][2] == 'Short':
        signal.append(BuyToCover(code, df, i))
    # trade quantity
    qnt = quantity(df, i)
    # change capital
    Account.capital -= df.loc[i, 'Close'] * qnt
    # generate signal
    signalLong = [code, df.loc[i, 'Date'], 'Long', qnt, df.loc[i, 'Close'], Account.capital]
    signal.append(signalLong)
    # add position
    Account.position.append(signalLong)
    return signal

def Short(code, df, i):
    signal = []
    # cover the long position first
    if len(Account.position) != 0 and Account.position[0][2] == 'Long':
        signal.append(SellToCover(code, df, i))
    # trade quantity
    qnt = quantity(df, i)
    # change capital
    Account.capital += df.loc[i, 'Close'] * qnt
    # generate signal
    signalShort = [code, df.loc[i, 'Date'], 'Short', qnt, df.loc[i, 'Close'], Account.capital]
    signal.append(signalShort)
    # add position
    Account.position.append(signalShort)
    return signal

def SellToCover(code, df, i):
    # row[3] is quantity
    coverQnt = sum(row[3] for row in Account.position)
    Account.position = []
    # change capital
    Account.capital += df.loc[i, 'Close'] * coverQnt
    # generate signal
    signal = [code, df.loc[i, 'Date'], 'SellToCover', coverQnt, df.loc[i, 'Close'], Account.capital]
    return signal


def BuyToCover(code, df, i):
    # row[3] is quantity
    coverQnt = sum(row[3] for row in Account.position)
    Account.position = []
    # change capital
    Account.capital -= df.loc[i, 'Close'] * coverQnt
    # generate signal
    signal = [code, df.loc[i, 'Date'], 'BuyToCover', coverQnt, df.loc[i, 'Close'], Account.capital]
    return signal


def quantity(df, i):
    # if Account.capital >= df['Close']:
    qnt = int(Account.capital / df.loc[i, 'Close'])
    qnt = 100
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
