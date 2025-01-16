#!/usr/bin/env python3


import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge as ridge
from sklearn.metrics import mean_absolute_error as mae

global LOC
LOC = '/home/bkelley/capstone'

# generates predictions for data except first 5 years
def backtest(data, model, predictors, start=365*5, step=70):
    all_pred = []
    for i in range(start, data.shape[0], step):
        train = data.iloc[:i, :]  # all rows up to i
        test = data.iloc[i:(i+step),:]  # takes next step days to make predicitons on
        model.fit(train[predictors], train['target'])
        preds = model.predict(test[predictors])
        preds = pd.Series(preds, index=test.index)
        combined = pd.concat([test['target'], preds], axis=1)
        combined.columns = ['actual', 'prediciton']
        combined['diff'] = (combined['prediciton'] - combined['actual']).abs()
        all_pred.append(combined)
    return pd.concat(all_pred)


def pct_diff(old, new):
    return (new - old) / old

def compute_rolling(data, horizion, col):
    label = f"rolling_{horizion}_{col}"
    data[label] = data[col].rolling(horizion).mean()
    data[f"{label}_pct"] = pct_diff(data[label], data[col])
    return data


def expand_mean(data):
    return data.expanding(1).mean()


if __name__ == "__main__":
    # read in data
    data = pd.read_csv(f"{LOC}/test_data/Hampton.csv", index_col="DATE")
    # Number of rows with null values 
    null_pct = data.apply(pd.isnull).sum()/data.shape[0]
    # remove columns where null % is low
    valid_columns = data.columns[null_pct < 0.05]
    # Assing data with only valid
    data = data[valid_columns].copy()
    # lowercase header names
    data.columns = data.columns.str.lower()
    # fill in missing data with last known value
    data = data.ffill()
    # convert index to pandas datetime
    data.index = pd.to_datetime(data.index)
    # check for gaps in year
    gaps = data.index.year.value_counts().sort_index()  # NOTE LARGE GAP 2008
    # ML TIME
    '''
    What Im trying to predict with this specific data set is the next days
    percipitation
    '''
    # set target (next days data)
    data['target'] = data.shift(-1)['prcp']
    # Use ffill again for most current row (as its nan)
    data = data.ffill()
    # CHECK for colinearlity (data / column dependent) 
    cc = data[['prcp', 'target']].corr()
    # Ridge regression time alpha will change most likely def = .1
    rr = ridge(alpha=.1)
    predictors = data.columns[~data.columns.isin(['target', 'name', 'station', 'prcp_attributes'])]
    # TIME For backtest 
    # DEBUG 
    data = data.drop('prcp_attributes', axis=1)  # ALL null, remove
    predictions = backtest(data, rr, predictors)
    # generate accuracy metric mean absoulte error
    mean_abs_error = mae(predictions['actual'], predictions['prediciton'])
    # HUGE ERROR, percipitation is not typcially time series dpenedent on a daily basis
    # print(mean_abs_error)
    rolling_horizion = [3, 14]
    #     col = ['prcp']
    for horiz in rolling_horizion:
        data = compute_rolling(data, horiz, 'prcp')
    # Get rid of first 14 days as we dont have the previous 14 to those
    data = data.iloc[14:, :]
    # Fill out NAN from pct column with 0's (cant divide by zero so pandas says NA
    data = data.fillna(0)
    # expanding mean
    for col in ['prcp']:
        data[f"month_avg_{col}"] = data[col].groupby(data.index.month, group_keys=False).apply(expand_mean)
        data[f"day_avg_{col}"] = data[col].groupby(data.index.day_of_year, group_keys=False).apply(expand_mean)
    # Rerun predictors, grab new columns and perform backtest
    predictors = data.columns[~data.columns.isin(['target', 'name', 'station', 'prcp_attributes'])]
    predictions = backtest(data, rr, predictors)
    mean_abs_error = mae(predictions['actual'], predictions['prediciton'])
    # print(mean_abs_error)
    # BAREYLY MADE A DIFF
    # Find the amount of time diff occured and
    # predictions['diff'].round().value_counts().sort_index().plot()
    # To improve accuracy
    #   Add in more predictor columns (need more data duhh)
    #   Look at different rolling horizions
    #   Change model use xxgboost or random forest 


