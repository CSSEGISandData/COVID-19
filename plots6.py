# -*- coding: utf-8 -*-
# @Author: lily
# @Date:   2020-04-04 17:09:18
# @Last Modified by:   lily
# @Last Modified time: 2020-04-04 18:25:04
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
import functions as my_func

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

"""general functions"""
### Attach a text label above each bar in *rects*, displaying its height.
### source: https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html
def autolabel(rects, ax, str_format):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(str_format.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

### different pct settings when plotting pie plot.
### adapted from: https://stackoverflow.com/questions/6170246/how-do-i-use-matplotlib-autopct
def my_autopct(pct):
    return ('%1.1f%%' % pct) if pct > 2 else ''

def my_autopct_v2(pct):
    return f'{pct*total/100:.0f}({pct:1.1f}%)' if pct > 2 else ''

######## getting colors that seperate the most based on number of colors needed
def get_colors(n_group, **kwarg):
    ######################################################
    ### Function: Return colors based on number of colors and colormap chosen by "choose_cmap" function
    ### input: 
        ### n_group(int): number of colors
        ### kwarg:
            ###'return_type': indicate data type of colors for return. 'hex' for string of hex codes; 'rgba' for numpy array ([r,g,b,a] for each color)
            ###'is_last_grey': indicate whether to set the last color to grey.
    ### output: colors in list of strings or numpy array.
    ######################################################
    ### decompose parameters
    if('return_type' in kwarg.keys()):
        return_type = kwarg['return_type']
    else:
        return_type = 'rgba'
        
    ### n<=8, colormap = Set2
    if(n_group <= 8):
        cmap_list = pl.cm.Set2(np.linspace(0,1,8))
        colors = cmap_list[:n_group]
    ### 8<n<=12, colormap = Set3 w/ grey at last
    elif(n_group > 8 and n_group <= 12):
        cmap_list = pl.cm.Set3(np.linspace(0,1,12))
        cmap_list[[8, 11]] = cmap_list[[11, 8]]
        colors = cmap_list[:n_group]
    ### 12<n<=20, colormap = tab20 w/ greys at last
    elif(n_group > 12 and n_group <= 20):
        cmap_list = pl.cm.tab20(np.linspace(0,1,20))
        cmap_list[[14, 18]] = cmap_list[[18, 14]]
        cmap_list[[15, 19]] = cmap_list[[19, 15]]
        colors = cmap_list[:n_group]
    ### n>20, colormap = gist_ncar
    else:
        cmap = plt.get_cmap('gist_ncar')
        gradient = np.linspace(0, 1, n_group)
        colors = []
        for g in gradient:
            colors.append(cmap(g))
        colors[-1] = [0.7, 0.7, 0.7, 1] # make the last color grey
    if('is_last_grey' in kwarg.keys()):
        if(kwarg['is_last_grey']):
            colors[-1] = [0.7, 0.7, 0.7, 1]
    if(return_type == 'rgba'):
        return colors
    elif(return_type == 'hex'):
        color_hex = []
        for color in colors:
            color_hex.append(matplotlib.colors.to_hex(color, keep_alpha=True))
        return color_hex

"""supporting function for """
def get_logistic_params(t, pt, **kwarg):
    popt_log = np.zeros((3,3))
    if('maxfev' in kwarg.keys()):
        maxfev = kwarg['maxfev']
    else:
        maxfev = 100000
    if('bounds' in kwarg.keys()):
        bounds = kwarg['bounds']
    else:
        bounds = (-np.inf, np.inf)
    if('p0' in kwarg.keys()):
        popt_log[0,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t,  pt, p0 = kwarg['p0'], maxfev = maxfev, bounds = bounds)
        popt_log[1,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-1],  pt[:-1], p0 = kwarg['p0'], maxfev = maxfev, bounds = bounds)
        popt_log[2,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-2],  pt[:-2], p0 = kwarg['p0'], maxfev = maxfev, bounds = bounds)
    else:
        popt_log[0,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t,  pt, maxfev = maxfev, bounds = bounds)
        popt_log[1,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-1],  pt[:-1], maxfev = maxfev, bounds = bounds)
        popt_log[2,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-2],  pt[:-2], maxfev = maxfev, bounds = bounds)
    
    return popt_log

def plot_predictions(ax1, tx0, y0, dy0, x1, tx1, popt_logs, scale_factor, color):
    ys = np.zeros((len(x1), 3))
    df = pd.DataFrame(columns = ['x', 'y'])
    for i in [0,1,2]:
        df_tmp = pd.DataFrame(columns = ['x', 'y'])
        df_tmp['x'] = tx1
        df_tmp['y'] = my_func.logistic_growth(x1, popt_logs[i,0], popt_logs[i,1], popt_logs[i,2]) / scale_factor
        ys[:,i] = my_func.logistic_growth(x1, popt_logs[i,0], popt_logs[i,1], popt_logs[i,2]) / scale_factor
        df = df.append(df_tmp)
    sns.set(style = 'ticks', rc={"lines.linewidth": 2})
    ax2 = ax1.twinx()
    for i in [0,1,2]:
        ax2.bar(tx1[1:], ys[1:,i] - ys[:-1, i], alpha = 0.2, color = 'grey')
    ax2.plot(tx0, dy0, '--', color = color)
    ax1.plot(tx0, y0, '.', color = color)
    sns.lineplot(x='x', y='y', data = df, ax = ax1, color = color)
    ax1.set_ylim(bottom = 0)
    ax2.set_ylim(bottom = 0)
    y_ends = ys[-1,:]
    ind_midds = np.zeros((1,3))
    for i in [0,1,2]:
        ind_midds[0,i] = list(ys[1:,i] - ys[:-1, i]).index(max(ys[1:,i] - ys[:-1, i]))
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Total')
    ax2.set_ylabel('Daily')
    ax1.legend(['Total Data', 'Logistic Fit'], loc = 'upper left')
    ax2.legend(['Daily Data', 'Daily Fitted'], loc = 'center left')
    return ax1, ax2, y_ends, ind_midds

