"""
Finance data preprocessing
"""
import pandas as pd
import xlrd

class Data:

    def __init__(self):
        self.df = self.getExcelData()
        pass

    def getExcelData(self):
        """
        get data from 'hsi_futures.xlsx'
        Date | Open | High | Low | Close | SMAVG5 | SMAVG10 | SMAVG15 | Volume | VolumeSMAVG5
        :return: data table
        """
        df = pd.DataFrame()
        xl = pd.ExcelFile("hsi_futures.xlsx")
        print xl.sheet_names
        sheets = xl.sheet_names
        for sheet in sheets:
            df = df.append(pd.read_excel("hsi_futures.xlsx", sheet))

        df['Date'] = pd.to_datetime(df['Date'])
        return df

    def getExcelInterval(self, start, end):
        """
        :param data:
        :param start:
        :param end:
        :return:
        """
        interval = (self.df['Date'] >= start) & (self.df['Date'] <= end)
        return self.df.loc[interval]

    def getAPIData(self):
        pass


# d = Data()
# inte = d.getExcelInterval('2016-01-26 14:45:00', '2016-02-26 16:00:00')
# print inte