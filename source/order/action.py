"""
Different type of signals: Buy, Sell
"""

def Buy(code, df, i):
    signal = [code, df.loc[i, 'Date'], 'Buy', df.loc[i, 'Close']]
    return signal

def Sell(code, df, i):
    signal = [code, df.loc[i, 'Date'], 'Sell', df.loc[i, 'Close']]
    return signal