"""plot region"""
def plot_region(df_region, region_name, **kwarg):
    ######### unravel params
    if('is_fitting' in kwarg.keys()):
        is_fitting = kwarg['is_fitting']
        if('fitting_params' in kwarg.keys()):
            fitting_params = kwarg['fitting_params']
        else:
            fitting_params = {}
    else:
        is_fitting = False
    if('plotting_params' in kwarg.keys()):
        plotting_params = kwarg['plotting_params']
    else:
        cat_color = {'Confirmed':'tab:blue',
                    'Deaths':'tab:orange', 
                    'Recovered':'tab:green', 
                    'Active':'tab:red'}
        plotting_params = {
            'figsize':(15, 15),
            'time_series_cols' : ['Confirmed', 'Deaths', 'Recovered', 'Active'],
            'locator_param' : 4,
            'locator_param_future':8,
            'num_of_rols' : 6,
            'cat_color' : cat_color
        }
    time_datetime = list(df_region.index)

    ######### figure
    fig = plt.figure(figsize = plotting_params['figsize'], constrained_layout = True, facecolor = "1")
    gs = fig.add_gridspec(plotting_params['num_of_rols'], 2)

    ### font size setting 
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


    ### time series plot 
    ax = fig.add_subplot(gs[0, 0])
    ax2 = ax.twinx()
    legend1 = []
    legend2 = []
    
    max_y2 = 0
    for cat in plotting_params['time_series_cols']:
        if(df_region.loc[time_datetime[-1],cat] < df_region.loc[time_datetime[-1],'Confirmed']/2):
            ax2.plot(df_region.loc[:,cat], color = plotting_params['cat_color'][cat])
            if(max_y2 < np.max(df_region.loc[:,cat])):
                max_y2 = np.max(df_region.loc[:,cat])
            legend2.append(f'{cat}: {df_region.loc[time_datetime[-1], cat]:,}')
        else:
            ax.plot(df_region.loc[:,cat], color = plotting_params['cat_color'][cat])
            legend1.append(f'{cat}: {df_region.loc[time_datetime[-1], cat]:,}')
            
    ax.legend(legend1, loc = 'upper left', title = 'left y', title_fontsize = 12)
    ax2.legend(legend2, loc = 'center left', title = 'right y', title_fontsize = 12)
    ax2.set_ylim([0, max_y2*1.5])
    ax.set_ylim(bottom = 0)
    
    myLocator = mticker.MultipleLocator(plotting_params['locator_param'])
    ax.xaxis.set_major_locator(myLocator)
    ax.tick_params(axis = 'x', labelrotation = 45)

    ax.set_title(f'{region_name}: {df_region.Confirmed[-1]:,} total')


    ### daily cases 
    ax = fig.add_subplot(gs[0, 1])
    df_difs = df_region.loc[:,plotting_params['time_series_cols']].diff()
    ax2 = ax.twinx()
    legend1 = []
    legend2 = []
    
    max_y2 = 0
    for cat in plotting_params['time_series_cols']:
        if(np.max(df_difs.loc[time_datetime[-1],cat]) < np.max(df_difs.loc[time_datetime[-1],'Confirmed'])/2):
            ax2.plot(df_difs.loc[:,cat], color = plotting_params['cat_color'][cat])
            if(max_y2 < np.max(df_difs.loc[:,cat])):
                max_y2 = np.max(df_difs.loc[:,cat])
            legend2.append(f'{cat}: {df_difs.loc[time_datetime[-1], cat]:,}')
        else:
            ax.plot(df_difs.loc[:,cat], color = plotting_params['cat_color'][cat])
            legend1.append(f'{cat}: {df_difs.loc[time_datetime[-1], cat]:,}')
    
    ax.legend(legend1, loc = 'upper left', title = 'left y', title_fontsize = 12)
    ax2.legend(legend2, loc = 'center left', title = 'right y', title_fontsize = 12)
    ax2.set_ylim([0, max_y2*1.5])
    ax.set_ylim(bottom = 0)

    myLocator = mticker.MultipleLocator(plotting_params['locator_param'])
    ax.xaxis.set_major_locator(myLocator)
    ax.tick_params(axis = 'x', labelrotation = 45)

    ax.set_title(f'{region_name} Daily Cases: {df_region.Daily_Confirmed[-1]:,} today')


    ### growth factor 
    ax = fig.add_subplot(gs[1, 0])
    x = my_func.get_datetime_arange(time_datetime[0] - timedelta(days=2), len(time_datetime)+3)
    ax.plot(df_region.GFc_rolling, color = plotting_params['cat_color']['Confirmed'])
    ax.plot(df_region.GFd_rolling, color = plotting_params['cat_color']['Deaths'])
    ax.plot(x, np.full(len(x), 1), '--', color = 'k')
    
    ax.legend(['Confirmed', 'Deaths', 'y=1'])
    ax.set_title(f'{region_name} Growth Factor: {df_region.GFc_rolling[-1]:.2f}/{df_region.GFd_rolling[-1]:.2f} today')
    ax.set_ylim([0, min(5, max(np.max(df_region.GFc_rolling) + 0.5, np.max(df_region.GFd_rolling) + 0.5))])
    
    ax.set_xlim([time_datetime[0], time_datetime[-1] + timedelta(days=2)])
    
    myLocator = mticker.MultipleLocator(plotting_params['locator_param'])
    ax.xaxis.set_major_locator(myLocator)
    ax.tick_params(axis = 'x', labelrotation = 45)

    ### closed cases
    ax = fig.add_subplot(gs[1, 1])
    if('Recovered' in plotting_params['time_series_cols']):
        ax.plot(df_region.Recovered_prop, color = plotting_params['cat_color']['Recovered'])
        ax.plot(df_region.Death_prop, color = plotting_params['cat_color']['Deaths'])
        ax2 = ax.twinx()
        ax2.plot(df_region.CFR, color = 'grey')
        ax.legend(['Recovered%', 'Deaths%'], loc = 'upper left')
        ax2.legend(['CFR'], loc = 'center right')
        ax.set_ylabel('Closed Cases')
        ax2.set_ylabel('CFR')
        ax.set_title(f'{region_name} Closed Cases Deaths% = {df_region.Death_prop[-1]:.1f}%; CFR = {df_region.CFR[-1]:.1f}%')
    else:
        ax.plot(df_region.CFR, color = 'grey')
        ax.set_title(f'{region_name} CFR = {df_region.CFR[-1]:.1f}%')
    
    myLocator = mticker.MultipleLocator(plotting_params['locator_param'])
    ax.xaxis.set_major_locator(myLocator)
    ax.tick_params(axis = 'x', labelrotation = 45)

    ### fitting
    if(is_fitting == True):
        ### fitting params
        if('future' in fitting_params.keys()):
            future = fitting_params['future']
        else:
            future = 0
        if('p0_exp' in fitting_params.keys()):
            p0_exp = fitting_params['p0_exp']
        else:
            p0_exp = (1,1)
        if('p0_log' in fitting_params.keys()):
            p0_log = fitting_params['p0_log']
        else:
            p0_log = (1,1,1)
        if('maxfev' in fitting_params.keys()):
            maxfev = fitting_params['maxfev']
        else:
            maxfev = 100000
        if('bounds_c' in fitting_params.keys()):
            bounds_c = fitting_params['bounds_c']
        else:
            bounds_c = (-np.inf, np.inf)
        if('bounds_d' in fitting_params.keys()):
            bounds_d = fitting_params['bounds_d']
        else:
            bounds_d = (-np.inf, np.inf)
        if('death_to_confirmed' in fitting_params.keys()):
            death_to_confirmed = fitting_params['death_to_confirmed']
            if('CFR' in fitting_params.keys()):
                cfr = fitting_params['CFR']
            else:
                cfr = df_region.CFR[-1]/100
        else:
            death_to_confirmed = False

        ### fitting data
        y_c = df_region.Confirmed.to_numpy()
        y_d = df_region.Deaths.to_numpy()
        
        res_c = df_region[df_region.GFc_thr != 0.0].bfill(axis=1).index[0]
        ind_tc = max(0, time_datetime.index(res_c)-3)
        # res_d = df_region[df_region.GFd_thr != 0.0].bfill(axis=1).index[0]
        # ind_td = max(0, time_datetime.index(res_d)-3)
        ind_td = ind_tc
        tc = np.arange(len(time_datetime))[ind_tc:] - ind_tc
        td = np.arange(len(time_datetime))[ind_td:] - ind_td
        pt_c = y_c[ind_tc:]
        pt_d = y_d[ind_td:]

        popt_exp_c, _ = opt.curve_fit(my_func.exp_growth,  tc,  pt_c, p0 = p0_exp, maxfev = maxfev)
        popt_exp_d, _ = opt.curve_fit(my_func.exp_growth,  td,  pt_d, p0 = p0_exp, maxfev = maxfev)
        if(future != 0):
            popt_logs_c = get_logistic_params(tc, pt_c, p0 = p0_log, maxfev = maxfev, bounds = bounds_c)
            popt_logs_d = get_logistic_params(td, pt_d, p0 = p0_log, maxfev = maxfev, bounds = bounds_d)
        else:
            popt_logs_c, _ = opt.curve_fit(my_func. logistic_growth,  tc,  pt_c, p0 = p0_log, maxfev = maxfev)
            popt_logs_d, _ = opt.curve_fit(my_func. logistic_growth,  td,  pt_d, p0 = p0_log, maxfev = maxfev)


        ### confirmed fitting plot
        ax = fig.add_subplot(gs[2, 0])
        x = np.arange(len(time_datetime))
        x1 = np.arange(len(tc) + future)
        tx = my_func.get_datetime_arange(time_datetime[0], len(time_datetime))
        tx1 = my_func.get_datetime_arange(time_datetime[ind_tc], len(tc) + future)

        if(future == 0):
            ax.plot(tx, y_c, '.', ms = 10, color = plotting_params['cat_color']['Confirmed'])
            ax.plot(tx1, my_func.exp_growth(x1, popt_exp_c[0], popt_exp_c[1]), '--', color = plotting_params['cat_color']['Confirmed'])
            ax.plot(tx1, my_func. logistic_growth(x1, popt_logs_c[0], popt_logs_c[1], popt_logs_c[2]), color = plotting_params['cat_color']['Confirmed'])
            ax.set_ylim([0, np.ceil(y_c[-1] + y_c[-1]/10)])
        else:
            dy_c = df_region.Daily_Confirmed_smoothed
            ax1, ax2, y_ends, ind_midds = plot_predictions(ax, tx, y_c, dy_c, x1, tx1, popt_logs_c, 1, plotting_params['cat_color']['Confirmed'])
            date_max = []
            for k in [0,1]:
                if(k == 0):
                    ind = int(np.min(ind_midds))
                else:
                    ind = int(np.max(ind_midds))
                date_max.append(time_datetime[ind_tc] + timedelta(days=ind))
            confirmed_total = np.mean(y_ends)
        if(future == 0):
            ax.legend(['Confirmed', 
                        'Confirmed Exp Fit', 
                        'Confirmed Logistic Fit'])
            ax.set_title(f'{region_name} Confirmed Fit: r = {popt_exp_c[0]:.2f}/{popt_logs_c[0]:.2f}', fontsize = 18)
        else:
            ax.set_title(f'{region_name} Confirmed Prediction: K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}')
            pp = f'{region_name} Confirmed Prediction: r={np.mean(popt_logs_c[:,0]):.2f}, K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}, peak increase at {date_max[0].date()} ~ {date_max[1].date()}'
            print(pp)
        
        myLocator = mticker.MultipleLocator(plotting_params['locator_param_future'])
        ax.xaxis.set_major_locator(myLocator)
        ax.tick_params(axis = 'x', labelrotation = 45)
        ax.set_xlim(left = time_datetime[0])


        ### death fitting plot
        ax = fig.add_subplot(gs[2, 1])
        x = np.arange(len(time_datetime))
        x1 = np.arange(len(tc) + future)
        tx = my_func.get_datetime_arange(time_datetime[0], len(time_datetime))
        tx1 = my_func.get_datetime_arange(time_datetime[ind_tc], len(tc) + future)
        
        if(y_d[-1] <= 50):
            ax.plot(tx, y_d, '.', ms = 10, color = plotting_params['cat_color']['Deaths'])
            ax.set_title(f'{region_name} Deaths, total = {y_d[-1]} too low to fit')
        else:
            if(future == 0):
                ax.plot(tx, y_d, '.', ms = 10, color = plotting_params['cat_color']['Deaths'])
                ax.plot(tx1, my_func.exp_growth(x1, popt_exp_d[0], popt_exp_d[1]), '--', color = plotting_params['cat_color']['Deaths'])
                ax.plot(tx1, my_func. logistic_growth(x1, popt_logs_d[0], popt_logs_d[1], popt_logs_d[2]), color = plotting_params['cat_color']['Deaths'])
                ax.set_ylim([0, np.ceil(y_d[-1] + y_d[-1]/10)])
            else:
                dy_d = df_region.Daily_Deaths_smoothed
                ax1, ax2, y_ends, ind_midds = plot_predictions(ax, tx, y_d, dy_d, x1, tx1, popt_logs_d, 1, plotting_params['cat_color']['Deaths'])
                date_max = []
                for k in [0,1]:
                    if(k == 0):
                        ind = int(np.min(ind_midds))
                    else:
                        ind = int(np.max(ind_midds))
                    date_max.append(time_datetime[ind_tc] + timedelta(days=ind))
                deaths_total = np.mean(y_ends)
            if(future == 0):
                ax.legend(['Deaths', 
                            'Deaths Exp Fit', 
                            'Deaths Logistic Fit'])
                ax.set_title(f'{region_name} Deaths Fit: r = {popt_exp_d[0]:.2f}/{popt_exp_d[0]:.2f}', fontsize = 18)
            else:
                ax.set_title(f'{region_name} Deaths Prediction: K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}', fontsize = 18)
                pp = f'{region_name} Deaths prediction: r={np.mean(popt_logs_d[:,0]):.2f}, K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f} ({deaths_total/confirmed_total*100:.1f}%), peak increase at {date_max[0].date()} ~ {date_max[1].date()}'
                print(pp)
                
        myLocator = mticker.MultipleLocator(plotting_params['locator_param_future'])
        ax.xaxis.set_major_locator(myLocator)
        ax.tick_params(axis = 'x', labelrotation = 45)
        ax.set_xlim(left = time_datetime[0])
        
        ### confirmed prediction based on death and current CFR
        if(future != 0 and death_to_confirmed and y_d[-1] > 50):
            ax = fig.add_subplot(gs[3, 0])
            ax1, ax2, y_ends, ind_midds = plot_predictions(ax, tx, y_c, dy_c, x1, tx1, popt_logs_d, cfr, plotting_params['cat_color']['Confirmed'])
            date_max = []
            for k in [0,1]:
                if(k == 0):
                    ind = int(np.min(ind_midds))
                else:
                    ind = int(np.max(ind_midds))
                date_max.append(time_datetime[ind_tc] + timedelta(days=ind))
            confirmed_total = np.mean(y_ends)
            ax.set_title(f'{region_name} Confirmed projection (based on CFR = {cfr*100:.1f}): K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}')
            pp = f'{region_name} Confirmed projection based on CFR = {cfr*100:.1f}%: K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}, peak increase at {date_max[0].date()}~{date_max[1].date()}'
            print(pp)

            myLocator = mticker.MultipleLocator(plotting_params['locator_param_future'])
            ax.xaxis.set_major_locator(myLocator)
            ax.tick_params(axis = 'x', labelrotation = 45)
            ax.set_xlim(left = time_datetime[0])

