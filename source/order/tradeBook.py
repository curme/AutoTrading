import pandas as pd

class tradeBook:
    def __init__(self):
        pass

    @staticmethod
    def simpleBook(signals):
        sig = pd.DataFrame(signals, columns=['Code', 'Time', 'Action', 'Price'])
        return sig