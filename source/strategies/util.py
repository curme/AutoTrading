

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