"""Plot continent"""
def plot_continents(df_continents):
    fig = plt.figure(figsize = (10, 6), constrained_layout=True, facecolor="1")
    gs = fig.add_gridspec(2,2)

    for i in [0,1]:
        for j in [0,1]:
            if(i == 0):
                cat = 'Total'
                plt_title = 'Total'
            else:
                cat = 'New'
                plt_title = 'New'
            if(j == 0):
                cat += '_Confirmed'
                plt_title += ' Confirmed cases by continent'
                df_plot = df_continents[cat]
            else:
                cat += '_Deaths'
                plt_title += ' Deaths by continent'
                df_plot = df_continents[cat]
            ax = fig.add_subplot(gs[j,i])

            df_plot = df_plot.sort_values(ascending=False)
            percentages = []
            labels = []
            total = np.sum(df_continents[cat])
            for cont in df_plot.index:
                percentages.append(df_plot[cont]/total*100)
                labels.append(cont)
            colors = pl.cm.Set2(np.linspace(0,1,len(percentages)))
            wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
                                              autopct = my_autopct, pctdistance=0.7,
                                              shadow=False, startangle=90,
                                              textprops = dict(size = 12))
            ax.legend(wedges, labels, loc="center right", 
                      bbox_to_anchor = (1, 0, 0.2, 1))
            ax.axis('equal')
            ax.set_title(plt_title)

"""us tests"""
def plot_tests_bar_and_percent(ax1, x, y1, y2, color1, color2):
    ax2 = ax1.twinx()
    for i, cat in enumerate(y1.columns):
        ax1.bar(x, y1[cat], color = color1[i])
    ax2.plot(x, y2, linewidth = 2, color = color2)
    ax1.legend(['Negative', 'Positive'])
    ax2.legend(['%positive'], loc = 'upper center')
    ax1.set_ylabel('Number of tests')
    ax2.set_ylabel('Positive%')
    return ax1, ax2

def tests_us_vs_state(df_tests_us_daily, df_tests_onestate_daily, df_us, df_st, state):
        
    fig = plt.figure(figsize = (15, 15), constrained_layout=True, facecolor="1")
    gs = fig.add_gridspec(3, 2)

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


    for i in [0,1]:
        if(i == 0):
            plt_title = 'US'
            df_plot = df_us
            df_test = df_tests_us_daily
        else:
            plt_title = state
            df_plot = df_st
            df_test = df_tests_onestate_daily


        ### bar graph of tests
        ax = fig.add_subplot(gs[0, i])
        x = df_test.index
        ax1, ax2 = plot_tests_bar_and_percent(ax, x, 
                                              df_test.loc[:,['totalTestResults', 'positive']], 
                                              df_test.positive/df_test.totalTestResults*100,
                                              [cat_color['Negative'], cat_color['Positive']],
                                              'grey')
        myLocator = mticker.MultipleLocator(4)
        ax.xaxis.set_major_locator(myLocator)
        ax.tick_params(axis = 'x', labelrotation = 45)
        ax.set_title(f'{plt_title} tests performed')


        ### daily increase
        ax = fig.add_subplot(gs[1, i])
        ax.bar(x, df_test.totalTestResultsIncrease, color = 'grey')
        ax.set_yscale('linear')
        myLocator = mticker.MultipleLocator(4)
        ax.xaxis.set_major_locator(myLocator)
        ax.tick_params(axis = 'x', labelrotation = 45)
        ax.set_title(f'{plt_title} tests daily increase')
        ax.set_ylabel('Number of tests')

        ### tests vs. positive
        ax = fig.add_subplot(gs[2, i])
        sns.regplot(data = df_test, x = 'positive', y = 'totalTestResults')
        sns.regplot(x = df_plot.loc[df_test.index, 'Confirmed'], y = df_test.totalTestResults)
        ax.set_yscale('linear')
        ax.legend(['Reported positive test cases', 'Reported confirmed cases'])
        ax.set_xlabel('Toatal number of cases')
        ax.set_ylabel('Total number of tests')

