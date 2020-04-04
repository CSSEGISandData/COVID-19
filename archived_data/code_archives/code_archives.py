# -*- coding: utf-8 -*-
# @Author: lily
# @Date:   2020-04-04 02:18:37
# @Last Modified by:   lily
# @Last Modified time: 2020-04-04 06:34:51

## update 'time_series_covid19.csv' based on daily reports from CSSE's github repository
def update_time_series(df_today, df_time_series, today):
    time_str, time_datetime = get_time_columns(df_time_series.columns)
    gps_today = list(df_today.groupby(['Country_Region', 'Province_State']).groups.keys())
    gps_ts = list(df_time_series.groupby(['Country_Region', 'Province_State']).groups.keys())
    gps = set(gps_today + gps_ts)
    for igp, gp in enumerate(gps):
        if(igp%30 == 0):
            print(igp)
        if(gp not in gps_ts):
            print(f'{gp} is new!')
            df_new = pd.DataFrame(columns = df_time_series.columns)
            for i, cat in enumerate(cdra_cols[:-1]):
                df_new.loc[i,'Country_Region'] = gp[0]
                df_new.loc[i,'Province_State'] = gp[1]
                df_new.loc[i, time_str] = 0
                df_new.loc[i, today] = df_today.groupby(['Country_Region', 'Province_State']).get_group(gp).loc[:,cat].to_list()[0]
                df_new.loc[i, 'Category'] = cat
            df_time_series = df_time_series.append(df_new, ignore_index = True)
        elif(gp not in gps_today):
            print(f'{gp} not in new today!')
            for cat in cdra_cols[:-1]:
                i = df_time_series[(df_time_series.Country_Region == gp[0]) 
                   * (df_time_series.Province_State == gp[1]) 
                   * (df_time_series.Category == cat)].index
                df_time_series.loc[i,today] = df_time_series.loc[i,time_str[-1]]
        else:
            for cat in cdra_cols[:-1]:
                i = df_time_series[(df_time_series.Country_Region == gp[0]) 
                   * (df_time_series.Province_State == gp[1]) 
                   * (df_time_series.Category == cat)].index
                a = df_today.groupby(['Country_Region', 'Province_State']).get_group(gp).sum()[cat]
                df_time_series.loc[i,today] = a
    time_str, time_datetime = get_time_columns(df_time_series.columns)
    cols_ordered = ['Province_State', 'Country_Region', 'Category'] + sorted(time_str)
    df_time_series = df_time_series.reindex(cols_ordered, axis=1)
    df_time_series.to_csv(os.path.join(path_time_series, 'time_series_covid19.csv'), index = False)
    print('New spreadsheet saved!')
    return df_time_series



"""Previous US state vs nation fitting"""

state = 'California'
future = 50

df_US = df_US_ori
df_st = df_US.groupby(['Province_State']).get_group(state)
df_US = reshape_dataframe(df_US.groupby('Category').sum().loc[:,time_str], time_str)
df_st = reshape_dataframe(df_st.groupby('Category').sum().loc[:,time_str], time_str)

fig = plt.figure(figsize = (15, 10), constrained_layout=True, facecolor="1")
gs = fig.add_gridspec(2, 2)

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


x0 = np.arange(len(time_str))
end = np.zeros((2))

