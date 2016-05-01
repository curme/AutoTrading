"""
Finance data preprocessing
"""
import pandas as pd

def getExcelData():
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
    return df

def getAPIData():
    pass