def plot_us_tests_by_state(df_us_tests, df_tests_states_daily, num_states, usstate_abbs_mapping):
    ############## figure ############
    fig = plt.figure(figsize = (18, 15), constrained_layout=True, facecolor="1")
    gs = fig.add_gridspec(3, 3)

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    ### value against rank
    states = df_us_tests.sort_values(by = 'positive', inplace = False, ascending=False).index[:num_states]
    cat_plots = ['Percent_Pos', 'Test_Per_Million', 'Pos_Per_Million']
    
    print('subplot', end = " ")
    for i in [0,1,2]:
        print(f'{i+1}', end = " ")
        ax = fig.add_subplot(gs[0, i])

        cat_x = f'rank_{cat_plots[i]}'
        cat_y = cat_plots[i]
        df_plot = df_us_tests.sort_values(by = cat_y, inplace = False, ascending=False)
        x = np.arange(-1, len(df_plot.index)+1)
        p1 = sns.scatterplot(x = cat_x, y = cat_y, 
                             hue = 'Governer_Affiliation', palette = cat_color, 
                             data=df_plot, ax = ax)
        ax.plot(x, np.full(len(x), np.median(df_plot[cat_y])), '--', color = 'k')

        for st in states:
            pos_st = [df_us_tests.loc[st, cat_x], df_us_tests.loc[st, cat_y]]
            p1.text(pos_st[0]+0.5, pos_st[1] +0.5, st, 
                    horizontalalignment='left', size='medium', 
                    color='black',weight='normal')
        ax.set_xlim([-0.5, len(df_plot.index)+0.5])
        ax.set_title(f'{cat_y}: US median = {np.median(df_plot[cat_y]):.1f}')

    ### relationship between values
    cat_pairs = [['rank_Percent_Pos', 'rank_Test_Per_Million'], 
                 ['rank_Test_Per_Million', 'rank_Pos_Per_Million'], 
                 ['rank_Percent_Pos', 'rank_Pos_Per_Million']]
    for i in [0,1,2]:
        print(f'{i+4}', end = " ")
        ax = fig.add_subplot(gs[1, i])
        p1 = sns.scatterplot(x = cat_pairs[i][0], y = cat_pairs[i][1], ax = ax, data = df_us_tests, 
                             hue = 'Governer_Affiliation', palette = cat_color, legend = False)
        df_fit = pd.DataFrame(columns = ['x', 'y', 'y_pred', 'res'])
        if(i == 0):
            x = np.arange(-1, len(df_us_tests.index) + 1)
            y = max(df_us_tests[cat_pairs[i][0]]) - x
            ax.plot(x, y, '--', color = 'k')
            df_fit['x'] = df_us_tests[cat_pairs[i][0]]
            df_fit['y'] = df_us_tests[cat_pairs[i][1]]
            df_fit['y_pred'] = max(df_fit['x']) - df_fit['x']
            df_fit['res'] = df_fit['y'] - df_fit['y_pred']
        else:
            x = np.arange(-1, len(df_us_tests.index) + 1)
            y = x
            ax.plot(x, y, '--', color = 'k')
            df_fit['x'] = df_us_tests[cat_pairs[i][0]]
            df_fit['y'] = df_us_tests[cat_pairs[i][1]]
            df_fit['y_pred'] = df_fit['x']
            df_fit['res'] = df_fit['y'] - df_fit['y_pred']

        states = []
        if(i == 0):
            states += list(df_fit.sort_values(by = 'res').index[:10])
        elif(i == 1):
            states += list(df_fit.sort_values(by = 'res').index[:10])
        elif(i == 2):
            states += list(df_fit.sort_values(by = 'res').index[-10:])

        for st in states:
            pos_st = [df_us_tests.loc[st, cat_pairs[i][0]], df_us_tests.loc[st, cat_pairs[i][1]]]
            p1.text(pos_st[0]+np.random.randint(-2, 2)/2, pos_st[1] +np.random.randint(-2, 2)/2, st, 
                    horizontalalignment='left', size='medium', 
                    color='black',weight='normal')
    
    ### top 10 states
    print(f'7~9:', end = " ")
    ax1 = fig.add_subplot(gs[2, 0])
    ax2 = fig.add_subplot(gs[2, 1])
    ax3 = fig.add_subplot(gs[2, 2])
    
    max_x3 = 0
    max_y3 = 0
    
    states_list = list(df_us_confirmed.index[0:num_states])
    
    for i, state in enumerate(states_list):
        print(i, end =" ")
        st = usstate_abbs_mapping[state]
        df_test = df_tests_states_daily.groupby('state').get_group(st)
        df_test.sort_values(by = 'date', inplace = True, ascending=True)
        df_test.set_index('date', inplace = True)

        x = np.arange(len(df_test.index))
        ax1.plot(df_test.positive/df_test.totalTestResults*100)
        ax2.plot(df_test.totalTestResultsIncrease, label='_nolegend_')
        sns.lineplot(data = df_test, x = 'positive', y = 'totalTestResults', ax = ax3)
        
        if(state != 'New York'):
            if(max_x3 < np.max(df_test.positive)):
                max_x3 = np.max(df_test.positive)
            if(max_y3 < np.max(df_test.totalTestResults)):
                max_y3 = np.max(df_test.totalTestResults)

    myLocator = mticker.MultipleLocator(4)
    ax1.xaxis.set_major_locator(myLocator)
    ax1.tick_params(axis = 'x', labelrotation = 45)
    ax1.set_title('%Positive')

    myLocator = mticker.MultipleLocator(4)
    ax2.xaxis.set_major_locator(myLocator)
    ax2.tick_params(axis = 'x', labelrotation = 45)
    ax2.set_title('%Daily increase in number of tests')

    ax3.set_xlim([0, max_x3*1.2])
    ax3.set_ylim([0, max_y3*1.2])
    ax3.legend(states_list, loc="center right", bbox_to_anchor = (1.01, 0, 0.3, 1))
    ax3.set_title('Positive vs. Total Tests')

def county_plot(df_today, states, num_counties, figsize):
    ############ params ############
    colors = get_colors(num_counties+1, is_last_grey = True)

    ############ figure ############
    fig = plt.figure(figsize = figsize, constrained_layout=True, facecolor="1")
    gs = fig.add_gridspec(len(states), 7)

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    print('States:', end = " ")
    for i, state in enumerate(states):
        print(f'{state},', end = " ")
        df_state = df_today.groupby('Country_Region').get_group('US').groupby('Province_State').get_group(state).loc[:,['Admin2'] + cdra_cols]
        df_state.set_index('Admin2', inplace = True)
        df_state = df_state.loc[(df_state!=0).any(axis=1)]
        df_state.loc[:,'CFR'] = df_state.Deaths/df_state.Confirmed*100
        df_state = df_state.replace([np.inf, -np.inf], 0)

        ############ total number pie chart ############
        ax = fig.add_subplot(gs[i,0:2])

        df_state.sort_values(by = 'Confirmed', inplace = True, ascending=False)
        percentages = []
        labels = []
        for county in list(df_state.index)[:num_counties]:
            percentages.append(df_state.loc[county, 'Confirmed']/np.sum(df_state.Confirmed)*100)
            if(percentages[-1] > 2):
                labels.append(county)
            else:
                labels.append('')
            if(sum(percentages) >= 99):
                break
        if(num_counties < len(df_state.index)):
            labels.append('Rest')
            percentages.append(100-sum(percentages))

        ax.pie(percentages, colors = colors,
               labels=labels, autopct = my_autopct, 
               pctdistance=0.8, labeldistance = 1.05,
               shadow=False, startangle=90,
               textprops = dict(size = 12))
        ax.axis('equal')
        ax.set_title(f"{state} confirmed cases: {np.sum(df_state.Confirmed):.0f} total")

        ############ total deaths pie chart ############
        ax = fig.add_subplot(gs[i,2:4])

        df_state.sort_values(by = 'Deaths', inplace = True, ascending=False)
        percentages = []
        labels = []
        for county in list(df_state.index)[:num_counties]:
            percentages.append(df_state.loc[county, 'Deaths']/np.sum(df_state.Deaths)*100)
            if(percentages[-1] > 2):
                labels.append(county)
            else:
                labels.append('')
            if(sum(percentages) >= 90):
                break
        if(num_counties < len(df_state.index)):
            labels.append('Rest')
            percentages.append(100-sum(percentages))

        ax.pie(percentages, colors = colors,
               labels=labels, autopct = my_autopct, 
               pctdistance=0.8, labeldistance = 1.05,
               shadow=False, startangle=90,
               textprops = dict(size = 12))
        ax.axis('equal')
        ax.set_title(f"{state} deaths: {np.sum(df_state.Deaths):.0f} total")

        ############ cfrs ############
        ax = fig.add_subplot(gs[i,4:])

        df_state.sort_values(by = 'Confirmed', inplace = True, ascending=False)
        y = df_state.CFR[df_state.CFR>0].to_numpy()
        x = np.arange(len(y))
        x1 = np.arange(-2, len(x)+2)
        fr_total = sum(df_state.Deaths)/sum(df_state.Confirmed)*100

        rects = ax.bar(x, y, color = 'grey')
        ax.plot(x1, np.full(len(x1), fr_total), '--', color = 'k')
        a = ax.set_xticks(x)
        a = ax.set_xticklabels(df_state[df_state.CFR>0].index)
        ax.tick_params(axis = 'x', labelrotation = -90)
        autolabel(rects, ax, '{:.2f}')
        ymax = np.ceil(np.max(y) + np.max(y)/10)
        ax.set_ylim([0, ymax])
        ax.set_xlim([-1, len(x) + 0.5])
        a = ax.set_title(f'CFRs: {state} mean = {fr_total:.2f}%')


