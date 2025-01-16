#!/usr/bin/env python3
import pandas as pd

global noaa, zephyr
noaa = '/home/bkelley/capstone/data_collection/weather/data/NOAA_forecast.csv'
zephyr = '/home/bkelley/capstone/data_collection/weather/data/model_forecast.csv'


def get_diff(noaa, zephyr):
    dfn = pd.read_csv(noaa, index_col=False)
    dfz = pd.read_csv(zephyr, index_col=False)
    dfn.set_index('date', inplace=True)
    dfz.set_index('date', inplace=True)
    # print(dfn)
    dfn.drop('Unnamed: 0', axis=1, inplace=True)
    dfz.drop('Unnamed: 0', axis=1, inplace=True)
    # 2 DF with same headers, grab all matching dates
    # Will subtract the noaa pred with my pred
    common_dates = dfz.index.intersection(dfn.index)
    # filter
    dfz_c = dfz.loc[common_dates]
    dfn_c = dfn.loc[common_dates]
    df_diff = dfz_c.subtract(dfn_c)
    # print(df_diff)
    column_averages = df_diff.mean()
    avg = column_averages.mean()
    print(avg)

if __name__=="__main__":
    get_diff(noaa, zephyr)
