# -*- coding: utf-8 -*-
# @Author: lily
# @Date:   2020-04-04 17:09:18
# @Last Modified by:   lily
# @Last Modified time: 2020-04-20 18:47:20
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
### label bar plot
def autolabel(rects, ax, str_format):
	######################################################
	### Function: Attach a text label above each bar in *rects*, displaying its height
	### source: https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html
	### input: 
		### rects: output from plt.bar
		### ax
		### str_format: string format. e.g. '{:.2f}'
	### output: manipulate image directly.
	######################################################

	for rect in rects:
		height = rect.get_height()
		if(height > 0):
			ax.annotate(str_format.format(height),
						xy=(rect.get_x() + rect.get_width() / 2, height),
						xytext=(0, 3),  # 3 points vertical offset
						textcoords="offset points",
						ha='center', va='bottom')

### pct settings when plotting pie plot.
def my_autopct(pct):
	######################################################
	### Function: plot .1f% if percent > 2%
	### Adapted from: https://stackoverflow.com/questions/6170246/how-do-i-use-matplotlib-autopct
	######################################################
	return ('%1.1f%%' % pct) if pct > 2 else ''

### getting colors that seperate the most based on number of colors needed
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

"""plot_region: get summary plots of a particular region"""
def get_logistic_params(t, pt, **kwarg):
	
	if('maxfev' in kwarg.keys()):
		maxfev = kwarg['maxfev']
	else:
		maxfev = 100000
	if('bounds' in kwarg.keys()):
		bounds = kwarg['bounds']
	else:
		bounds = (-np.inf, np.inf)
	if('plot_range' in kwarg.keys()):
		plot_range = kwarg['plot_range']
	else:
		plot_range = True
	if(plot_range):
		popt_log = np.zeros((3,3))
		r2 = np.zeros(3)
	else:
		popt_log = np.zeros((1,3))
		r2 = np.zeros(1)
	if('p0' in kwarg.keys()):
		if(plot_range):
			popt_log[0,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t,  pt, p0 = kwarg['p0'], maxfev = maxfev, bounds = bounds)
			popt_log[1,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-1],  pt[:-1], p0 = kwarg['p0'], maxfev = maxfev, bounds = bounds)
			popt_log[2,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-2],  pt[:-2], p0 = kwarg['p0'], maxfev = maxfev, bounds = bounds)
		else:
			popt_log[0,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t,  pt, p0 = kwarg['p0'], maxfev = maxfev, bounds = bounds)
	else:
		if(plot_range):
			popt_log[0,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t,  pt, maxfev = maxfev, bounds = bounds)
			popt_log[1,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-1],  pt[:-1], maxfev = maxfev, bounds = bounds)
			popt_log[2,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t[:-2],  pt[:-2], maxfev = maxfev, bounds = bounds)
		else:
			popt_log[0,:], pcov_log = opt.curve_fit(my_func.logistic_growth,  t,  pt, maxfev = maxfev, bounds = bounds)
	for i in np.arange(popt_log.shape[0]):
		r2[i] = my_func.get_r_squared(t, pt, popt_log[i,:], 'logistic_growth')

	# print(popt_log)
	return popt_log, r2

def plot_predictions(ax1, tx0, y0, dy0, x1, tx1, popt_logs, scale_factor, color, plot_range):
	if(plot_range):
		i_range = [0,1,2]
	else:
		i_range = [0]
	ys = np.zeros((len(x1), 3))
	df = pd.DataFrame(columns = ['x', 'y'])
	for i in i_range:
		df_tmp = pd.DataFrame(columns = ['x', 'y'])
		df_tmp['x'] = tx1
		df_tmp['y'] = my_func.logistic_growth(x1, *popt_logs[i,:]) / scale_factor
		ys[:,i] = my_func.logistic_growth(x1, *popt_logs[i,:]) / scale_factor
		df = df.append(df_tmp)
	sns.set(style = 'ticks', rc={"lines.linewidth": 2})
	ax2 = ax1.twinx()
	for i in i_range:
		ax2.bar(tx1[1:], ys[1:,i] - ys[:-1, i], alpha = 0.2, color = 'grey')
	ax2.plot(tx0, dy0, '--', color = color)
	ax1.plot(tx0, y0, '.', color = color)
	sns.lineplot(x='x', y='y', data = df, ax = ax1, color = color)
	ax1.set_ylim(bottom = 0)
	ax2.set_ylim(bottom = 0)
	y_ends = ys[-1,:]
	ind_midds = np.zeros((1,3))-1
	ind_maxes = np.zeros((1,3))-1
	for i in i_range:
		ind_midds[0,i] = int(list(ys[1:,i] - ys[:-1, i]).index(max(ys[1:,i] - ys[:-1, i])
			))
		if(len(np.argwhere(np.abs(np.diff(ys[int(ind_midds[0,i]):,i]) < 1)))):
			ind_maxes[0,i] = np.argwhere(np.abs(np.diff(ys[int(ind_midds[0,i]):,i]) < 1))[0] + ind_midds[0,i]
	ax1.set_xlabel('Time')
	ax1.set_ylabel('Total')
	ax2.set_ylabel('Daily')
	ax1.legend(['Total Data', 'Logistic Fit'], loc = 'upper left')
	ax2.legend(['Daily Data', 'Daily Fitted'], loc = 'center left')
	return ax1, ax2, y_ends, ind_midds, ind_maxes

