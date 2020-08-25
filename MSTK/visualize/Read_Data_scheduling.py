#-*-coding:utf-8-*-

import numpy as np
import pandas as pd
import csv
from parse import parse
import math
from datetime import datetime, timedelta

data_year = 2020
file_name = 'DATA_20200716/IPS_20200706.xlsx'
period = 7

def readFile(filename, sheet):
    df = pd.read_excel(filename, header = [0,1], sheet_name = sheet)
    return df

def fillNanIndex(df, Index):
    df_fill = df[Index]
    df_fill = df_fill.fillna(method = 'ffill')
    df[Index] = df_fill
    return df

def readIndex(df, i, col):
    return df[df.columns[col][0], df.columns[col][1]][i]

def readValue(df, i, j, col):
    return df[df.columns[5*j+col][0], df.columns[5*j+col][1]][i]

def setDateTime(dateString, timeString):
    parseResult = 0

    parseResult = parse("{}월 {}일",dateString)
    Month = int(parseResult[0])
    Day = int(parseResult[1])

    parseResult = parse("{}:{}", timeString)
    Hour = int(parseResult[0])
    Minute = int(parseResult[1])
    Result = datetime(data_year, Month, Day, Hour, Minute)
    return Result

def readLine(df, i, j):
    Plant = readIndex(df,i,1)
    Oper = readIndex(df,i,2)
    Resource = readIndex(df,i,3)
    Date = df.columns[5*j+5][0]
    ST = readValue(df,i,j,5)
    ET = readValue(df,i,j,6)
    Item = int(readValue(df,i,j,7))
    Qty = readValue(df,i,j,8)
    UoM = readValue(df,i,j,9)
    ST = setDateTime(Date, ST)
    ET = setDateTime(Date, ET)
    if ET < ST:
        ET = ET + timedelta(days = 1)
    Line = np.array([Resource, ST, ET, Item])
    return Line

def readPandas(df, df_use, size, period):
    count = 0

    for j in range(period):
        for i in range(size):
            if df[df.columns[5*j+5][0], df.columns[5*j+5][1]][i] == df[df.columns[5*j+5][0], df.columns[5*j+5][1]][i]:
                #nan check
                df_use.loc[count,:] = readLine(df,i,j)
                count = count + 1
    return df_use

def main():
    df = readFile(file_name, "Sheet 1")
    df = fillNanIndex(df, ['Plant', 'Oper ID', '설비 ID'])
    size = len(df)

    df_use = pd.DataFrame(index = range(1), columns = ['Resource_ID', 'Starting Time', 'End Time', 'Item'])
    df_use = readPandas(df, df_use, size, period)
    # print(df_use)
    df_use.to_csv('test_scheduling.csv')
    return df_use

if __name__ == "__main__":
    print("Run Read_Data.py")
    main()