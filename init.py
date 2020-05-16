'''
This file contains functions for reading CSV file, preprocessing,
and the calculation for expected return and covariance matrix

Each asset is assigned a number by its order in C_Fund_Summary_Final.csv
'''
import numpy as np
import pandas as pd

DATA_FILENAME = "C_Fund_Return_Final.csv"
# This file was initially GB2312, I have changed it to utf-8
SUMMARY_FILENAME = "C_Fund_Summary_Final.csv"

dataTable = None
summaryTable = None
assetsList = None
asset_to_num = None
NUM = 57 # number of all available assets
DAY_LIM = 4000 # number of all available dates, infact, the precise number is 3640

def read_CSV():
    global dataTable, summaryTable
    dataTable = pd.read_csv(DATA_FILENAME)
    summaryTable = pd.read_csv(SUMMARY_FILENAME, encoding="utf-8")
    # print(dataTable)
    return dataTable, summaryTable

# build the mapping between Symbol and number
def getAssetsList():
    global assetsList, asset_to_num
    assetsList = summaryTable["Symbol"]
    asset_to_num = {}
    for i in range(len(assetsList)):
        asset_to_num[assetsList[i]] = i
    # print(asset_to_num)
    return assetsList, asset_to_num

'''
def date_to_int(str_1):
    date_1 = str_1.split("/")
    return int(date_1[0]) * 400 + int(date_1[1]) * 31 + int(date_1[2])
'''

# preprocess the date, calculate the available start date and the end date of each asset
# also check whether the data is continuous for each asset
start_date = np.zeros(NUM, np.int)
end_date = np.zeros(NUM, np.int)
close_price = np.zeros((NUM, DAY_LIM))

def preprocess():
    global start_date, end_date, close_price
    # First parse: get all dates and then sort them, and finally renumber the date
    all_dates = []
    date_to_num = {}
    for i in range(dataTable.shape[0]):
        this_line = dataTable.iloc[i]
        this_day = this_line["TradingDate"]
        if this_day not in date_to_num:
            date_to_num[this_day] = 1
            all_dates.append(this_day)
    all_dates = sorted(all_dates)
    # print(len(all_dates))
    # print(all_dates)
    for i in range(len(all_dates)):
        date_to_num[all_dates[i]] = i+1 # avoid the case of 0

    # Second parse: get the close_price, start_date and end_date array
    for i in range(dataTable.shape[0]):
        this_line = dataTable.iloc[i]
        this_day = date_to_num[this_line["TradingDate"]]
        this_asset = asset_to_num[this_line["Symbol"]]
        close_price[this_asset][this_day] = this_line["ClosePrice"]

        # the data is monotone in date for one asset, so the following code is correct
        if start_date[this_asset] == 0:
            start_date[this_asset] = this_day
        end_date[this_asset] = this_day

    # print(start_date)
    # print(end_date)
    # print(close_price)
    return

# This function calculate the cov matrix.
# Make sure that for each pair of asset, the cov is only calculated on the date when their data are both available
def calcCovMatrix():
    cov_matrix = np.zeros((NUM, NUM))
    corr_matrix = np.zeros((NUM, NUM))
    for i in range(NUM):
        for j in range(NUM):
            L = max((start_date[i], start_date[j]))
            R = min((end_date[i], end_date[j]))
            if L > R:
                cov_matrix[i][j] = 0
                corr_matrix[i][j] = 0
            else:
                data_i = close_price[i][L:R+1]
                data_j = close_price[j][L:R+1]
                # print(data_i.shape)
                # print(data_j)
                cov_22 = np.cov(data_i, data_j) # 2*2 covariance matrix
                cov_matrix[i][j] = cov_22[0][1]
                if np.fabs(cov_22[0][0]) > 1e-5 and np.fabs(cov_22[1][1]) > 1e-5:
                    corr_matrix[i][j] = cov_22[0][1] / np.sqrt(cov_22[0][0] * cov_22[1][1]) # a little bit faster
                    # corr_matrix[i][j] = np.corrcoef(data_i, data_j)[0][1]
                else: # otherwise, it may divide zero
                    corr_matrix[i][j] = 0
    print(corr_matrix)
    return cov_matrix, corr_matrix

# This is the most TRIVIAL one for expected return from historical data
# If you want to implement a new one, just write a new function below, and then change main.py
# Just (price_in_the_end - price_in_the_first) / price_in_the_first
def calcExpectedReturn_1():
    exp_return = np.zeros(NUM)
    for i in range(NUM):
        exp_return[i] = (close_price[i][end_date[i]] - close_price[i][start_date[i]]) / close_price[i][start_date[i]]
    # print(exp_return)
    return exp_return