for i in [0,1]:
    for j in [0,1]:
        if(j == 0):
            cat = 'Confirmed'
        elif(j == 1):
            cat = 'Deaths'
        if(i == 0):
            df_plot = df_US
            title = 'US'
        elif(i == 1):
            df_plot = df_st
            title = state
        
        y0 = df_plot.loc[time_str, cat].to_numpy()
        dy0 = df_plot.loc[time_str, f'Daily_{cat}_smoothed']
        res = df_plot[df_plot.GF_rolling_thr != 0.0].bfill(axis=1).index[0]
        ind_t0 = max(0, time_str.index(res)-3)
        t = np.arange(len(time_str))[ind_t0:]- ind_t0
        pt = y0[ind_t0:]
        popt_logs = get_logistic_params(t, pt, p0 = (0.1, 100, 1))
        x1 = np.arange(len(t) + future)
        
        ax = fig.add_subplot(gs[j, i])
        if(future == 0):
            ax.plot(x, y1, '.', ms = 10, color = cat_color[cat])
            popt_exp, pcov_exp = opt.curve_fit(exp_growth,  t,  pt, p0 = (0.1, 10), maxfev = 100000)
            popt_log, pcov_log = opt.curve_fit(logistic_growth,  t,  pt, p0 = (0.1, 100, 1), maxfev=100000)
            ax.plot(x1 + ind_t0, exp_growth(x1, popt_exp[0], popt_exp[1]), '--', color = cat_color[cat])
            ax.plot(x1 + ind_t0, logistic_growth(x1, popt_log[0], popt_log[1], popt_log[2]), color = cat_color[cat])
        else:
            ax, ax, y_ends, ind_midds = plot_predictions(ax, x0, y0, dy0, x1, ind_t0, popt_logs, cat_color[cat])
        date_max = []
        for k in [0,1]:
            if(k == 0):
                ind = int(np.min(ind_midds))
            else:
                ind = int(np.max(ind_midds))
            if(ind < len(time_str)-ind_t0):
                date_max.append(time_str[ind-ind_t0])
            else:
                date_max.append(f'+{ind-(len(time_str)-ind_t0)}')
        if(j == 0):
            rate = np.mean(y_ends)
        else:
            rate = np.mean(y_ends)/rate * 100
        if(future == 0):
            ax.legend(['Confirmed', 
                        'Confirmed Exp Fit', 
                        'Confirmed Logistic Fit'])
            ax.set_title(f'{title} {cat}: r={popt_exp[0]:.2f}/{popt_log[0]:.2f}', fontsize = 18)
        else:
            ax.set_title(f'{title} {cat}')
            if(j == 0):
                pp = f'{title} {cat}: r={np.mean(popt_logs[:,0]):.2f}, K = {np.min(y_ends):.0f}~{np.max(y_ends):.0f}, peak increase at {date_max[0]}~{date_max[1]}'
            else:
                pp = f'{title} {cat}: r={np.mean(popt_logs[:,0]):.2f}, K = {np.min(y_ends):.0f}~{np.max(y_ends):.0f}, peak increase at {date_max[0]}~{date_max[1]}, CFR ~ {rate:.1f}%'
            print(pp)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_fn_future))
        myLocator = mticker.MultipleLocator(6)
        ax.xaxis.set_major_locator(myLocator)
        ax.tick_params(axis = 'x', labelrotation = 45)
        ax.set_xlim(left = 0)

"""JHU vs 1p3a"""
# state = 'California'
# ys = np.zeros((len(time_str), 4))
# x = np.arange(len(time_str))

# ys[:,0] = df_US.loc[time_str, 'Confirmed'].to_numpy()
# ys[:,1] = df_US_1p3a.loc[time_str, 'US'].to_numpy()
# ys[:,2] = df_CA.loc[time_str, 'Confirmed'].to_numpy()
# ys[:,3] = df_US_1p3a.loc[time_str, 'CA'].to_numpy()
# d1 = df_US.loc[time_str, 'Deaths'].to_numpy()
# d2 = df_CA.loc[time_str, 'Deaths'].to_numpy()

# res1 = df_US[df_US.GF_rolling_thr != 0.0].bfill(axis=1).index[0]
# res2 = df_CA[df_CA.GF_rolling_thr != 0.0].bfill(axis=1).index[0]

# ind1_t0 = max(0, time_str.index(res1)-3)
# ind2_t0 = max(0, time_str.index(res2)-3)

# t1 = np.arange(len(time_str))[ind1_t0:]- ind1_t0
# t2 = np.arange(len(time_str))[ind2_t0:]- ind2_t0

# future = 50
# yscale = 'linear'


# fig = plt.figure(figsize = (15, 10), constrained_layout=True, facecolor="1")
# gs = fig.add_gridspec(2, 2)

# ### US: confirmed
# ax = fig.add_subplot(gs[0, 0])

# x1 = np.arange((len(t1) + future))
# ax.plot(x, ys[:,0], '.')
# ax.plot(x, ys[:,1], '*')
# if(future == 0):
#     r_exp = 0
#     for i in [0,1]:
#         popt, pcov = opt.curve_fit(exp_growth, t1, ys[ind1_t0:,i], maxfev = 10000)
#         ax.plot(x1 + ind1_t0, exp_growth(x1, popt[0], popt[1]), '--')
#         r_exp += popt[0]
#     r_exp = r_exp/2
# else:
#     r_exp = np.nan
# r_log = 0
# k_log = []
# for i in [0,1]:
#     popt, pcov = opt.curve_fit(logistic_growth, t1, ys[ind1_t0:,i], p0 = [0.1, 100, 1], maxfev = 10000)
#     ax.plot(x1 + ind1_t0, logistic_growth(x1, popt[0], popt[1], popt[2]))
#     r_log += popt[0]
#     k_log.append(logistic_growth(x1, popt[0], popt[1], popt[2])[-1])
# r_log = r_log/2
# ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_fn_future))
# myLocator = mticker.MultipleLocator(4)
# ax.xaxis.set_major_locator(myLocator)
# ax.set_yscale(yscale)
# # ax.set_ylim([0, 3*10**11])
# ax.tick_params(axis = 'x', labelrotation = 45)
# if(future == 0):
#     ax.legend(['Confirmed_JHU', 
#                 'Confirmed_1p3a',
#                 'Exponential Fit: JHU',
#                 'Exponential Fit: 1p3a',
#                 'Logistic Fit: JHU', 
#                 'Logistic Fit: 1p3a'])
#     ax.set_title(f'US Confirmed: growth rate {r_exp:.2f}/{r_log:.2f}')
# else:
#     ax.legend(['Confirmed_JHU', 
#                 'Confirmed_1p3a',
#                 'Logistic Fit: JHU', 
#                 'Logistic Fit: 1p3a'])
#     ax.set_title(f'US Confirmed: r={r_exp:.2f}/{r_log:.2f}, K={k_log[0]:.0f}/{k_log[1]:.0f}')
# total_us = k_log[0]

