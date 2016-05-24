"""
Finance data preprocessing
"""
import pandas as pd
import os, sys

# import xlrd
DATA_PATH = "./dataManager"


class DataManager:
    def __init__(self):
        # self.df = self.getExcelData()
        # self.df = self.getCSVData()
        pass

    def getAssetList(self, path=DATA_PATH):
        subdirectories = os.listdir(path)
        name_list = []
        for subDir in subdirectories:
            file_paths = self.get_filepaths(path+'/'+subDir)
            for file_path in file_paths:
                file_name = file_path.split("/")
                asset = file_name[-1].split('.csv')
                name_list.append(asset[0])
        return name_list

    def getCSVData(self, name="hsi_futures_jan"):
        file_path = self.find(name + ".csv", DATA_PATH)
        df = pd.read_csv(file_path)
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        self.df = df
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M')
        df.sort_values("Date", ascending=True, inplace=True)
        data = df.set_index([range(df.shape[0])])
        return data

    def getMultipelDataframe(self, name="comdty"):
        file_paths = self.get_filepaths("../dataManager/data/" + name)
        dfs = {}
        for file_path in file_paths:
            df = pd.read_csv(file_path)
            df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            file_name = file_path.split("/")
            asset = file_name[4].split('.csv')
            dfs[asset[0]] = df
        self.dfs = dfs
        return dfs

    def getExcelData(self):
        """
        get data from 'hsi_futures.xlsx'
        Date | Open | High | Low | Close | SMAVG5 | SMAVG10 | SMAVG15 | Volume | VolumeSMAVG5
        :return: data table
        """
        df = pd.DataFrame()
        xl = pd.ExcelFile("../dataManager/hsi_futures.xlsx")
        # print xl.sheet_names
        sheets = xl.sheet_names
        for sheet in sheets:
            df = df.append(pd.read_excel("../dataManager/hsi_futures.xlsx", sheet))
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values("Date", ascending=True, inplace=True)
        data = df.set_index([range(df.shape[0])])
        return data

    def getDataOfDate(self, date_time):
        idx = (self.df['Date'] == date_time)
        data = self.df.loc[idx]
        return data

    def getMultipleDataOfDate(self, date_time):
        subDFs = {}
        for idx in self.dfs:
            df = self.dfs[idx]
            dd = (df['Date'] == date_time)
            _df = df.loc[dd]
            subDFs[idx] = _df
        return subDFs

    def getMultipleDataInterval(self, start, end):
        subDFs = {}
        for idx in self.dfs:
            df = self.dfs[idx]
            dd = (df['Date'] >= start) & (self.df['Date'] <= end)
            _df = df.loc[dd]
            subDFs[idx] = _df
        return

    def getInterval(self, start, end):
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

    def get_filepaths(self, directory):
        file_paths = []  # List which will store all of the full filepaths.
        for root, directories, files in os.walk(directory):
            for filename in files:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)  # Add it to the list.
        return file_paths  # Self-explanatory.

    def find(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

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
