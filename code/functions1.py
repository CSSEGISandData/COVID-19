# -*- coding: utf-8 -*-
# @Author: lily
# @Date:   2020-04-04 15:05:37
# @Last Modified by:   lily
# @Last Modified time: 2020-04-25 17:11:31
import io, os, sys, types, pickle, warnings
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import scipy.optimize as opt
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import colors as mcolors
import matplotlib.pylab as pl

import seaborn as sns

warnings.filterwarnings('ignore')

master_path = os.getcwd()
if master_path not in sys.path:
    sys.path.append(master_path)


""" Params """
cat_color = {'Confirmed':'tab:blue', 
              'Deaths':'tab:orange', 
              'Recovered':'tab:green', 
              'Active':'tab:red', 
              'Positive':'tab:purple', 
              'Negative':'tab:olive', 
              'Democratic':'tab:blue', 
              'Republican':'tab:red',
              'Independent':'tab:green'}
cdra_cols = ['Confirmed', 'Deaths', 'Recovered', 'Active']
pn_cols = ['Positive', 'Negative']
party_cols = ['Democratic', 'Republican', 'Independent']

SMALL_SIZE = 10
MEDIUM_SIZE = 12
BIGGER_SIZE = 16
MILLION = 1000000
locator_param = 6

######### data acquisition #########
### get lists of subfolders and files of a given path.
def parse_folder_info(path):
    folders = [f for f in os.listdir(path) if not os.path.isfile(os.path.join(path, f))]
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if('.DS_Store' in files):
        files.remove('.DS_Store')
    if('._.DS_Store' in files):
        files.remove('._.DS_Store')
    return folders, files

def get_file_paths(path):
    file_paths = []
    folders, files = parse_folder_info(path)
    if not files:
        for folder in folders:
            paths = get_file_paths(os.path.join(path, folder))
            file_paths = file_paths + paths
    else:
        for file in files:
            file_paths = file_paths + [str(os.path.join(path, file))]
    return file_paths

### get intersection of two lists
def intersection(list1, list2):
    return set(list1).intersection(list2)

### get time columns as string list and datetime list
def get_time_columns(columns):
    time_str = []
    time_datetime = []
    for col in columns:
        if col[0].isnumeric():
            time_str.append(col)
            time_datetime.append(datetime.strptime(col, '%m/%d/%y'))
    return time_str, time_datetime

### reformat time columns to datetime format
def reformat_time(df):
    time_str, time_datetime = get_time_columns(df.columns)
    times_dic = {}
    for i, time in enumerate(time_str):
        times_dic[time] = time_datetime[i]
    return df.rename(columns = times_dic)

### get numpy array of datetime arange
def get_datetime_arange(start, n):
    return np.arange(start, start + timedelta(days=n), timedelta(days=1)).astype(datetime)

######### data fitting #########
### exponential growth function
def exp_growth(t, r, x0):
    return x0 * (1 + r) ** t

### logistic growth function
def logistic_growth(t, r, K, P0):
    return K / (1 + (K - P0)/P0 * np.exp(-r*t))

### getting R^2
def get_r_squared(x, y, popt, func):
    if(func == 'exp_growth'):
        y_fit = exp_growth(x, *popt)
    elif(func == 'logistic_growth'):
        y_fit = logistic_growth(x, *popt)
    residuals = y - y_fit
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y-np.mean(y))**2)
    r_squared = 1 - (ss_res / ss_tot)
    return r_squared