def plot_region(df_region, region_name, **kwarg):
	######################################################
	### Function: plot time_series, stats, and fit information of a time_series data of a particular region
	### Input:
		### df_region(dataframe): output from reshape_dataframe. index = datetime
		### region_name(string): name of region
		### additional params
			### is_fitting (True/False): default = False
			### fitting_params (dic)
				# future = 0
				# p0_exp = (1,1)
				# p0_log = (1,1,1)
				# maxfev = 100000
				# bounds_c = (-np.inf, np.inf)
				# bounds_d = (-np.inf, np.inf)
				# death_to_confirmed = False
				# CFR = df_region.CFR[-1]/100
				# thr_c = "rolling", "total", "int(ind)"
				# thr_d = "rolling", "total", "int(ind)"
			### plotting_params (dic): default as below.
				# 'figsize':(15, 15),
				# 'time_series_cols' : ['Confirmed', 'Deaths', 'Recovered', 'Active'],
				# 'locator_param' : 4,
				# 'locator_param_future':8,
				# 'num_of_rols' : 6,
				# 'cat_color' : {'Confirmed':'tab:blue',
				#                 'Deaths':'tab:orange', 
				#                 'Recovered':'tab:green', 
				#                 'Active':'tab:red'}
	### Output: Figure. Total, Daily, Growth Factor, CFR, confirmed/death fits
	######################################################
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
	ax.set_ylim([0, min(2.5, max(np.max(df_region.GFc_rolling) + 0.5, np.max(df_region.GFd_rolling) + 0.5))])
	
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
		if('plot_range' in fitting_params.keys()):
			plot_range = fitting_params['plot_range']
		else:
			plot_range = True

		### fitting data
		y_c = df_region.Confirmed.to_numpy()
		y_d = df_region.Deaths.to_numpy()
		
		if('thr_c' in fitting_params.keys()):
			if(np.char.isnumeric(fitting_params['thr_c'])):
				ind_tc = int(fitting_params['thr_c'])
			elif(fitting_params['thr_c'] == 'total'):
				res_c = df_region[df_region.Confirmed > 100].index[0]
				ind_tc = min(max(0, time_datetime.index(res_c)-3), len(time_datetime)-20)
			elif(fitting_params['thr_c'] == 'rolling'):
				res_c = df_region[df_region.GFc_thr != 0.0].bfill(axis=1).index[0]
				ind_tc = min(max(0, time_datetime.index(res_c)-3), len(time_datetime)-20)
		else:
			res_c = df_region[df_region.GFc_thr != 0.0].bfill(axis=1).index[0]
			ind_tc = min(max(0, time_datetime.index(res_c)-3), len(time_datetime)-20)
		if('thr_d' in fitting_params.keys()):
			if(fitting_params['thr_d'] == 'total'):
				res_d = df_region[df_region.Deaths > 10].index[0]
			elif(fitting_params['thr_d'] == 'rolling'):
				res_d = df_region[df_region.GFd_thr != 0.0].bfill(axis=1).index[0]
			ind_td = min(max(0, time_datetime.index(res_d)-3), len(time_datetime)-20)
		else:
			ind_td = ind_tc
		
		tc = np.arange(len(time_datetime))[ind_tc:] - ind_tc
		td = np.arange(len(time_datetime))[ind_td:] - ind_td
		pt_c = y_c[ind_tc:]
		pt_d = y_d[ind_td:]

		popt_exp_c, _ = opt.curve_fit(my_func.exp_growth,  tc,  pt_c, p0 = p0_exp, maxfev = maxfev)
		r2_exp_c = my_func.get_r_squared(tc, pt_c, popt_exp_c, 'exp_growth')
		popt_exp_d, _ = opt.curve_fit(my_func.exp_growth,  td,  pt_d, p0 = p0_exp, maxfev = maxfev)
		r2_exp_d = my_func.get_r_squared(td, pt_d, popt_exp_d, 'exp_growth')
		if(future != 0):
			popt_logs_c, r2_logs_c = get_logistic_params(tc, pt_c, p0 = p0_log, maxfev = maxfev, bounds = bounds_c, plot_range = plot_range)
			popt_logs_d, r2_logs_d = get_logistic_params(td, pt_d, p0 = p0_log, maxfev = maxfev, bounds = bounds_d, plot_range = plot_range)
		else:
			popt_logs_c, _ = opt.curve_fit(my_func. logistic_growth,  tc,  pt_c, p0 = p0_log, maxfev = maxfev, bounds = bounds_c)
			r2_logs_c = my_func.get_r_squared(tc, pt_c, popt_logs_c, 'logistic_growth')
			popt_logs_d, _ = opt.curve_fit(my_func. logistic_growth,  td,  pt_d, p0 = p0_log, maxfev = maxfev, bounds = bounds_d)
			r2_logs_d = my_func.get_r_squared(td, pt_d, popt_logs_d, 'logistic_growth')


		### confirmed fitting plot
		ax = fig.add_subplot(gs[2, 0])
		x = np.arange(len(time_datetime))
		x1 = np.arange(len(tc) + future)
		tx = my_func.get_datetime_arange(time_datetime[0], len(time_datetime))
		tx1 = my_func.get_datetime_arange(time_datetime[ind_tc], len(tc) + future)

		if(future == 0):
			ax.plot(tx, y_c, '.', ms = 10, color = plotting_params['cat_color']['Confirmed'])
			ax.plot(tx1, my_func.exp_growth(x1, *popt_exp_c), '--', color = plotting_params['cat_color']['Confirmed'])
			ax.plot(tx1, my_func. logistic_growth(x1, *popt_logs_c), color = plotting_params['cat_color']['Confirmed'])
			ax.set_ylim([0, np.ceil(y_c[-1] + y_c[-1]/10)])
		else:
			dy_c = df_region.Daily_Confirmed_smoothed
			ax1, ax2, y_ends, ind_midds, ind_maxes = plot_predictions(ax, tx, y_c, dy_c, x1, tx1, popt_logs_c, 1, plotting_params['cat_color']['Confirmed'], plot_range = plot_range)
			date_midds = []
			date_maxs = []
			for k in [0,1]:
				if(k == 0):
					ind_mid = int(np.min(ind_midds))
					ind_max = int(np.min(ind_maxes))
				else:
					ind_mid = int(np.max(ind_midds))
					ind_max = int(np.max(ind_maxes))
				date_midds.append(time_datetime[ind_tc] + timedelta(days=ind_mid))
				date_maxs.append(time_datetime[ind_tc] + timedelta(days=ind_max))
			confirmed_total = np.mean(y_ends)
		if(future == 0):
			ax.legend(['Confirmed', 
						f'Exp Fit: R2 = {r2_exp_c:.2f}', 
						f'Logistic Fit: R2 = {r2_logs_c:.2f}'])
			ax.set_title(f'{region_name} Confirmed Fit: r = {popt_exp_c[0]:.2f}/{popt_logs_c[0]:.2f}', fontsize = 14)
		else:
			if(plot_range):
				ax.set_title(f'{region_name} Confirmed Prediction: K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}', fontsize = 14)
			else:
				ax.set_title(f'{region_name} Confirmed Prediction: K = {np.max(y_ends):,.0f}', fontsize = 14)
			pp = f'{region_name} Confirmed cases: max daily increase at {df_region[df_region.Daily_Confirmed_smoothed == np.max(df_region.Daily_Confirmed_smoothed)].index[-1].date()}, '
			if(df_region.GFc_rolling[-1]<1):
				pp += f'new cases decreasing since {(df_region[df_region.GFc_rolling>1].index[-1] + timedelta(days=1)).date()}. '
			else:
				pp += f'GF > 1 for today ({time_datetime[-1].date()}). '
			pp += f'Prediction: r={np.mean(popt_logs_c[:,0]):.2f}, '
			if(plot_range):
				pp += f'K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}, '
				pp += f'R^2 = {np.max(r2_logs_c):.2f} ~ {np.min(r2_logs_c):.2f}; '
				pp += f'Predicted peak increase at {date_midds[0].date()} ~ {date_midds[1].date()}, '
			else:
				pp += f'K = {np.max(y_ends):,.0f}, '
				pp += f'R^2 = {r2_logs_c[0]:.2f}; '
				pp += f'Predicted peak increase at {date_midds[1].date()}, '
			if(np.max(ind_maxes) == -1):
				pp += f'max will not be reached by {(time_datetime[-1] + timedelta(days=future)).date()}.'
			else:
				if(-1 not in ind_maxes):
					pp += f'max will be reached at {date_maxs[0].date()} ~ {date_maxs[1].date()}.'
				else:
					pp += f'max will be reached at {date_maxs[1].date()}.'
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
				ax.plot(tx1, my_func.exp_growth(x1, *popt_exp_d), '--', color = plotting_params['cat_color']['Deaths'])
				ax.plot(tx1, my_func. logistic_growth(x1, *popt_logs_d), color = plotting_params['cat_color']['Deaths'])
				ax.set_ylim([0, np.ceil(y_d[-1] + y_d[-1]/10)])
			else:
				dy_d = df_region.Daily_Deaths_smoothed
				ax1, ax2, y_ends, ind_midds, ind_maxes = plot_predictions(ax, tx, y_d, dy_d, x1, tx1, popt_logs_d, 1, plotting_params['cat_color']['Deaths'], plot_range = plot_range)
				date_midds = []
				date_maxs = []
				for k in [0,1]:
					if(k == 0):
						ind_mid = int(np.min(ind_midds))
						ind_max = int(np.min(ind_maxes))
					else:
						ind_mid = int(np.max(ind_midds))
						ind_max = int(np.max(ind_maxes))
					date_midds.append(time_datetime[ind_td] + timedelta(days=ind_mid))
					date_maxs.append(time_datetime[ind_td] + timedelta(days=ind_max))
				# print(date_max)
				deaths_total = np.mean(y_ends)
			if(future == 0):
				ax.legend(['Deaths', 
							f'Exp Fit: R2 = {r2_exp_d:.2f}', 
							f'Logistic Fit: R2 = {r2_logs_d:.2f}'])
				ax.set_title(f'{region_name} Deaths Fit: r = {popt_exp_d[0]:.2f}/{popt_exp_d[0]:.2f}', fontsize = 18)
			else:
				if(plot_range):
					ax.set_title(f'{region_name} Deaths Prediction: K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}', fontsize = 14)
				else:
					ax.set_title(f'{region_name} Deaths Prediction: K = {np.max(y_ends):,.0f}', fontsize = 14)
				pp = f'{region_name} Deaths: max daily increase at {df_region[df_region.Daily_Deaths_smoothed == np.max(df_region.Daily_Deaths_smoothed)].index[-1].date()}, '
				if(df_region.GFd_rolling[-1]<1):
					pp += f'new cases decreasing since {(df_region[df_region.GFd_rolling>1].index[-1] + timedelta(days=1)).date()}. '
				else:
					pp += f'GF > 1 for today ({time_datetime[-1].date()}). '

				pp += f'Prediction: r={np.mean(popt_logs_d[:,0]):.2f}, '
				if(plot_range):
					pp += f'K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}, '
					pp += f'R^2 = {np.max(r2_logs_d):.2f} ~ {np.min(r2_logs_d):.2f}; '
					pp += f'peak increase at {date_midds[0].date()} ~ {date_midds[1].date()}, '
				else:
					pp += f'K = {np.max(y_ends):,.0f}, '
					pp += f'R^2 = {r2_logs_d[0]:.2f}, '
					pp += f'Predicted peak increase at {date_midds[1].date()}, '
				pp += f'CFR = {deaths_total/confirmed_total*100:.2f}%; '
				if(np.max(ind_maxes) == -1):
					pp += f'max will not be reached by {(time_datetime[-1] + timedelta(days=future)).date()}.'
				else:
					if(-1 not in ind_maxes):
						pp += f'max will be reached at {date_maxs[0].date()} ~ {date_maxs[1].date()}.'
					else:
						pp += f'max will be reached at {date_maxs[1].date()}.'

				print(pp)
				
		myLocator = mticker.MultipleLocator(plotting_params['locator_param_future'])
		ax.xaxis.set_major_locator(myLocator)
		ax.tick_params(axis = 'x', labelrotation = 45)
		ax.set_xlim(left = time_datetime[0])
		
		### confirmed prediction based on death and current CFR
		if(future != 0 and death_to_confirmed and y_d[-1] > 50):
			ax = fig.add_subplot(gs[3, 0])
			ax1, ax2, y_ends, ind_midds, ind_maxes = plot_predictions(ax, tx, y_c, dy_c, x1, tx1, popt_logs_d, cfr, plotting_params['cat_color']['Confirmed'], plot_range = plot_range)
			date_midds = []
			date_maxs = []
			for k in [0,1]:
				if(k == 0):
					ind_mid = int(np.min(ind_midds))
					ind_max = int(np.min(ind_maxes))
				else:
					ind_mid = int(np.max(ind_midds))
					ind_max = int(np.max(ind_maxes))
				date_midds.append(time_datetime[ind_tc] + timedelta(days=ind_mid))
				date_maxs.append(time_datetime[ind_tc] + timedelta(days=ind_max))
			confirmed_total = np.mean(y_ends)
			
			if(plot_range):
				ax.set_title(f'{region_name} Confirmed projection (based on CFR = {cfr*100:.1f}%)\nK = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}')
			else:
				ax.set_title(f'{region_name} Confirmed projection (based on CFR = {cfr*100:.1f}%)\nK = {np.max(y_ends):,.0f}')
			pp = f'{region_name} Confirmed Prediction (based on CFR = {cfr*100:.1f}%): '
			if(plot_range):
				pp += f'K = {np.min(y_ends):,.0f}~{np.max(y_ends):,.0f}, '
				pp += f'peak increase at {date_midds[0].date()} ~ {date_midds[1].date()}, '

			else:
				pp += f'K = {np.max(y_ends):,.0f}, '
				pp += f'peak increase at {date_midds[1].date()}, '
			if(np.max(ind_maxes) == -1):
				pp += f'max will not be reached by {(time_datetime[-1] + timedelta(days=future)).date()}.'
			else:
				if(-1 not in ind_maxes):
					pp += f'max will be reached at {date_maxs[0].date()} ~ {date_maxs[1].date()}.'
				else:
					pp += f'max will be reached at {date_maxs[1].date()}.'
			print(pp)

			myLocator = mticker.MultipleLocator(plotting_params['locator_param_future'])
			ax.xaxis.set_major_locator(myLocator)
			ax.tick_params(axis = 'x', labelrotation = 45)
			ax.set_xlim(left = time_datetime[0])

