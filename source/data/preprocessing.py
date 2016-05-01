from openpyxl import load_workbook
import numpy as np
import pandas as pd
import xlrd
import glob, os


df = pd.DataFrame()
xl = pd.ExcelFile("hsi_futures.xlsx")
# Date | Open | High | Low | Close | SMAVG5 | SMAVG10 | SMAVG15 | Volume | VolumeSMAVG5
print xl.sheet_names
sheets = xl.sheet_names
for sheet in sheets:
    df = df.append(pd.read_excel("hsi_futures.xlsx", sheet))
print df.ix[0, "Date"]