######### data processing #########
### reshape dataframe so that the index is the dates and the columns are the relative values. better for rolling.
def reshape_dataframe(df, time_str, **kwarg):
    if('Population' in kwarg.keys()):
        population = kwarg['Population']
    else:
        population = 1
    if('Confirmed' in df.index):
        df_new = df.transpose().copy(deep=True)
        df_new.rename_axis('Date', axis = 'columns', inplace = True)
        if('Recovered' in df.index):
            df_new['Active'] = df_new['Confirmed'] - (df_new['Deaths'] + df_new['Recovered'])
            df_new['CFR'] = df_new['Deaths']/df_new['Confirmed'] * 100
            df_new['Recovered_prop'] = df_new.Recovered/(df_new.Deaths + df_new.Recovered) * 100
            df_new['Death_prop'] = df_new.Deaths/(df_new.Deaths + df_new.Recovered) * 100
        else:
            df_new['CFR'] = df_new['Deaths']/df_new['Confirmed'] * 100
        df_new['Population'] = population
        df_new['Daily_Confirmed'] = df_new['Confirmed'].diff()
        df_new['Daily_Deaths'] = df_new['Deaths'].diff()
        df_new['Daily_Confirmed_smoothed'] = df_new.Daily_Confirmed.rolling(window = 2).mean()
        df_new['Daily_Deaths_smoothed'] = df_new.Daily_Deaths.rolling(window = 2).mean()
        df_new.loc[time_str[2:],'GFc'] = np.divide(df_new.loc[time_str[2:],'Daily_Confirmed'].to_list(), df_new.loc[time_str[1:-1],'Daily_Confirmed'].to_list())
        df_new.loc[time_str[2:],'GFd'] = np.divide(df_new.loc[time_str[2:],'Daily_Deaths'].to_list(), df_new.loc[time_str[1:-1],'Daily_Deaths'].to_list())
        df_new['GFc_thr'] = df_new.GFc.rolling(window = 3).mean()
        df_new['GFd_thr'] = df_new.GFd.rolling(window = 3).mean()
        df_new[~np.isfinite(df_new)] = 0
        df_new.loc[time_str[2:],'GFc_rolling'] = np.divide(df_new.loc[time_str[2:],'Daily_Confirmed_smoothed'].to_list(), df_new.loc[time_str[1:-1],'Daily_Confirmed_smoothed'].to_list())
        df_new.loc[time_str[2:],'GFd_rolling'] = np.divide(df_new.loc[time_str[2:],'Daily_Deaths_smoothed'].to_list(), df_new.loc[time_str[1:-1],'Daily_Deaths_smoothed'].to_list())
        df_new[~np.isfinite(df_new)] = 0
    else:
        df_new = df.copy(deep = True)
        df_new.rename(columns = {df_new.columns[0]:'Confirmed'}, inplace = True)
        df_new.rename_axis('Date', inplace = True)
        df_new['Daily'] = df_new['Confirmed'].diff()
        df_new['Daily_smoothed'] = df_new.Daily.rolling(window = 2).mean()
        df_new.loc[time_str[2:],'GF'] = np.divide(df_new.loc[time_str[2:],'Daily'].to_list(), df_new.loc[time_str[1:-1],'Daily'].to_list())
        df_new['GF_rolling_thr'] = df_new.GF.rolling(window = 3).mean()
        df_new[~np.isfinite(df_new)] = 0
        df_new.loc[time_str[2:],'GF_rolling'] = np.divide(df_new.loc[time_str[2:],'Daily_smoothed'].to_list(), df_new.loc[time_str[1:-1],'Daily_smoothed'].to_list())
        df_new[~np.isfinite(df_new)] = 0
    return df_new

def reshape_dataframe_v2(df_confirmed, df_deaths, df_population, time_datetime):
    df_confirmed['New_Today'] = df_confirmed[time_datetime[-1]] - df_confirmed[time_datetime[-2]]
    df_deaths['New_Today'] = df_deaths[time_datetime[-1]] - df_deaths[time_datetime[-2]]
    df_confirmed['Population'] = df_population
    df_deaths['Population'] = df_population
    df_confirmed['Per_Million'] = df_confirmed.loc[:,time_datetime[-1]] / (df_confirmed['Population']/MILLION)
    df_deaths['Per_Million'] = df_deaths.loc[:,time_datetime[-1]] / (df_deaths['Population']/MILLION)
    df_confirmed['GF_today'] = (df_confirmed[time_datetime[-2]] - df_confirmed[time_datetime[-1]])/(df_confirmed[time_datetime[-3]] - df_confirmed[time_datetime[-2]])
    df_deaths['GF_today'] = (df_deaths[time_datetime[-2]] - df_deaths[time_datetime[-1]])/(df_deaths[time_datetime[-3]] - df_deaths[time_datetime[-2]])
    df_confirmed[~np.isfinite(df_confirmed)] = 0
    df_deaths[~np.isfinite(df_deaths)] = 0
    return df_confirmed, df_deaths