"""plot by region"""
### get growth rate by fitting time series data to exponeitial or logistic growth model.
def get_growth_rate(df_ctry, time_str):
    x = np.arange(len(time_str))
    y = df_ctry.Confirmed.to_list()

    res = df_ctry[df_ctry.GF_rolling_thr != 0.0].bfill(axis=1).index[0]
    ind_t0 = max(0, time_str.index(res)-3)
    t = np.arange(len(time_str))[ind_t0:]- ind_t0
    pt = y[ind_t0:]
    
    r = []
    
    try:
        popt_log, pcov_log = opt.curve_fit(my_func.logistic_growth,  t,  pt, maxfev=100000)
        r.append(popt_log[0])
    except RuntimeError:
        r.append(np.inf)
    try:
        popt_log1, pcov_log1 = opt.curve_fit(my_func.logistic_growth,  t,  pt, p0 = (0.1, 100, 1), maxfev=100000)
        r.append(popt_log1[0])
    except RuntimeError:
        r.append(np.inf)
    return np.min(r)


def plot_by_regions(df_confirmed, df_deaths, time_datetime, **kwarg):
    if('num_lineplot' in kwarg.keys()):
        num_lineplot = kwarg['num_lineplot']
    else:
        num_lineplot = 10
    if('num_barplot' in kwarg.keys()):
        num_barplot = kwarg['num_barplot']
    else:
        num_barplot = 20
    
    ############ figure ############
    fig = plt.figure(figsize = (15, 30), constrained_layout=True, facecolor="1")
    gs = fig.add_gridspec(6, 8)

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    
    print("subplots:", end = " ")
    ############ case per million ############
    ax = fig.add_subplot(gs[5, 0:4])
    print("11", end = " ")
    
    df_confirmed.sort_values(by = 'Per_Million', inplace = True, ascending=False)
    plot_list = list(df_confirmed.index[0:num_barplot])
    compare_list = list(df_confirmed.sort_values(by = time_datetime[-1], ascending=False).index[:num_barplot])
    iH = [i for i in range(len(plot_list)) if plot_list[i] not in compare_list]
    y = df_confirmed.loc[plot_list, 'Per_Million'].to_numpy()
    

    x = np.arange(len(plot_list))

    rects1 = ax.bar(x, y, color = 'grey')
    rects2 = ax.bar(x[iH], y[iH], color = 'tab:red')
    a = ax.set_xticks(x)
    a = ax.set_xticklabels(plot_list)
    ax.tick_params(axis = 'x', labelrotation = -90)
    autolabel(rects1, ax, '{:.1f}')
    autolabel(rects2, ax, '{:.1f}')
    ax.set_yscale('log')
    # ymax = np.ceil(np.max(y)*1.2)
    # ax.set_ylim([-0.5, ymax])
    a = ax.set_title('Top 30 regions by case per million')
    ax.set_xlim([-1, len(x) + 0.5])

    ############ death per million ############
    ax = fig.add_subplot(gs[5, 4:])
    print("12,", end = " ")

    df_deaths.sort_values(by = 'Per_Million', inplace = True, ascending=False)
    plot_list = list(df_deaths.index[0:num_barplot])
    compare_list = list(df_deaths.sort_values(by = time_datetime[-1], ascending=False).index[:num_barplot])
    iH = [i for i in range(len(plot_list)) if plot_list[i] not in compare_list]
    y = df_deaths.loc[plot_list, 'Per_Million'].to_numpy()
    

    x = np.arange(len(plot_list))

    rects1 = ax.bar(x, y, color = 'grey')
    rects2 = ax.bar(x[iH], y[iH], color = 'tab:red')
    a = ax.set_xticks(x)
    a = ax.set_xticklabels(plot_list)
    ax.tick_params(axis = 'x', labelrotation = -90)
    autolabel(rects1, ax, '{:.1f}')
    autolabel(rects2, ax, '{:.1f}')
    ax.set_yscale('log')
    # ymax = np.ceil(np.max(y)*1.2)
    # ax.set_ylim([-0.5, ymax])
    a = ax.set_title('Top 30 regions by deaths per million')
    ax.set_xlim([-1, len(x) + 0.5])

    ############ total confirmed: normalize axis ############
    ax = fig.add_subplot(gs[0, 0:5])
    print("1,", end = " ")
    
    df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    plot_list = list(df_confirmed.index[0:num_lineplot])
    if('list_addins' in kwarg.keys()):
        plot_list += kwarg['list_addins']
        plot_list = list(set(plot_list))
        df_plot = df_confirmed.loc[plot_list,:].sort_values(by = time_datetime[-1], ascending=False)
        plot_list = list(df_plot.index)
    df_plot = df_confirmed.loc[plot_list,time_datetime]

    colors = get_colors(len(plot_list))
    max_x = 0
    max_y = np.max(df_plot.to_numpy().flatten())

    for i, ele in enumerate(plot_list):
        if(df_plot.loc[ele,time_datetime[-1]]>100):
            xi = len(df_plot.loc[ele, df_plot.loc[ele,:]>100].to_numpy())
            if(xi > max_x and ele != 'China'):
                max_x = xi
            if('special' in kwarg.keys()):
                if(ele == kwarg['special']):
                    ax.plot(df_plot.loc[ele, df_plot.loc[ele,:]>100].to_numpy(), linewidth = 3, color = colors[i])
                else:
                    ax.plot(df_plot.loc[ele, df_plot.loc[ele,:]>100].to_numpy(), color = colors[i])
            else:
                ax.plot(df_plot.loc[ele, df_plot.loc[ele,:]>100].to_numpy(), color = colors[i])

    x = np.arange(max_x)
    ax.plot(x, 100 * (1+0.33) ** x, ls='--', color='k')
    ax.plot(x, 100 * (1+0.5) ** x, ls='-.', color='k')

    ax.set_ylim([100, max_y+max_y/2])
    ax.set_xlim([0, max_x + 2])
    ax.legend(plot_list + 
               [f'33% daily incrase',
               f'50% daily increase'], 
               loc="center right",
               bbox_to_anchor = (1, 0, 0.35, 1)) #
    ax.set_yscale('log')
    ax.set_xlabel('Days Since 100 Confirmed Cases')
    ax.set_title('Confirmed cases by country/region')

    ############ total confirmed: pie chart ############
    ax = fig.add_subplot(gs[0,5:])
    print("2,", end = " ")

    df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    percentages = []
    labels = []
    df_confirmed_total = np.sum(df_confirmed.loc[:,time_datetime[-1]])

    for ele in df_confirmed.index[0:num_lineplot]:
        percentages.append(df_confirmed.loc[ele, time_datetime[-1]]/df_confirmed_total*100)
        labels.append(ele)
    labels.append('Rest')
    percentages.append(100-sum(percentages))

    colors = get_colors(len(labels), is_last_grey = True)
    wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
                                      autopct = my_autopct, pctdistance=0.8,
                                      shadow=False, startangle=90,
                                      textprops = dict(size = 12))
    
    ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0, 1))
    ax.axis('equal')
    ax.set_title("Total Confirmed Cases")


    ############ total deaths: normalized axis ############
    ax = fig.add_subplot(gs[1, 0:5])
    print("3,", end = " ")
    
    df_deaths.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    plot_list = list(df_deaths.index[0:num_lineplot])
    if('list_addins' in kwarg.keys()):
            plot_list += kwarg['list_addins']
            plot_list = list(set(plot_list))
            df_plot = df_deaths.loc[plot_list,:].sort_values(by = time_datetime[-1], ascending=False)
            plot_list = list(df_plot.index)
    df_plot = df_deaths.loc[plot_list,time_datetime]

    colors = get_colors(len(plot_list))
    max_x = 0
    max_y = np.max(df_plot.to_numpy().flatten())

    for i, ele in enumerate(plot_list):
        if(df_plot.loc[ele,time_datetime[-1]]>10):
            xi = len(df_plot.loc[ele, df_plot.loc[ele,:]>10].to_numpy())
            if(xi > max_x):
                max_x = xi
            if('special' in kwarg.keys()):
                if(ele == kwarg['special']):
                    ax.plot(df_plot.loc[ele,df_plot.loc[ele,:]>10].to_numpy(), color = colors[i], linewidth = 3)
                else:
                    ax.plot(df_plot.loc[ele,df_plot.loc[ele,:]>10].to_numpy(), color = colors[i])
            else:
                ax.plot(df_plot.loc[ele,df_plot.loc[ele,:]>10].to_numpy(), color = colors[i])

    x = np.arange(max_x)
    ax.plot(x, 10 * (1+0.20) ** x, ls='--', color='k')
    ax.plot(x, 10 * (1+0.40) ** x, ls='-.', color='k')

    ax.set_ylim([10, max_y+max_y/10])
    ax.set_xlim([0, max_x + 2])

    ax.legend(plot_list + 
               [f'20% daily incrase',
                f'40% daily increase'],
               loc="center right") #bbox_to_anchor = (1, 0, 0.35, 1)
    ax.set_yscale('log')
    ax.set_xlabel('Days since 10 deaths')
    ax.set_title('Total Deaths')


    ############ total deaths: pie chart ############
    ax = fig.add_subplot(gs[1,5:])
    print("4,", end = " ")
    
    df_deaths.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    percentages = []
    labels = []
    df_deaths_total = np.sum(df_deaths.loc[:,time_datetime[-1]])
    for ele in df_deaths.index[0:num_lineplot]:
        percentages.append(df_deaths.loc[ele, time_datetime[-1]]/df_deaths_total*100)
        labels.append(ele)
    labels.append('Rest')
    percentages.append(100-sum(percentages))

    colors = get_colors(len(labels), is_last_grey = True)
    wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
                                      autopct = my_autopct, pctdistance=0.8,
                                      shadow=False, startangle=90,
                                      textprops = dict(size = 12))
    ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0, 1))
    ax.axis('equal')
    ax.set_title("Total Deaths")


    ############ daily confirmed ############
    ax = fig.add_subplot(gs[2, 0:4])
    print("5,", end = " ")
    
    df_confirmed.sort_values(by = 'New_Today', inplace = True, ascending=False)
    plot_list = list(df_confirmed.index[0:num_lineplot])
    if('list_addins' in kwarg.keys()):
        plot_list += kwarg['list_addins']
        plot_list = list(set(plot_list))
        df_plot = df_confirmed.loc[plot_list,:].sort_values(by = 'New_Today', ascending=False)
        plot_list = list(df_plot.index)
    df_plot = df_confirmed.loc[plot_list,time_datetime]

    colors = get_colors(len(plot_list))
    data_max = 0
    x_max = 0
    for i, ele in enumerate(plot_list):
        if(df_plot.loc[ele,time_datetime[-1]]>100):
            yi = df_plot.loc[ele,time_datetime].transpose().diff().loc[df_plot.loc[ele,time_datetime]>100].to_numpy()
            xi = np.arange(len(yi))
            if(np.max(yi) > data_max):
                data_max = np.max(yi)
            if(ele != 'China' and len(xi) > x_max):
                x_max = len(xi)
            if('special' in kwarg.keys()):
                if(ele == kwarg['special']):
                    ax.plot(xi, yi, color = colors[i], linewidth = 3)
                else:
                    ax.plot(xi, yi, color = colors[i])
            else:
                ax.plot(xi, yi, color = colors[i], linewidth = 3)

    ax.legend(plot_list, loc = 'upper left')
    ax.set_yscale('linear')
    ax.set_ylim([0, data_max + data_max/10])
    ax.set_xlim([0, x_max + 2])
    a = ax.set_title(f'Daily confirmed cases')
    ax.set_xlabel('Days Since 100 Confirmed Cases')
    
    
    ############ daily deaths ############
    ax = fig.add_subplot(gs[2, 4:])
    print("6,", end = " ")
    
    df_deaths.sort_values(by = 'New_Today', inplace = True, ascending=False)
    plot_list = list(df_deaths.index[0:num_lineplot])
    if('list_addins' in kwarg.keys()):
            plot_list += kwarg['list_addins']
            plot_list = list(set(plot_list))
            df_plot = df_deaths.loc[plot_list,:].sort_values(by = 'New_Today', ascending=False)
            plot_list = list(df_plot.index)
    df_plot = df_deaths.loc[plot_list,time_datetime]

    colors = get_colors(len(plot_list))
    data_max = 0
    x_max = 0
    for i, ele in enumerate(plot_list):
        if(df_plot.loc[ele,time_datetime[-1]]>10):
            yi = df_plot.loc[ele,time_datetime].transpose().diff().loc[df_plot.loc[ele,time_datetime]>10].to_numpy()
            xi = np.arange(len(yi))
            if(np.max(yi) > data_max):
                data_max = np.max(yi)
            if(ele != 'China' and len(xi) > x_max):
                x_max = len(xi)
            if('special' in kwarg.keys()):
                if(ele == kwarg['special']):
                    ax.plot(xi, yi, color = colors[i], linewidth = 3)
                else:
                    ax.plot(xi, yi, color = colors[i])
            else:
                ax.plot(xi, yi, color = colors[i], linewidth = 3)

    ax.legend(plot_list, loc = 'upper left')
    ax.set_yscale('linear')
    ax.set_ylim([0, data_max + data_max/10])
    ax.set_xlim([0, x_max + 2])
    a = ax.set_title(f'Daily deaths')
    ax.set_xlim(left = 0)
    ax.set_xlabel('Days Since 10 Deaths')


    ############ growth factors ############
    ax = fig.add_subplot(gs[3, 0:4])
    print("7,", end = " ")

    df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    plot_list = list(df_confirmed.index[0:num_barplot])
    # plot_list = [ele for ele in df_confirmed.index if df_confirmed.loc[ele,time_datetime[-1]] >= 500]

    df_gf = df_confirmed.loc[plot_list,time_datetime].transpose()
    for ele in plot_list:
        df_ele = pd.DataFrame(df_confirmed.loc[ele,time_datetime])
        df_ele = my_func.reshape_dataframe(df_ele, time_datetime)
        df_gf[ele] = df_ele.GF_rolling

    x = np.arange(len(plot_list))
    x1 = np.arange(-2, len(x)+2)
    y = df_gf.loc[time_datetime[-1],:]

    rects1 = ax.bar(x, y, color = 'grey')
    ax.plot(x1, np.full(len(x1), 1), '--', color = 'k')
    a = ax.set_xticks(x)
    a = ax.set_xticklabels(plot_list)
    ax.tick_params(axis = 'x', labelrotation = -90)
    autolabel(rects1, ax, '{:.1f}')
    ymax = np.ceil(np.max(y)) + 1
    ax.set_ylim([-0.5, ymax])
    a = ax.set_title('Growth Factors')
    ax.set_xlim([-1, len(x) + 0.5])


    ############ fatality rate ############
    ax = fig.add_subplot(gs[3, 4:])
    print("8,", end = " ")
    
    df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    plot_list = list(df_confirmed.index[0:num_barplot])
    # plot_list = [ele for ele in df_confirmed.index if df_confirmed.loc[ele,time_datetime[-1]] >= 500]
    fatal_rates = df_deaths.loc[plot_list,time_datetime] / df_confirmed.loc[plot_list,time_datetime] * 100
    x = np.arange(len(plot_list))
    x1 = np.arange(-2, len(x)+2)
    fr_total = np.sum(df_deaths.loc[:,time_datetime[-1]]) / np.sum(df_confirmed.loc[:,time_datetime[-1]]) * 100
    y = fatal_rates.loc[plot_list,time_datetime[-1]]

    rects1 = ax.bar(x[y<=fr_total], y[y<=fr_total], color = 'tab:grey')
    rects2 = ax.bar(x[y>fr_total], y[y>fr_total], color = 'tab:red')
    ax.plot(x1, np.full(len(x1), fr_total), '--', color = 'k')
    a = ax.set_xticks(x)
    a = ax.set_xticklabels(plot_list)
    ax.tick_params(axis = 'x', labelrotation = -90)
    autolabel(rects1, ax, '{:.1f}')
    autolabel(rects2, ax, '{:.1f}')
    ymax = np.ceil(np.max(fatal_rates.loc[:,time_datetime[-1]]) + 1)
    ax.set_ylim([0, ymax])
    ax.set_xlim([-1, len(x) + 0.5])
    a = ax.set_title(f'CFRs: global mean = {fr_total:.2f}%')

    ########## r for logistic growth fit ############
    ax = fig.add_subplot(gs[4, 0:4])
    print("9:", end = " ")
    
    df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    plot_list = list(df_confirmed.index[0:num_barplot])

    x = np.arange(len(plot_list))
    x1 = np.arange(-2, len(x)+2)
    # if not 'rs_global' in locals():
    rs_global = []
    for i in x:
        print(f'{i}-', end = "")
        ele = plot_list[i]
        df_ele = pd.DataFrame(df_confirmed.loc[ele,time_datetime])
        df_ele = my_func.reshape_dataframe(df_ele, time_datetime)
        rs_global.append(get_growth_rate(df_ele, time_datetime))
    rs_global = np.array(rs_global)

    rects = ax.bar(x[rs_global<1], rs_global[rs_global<1], color = 'tab:grey')
    ax.bar(x[rs_global>=1], rs_global[rs_global>=1], color = 'tab:grey')
    ax.plot(x1, np.full(len(x1), np.median(rs_global)), '--', color = 'k')
    a = ax.set_xticks(x)
    a = ax.set_xticklabels(plot_list)
    ax.tick_params(axis = 'x', labelrotation = -90)
    autolabel(rects, ax, '{:.2f}')
    ax.set_ylim([0, 1])
    ax.set_xlim([-1, len(x) + 0.5])
    a = ax.set_title(f'Logistic fitted r, median = {np.median(rs_global):.2f}')

    plt.tight_layout()

