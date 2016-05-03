"""
Finance data preprocessing
"""
import pandas as pd
import xlrd

class Data:

    def __init__(self):
        #self.df = self.getExcelData()
        self.df = self.getCSVData()
        pass
    def getCSVData(self):
        df = pd.read_csv("../data/hsi_futures_dec.csv")
        df['Date'] = pd.to_datetime(df['Date'],format='%d/%m/%Y %H:%M')
        df.sort_values("Date", ascending= True, inplace=True)
        data = df.set_index([range(df.shape[0])])
        return data

    def getExcelData(self):
        """
        get data from 'hsi_futures.xlsx'
        Date | Open | High | Low | Close | SMAVG5 | SMAVG10 | SMAVG15 | Volume | VolumeSMAVG5
        :return: data table
        """
        df = pd.DataFrame()
        xl = pd.ExcelFile("../data/hsi_futures.xlsx")
        #print xl.sheet_names
        sheets = xl.sheet_names
        for sheet in sheets:
            df = df.append(pd.read_excel("../data/hsi_futures.xlsx", sheet))

        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values("Date", ascending= True, inplace=True)

        data = df.set_index([range(df.shape[0])])
        return data

    def getExcelInterval(self, start, end):
        """
        Includes both start and end
        :param start    : start date (e.g start = '2016-01-26 14:45:00')
        :param end      : end date (e.g end = '2016-02-26 14:45:00')
        :return         : data between start and end
        """

        interval = (self.df['Date'] >= start) & (self.df['Date'] <= end)
        _df = self.df.loc[interval]
        data = _df.set_index([range(_df.shape[0])])
        return data

    def getAPIData(self):
        pass

    @staticmethod
    def toFloatArray(df):
        dt_array = list(df.values)
        float_array = map(float, dt_array)
        return float_array



# d = Data()
# inte = d.getExcelInterval('2016-01-26 14:45:00', '2016-02-26 16:00:00')
# print inte