# ## State: Confirmed
# ax = fig.add_subplot(gs[0, 1])

# x1 = np.arange((len(t2) + future))
# ax.plot(x, ys[:,2], '.')
# if(state == 'California'):
#     ax.plot(x, ys[:,3], '*')
# if(future == 0):
#     r_exp = 0
#     if(state == 'California'):
#         for i in [2,3]:
#             popt, pcov = opt.curve_fit(exp_growth, t2, ys[ind2_t0:,i], maxfev = 10000)
#             ax.plot(x1 + ind2_t0, exp_growth(x1, popt[0], popt[1]), '--')
#             r_exp += popt[0]
#         r_exp = r_exp/2
#     else:
#         i = 2
#         popt, pcov = opt.curve_fit(exp_growth, t2, ys[ind2_t0:,i], maxfev = 10000)
#         ax.plot(x1 + ind2_t0, exp_growth(x1, popt[0], popt[1]))
#         r_exp = popt[0]
# else:
#         r_exp = np.nan
# r_log = 0
# k_log = []
# if(state == 'California'):
#     for i in [2,3]:
#         popt, pcov = opt.curve_fit(logistic_growth, t2, ys[ind2_t0:,i], p0 = [0.1, 100, 1], maxfev = 10000)
#         ax.plot(x1 + ind2_t0, logistic_growth(x1, popt[0], popt[1], popt[2]), '--')
#         r_log += popt[0]
#         k_log.append(logistic_growth(x1, popt[0], popt[1], popt[2])[-1])
#     r_log = r_log/2
# else:
#     i = 2
#     popt, pcov = opt.curve_fit(logistic_growth, t2, ys[ind2_t0:,i], p0 = [0.1, 100, 1], maxfev = 10000)
#     ax.plot(x1 + ind2_t0, logistic_growth(x1, popt[0], popt[1], popt[2]))
#     r_log = popt[0]
#     k_log = logistic_growth(x1, popt[0], popt[1], popt[2])[-1]
# ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_fn_future))
# myLocator = mticker.MultipleLocator(4)
# ax.xaxis.set_major_locator(myLocator)
# ax.set_yscale(yscale)
# # ax.set_ylim([0, 60000])
# ax.tick_params(axis = 'x', labelrotation = 45)
# if(future == 0):
#     if(state == 'California'):
#         ax.legend(['Confirmed_JHU', 
#                     'Confirmed_1p3a',
#                     'Exponential Fit: JHU',
#                     'Exponential Fit: 1p3a',
#                     'Logistic Fit: JHU', 
#                     'Logistic Fit: 1p3a'])
#     else:
#         ax.legend(['Confirmed_JHU', 
#                     'Exponential Fit: JHU',
#                     'Logistic Fit: JHU'])
#     ax.set_title(f'{state} Confirmed: growth rate {r_exp:.2f}/{r_log:.2f}')
# else:
#     if(state == 'California'):
#         ax.legend(['Confirmed_JHU',
#                     'Confirmed_1p3a'
#                     'Logistic Fit: JHU', 
#                     'Logistic Fit: 1p3a'])
#         ax.set_title(f'{state} Confirmed: r={r_exp:.2f}/{r_log:.2f}, K={k_log[0]:.0f}/{k_log[1]:.0f}')
#         total_st = k_log[0]
#     else:
#         ax.legend(['Confirmed_JHU',
#                     'Logistic Fit: JHU'])
#         ax.set_title(f'{state} Confirmed: r={r_exp:.2f}/{r_log:.2f}, K={k_log:.0f}')
#         total_st = k_log


# ### US: deaths
# ax = fig.add_subplot(gs[1, 0])

# x1 = np.arange((len(t1) + future))
# ax.plot(x, d1, '.')
# if(future == 0):
#     popt, pcov = opt.curve_fit(exp_growth, t1, d1[ind1_t0:], maxfev = 10000)
#     ax.plot(x1 + ind1_t0, exp_growth(x1, popt[0], popt[1]))
# popt, pcov = opt.curve_fit(logistic_growth, t1, d1[ind1_t0:], p0 = [0.1, 100, 1], maxfev = 10000)
# ax.plot(x1 + ind1_t0, logistic_growth(x1, popt[0], popt[1], popt[2]))
# k_log = logistic_growth(x1, popt[0], popt[1], popt[2])[-1]

# ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_fn_future))
# myLocator = mticker.MultipleLocator(4)
# ax.xaxis.set_major_locator(myLocator)
# ax.set_yscale(yscale)
# ax.tick_params(axis = 'x', labelrotation = 45)
# if(future == 0):
#     ax.legend(['Deaths', 
#                 'Deaths Exponential Fit',
#                 'Deaths Logistic Fit'])
#     ax.set_title(f'US Deaths: r = {popt[0]:.2f}')
# else:
#     ax.legend(['Deaths', 
#                 'Deaths Logistic Fit'])
#     ax.set_title(f'US Deaths: r = {popt[0]:.2f}, K={k_log:.0f} ({k_log/total_us*100:.1f}%)')

# ### State: deaths
# ax = fig.add_subplot(gs[1, 1])

# x1 = np.arange((len(t2) + future))
# ax.plot(x, d2, '.')
# if(future == 0):
#     popt, pcov = opt.curve_fit(exp_growth, t2, d2[ind2_t0:], maxfev = 10000)
#     ax.plot(x1 + ind2_t0, exp_growth(x1, popt[0], popt[1]))
# popt, pcov = opt.curve_fit(logistic_growth, t2, d2[ind2_t0:], p0 = [0.1, 100, 1], maxfev = 10000)
# ax.plot(x1 + ind2_t0, logistic_growth(x1, popt[0], popt[1], popt[2]))
# k_log = logistic_growth(x1, popt[0], popt[1], popt[2])[-1]

# ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_fn_future))
# myLocator = mticker.MultipleLocator(4)
# ax.xaxis.set_major_locator(myLocator)
# ax.set_yscale(yscale)
# ax.tick_params(axis = 'x', labelrotation = 45)
# if(future == 0):
#     ax.legend(['Deaths', 
#                 'Deaths Exponential Fit',
#                 'Deaths Logistic Fit'])
#     ax.set_title(f'{state} Deaths: r = {popt[0]:.2f}')
# else:
#     ax.legend(['Deaths', 
#                 'Deaths Logistic Fit'])
#     ax.set_title(f'{state} Deaths: r = {popt[0]:.2f}, K={k_log:.0f} ({k_log/total_st*100:.1f}%)')

### US by states
############ params ############
num_states = 10
colors_line = pl.cm.tab10(np.linspace(0,1,num_states))
colors_pie = pl.cm.Set3(np.linspace(0,1,11))
colors_pie[7,:] = colors_pie[10:]
colors_pie[10,:] = 0.85

############ figure ############
fig = plt.figure(figsize = (15, 20), constrained_layout=True, facecolor="1")
gs = fig.add_gridspec(4, 2)

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

ind_t0 = time_str.index(time_str[0])
time_plot = time_str[ind_t0:]


############ r for logistic growth fit ############
ax6 = fig.add_subplot(gs[3, 1])

df_us_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
states = list(df_us_confirmed.index[0:num_states])

x = np.arange(len(states))
x1 = np.arange(-2, len(x)+2)
y = []
for i in x:
    ctry = states[i]
    df_ctry = pd.DataFrame(df_us_confirmed.loc[ctry,time_plot])
    df_ctry = reshape_dataframe(df_ctry, time_plot)
    y.append(get_growth_rate(df_ctry, time_plot))
y = np.array(y)
r_median = np.median(y)

rects = ax6.bar(x, y, color = 'grey')
ax6.plot(x1, np.full(len(x1), np.median(y)), '--', color = 'k')
a = ax6.set_xticks(x)
a = ax6.set_xticklabels(states)
ax6.tick_params(axis = 'x', labelrotation = -90)
autolabel(rects, ax6, '{:.2f}')
# ymax = np.ceil(np.max(y)) + 0.5
ymax = 1.5
ax6.set_ylim([0, ymax])
ax6.set_xlim([-1, len(x) + 0.5])
a = ax6.set_title(f'Logistic fitted r, median = {np.median(y):.2f}')

############ total number normalized ############
ax2 = fig.add_subplot(gs[0, 0])

df_us_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
states = list(df_us_confirmed.index[0:num_states])
df_plot = df_us_confirmed.loc[states,time_plot]

max_x = 0
for i, ctr in enumerate(states):
    xi = len(df_plot.loc[ctr, df_plot.loc[ctr,:]>100].to_numpy())
    if(ctr == 'California'):
        ax2.plot(df_plot.loc[ctr, df_plot.loc[ctr,:]>100].to_numpy(), color = colors_line[i], linewidth = 3)
    else:
        ax2.plot(df_plot.loc[ctr, df_plot.loc[ctr,:]>100].to_numpy(), color = colors_line[i])
    if(xi > max_x):
        max_x = xi