def consolidate_testing(df_covid_tracking, df_state_stats):
    us_tests_cols = ['State', 'Governer_Affiliation', 'Population', 'positive', 'negative', 'pending', 'hospitalized', 'death', 'totalTestResults']

    df_us_tests = pd.DataFrame(columns = us_tests_cols, index = df_covid_tracking.index)
    cols1 = intersection(us_tests_cols, list(df_covid_tracking.columns))
    cols2 = intersection(us_tests_cols, list(df_state_stats.columns))
    df_us_tests.loc[:,cols1] = df_covid_tracking.loc[:,cols1]
    df_us_tests.loc[:,cols2] = df_state_stats.loc[:,cols2]
    df_us_tests.fillna(0.0, inplace = True)
    df_us_tests.loc[:,'Percent_Pos'] = df_us_tests.positive / df_us_tests.totalTestResults * 100
    df_us_tests.loc[:,'Test_Per_Million'] = df_us_tests.totalTestResults / (df_us_tests.Population/MILLION)
    df_us_tests.fillna(0.0, inplace = True)
    df_us_tests.loc[:,'Pos_Per_Million'] = np.round(df_us_tests.positive/(df_us_tests.Population/MILLION))
    df_us_tests['rank_Percent_Pos'] = df_us_tests['Percent_Pos'].rank(ascending = False)
    df_us_tests['rank_Test_Per_Million'] = df_us_tests['Test_Per_Million'].rank(ascending = False)
    df_us_tests['rank_Pos_Per_Million'] = df_us_tests['Pos_Per_Million'].rank(ascending = False)
    return df_us_tests

def get_df_ctry_today(df_confirmed, df_deaths, df_world_population, time_str):
    df_ctry_today = pd.DataFrame(columns = ['Total_Confirmed', 'New_Confirmed', 'Total_Deaths', 'New_Deaths']+list(df_world_population.columns), 
                                 index = df_confirmed.index)
    today = time_str[-1]
    df_ctry_today['Total_Confirmed'] = df_confirmed[today]
    df_ctry_today['New_Confirmed'] = df_confirmed['New_Today']
    indexis_intersect = intersection(list(df_world_population.index), list(df_confirmed.index))
    df_ctry_today.loc[:,list(df_world_population.columns)] = df_world_population.loc[indexis_intersect,:]
    df_ctry_today['Pos_per_Million'] = df_ctry_today.Total_Confirmed/(df_ctry_today.Population/MILLION)
    df_ctry_today['Total_Deaths'] = df_deaths[today]
    df_ctry_today['New_Deaths'] = df_deaths.loc[:,time_str[-1]] - df_deaths.loc[:,time_str[-2]]
    df_ctry_today.dropna(axis = 0, how = 'any', inplace = True)
    thr = 500
    cat = 'Confirmed_Cat'
    df_ctry_today.loc[df_ctry_today.Total_Confirmed>=thr, cat] = f'above_{thr}'
    df_ctry_today.loc[df_ctry_today.Total_Confirmed<thr, cat] = f'below_{thr}'
    thr = np.percentile(df_ctry_today.Population, 50)
    cat = 'Population_Cat'
    df_ctry_today.loc[df_ctry_today.Population>=thr, cat] = f'above_{thr/MILLION:.1f}M'
    df_ctry_today.loc[df_ctry_today.Population<thr, cat] = f'below_{thr/MILLION:.1f}M'
    return df_ctry_today