"""Pie charts by continent"""
def plot_continents(df_continents):
	######################################################
	### Function: pie charts of cumulative data divided by continent.
	### Input: df_continents(DataFrame): columns = ['Total_Confirmed', 'New_Confirmed', 'Total_Deaths', 'New_Deaths','Population', 'Land Area', 'Pos_per_Million']
	### Output: Figure, with pie chart of new and total confirmed/deaths cases by continent.
	######################################################
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
	fig.subplots_adjust(left=0.0,right=0.95)

"""us tests"""
def plot_tests_bar_and_percent(ax1, x, y1, y2, color1, color2):
	ax2 = ax1.twinx()
	for i, cat in enumerate(y1.columns):
		ax1.bar(x, y1[cat], color = color1[i], alpha = 0.8)
	ax2.plot(x, y2, linewidth = 2, color = color2)
	ax1.legend(['Negative', 'Positive'], loc = 'upper left')
	ax2.legend(['%positive'], loc = 'upper center')
	ax1.set_ylabel('Number of tests')
	ax2.set_ylabel('Positive%')
	return ax1, ax2

def tests_us_vs_state(df_tests_us_daily, df_tests_onestate_daily, df_us, df_st, state, **kwargs):
		
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
											  'k')
		myLocator = mticker.MultipleLocator(4)
		ax.xaxis.set_major_locator(myLocator)
		ax.tick_params(axis = 'x', labelrotation = 45)
		ax.set_title(f'{plt_title} tests performed')
		if('yscales' in kwargs.keys()):
			ax.set_yscale(kwargs['yscales'][1])


		### daily increase
		ax = fig.add_subplot(gs[1, i])