x = np.arange(max_x)
ax2.plot(x, 100 * (1 + r_median) ** x, ls='--', color='k')
ax2.legend(states + [f'{r_median*100:.0f}% daily growth'],
           loc="center right", bbox_to_anchor = (1, 0, 0.35, 1))
ax2.set_ylim(bottom = 100)
ax2.set_xlim(left = 0)
ax2.set_yscale('log')
ax2.set_xlabel('Days Since 100 Confirmed Cases')
ax2.set_title(f'Confirmed cases: Top {num_states} States')


############ total number pie chart ############
ax = fig.add_subplot(gs[0,1])

df_us_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
percentages = []
labels = []
us_confirmed_total = np.sum(df_us_confirmed.loc[:,time_str[-1]])
for state in df_us_confirmed.index[0:num_states]:
    percentages.append(df_us_confirmed.loc[state, time_str[-1]]/us_confirmed_total*100)
    labels.append(state)
labels.append('Rest')
percentages.append(100-sum(percentages))

wedges, texts, autotexts = ax.pie(percentages, colors = colors_pie, 
                                  autopct = my_autopct, pctdistance=0.8,
                                  shadow=False, startangle=90,
                                  textprops = dict(size = 12))

ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0.2, 1))
ax.axis('equal')
ax.set_title("US Confirmed Cases")


############ daily cases normalized ############
ax3 = fig.add_subplot(gs[2, 0])

df_us_confirmed.sort_values(by = 'New_Today', inplace = True, ascending=False)
states = list(df_us_confirmed.index[0:num_states])

data_max = 0
for i, ctr in enumerate(states):
    yi = df_us_confirmed.loc[ctr,time_str].transpose().diff().loc[df_us_confirmed.loc[ctr,time_str]>100].to_numpy()
    xi = np.arange(len(yi))
    if(np.max(yi) > data_max):
        data_max = np.max(yi)
    if(ctr == 'California'):
        ax3.plot(xi, yi, color = colors_line[i], linewidth = 3)
    else:
        ax3.plot(xi, yi, color = colors_line[i])

ax3.legend(states, loc="center right", bbox_to_anchor = (1, 0, 0.35, 1))
ax3.set_yscale('linear')
a = ax3.set_title(f'Daily cases: top {num_states}')
ax3.set_ylim([0, data_max + 100])
ax3.set_xlim(left = 0)
ax3.set_xlabel('Days Since 100 Confirmed Cases')


############ total deaths ############
ax1 = fig.add_subplot(gs[1, 0])

df_us_deaths.sort_values(by = time_str[-1], inplace = True, ascending=False)
states = list(df_us_deaths.index[0:num_states])
df_plot = df_us_deaths.loc[states,time_str]

max_x = 0
for i, ctr in enumerate(states):
    xi = len(df_plot.loc[ctr, df_plot.loc[ctr,:]>10].to_numpy())
    if(ctr == 'California'):
        ax1.plot(df_plot.loc[ctr, df_plot.loc[ctr,:]>10].to_numpy(), color = colors_line[i], linewidth = 3)
    else:
        ax1.plot(df_plot.loc[ctr, df_plot.loc[ctr,:]>10].to_numpy(), color = colors_line[i])
    if(xi > max_x):
        max_x = xi
x = np.arange(max_x)
max_y = np.max(df_plot.loc[states,:].to_numpy().flatten())

ax1.plot(x, 10 * (1 + 0.3) ** x, ls='--', color='k')

ax1.legend(states + ['30% daily growth'],
          loc="center right", bbox_to_anchor = (1, 0, 0.35, 1))
ax1.set_yscale('log')
ax1.set_xlabel('Days since 10 deaths')
ax1.set_ylim([10, max_y + 10])
# plt.ylim(top = 2000)
ax1.set_title(f'Total deaths: top {num_states}')
myLocator = mticker.MultipleLocator(4)
ax1.xaxis.set_major_locator(myLocator)
ax1.tick_params(axis = 'x', labelrotation = 45)


############ total deaths pie chart ############
ax = fig.add_subplot(gs[1,1])

df_us_deaths.sort_values(by = time_str[-1], inplace = True, ascending=False)
percentages = []
labels = []
us_deaths_total = np.sum(df_us_deaths.loc[:,time_str[-1]])
for state in df_us_deaths.index[0:num_states]:
    percentages.append(df_us_deaths.loc[state, time_str[-1]]/us_deaths_total*100)
    labels.append(state)
labels.append('Rest')
percentages.append(100-sum(percentages))

wedges, texts, autotexts = ax.pie(percentages, colors = colors_pie, 
                                  autopct = my_autopct, pctdistance=0.8,
                                  shadow=False, startangle=90,
                                  textprops = dict(size = 12))
ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0.2, 1))
ax.axis('equal')
ax.set_title("US Deaths")


############ fatality rate ############
ax5 = fig.add_subplot(gs[3, 0])