def plot_confirmed_per_over_time(df_us_confirmed, n, time_datetime):
    def format_fn(tick_val, tick_pos):
        if(tick_val >= 0 and tick_val < len(time_datetime)):
            return time_str[int(tick_val)]
        else:
            return None
        
    labels = []
    percentages = np.zeros((len(time_datetime), n+1))
    total_labels = []
    label_lists = []
    for x in range(len(time_datetime)):
        time = time_datetime[x]
        df_us_confirmed.sort_values(by = time, inplace = True, ascending=False)
        us_confirmed_total = np.sum(df_us_confirmed.loc[:,time])
        ll = []
        for i, state in enumerate(df_us_confirmed.index[0:n]):
            if(df_us_confirmed.loc[state, time] > 0):
                ll.append(state)
                label_lists.append(state)
            else:
                ll.append('')
            percentages[x,i] = (df_us_confirmed.loc[state, time]/us_confirmed_total*100)
        percentages[x,n] = (100-np.sum(percentages[x,:]))
        ll.append('Others')
        total_labels.append(ll)
    label_lists = list(set(label_lists))
    
    colors_bar = get_colors(len(label_lists))
    color_codes = {}
    for i, label in enumerate(label_lists):
        color_codes[label] = colors_bar[i]
    label_lists.append('Others')
    color_codes['Others'] = [0.85, 0.85, 0.85, 1]
    
    is_label = {}
    for label in label_lists:
        is_label[label] = 1
    fix, ax = plt.subplots(1,1, figsize = (15,5))
    legend = []
    
    for x in range(len(time_datetime)):
        print(f'{x}-', end = "")
        state = total_labels[x][0]
        if(is_label[state] == 1):
            plt.bar(x, percentages[x, 0], color = color_codes[state])
            legend.append(state)
            is_label[state] = 0
        else:
            plt.bar(x, percentages[x, 0], color = color_codes[state], label='_nolegend_')
        for i, percent in enumerate(percentages[x, 1:]):
            state = total_labels[x][i+1]
            if(state):
                if(is_label[state] == 1):
                    plt.bar(x, percent, bottom = np.sum(percentages[x, 0:i+1]), color = color_codes[state])
                    legend.append(state)
                    is_label[state] = 0
                else:
                    plt.bar(x, percent, bottom = np.sum(percentages[x, 0:i+1]), color = color_codes[state], label='_nolegend_')
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_fn))
    myLocator = mticker.MultipleLocator(4)
    ax.xaxis.set_major_locator(myLocator)
    ax.tick_params(axis = 'x', labelrotation = 45)
    ax.set_xlim([-1, len(time_datetime) + 0.5])
    ax.set_ylabel('Percentage')
    plt.title('Percent of confirmed cases by region over time')
    plt.legend(legend, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol= int(len(legend)/3))