#         ax.bar(x, df_test.totalTestResultsIncrease, color = 'grey')
#         ax.set_yscale('linear')
		ax1, ax2 = plot_tests_bar_and_percent(ax, x, 
											  df_test.loc[:,['totalTestResultsIncrease', 'positiveIncrease']], 
											  df_test.positiveIncrease/df_test.totalTestResultsIncrease*100,
											  [cat_color['Negative'], cat_color['Positive']],
											  'k')
		myLocator = mticker.MultipleLocator(4)
		ax.xaxis.set_major_locator(myLocator)
		ax.tick_params(axis = 'x', labelrotation = 45)
		ax.set_title(f'{plt_title} daily tests performed')
		ax.set_ylabel('Number of tests')
		if('yscales' in kwargs.keys()):
			ax1.set_yscale(kwargs['yscales'][2])

		### tests vs. positive
		ax = fig.add_subplot(gs[2, i])
		sns.regplot(data = df_test, x = 'positive', y = 'totalTestResults')
		sns.regplot(x = df_plot.loc[df_test.index, 'Confirmed'], y = df_test.totalTestResults)
		ax.set_yscale('linear')
		ax.legend(['Reported positive test cases', 'Reported confirmed cases'])
		ax.set_xlabel('Toatal number of cases')
		ax.set_ylabel('Total number of tests')
		if('yscales' in kwargs.keys()):
			ax.set_yscale(kwargs['yscales'][3])


def plot_us_tests_by_state(df_us_tests, df_tests_states_daily, df, num_states, usstate_abbs_mapping):
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
	
	states_list = list(df.index[0:num_states])
	
	for i, state in enumerate(states_list):
		print(i, end =" ")
		st = usstate_abbs_mapping[state]
		df_test = df_tests_states_daily.groupby('state').get_group(st)
		df_test.sort_values(by = 'date', inplace = True, ascending=True)
		df_test.set_index('date', inplace = True)

		x = np.arange(len(df_test.index))
		ax1.plot(df_test.positive/df_test.totalTestResults*100)
		ax2.plot(df_test.totalTestResultsIncrease, label='_nolegend_')
		sns.lineplot(data = df_test, x = 'totalTestResults', y = 'positive', ax = ax3)
		
		if(state != 'New York'):
			if(max_y3 < np.max(df_test.positive)):
				max_y3 = np.max(df_test.positive)
			if(max_x3 < np.max(df_test.totalTestResults)):
				max_x3 = np.max(df_test.totalTestResults)

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

