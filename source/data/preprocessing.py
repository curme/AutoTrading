"""
Finance data preprocessing
"""
import pandas as pd
import xlrd
import os

class Data:

    def __init__(self):
        self.df = self.getExcelData()
        #self.df = self.getTxtData()
        pass

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


    def getTxtData(self):
        """
        get data from folder "hkex stocks"
        Date | Open | High | Low | Close | OpenInt
        :return: data dictionary, values are tables
        """
        data = {}
        path = "../data/hkex stocks/"
        fileList = os.listdir(path)
        for f in fileList:
            stockid = f.split('.')[0]
            try:
                df = pd.read_csv(path+f, parse_dates=[['Date', 'Time']])
                df = df.rename(columns = {'Date_Time':'Date'})
                df = df.set_index([range(df.shape[0])])
                data[stockid] = df
            except:
                continue
        return data

    def getTxtInterval(self, name, start, end):
        interval = (self.df[name]['Date'] >= start) & (self.df[name]['Date'] <= end)
        d = self.df[name].loc[interval].copy()
        d = d.set_index([range(d.shape[0])])
        return d

    def getStocknames(self):
        return [key for key in self.df]

'''
EXCEL DATA TEST
'''
# d = Data()
# inte = d.getExcelInterval('2016-01-26 14:45:00', '2016-02-26 16:00:00')
# print inte

'''
TXT DATA TEST
'''
# d = Data()
# name = d.getStocknames()
# for n in name:
#     if name.index(n) < 10:
#         print n+': '
#         print d.getTxtInterval(n, '2016-03-27 14:45:00', '2016-04-03 16:00:00')