"""world case vs. population"""
def get_residuals(df_fit, fit_intercept, cat_x, cat_y):
    X = np.array([df_fit[cat_x]]).transpose()
    y = df_fit[cat_y].to_numpy()
    reg = LinearRegression(fit_intercept = fit_intercept).fit(X, y)
    y_predicted = reg.predict(X)
    residuals = (y-y_predicted)
    df_fit.loc[:,'Residuals'] = residuals
    return df_fit, reg

def add_country_annotations(ax, p1, df_fit, countries, color, cat_x, cat_y):
    for ctry in countries:
        pos = [df_fit.loc[ctry, cat_x], 
                  df_fit.loc[ctry, cat_y]]
        ax.plot(pos[0], pos[1], 'o', color = color)
        p1.text(pos[0]+0.01, pos[1] +0.01, ctry, 
                horizontalalignment='left', size='medium', 
                color='black',weight='normal')
    return ax

def get_annotation_list(df_fit, key_countries, is_joint):
    countries = []
    if(is_joint):
        countries += list(df_fit.sort_values(by = 'Residuals').index[-3:])
        countries += list(df_fit.sort_values(by = 'Residuals').index[:3])
        countries += my_func.intersection(list(df_fit.index), key_countries)
        countries = list(set(countries))
    else:
        countries += list(df_fit.sort_values(by = 'Residuals').index[-5:])
        countries += list(df_fit.sort_values(by = 'Residuals').index[:5])
    return countries


def world_cases_vs_population(key_countries, df_ctry_today):
    
    fig = plt.figure(figsize = (15, 10), constrained_layout=True, facecolor="1")
    gs = fig.add_gridspec(2,3)


    ###
    ax = fig.add_subplot(gs[0,0])
    cat_x = 'Total_Confirmed'
    cat_y = 'New_Confirmed'
    df_fit = df_ctry_today[[cat_x, cat_y]]
    df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
    p1 = sns.regplot(data = df_fit, 
                     x = cat_x, y = cat_y, ax = ax, scatter_kws={'alpha':0.3})
    df_fit, reg = get_residuals(df_fit, False, cat_x, cat_y)
    countries = get_annotation_list(df_fit, key_countries, True)
    ax = add_country_annotations(ax, p1, df_fit, countries, 'tab:blue', cat_x, cat_y)
    ax.set_xscale('log')
    ax.set_yscale('log')
    # ax.set_title(f'All countries: \n {cat_x} vs {cat_y} \n y={10**reg.intercept_:.2f}*x^{reg.coef_[0]:.1f}' )
    ax.set_title(f'All countries: \n {cat_x} vs {cat_y} \n y={reg.coef_[0]:.2f}*x')

    ###
    ax = fig.add_subplot(gs[1,0])
    cat_x = 'Total_Confirmed'
    cat_y = 'Total_Deaths'

    df_fit = df_ctry_today.loc[df_ctry_today.Total_Confirmed>100, [cat_x, cat_y]]
    df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
    p1 = sns.regplot(data = df_fit, 
                     x = cat_x, y = cat_y, ax = ax, scatter_kws={'alpha':0.3})
    df_fit, reg = get_residuals(df_fit, True, cat_x, cat_y)
    countries = get_annotation_list(df_fit, key_countries, True)
    ax = add_country_annotations(ax, p1, df_fit, countries, 'tab:blue', cat_x, cat_y)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title(f'Countries w/ confirmed cases >100: \n {cat_x} vs {cat_y}\n y={reg.coef_[0]:.2f}*x')

    ###
    cat_x = 'Population'
    cat_y = 'Pos_per_Million'
    cat = 'Confirmed_Cat'

    df_fit = np.log10(df_ctry_today[[cat_x, cat_y]])
    df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
    df_fit[cat] = df_ctry_today[cat]
    cats = list(set(df_ctry_today[cat]))

    for i in [0,1]:
        ax = fig.add_subplot(gs[i, 1])
        if(i == 0):
            df_fit = np.log10(df_ctry_today[[cat_x, cat_y]])
            df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
            df_fit[cat] = df_ctry_today[cat]
            for icat in cats:
                p1 = sns.regplot(data = df_fit[df_fit[cat] == icat], 
                            x = cat_x, y = cat_y, ax = ax)
            ax.legend(cats, title = cat)
            ax.set_title(f'All countries:\n{cat_x} vs {cat_y}')
        if(i == 1):
            icat = [i for i in cats if 'above' in i][0]
            df_fit = np.log10(df_ctry_today.groupby(cat).get_group(icat)[[cat_x, cat_y]])
            df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
            if(cats.index(icat) == 0):
                color = 'tab:blue'
            else:
                color = 'tab:orange'
            p1 = sns.regplot(data = df_fit, 
                            x = cat_x, y = cat_y, ax = ax, color = color, scatter_kws={'alpha':0.3})
            # ax.set_title(f'Confirmed cases {icat}:\n{cat_x} vs {cat_y}\n y={10**reg.intercept_:.2f}*x^{reg.coef_[0]:.1f}')
            ax.set_title(f'Confirmed cases {icat}:\n{cat_x} vs {cat_y}')
            df_fit, reg = get_residuals(df_fit, True, cat_x, cat_y)
            ax = add_country_annotations(ax, p1, df_fit, key_countries, color, cat_x, cat_y)


    ##
    cat_x = 'Total_Confirmed'
    cat_y = 'Pos_per_Million'
    cat = 'Population_Cat'

    df_fit = np.log10(df_ctry_today[[cat_x, cat_y]])
    df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
    df_fit[cat] = df_ctry_today[cat]
    cats = list(set(df_ctry_today[cat]))

    for i in [0,1]:
        ax = fig.add_subplot(gs[i, 2])
        if(i == 0):
            df_fit = np.log10(df_ctry_today[[cat_x, cat_y]])
            df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
            df_fit[cat] = df_ctry_today[cat]
            for icat in cats:
                p1 = sns.regplot(data = df_fit[df_fit[cat] == icat], 
                            x = cat_x, y = cat_y, ax = ax)
            ax.legend(cats, title = cat)
            ax.set_title(f'All countries:\n{cat_x} vs {cat_y}')
        if(i == 1):
            ax = fig.add_subplot(gs[i,2])
            icat = [i for i in cats if 'above' in i][0]
            df_fit = np.log10(df_ctry_today.groupby(cat).get_group(icat)[[cat_x, cat_y]])
            df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")

            if(cats.index(icat) == 0):
                color = 'tab:blue'
            else:
                color = 'tab:orange'

            p1 = sns.regplot(data = df_fit, 
                            x = cat_x, y = cat_y, ax = ax, color = color, scatter_kws={'alpha':0.3})
            # ax.set_title(f'Population {icat}:\n{cat_x} vs {cat_y}\n y={10**reg.intercept_:.2f}*x^{reg.coef_[0]:.1f}')
            ax.set_title(f'Population {icat}:\n{cat_x} vs {cat_y}')
            df_fit, reg = get_residuals(df_fit, True, cat_x, cat_y)
            countries = get_annotation_list(df_fit, key_countries, True)
            ax = add_country_annotations(ax, p1, df_fit, countries, color, cat_x, cat_y)