def county_plot(df_today, states, num_counties, figsize, pct_type):
	def my_autopct_v2(pct):
		return f'{pct*total/100:.0f}({pct:1.1f}%)' if pct > 2 else ''

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
		total = np.sum(df_state.Confirmed)
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

		if(pct_type == 1):
			ax.pie(percentages, colors = colors,
				   labels=labels, autopct = my_autopct, 
				   pctdistance=0.8, labeldistance = 1.05,
				   shadow=False, startangle=90,
				   textprops = dict(size = 12))
		elif(pct_type == 2):
			ax.pie(percentages, colors = colors,
				   labels=labels, autopct = my_autopct_v2, 
				   pctdistance=0.7, labeldistance = 1.05,
				   shadow=False, startangle=90,
				   textprops = dict(size = 12))
		ax.axis('equal')
		ax.set_title(f"{state} confirmed cases: {np.sum(df_state.Confirmed):.0f} total")

		############ total deaths pie chart ############
		ax = fig.add_subplot(gs[i,2:4])

		df_state.sort_values(by = 'Deaths', inplace = True, ascending=False)
		percentages = []
		labels = []
		total = np.sum(df_state.Deaths)
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

		if(pct_type == 1):
			ax.pie(percentages, colors = colors,
				   labels=labels, autopct = my_autopct, 
				   pctdistance=0.8, labeldistance = 1.05,
				   shadow=False, startangle=90,
				   textprops = dict(size = 12))
		elif(pct_type == 2):
			ax.pie(percentages, colors = colors,
				   labels=labels, autopct = my_autopct_v2, 
				   pctdistance=0.7, labeldistance = 1.05,
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

"""plot different sub-regions of a region."""
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


### reformat county ticks
def reformat_xtick(county_list, stat_abbs_mapping):
	new_list = []
	for county in county_list:
		county_strip = [x.strip() for x in county.split(',')]
		# print(county_strip)
		if(len(county_strip) == 2):
			new_list.append(county_strip[0])
		else:
			ct = county_strip[0]
			st = stat_abbs_mapping[county_strip[1]]
			new_list.append(f'{ct}, {st}')
	return new_list

### plots for different sub-regions of a region
def plot_by_regions(df_confirmed, df_deaths, time_datetime, **kwarg):

	############ params ############
	if('num_lineplot' in kwarg.keys()):
		num_lineplot = kwarg['num_lineplot']
	else:
		num_lineplot = 10
	if('num_barplot' in kwarg.keys()):
		num_barplot = kwarg['num_barplot']
	else:
		num_barplot = 20
	if('yscales' in kwarg.keys()):
		yscales = kwarg['yscales']
	else:
		yscales = ['log', 'log', 'log', 'linear', 'log']
	if('k_lines' in kwarg.keys()):
		k_lines = kwarg['k_lines']
	else:
		k_lines = [0.2, 0.4, 0.2, 0.4, 0.2, 0.4, 0.2, 0.4]
	if('figsize' in kwarg.keys()):
		figsize = kwarg['figsize']
	else:
		figsize = (15, 35)
	if('is_format_xtick' in kwarg.keys()):
		is_format_xtick = kwarg['is_format_xtick']
	else:
		is_format_xtick = False
	if('stat_abbs_mapping' in kwarg.keys()):
		stat_abbs_mapping = kwarg['stat_abbs_mapping']

	color_special = 'k'

	############ figure ############
	fig = plt.figure(figsize = figsize, constrained_layout=True, facecolor="1", dpi = 72)
	# if('suptitle' in kwarg.keys()):
	# 	fig.suptitle(kwarg['suptitle'], fontsize=18, fontweight='bold')

	ncol = 2
	ncol_half = int(ncol/2)
	ncol_lh = int(ncol/2)
	gs = fig.add_gridspec(6, ncol)

	plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
	plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
	plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
	plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
	plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
	plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
	plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
	
	print("subplots:", end = " ")

	i_fig = -1
	############ case per million ############
	if('Per_Million' in df_confirmed):
		ax = fig.add_subplot(gs[2, 0:ncol_half])
		i_fig += 1
		print(i_fig, end = " ")
		
		df_confirmed.sort_values(by = 'Per_Million', inplace = True, ascending=False)
		plot_list = list(df_confirmed.index[0:num_lineplot])

		if('list_addins' in kwarg.keys()):
			plot_list += kwarg['list_addins']
			plot_list = list(set(plot_list))
			df_plot = df_confirmed.loc[plot_list,:].sort_values(by = 'Per_Million', ascending=False)
			plot_list = list(df_plot.index)
		df_plot = df_confirmed.loc[plot_list,time_datetime]

		colors = get_colors(len(plot_list))
		max_x = 0
		max_y = 0

		for i, ele in enumerate(plot_list):
			y = df_confirmed.loc[ele,time_datetime]/(df_confirmed.loc[ele,'Population']/MILLION)
			if(y[-1] > 100):
				xi = len(y[y>100])
				yi = max(y)
				if(xi > max_x and ele != 'China'):
					max_x = xi
				if(yi > max_y):
					max_y = yi
				if('special' in kwarg.keys()):
					if(ele == kwarg['special']):
						ax.plot(y[y>100].to_numpy(), linewidth = 3, color = color_special)
					else:
						ax.plot(y[y>100].to_numpy(), color = colors[i], linewidth = 3)
				else:
					ax.plot(y[y>100].to_numpy(), color = colors[i])
		# print(max_x, max_y)

		if(is_format_xtick):
			plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

		x = np.arange(max_x)
		ax.plot(x, 100 * (1+k_lines[4]) ** x, ls='--', color='k')
		ax.plot(x, 100 * (1+k_lines[5]) ** x, ls='-.', color='k')

		ax.set_ylim([100, max_y+max_y/2])
		ax.set_xlim([0, max_x + 2])
		ax.legend(plot_list + 
				   [f'{k_lines[4]*100:.0f}% daily incrase',
				   f'{k_lines[5]*100:.0f}% daily increase'], 
				   loc="center right",
				   bbox_to_anchor = (1.1, 0, 0.25, 1)) #
		ax.set_yscale(yscales[0])
		ax.set_xlabel('Days Since 100 Confirmed/Million')
		ax.set_title(f'Total Confirmed/Million')

		# compare_list = list(df_confirmed.sort_values(by = time_datetime[-1], ascending=False).index[:num_barplot])
		
		# iH = [i for i in range(len(plot_list)) if plot_list[i] not in compare_list]

		# y = df_confirmed.loc[plot_list, 'Per_Million'].to_numpy()
		# x = np.arange(len(plot_list))

		# if(is_format_xtick):
		# 	plot_list = reformat_xtick(plot_list, stat_abbs_mapping)


		# rects1 = ax.bar(x, y, color = 'grey')
		# rects2 = ax.bar(x[iH], y[iH], color = 'tab:red')

		# autolabel(rects1, ax, '{:.1f}')
		# autolabel(rects2, ax, '{:.1f}')

		# a = ax.set_xticks(x)
		# a = ax.set_xticklabels(plot_list)
		# ax.tick_params(axis = 'x', labelrotation = -90)
		# ax.set_xlim([-1, len(x) + 0.5])

		# ax.set_yscale(yscales[4])
		# ymax = np.ceil(np.max(y)*1.2)
		# ax.set_ylim([-0.5, ymax])

		# a = ax.set_title(f'Case per Million')
		

	############ death per million ############
	if('Per_Million' in df_deaths):
		ax = fig.add_subplot(gs[2, ncol_half:])
		i_fig += 1
		print(i_fig, end = " ")

		df_deaths.sort_values(by = 'Per_Million', inplace = True, ascending=False)
		plot_list = list(df_deaths.index[0:num_lineplot])
		if('list_addins' in kwarg.keys()):
			plot_list += kwarg['list_addins']
			plot_list = list(set(plot_list))
			df_plot = df_deaths.loc[plot_list,:].sort_values(by = 'Per_Million', ascending=False)
			plot_list = list(df_plot.index)
		df_plot = df_deaths.loc[plot_list,time_datetime]

		colors = get_colors(len(plot_list))
		max_x = 0
		max_y = 0

		for i, ele in enumerate(plot_list):
			y = df_plot.loc[ele,time_datetime]/(df_deaths.loc[ele,'Population']/MILLION)
			if(y[-1] > 10):
				xi = len(y[y>10])
				yi = max(y)
				if(xi > max_x and ele != 'China'):
					max_x = xi
				if(yi > max_y):
					max_y = yi
				if('special' in kwarg.keys()):
					if(ele == kwarg['special']):
						ax.plot(y[y>10].to_numpy(), linewidth = 3, color = color_special)
					else:
						ax.plot(y[y>10].to_numpy(), color = colors[i], linewidth = 3)
				else:
					ax.plot(y[y>10].to_numpy(), color = colors[i])

		# print(max_x, max_y)

		if(is_format_xtick):
			plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

		x = np.arange(max_x)
		ax.plot(x, 10 * (1+k_lines[6]) ** x, ls='--', color='k')
		ax.plot(x, 10 * (1+k_lines[7]) ** x, ls='-.', color='k')

		ax.set_ylim([10, max_y+max_y/2])
		ax.set_xlim([0, max_x + 2])
		ax.legend(plot_list + 
				   [f'{k_lines[6]*100:.0f}% daily incrase',
				   f'{k_lines[7]*100:.0f}% daily increase'], 
				   loc="center right",
				   bbox_to_anchor = (1.1, 0, 0.25, 1)) #
		ax.set_yscale(yscales[0])
		ax.set_xlabel('Days Since 10 Deaths/Million')
		ax.set_title(f'Total Deaths/Million')

		# compare_list = list(df_deaths.sort_values(by = time_datetime[-1], ascending=False).index[:num_barplot])

		# iH = [i for i in range(len(plot_list)) if plot_list[i] not in compare_list]
		# y = df_deaths.loc[plot_list, 'Per_Million'].to_numpy()
		# x = np.arange(len(plot_list))

		# if(is_format_xtick):
		# 	plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

		# rects1 = ax.bar(x, y, color = 'grey')
		# rects2 = ax.bar(x[iH], y[iH], color = 'tab:red')

		# autolabel(rects1, ax, '{:.1f}')
		# autolabel(rects2, ax, '{:.1f}')

		# a = ax.set_xticks(x)
		# a = ax.set_xticklabels(plot_list)
		# ax.tick_params(axis = 'x', labelrotation = -90)
		# ax.set_xlim([-1, len(x) + 0.5])
		
		# ax.set_yscale(yscales[4])
		# ymax = np.ceil(np.max(y)*1.2)
		# ax.set_ylim([-0.5, ymax])

		# a = ax.set_title(f'Deaths per Million')
	

	############ total confirmed: normalize axis ############
	ax = fig.add_subplot(gs[0, 0:ncol_lh])
	i_fig += 1
	print(i_fig, end = " ")
	
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
					ax.plot(df_plot.loc[ele, df_plot.loc[ele,:]>100].to_numpy(), linewidth = 3, color = color_special)
				else:
					ax.plot(df_plot.loc[ele, df_plot.loc[ele,:]>100].to_numpy(), color = colors[i], linewidth = 3)
			else:
				ax.plot(df_plot.loc[ele, df_plot.loc[ele,:]>100].to_numpy(), color = colors[i])

	x = np.arange(max_x)
	ax.plot(x, 100 * (1+k_lines[0]) ** x, ls='--', color='k')
	ax.plot(x, 100 * (1+k_lines[1]) ** x, ls='-.', color='k')

	if(is_format_xtick):
		plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

	ax.set_ylim([100, max_y+max_y/2])
	ax.set_xlim([0, max_x + 2])
	ax.legend(plot_list + 
			   [f'{k_lines[0]*100:.0f}% daily incrase',
			   f'{k_lines[1]*100:.0f}% daily increase'], 
			   loc="center right",
			   bbox_to_anchor = (1.1, 0, 0.25, 1)) #
	ax.set_yscale(yscales[0])
	ax.set_xlabel('Days Since 100 Confirmed Cases')
	ax.set_title(f'Total Confirmed')

	############ total confirmed: pie chart ############
	ax = fig.add_subplot(gs[0,ncol_lh:])
	i_fig += 1
	print(i_fig, end = " ")

	df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
	percentages = []
	labels = []
	df_confirmed_total = np.sum(df_confirmed.loc[:,time_datetime[-1]])

	for ele in df_confirmed.index[0:num_lineplot]:
		percentages.append(df_confirmed.loc[ele, time_datetime[-1]]/df_confirmed_total*100)
		labels.append(ele)

	if(is_format_xtick):
		labels = reformat_xtick(labels, stat_abbs_mapping)

	labels.append('Rest')
	percentages.append(100-sum(percentages))

	colors = get_colors(len(labels), is_last_grey = True)
	wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
									  autopct = my_autopct, pctdistance=0.8,
									  shadow=False, startangle=90,
									  textprops = dict(size = 12))
	
	ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1.12, 0, 0, 1))
	ax.axis('equal')
	ax.set_title(f"Total Confirmed Pie Chart")

	############ total deaths: normalized axis ############
	ax = fig.add_subplot(gs[1, 0:ncol_lh])
	i_fig += 1
	print(i_fig, end = " ")
	
	df_deaths.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
	plot_list = list(df_deaths.index[0:num_lineplot])
	if('list_addins' in kwarg.keys()):
			plot_list += kwarg['list_addins']
			plot_list = list(set(plot_list))
			df_plot = df_deaths.loc[plot_list,:].sort_values(by = time_datetime[-1], ascending=False)
			df_plot = df_plot[df_plot.loc[:,time_datetime[-1]]>10]
			plot_list = list(df_plot.index)
			print(plot_list)
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
					ax.plot(df_plot.loc[ele,df_plot.loc[ele,:]>10].to_numpy(), color = color_special, linewidth = 3)
				else:
					ax.plot(df_plot.loc[ele,df_plot.loc[ele,:]>10].to_numpy(), color = colors[i], linewidth = 3)
			else:
				ax.plot(df_plot.loc[ele,df_plot.loc[ele,:]>10].to_numpy(), color = colors[i])

	x = np.arange(max_x)
	ax.plot(x, 10 * (1+k_lines[2]) ** x, ls='--', color='k')
	ax.plot(x, 10 * (1+k_lines[3]) ** x, ls='-.', color='k')

	ax.set_yscale(yscales[0])

	ax.set_ylim([10, max_y+max_y/10])
	ax.set_xlim([0, max_x + 2])

	if(is_format_xtick):
		plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

	ax.legend(plot_list + 
			   [f'{k_lines[2]*100:.0f}% daily incrase',
				f'{k_lines[3]*100:.0f}% daily increase'],
			   loc="center right",
			   bbox_to_anchor = (1.1, 0, 0.25, 1)) #bbox_to_anchor = (1, 0, 0.35, 1)
	ax.set_xlabel('Days since 10 deaths')
	ax.set_title(f'Total Deaths')


	############ total deaths: pie chart ############
	ax = fig.add_subplot(gs[1,ncol_lh:])
	i_fig += 1
	print(i_fig, end = " ")
	
	df_deaths.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
	percentages = []
	labels = []
	df_deaths_total = np.sum(df_deaths.loc[:,time_datetime[-1]])
	for ele in df_deaths.index[0:num_lineplot]:
		percentages.append(df_deaths.loc[ele, time_datetime[-1]]/df_deaths_total*100)
		labels.append(ele)

	if(is_format_xtick):
		labels = reformat_xtick(labels, stat_abbs_mapping)

	labels.append('Rest')
	percentages.append(100-sum(percentages))

	colors = get_colors(len(labels), is_last_grey = True)
	wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
									  autopct = my_autopct, pctdistance=0.8,
									  shadow=False, startangle=90,
									  textprops = dict(size = 12))
	ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1.12, 0, 0, 1))
	ax.axis('equal')
	ax.set_title(f"Total Deaths Pie Chart")
	# fig.subplots_adjust(left=-0.1,right=0.9)

	############ daily confirmed ############
	ax = fig.add_subplot(gs[3, 0:ncol_half])
	i_fig += 1
	print(i_fig, end = " ")
	
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
					ax.plot(xi, yi, color = color_special, linewidth = 3)
				else:
					ax.plot(xi, yi, color = colors[i], linewidth = 3)
			else:
				ax.plot(xi, yi, color = colors[i], linewidth = 3)

	if(is_format_xtick):
		plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

	ax.legend(plot_list, loc = 'upper left')
	ax.set_yscale(yscales[1])
	ax.set_ylim([0, data_max + data_max/10])
	ax.set_xlim([0, x_max + 2])
	a = ax.set_title(f'Daily Confirmed')
	ax.set_xlabel('Days Since 100 Confirmed Cases')
	
	
	############ daily deaths ############
	ax = fig.add_subplot(gs[3, ncol_half:])
	i_fig += 1
	print(i_fig, end = " ")

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
					ax.plot(xi, yi, color = color_special, linewidth = 3)
				else:
					ax.plot(xi, yi, color = colors[i],  linewidth = 3)
			else:
				ax.plot(xi, yi, color = colors[i], linewidth = 3)

	if(is_format_xtick):
		plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

	ax.legend(plot_list, loc = 'upper left')
	ax.set_yscale(yscales[1])
	ax.set_ylim([0, data_max + data_max/10])
	ax.set_xlim([0, x_max + 2])
	a = ax.set_title(f'Daily Deaths')
	ax.set_xlim(left = 0)
	ax.set_xlabel('Days Since 10 Deaths')


	########### growth factors: confirmed ############
	ax = fig.add_subplot(gs[4, 0:ncol_half])
	i_fig += 1
	print(i_fig, end = " ")


	df_confirmed.sort_values(by = 'GF_today', inplace = True, ascending=False)
	plot_list = list(df_confirmed.index[0:int(num_barplot)])
	top_confirmed = list(df_confirmed.sort_values(by = time_datetime[-1], inplace = False, ascending=False).index[0:int(num_barplot)])


	df_gf = df_confirmed.loc[plot_list,time_datetime].transpose()
	# print(df_gf.index)
	# print(df_confirmed.index)
	for ele in plot_list:
		df_ele = pd.DataFrame(df_confirmed.loc[ele,time_datetime])
		# print(df_ele.columns)
		df_ele.loc[:, ele] = df_ele.loc[:, ele].astype('float')
		df_ele = my_func.reshape_dataframe(df_ele, time_datetime)
		df_gf[ele] = df_ele.GF_rolling
	df_gf = df_gf.transpose()
	df_gf.sort_values(by = time_datetime[-1], ascending = False, inplace = True)
	plot_list = list(df_gf.index)
	intersect_list = list(my_func.intersection(plot_list, top_confirmed))
	true_table = [(i in intersect_list) for i in plot_list]

	if(is_format_xtick):
		plot_list = reformat_xtick(plot_list, stat_abbs_mapping)


	x = np.arange(len(plot_list))
	x1 = np.arange(-2, len(x)+2)
	y = df_gf.loc[:, time_datetime[-1]]
	
	rects1 = ax.bar(x[true_table], y[true_table], color = 'grey')
	rects2 = ax.bar(x[~np.array(true_table)], y[~np.array(true_table)], color = 'tab:red')

	autolabel(rects1, ax, '{:.1f}')
	autolabel(rects2, ax, '{:.1f}')

	ax.plot(x1, np.full(len(x1), 1), '--', color = 'k')
	a = ax.set_xticks(x)
	a = ax.set_xticklabels(plot_list)
	ax.tick_params(axis = 'x', labelrotation = -90)
	ax.set_xlim([-1, len(x) + 0.5])

	ax.set_yscale(yscales[2])
	# ymax = np.ceil(np.max(y)) + np.ceil(np.max(y))/2
	# ax.set_ylim([0, ymax])

	a = ax.set_title(f'Growth Factors: Confirmed')
	
	
	############ growth factors: deaths ############
	ax = fig.add_subplot(gs[4, ncol_half:])
	i_fig += 1
	print(i_fig, end = " ")

	df_deaths.sort_values(by = 'GF_today', inplace = True, ascending=False)
	plot_list = list(df_deaths.index[0:int(num_barplot)])
	top_deaths = list(df_deaths.sort_values(by = time_datetime[-1], inplace = False, ascending=False).index[0:int(num_barplot)])

	df_gf = df_deaths.loc[plot_list,time_datetime].transpose()
	for ele in plot_list:
		df_ele = pd.DataFrame(df_confirmed.loc[ele,time_datetime])
		df_ele.loc[:, ele] = df_ele.loc[:, ele].astype('float')
		df_ele = my_func.reshape_dataframe(df_ele, time_datetime)
		df_gf[ele] = df_ele.GF_rolling

	df_gf = df_gf.transpose()
	df_gf.sort_values(by = time_datetime[-1], ascending = False, inplace = True)
	plot_list = list(df_gf.index)
	intersect_list = list(my_func.intersection(plot_list, top_deaths))
	true_table = [(i in intersect_list) for i in plot_list]

	if(is_format_xtick):
		plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

	x = np.arange(len(plot_list))
	x1 = np.arange(-2, len(x)+2)
	y = df_gf.loc[:, time_datetime[-1]]

	rects1 = ax.bar(x[true_table], y[true_table], color = 'grey')
	rects2 = ax.bar(x[~np.array(true_table)], y[~np.array(true_table)], color = 'tab:red')

	autolabel(rects1, ax, '{:.1f}')
	autolabel(rects2, ax, '{:.1f}')

	ax.plot(x1, np.full(len(x1), 1), '--', color = 'k')
	a = ax.set_xticks(x)
	a = ax.set_xticklabels(plot_list)
	ax.tick_params(axis = 'x', labelrotation = -90)
	ax.set_xlim([-1, len(x) + 0.5])

	ax.set_yscale(yscales[2])
	# ymax = np.ceil(np.max(y)) + np.ceil(np.max(y))/2
	# ax.set_ylim(top = ymax)
	a = ax.set_title('Growth Factors: Deaths')
	

	############ fatality rate ############
	ax = fig.add_subplot(gs[5, 0:ncol_half])
	i_fig += 1
	print(i_fig, end = " ")
	
	df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
	plot_list = list(df_confirmed.index[0:num_barplot])
	# plot_list = [ele for ele in df_confirmed.index if df_confirmed.loc[ele,time_datetime[-1]] >= 500]
	fatal_rates = df_deaths.loc[plot_list,time_datetime] / df_confirmed.loc[plot_list,time_datetime] * 100
	x = np.arange(len(plot_list))
	x1 = np.arange(-2, len(x)+2)
	fr_total = np.sum(df_deaths.loc[:,time_datetime[-1]]) / np.sum(df_confirmed.loc[:,time_datetime[-1]]) * 100
	y = fatal_rates.loc[plot_list,time_datetime[-1]]

	if(is_format_xtick):
		plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

	rects1 = ax.bar(x[y<=fr_total], y[y<=fr_total], color = 'tab:grey')
	rects2 = ax.bar(x[y>fr_total], y[y>fr_total], color = 'tab:red')
	ax.plot(x1, np.full(len(x1), fr_total), '--', color = 'k')
	
	autolabel(rects1, ax, '{:.1f}')
	autolabel(rects2, ax, '{:.1f}')

	a = ax.set_xticks(x)
	a = ax.set_xticklabels(plot_list)
	ax.tick_params(axis = 'x', labelrotation = -90)
	ax.set_xlim([-1, len(x) + 0.5])
	
	ymax = np.ceil(np.max(fatal_rates.loc[:,time_datetime[-1]]) + 1)
	ax.set_ylim([0, ymax])
	ax.set_yscale(yscales[3])
	
	a = ax.set_title(f'CFRs: mean = {fr_total:.2f}%')

	########## r for logistic growth fit ############
	# ax = fig.add_subplot(gs[4, ncol_half:])
	# print("9:", end = " ")
	
	# df_confirmed.sort_values(by = time_datetime[-1], inplace = True, ascending=False)
	# plot_list = list(df_confirmed.index[0:num_barplot])

	# x = np.arange(len(plot_list))
	# x1 = np.arange(-2, len(x)+2)
	# # if not 'rs_global' in locals():
	# rs_global = []
	# for i in x:
	# 	print(f'{i}-', end = "")
	# 	ele = plot_list[i]
	# 	df_ele = pd.DataFrame(df_confirmed.loc[ele,time_datetime])
	# 	df_ele.loc[:, ele] = df_ele.loc[:, ele].astype('float')
	# 	df_ele = my_func.reshape_dataframe(df_ele, time_datetime)
	# 	rs_global.append(get_growth_rate(df_ele, time_datetime))
	# rs_global = np.array(rs_global)

	# rects = ax.bar(x[rs_global<1], rs_global[rs_global<1], color = 'tab:grey')
	# ax.bar(x[rs_global>=1], rs_global[rs_global>=1], color = 'tab:grey')
	# ax.plot(x1, np.full(len(x1), np.median(rs_global)), '--', color = 'k')

	# autolabel(rects, ax, '{:.2f}')

	# if(is_format_xtick):
	# 	plot_list = reformat_xtick(plot_list, stat_abbs_mapping)

	# a = ax.set_xticks(x)
	# a = ax.set_xticklabels(plot_list)
	# ax.tick_params(axis = 'x', labelrotation = -90)
	# ax.set_xlim([-1, len(x) + 0.5])

	# ax.set_ylim([0, 1])
	# ax.set_yscale(yscales[3])
	
	# a = ax.set_title(f'Logistic fitted r, median = {np.median(rs_global):.2f}')
	

	# plt.tight_layout()