df_us_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
states = list(df_us_confirmed.index[0:num_states])

fatal_rates = df_us_deaths.loc[states,time_plot] / df_us_confirmed.loc[states,time_plot] * 100
x = np.arange(len(states))
x1 = np.arange(-2, len(x)+2)
fr_total = df_US.CFR[-1]

rects = ax5.bar(x, fatal_rates.loc[:,time_plot[-1]], color = 'grey')
ax5.plot(x1, np.full(len(x1), fr_total), '--', color = 'k')
a = ax5.set_xticks(x)
a = ax5.set_xticklabels(states)
ax5.tick_params(axis = 'x', labelrotation = -90)
autolabel(rects, ax5, '{:.2f}')
ymax = np.ceil(np.max(fatal_rates.loc[:,time_plot[-1]]) + 1)
ax5.set_ylim([0, ymax])
ax5.set_xlim([-1, len(x) + 0.5])
a = ax5.set_title(f'CFRs: US mean = {fr_total:.2f}%')


############ growth factors ############
ax4 = fig.add_subplot(gs[2, 1])

df_us_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
states = list(df_us_confirmed.index[0:num_states])

df_gf = df_us_confirmed.loc[states,time_plot].transpose()
for ctry in states:
    df_ctry = pd.DataFrame(df_us_confirmed.loc[ctry,time_plot])
    df_ctry = reshape_dataframe(df_ctry, time_plot)
    df_gf[ctry] = df_ctry.GF_rolling

x = np.arange(len(states))
x1 = np.arange(-2, len(x)+2)
y = df_gf.loc[time_plot[-1],:]

rects1 = ax4.bar(x, y, color = 'grey')
ax4.plot(x1, np.full(len(x1), 1), '--', color = 'k')
a = ax4.set_xticks(x)
a = ax4.set_xticklabels(states)
ax4.tick_params(axis = 'x', labelrotation = -90)
autolabel(rects1, ax4, '{:.2f}')
ymax = np.ceil(np.max(y)) + 5
ax4.set_ylim([-1, ymax])
a = ax4.set_title('Growth Factors')
ax4.set_xlim([-1, len(x) + 0.5])

### world comparison
############ figure ############
fig = plt.figure(figsize = (18, 30), constrained_layout=True, facecolor="1")
gs = fig.add_gridspec(5, 2)

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


########## r for logistic growth fit ############
ax6 = fig.add_subplot(gs[4, 0])

df_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
# countries = [ctry for ctry in df_confirmed.index if df_confirmed.loc[ctry,time_str[-1]] >= 500]
countries = list(df_confirmed.index[0:30])

x = np.arange(len(countries))
x1 = np.arange(-2, len(x)+2)
# if not 'rs_global' in locals():
rs_global = []
for i in x:
    ctry = countries[i]
    df_ctry = pd.DataFrame(df_confirmed.loc[ctry,time_plot])
    df_ctry = reshape_dataframe(df_ctry, time_plot)
    rs_global.append(get_growth_rate(df_ctry, time_plot))
rs_global = np.array(rs_global)

rects = ax6.bar(x[rs_global<1], rs_global[rs_global<1], color = 'tab:grey')
ax6.bar(x[rs_global>=1], rs_global[rs_global>=1], color = 'tab:grey')
ax6.plot(x1, np.full(len(x1), np.median(rs_global)), '--', color = 'k')
a = ax6.set_xticks(x)
a = ax6.set_xticklabels(countries)
ax6.tick_params(axis = 'x', labelrotation = -90)
autolabel(rects, ax6, '{:.2f}')
ymax = np.ceil(np.max(y)) + 0.2
ax6.set_ylim([0, 1])
ax6.set_xlim([-1, len(x) + 0.5])
a = ax6.set_title(f'Logistic fitted r, median = {np.median(rs_global):.2f}')


############ total confirmed: normalize axis ############
ax2 = fig.add_subplot(gs[0, 0])

df_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
countries = list(df_confirmed.index[0:10])
countries += ['Korea, South', 'Canada', 'Japan', 'Singapore']

df_plot = df_confirmed.loc[countries,time_str]


colors = pl.cm.tab20(np.linspace(0,1,len(countries)))
max_x = 0
max_y = np.max(df_plot.to_numpy().flatten())
for i, ctr in enumerate(countries):
    xi = len(df_plot.loc[ctr, df_plot.loc[ctr,:]>100].to_numpy())
    if(xi > max_x):
        max_x = xi
    if(ctr == 'US'):
        ax2.plot(df_plot.loc[ctr, df_plot.loc[ctr,:]>100].to_numpy(), linewidth = 3, color = colors[i])
    else:
        ax2.plot(df_plot.loc[ctr, df_plot.loc[ctr,:]>100].to_numpy(), color = colors[i])