"""China"""
def plot_china_prov(df_mc_confirmed, df_mc_deaths, df_hb, df_co, **kwarg):
    ######### unravel params
    if('is_fitting' in kwarg.keys()):
        is_fitting = kwarg['is_fitting']
        if('fitting_params' in kwarg.keys()):
            fitting_params = kwarg['fitting_params']
        else:
            fitting_params = {}
    else:
        is_fitting = False
    if('plotting_params' in kwarg.keys()):
        plotting_params = kwarg['plotting_params']
    else:
        cat_color = {'Confirmed':'tab:blue',
                    'Deaths':'tab:orange', 
                    'Recovered':'tab:green', 
                    'Active':'tab:red'}
        plotting_params = {
            'figsize':(15, 15),
            'time_series_cols' : ['Confirmed', 'Deaths', 'Recovered', 'Active'],
            'locator_param' : 4,
            'num_of_rols' : 6,
            'cat_color' : cat_color
        }
    time_datetime = list(df_prov.index)

    fig = plt.figure(figsize = plotting_params['figsize'], constrained_layout=True, facecolor="1")
    gs = fig.add_gridspec(plotting_params['num_of_rols'],2)
    
    ############ China confirmed pie chart
    ax = fig.add_subplot(gs[0,0])

    df_mc_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    percentages = []
    labels = []
    df_mc_confirmed_total = np.sum(df_mc_confirmed.loc[:,time_datetime[-1]])
    for iprov in df_mc_confirmed.index[0:10]:
        percentages.append(df_mc_confirmed.loc[iprov, time_datetime[-1]]/df_mc_confirmed_total*100)
        labels.append(iprov)
    labels.append('Rest')
    percentages.append(100-sum(percentages))

    colors = get_colors(len(labels), is_last_grey = True)
    wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
                                      autopct = my_autopct, pctdistance=0.8,
                                      shadow=False, startangle=90,
                                      textprops = dict(size = 12))
    ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0, 1))
    ax.axis('equal')
    ax.set_title("Total Confirmed Cases in China")

    ############ China deaths pie chart
    ax = fig.add_subplot(gs[0,1])

    df_mc_deaths.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
    percentages = []
    labels = []
    df_mc_deaths_total = np.sum(df_mc_deaths.loc[:,time_datetime[-1]])
    for iprov in df_mc_deaths.index[0:10]:
        percentages.append(df_mc_deaths.loc[iprov, time_datetime[-1]]/df_mc_deaths_total*100)
        labels.append(iprov)
    labels.append('Rest')
    percentages.append(100-sum(percentages))

    colors = get_colors(len(labels), is_last_grey = True)
    wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
                                      autopct = my_autopct, pctdistance=0.8,
                                      shadow=False, startangle=90,
                                      textprops = dict(size = 12))
    ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0, 1))
    ax.axis('equal')
    ax.set_title("Total Deaths in China")

    x = np.arange(len(time_datetime))
    y1 = df_hb.Confirmed.to_list()
    y2 = df_co.Confirmed.to_list()
    y3 = df_hb.Deaths.to_list()
    y4 = df_co.Deaths.to_list()

    ind_t0 = len(time_datetime)
    t = np.arange(len(time_datetime))[:ind_t0]
    pt1 = y1[:ind_t0]
    pt2 = y2[:ind_t0]

    # popt_exp, pcov_exp = opt.curve_fit(exp_growth,  t,  p_t)
    popt1, pcov1 = opt.curve_fit(my_func.logistic_growth,  t,  pt1, maxfev=10000)
    # popt1, pcov1 = opt.curve_fit(my_func.logistic_growth,  t,  pt, p0 = [0.1, 100, 1], maxfev=10000)
    popt2, pcov2 = opt.curve_fit(my_func.logistic_growth,  t,  pt2, maxfev=10000)
    popt3, pcov3 = opt.curve_fit(my_func.logistic_growth,  x,  y3, maxfev=10000)
    popt4, pcov4 = opt.curve_fit(my_func.logistic_growth,  x,  y4, maxfev=10000)
    
    future = 0
    x1 = np.arange(len(x) + future)
    xt1 = time_datetime
    xt2 = my_func.get_datetime_arange(time_datetime[0], len(x1))

    ax1 = fig.add_subplot(gs[1, 0])
    plt.plot(xt1, y1, '.', ms = 10, color = plotting_params['cat_color']['Confirmed'])
    plt.plot(xt2, my_func.logistic_growth(x1, popt1[0], popt1[1], popt1[2]), '-', color = plotting_params['cat_color']['Confirmed'])
    c1_end = my_func.logistic_growth(x1, popt1[0], popt1[1], popt1[2])[-1]
    plt.plot(xt1, y3, '*', ms = 10, color = plotting_params['cat_color']['Deaths'])
    plt.plot(xt2, my_func.logistic_growth(x1, popt3[0], popt3[1], popt3[2]), '-', color = plotting_params['cat_color']['Deaths'])
    d1_end = my_func.logistic_growth(x1, popt3[0], popt3[1], popt3[2])[-1]

    plt.title(f'Logistic Growth Fit for Hubei, r = {popt1[0]:.2f}')
    myLocator = mticker.MultipleLocator(4)
    ax1.xaxis.set_major_locator(myLocator)
    ax1.tick_params(axis = 'x', labelrotation = 45)
    # _ = ax1.set_xlim(right = len(time_datetime))
    ax1.legend(['Confirmed', 
                f'Confirmed Logistic Fit: {c1_end:.0f}', 
                'Deaths', 
                f'Deaths Logistic Fit: {d1_end:.0f}'])


    ax2 = fig.add_subplot(gs[1, 1])
    plt.plot(x, y2, '.', ms = 10, color = plotting_params['cat_color']['Confirmed'])
    plt.plot(x1, my_func.logistic_growth(x1, popt2[0], popt2[1], popt2[2]), '-', color = plotting_params['cat_color']['Confirmed'])
    c2_end = my_func.logistic_growth(x1, popt2[0], popt2[1], popt2[2])[-1]
    plt.plot(x, y4, '*', ms = 10, color = plotting_params['cat_color']['Deaths'])
    plt.plot(x1, my_func.logistic_growth(x1, popt4[0], popt4[1], popt4[2]), '-', color = plotting_params['cat_color']['Deaths'])
    d2_end = my_func.logistic_growth(x1, popt4[0], popt4[1], popt4[2])[-1]

    plt.title(f'Logistic Growth Fit for Other Chinese Provs, r = {popt2[0]:.2f}')
    myLocator = mticker.MultipleLocator(4)
    ax2.xaxis.set_major_locator(myLocator)
    ax2.tick_params(axis = 'x', labelrotation = 45)
    ax2.legend(['Confirmed', 
                f'Confirmed Logistic Fit: {c2_end:.0f}', 
                'Deaths', 
                f'Deaths Logistic Fit: {d2_end:.0f}'])