### plot percentage change for top sub-regions of a given region over time.
def plot_percentage_over_time(df, n, **kwarg):
		
	time_datetime = list(df.columns)

	if('title' in kwarg.keys()):
		title = kwarg['title']
	else:
		title = 'Percentage of regions over time'

	def format_fn(tick_val, tick_pos):
		if(tick_val >= 0 and tick_val < len(time_datetime)):
			return time_datetime[int(tick_val)].date()
		else:
			return None
		
	labels = []
	percentages = np.zeros((len(time_datetime), n+1))
	total_labels = []
	label_lists = []
	for x in range(len(time_datetime)):
		time = time_datetime[x]
		# print(time)
		# print(df)
		df.sort_values(by = time, inplace = True, ascending=False)
		df_time_total = np.sum(df.loc[:,time])
		ll = []
		for i, state in enumerate(df.index[0:n]):
			if(df.loc[state, time] > 0):
				ll.append(state)
				label_lists.append(state)
			else:
				ll.append('')
			percentages[x,i] = (df.loc[state, time]/df_time_total*100)
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
	plt.title(title)
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
	print("1-", end = "")
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
	print("2-", end = "")
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
		print(f"{i}-", end = "")
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
			# ax = add_country_annotations(ax, p1, df_fit, key_countries, color, cat_x, cat_y)


	##
	cat_x = 'Total_Confirmed'
	cat_y = 'Pos_per_Million'
	cat = 'Population_Cat'

	df_fit = np.log10(df_ctry_today[[cat_x, cat_y]])
	df_fit = df_fit.replace([np.inf, -np.inf], np.nan).dropna(how="any")
	df_fit[cat] = df_ctry_today[cat]
	cats = list(set(df_ctry_today[cat]))

	for i in [0,1]:
		print(f"{i}-", end = "")
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
			# ax = add_country_annotations(ax, p1, df_fit, countries, color, cat_x, cat_y)

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
	time_datetime = list(df_hb.index)

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
	plt.plot(x1, my_func.logistic_growth(x1, *popt2), '-', color = plotting_params['cat_color']['Confirmed'])
	c2_end = my_func.logistic_growth(x1, *popt2)[-1]
	plt.plot(x, y4, '*', ms = 10, color = plotting_params['cat_color']['Deaths'])
	plt.plot(x1, my_func.logistic_growth(x1, *popt4), '-', color = plotting_params['cat_color']['Deaths'])
	d2_end = my_func.logistic_growth(x1, *popt4)[-1]

	plt.title(f'Logistic Growth Fit for Other Chinese Provs, r = {popt2[0]:.2f}')
	myLocator = mticker.MultipleLocator(4)
	ax2.xaxis.set_major_locator(myLocator)
	ax2.tick_params(axis = 'x', labelrotation = 45)
	ax2.legend(['Confirmed', 
				f'Confirmed Logistic Fit: {c2_end:.0f}', 
				'Deaths', 
				f'Deaths Logistic Fit: {d2_end:.0f}'])