x = np.arange(max_x)
ax2.plot(x, 100 * (1+0.33) ** x, ls='--', color='k')
ax2.plot(x, 100 * (1+0.5) ** x, ls='-.', color='k')

ax2.set_ylim([100, max_y+max_y/10])
ax2.set_xlim([0, 50])
ax2.legend(countries + 
           [f'33% daily incrase',
           f'50% daily increase'], 
           loc="center right") #bbox_to_anchor = (1, 0, 0.35, 1)
ax2.set_yscale('log')
ax2.set_xlabel('Days Since 100 Confirmed Cases')
ax2.set_title('Confirmed cases by country/region')

############ total confirmed: pie chart ############
ax = fig.add_subplot(gs[0,1])

df_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
percentages = []
labels = []
df_confirmed_total = np.sum(df_confirmed.loc[:,time_str[-1]])
for ctry in df_confirmed.index[0:10]:
    percentages.append(df_confirmed.loc[ctry, time_str[-1]]/df_confirmed_total*100)
    labels.append(ctry)
labels.append('Rest')
percentages.append(100-sum(percentages))

colors = pl.cm.Set3(np.linspace(0,1,11))
colors[7,:] = colors[10,:]
colors[10,:] = [0.85, 0.85, 0.85, 1]
wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
                                  autopct = my_autopct, pctdistance=0.8,
                                  shadow=False, startangle=90,
                                  textprops = dict(size = 12))
ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0, 1))
ax.axis('equal')
ax.set_title("Total Confirmed Cases")


############ total deaths: normalized axis ############
ax1 = fig.add_subplot(gs[1, 0])

df_deaths.sort_values(by = time_str[-1], inplace = True, ascending=False)
countries = list(df_deaths.index[0:10])
countries += ['Korea, South', 'Canada', 'Japan', 'Singapore']
df_plot = df_deaths.loc[countries,time_str]

colors = pl.cm.tab20(np.linspace(0,1,len(countries)))
max_x = 0
max_y = np.max(df_plot.to_numpy().flatten())
for i, ctr in enumerate(countries):
    xi = len(df_plot.loc[ctr, df_plot.loc[ctr,:]>10].to_numpy())
    if(xi > max_x):
        max_x = xi
    if(ctr == 'US'):
        ax1.plot(df_plot.loc[ctr,df_plot.loc[ctr,:]>10].to_numpy(), color = colors[i], linewidth = 3)
    else:
        ax1.plot(df_plot.loc[ctr,df_plot.loc[ctr,:]>10].to_numpy(), color = colors[i])

x = np.arange(max_x)
ax1.plot(x, 10 * (1+0.20) ** x, ls='--', color='k')
ax1.plot(x, 10 * (1+0.40) ** x, ls='-.', color='k')

ax1.set_ylim([10, max_y+max_y/10])

ax1.legend(countries + 
           [f'20% daily incrase',
            f'40% daily increase'],
           loc="center right") #bbox_to_anchor = (1, 0, 0.35, 1)
ax1.set_yscale('log')
ax1.set_xlabel('Days since 10 deaths')
ax1.set_title('Deaths by country/region')


############ total deaths: pie chart ############
ax = fig.add_subplot(gs[1,1])

df_deaths.sort_values(by = time_str[-1], inplace = True, ascending=False)
percentages = []
labels = []
df_deaths_total = np.sum(df_deaths.loc[:,time_str[-1]])
for ctry in df_deaths.index[0:10]:
    percentages.append(df_deaths.loc[ctry, time_str[-1]]/df_deaths_total*100)
    labels.append(ctry)
labels.append('Rest')
percentages.append(100-sum(percentages))

colors = pl.cm.Set3(np.linspace(0,1,11))
colors[7,:] = colors[10,:]
colors[10,:] = [0.85, 0.85, 0.85, 1]
wedges, texts, autotexts = ax.pie(percentages, colors = colors, 
                                  autopct = my_autopct, pctdistance=0.8,
                                  shadow=False, startangle=90,
                                  textprops = dict(size = 12))
ax.legend(wedges, labels, loc="center right", bbox_to_anchor = (1, 0, 0, 1))
ax.axis('equal')
ax.set_title("Total Deaths")


############ daily confirmed ############
ax3 = fig.add_subplot(gs[2, 0])

df_confirmed.sort_values(by = 'New_Today', inplace = True, ascending=False)
countries = list(set(list(df_confirmed.index[0:10]) + ['China', 'Korea, South', 'Japan', 'Singapore']))
df_plot = df_confirmed.loc[countries,:].sort_values(by = 'New_Today', ascending=False)
countries = list(df_plot.index)

colors = pl.cm.tab20(np.linspace(0,1,len(countries)))
data_max = 0
x_max = 0
for i, ctr in enumerate(countries):
    yi = df_confirmed.loc[ctr,time_str].transpose().diff().loc[df_confirmed.loc[ctr,time_str]>100].to_numpy()
    xi = np.arange(len(yi))
    if(np.max(yi) > data_max):
        data_max = np.max(yi)
    if(len(xi) > x_max and ctr != 'China'):
        x_max = len(xi)
    if(ctr == 'US'):
        ax3.plot(xi, yi, color = colors[i], linewidth = 3)
    else:
        ax3.plot(xi, yi, color = colors[i])

ax3.legend(countries, loc = 'upper left')
ax3.set_yscale('linear')
ax3.set_ylim([0, data_max + data_max/10])
ax3.set_xlim([0, x_max + 2])
a = ax3.set_title('Daily confirmed cases: top 10')
ax3.set_xlabel('Days Since 100 Confirmed Cases')

############ daily deaths ############
ax3 = fig.add_subplot(gs[2, 1])

df_deaths.sort_values(by = 'New_Today', inplace = True, ascending=False)
countries = list(set(list(df_deaths.index[0:10]) + ['China', 'Korea, South', 'Japan']))
df_plot = df_deaths.loc[countries,:].sort_values(by = 'New_Today', ascending=False)
countries = list(df_plot.index)

colors = pl.cm.tab20(np.linspace(0,1,len(countries)))
data_max = 0
x_max = 0
for i, ctr in enumerate(countries):
    yi = df_deaths.loc[ctr,time_str].transpose().diff().loc[df_deaths.loc[ctr,time_str]>10].to_numpy()
    xi = np.arange(len(yi))
    if(np.max(yi) > data_max):
        data_max = np.max(yi)
    if(len(xi) > x_max and ctr != 'China'):
        x_max = len(xi)
    if(ctr == 'US'):
        ax3.plot(xi, yi, color = colors[i], linewidth = 3)
    else:
        ax3.plot(xi, yi, color = colors[i])

ax3.legend(countries, loc = 'upper left')
ax3.set_yscale('linear')
ax3.set_ylim([0, data_max + data_max/10])
ax3.set_xlim([0, x_max + 2])
a = ax3.set_title('Daily deaths: top 10')
ax3.set_xlim(left = 0)
ax3.set_xlabel('Days Since 10 Deaths')


############ growth factors ############
ax4 = fig.add_subplot(gs[3, 0])

df_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
countries = list(df_confirmed.index[0:30])
# countries = [ctry for ctry in df_confirmed.index if df_confirmed.loc[ctry,time_str[-1]] >= 500]

df_gf = df_confirmed.loc[countries,time_str].transpose()
for ctry in countries:
    df_ctry = pd.DataFrame(df_confirmed.loc[ctry,time_str])
    df_ctry = reshape_dataframe(df_ctry, time_str)
    df_gf[ctry] = df_ctry.GF_rolling

x = np.arange(len(countries))
x1 = np.arange(-2, len(x)+2)
y = df_gf.loc[time_str[-1],:]

rects1 = ax4.bar(x, y, color = 'grey')
ax4.plot(x1, np.full(len(x1), 1), '--', color = 'k')
a = ax4.set_xticks(x)
a = ax4.set_xticklabels(countries)
ax4.tick_params(axis = 'x', labelrotation = -90)
autolabel(rects1, ax4, '{:.1f}')
ymax = np.ceil(np.max(y)) + 1
ax4.set_ylim([-0.5, ymax])
a = ax4.set_title('Growth Factors')
ax4.set_xlim([-1, len(x) + 0.5])


############ fatality rate ############
ax5 = fig.add_subplot(gs[3, 1])

df_confirmed.sort_values(by = time_str[-1], inplace = True, ascending=False)
countries = list(df_confirmed.index[0:30])
# countries = [ctry for ctry in df_confirmed.index if df_confirmed.loc[ctry,time_str[-1]] >= 500]
fatal_rates = df_deaths.loc[countries,time_str] / df_confirmed.loc[countries,time_str] * 100
x = np.arange(len(countries))
x1 = np.arange(-2, len(x)+2)
fr_total = df_total.CFR[-1]
y = fatal_rates.loc[:,time_str[-1]]

rects1 = ax5.bar(x[y<=fr_total], y[y<=fr_total], color = 'tab:grey')
rects2 = ax5.bar(x[y>fr_total], y[y>fr_total], color = 'tab:red')
ax5.plot(x1, np.full(len(x1), fr_total), '--', color = 'k')
a = ax5.set_xticks(x)
a = ax5.set_xticklabels(countries)
ax5.tick_params(axis = 'x', labelrotation = -90)
autolabel(rects1, ax5, '{:.1f}')
autolabel(rects2, ax5, '{:.1f}')
ymax = np.ceil(np.max(fatal_rates.loc[:,time_str[-1]]) + 1)
ax5.set_ylim([0, ymax])
ax5.set_xlim([-1, len(x) + 0.5])
a = ax5.set_title(f'CFRs: global mean = {fr_total:.2f}%')
