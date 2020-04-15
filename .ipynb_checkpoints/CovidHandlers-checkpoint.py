import pandas as pd

def get_df_by_country(country):
    if country=='USA':
        result_df = get_usa_df()
    else:    
        confirmed_df = pd.read_csv('csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
        death_df = pd.read_csv('csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        recovery_df = pd.read_csv('csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

        columns_name = ['Confirmed', 'Death', 'Recovery']
        df_list = [confirmed_df, death_df, recovery_df]

        temp_list = []
        i = 0
        for df in df_list:
            df = df[df['Country/Region'] == country]
            df = df.groupby('Country/Region').sum()
            df = df.reset_index(drop=True)
            df = df.drop(df.columns.values[:2], axis=1)
            df = df.transpose()
            df = df.rename(columns={0:columns_name[i]})
            df.index = pd.to_datetime(df.index)
            temp_list.append(df)
            i = i + 1
        df_list = temp_list

        full_df = pd.concat(df_list, axis=1)

        full_df['Confirmed Daily'] = full_df['Confirmed'] - full_df['Confirmed'].shift(1)
        full_df['Death Daily'] = full_df['Death'] - full_df['Death'].shift(1)
        full_df['Recovery Daily'] = full_df['Recovery'] - full_df['Recovery'].shift(1)
        full_df.fillna(value=0, inplace=True)
        full_df = full_df.astype('int64')

        full_df['Confirmed Daily pct'] = full_df['Confirmed Daily'] / full_df['Confirmed'].shift(1) * 100
        full_df['Death Daily pct'] = full_df['Death Daily'] / full_df['Death'].shift(1) * 100
        full_df['Recovery Daily pct'] = full_df['Recovery Daily'] / full_df['Recovery'].shift(1) * 100
        full_df.fillna(value=0, inplace=True)
        result_df = full_df
    return result_df

def get_usa_df():
    confirmed_df = pd.read_csv('csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
    death_df = pd.read_csv('csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
    
    columns_name = ['Confirmed', 'Death']
    df_list = [confirmed_df, death_df]
    
    temp_list = []
    i = 0
    for df in df_list:
        df = df.groupby('Country_Region').sum()
        df = df.reset_index(drop=True)
        df = df[df.columns[5 + i:]]
        df = df.transpose()
        df = df.rename(columns={0:columns_name[i]})
        df.index = pd.to_datetime(df.index)
        temp_list.append(df)
        i = i + 1
    df_list = temp_list
    
    full_df = pd.concat(df_list, axis=1)
    
    full_df['Confirmed Daily'] = full_df['Confirmed'] - full_df['Confirmed'].shift(1)
    full_df['Death Daily'] = full_df['Death'] - full_df['Death'].shift(1)
    full_df.fillna(value=0, inplace=True)
    full_df = full_df.astype('int64')
    
    full_df['Confirmed Daily pct'] = full_df['Confirmed Daily'] / full_df['Confirmed'].shift(1) * 100
    full_df['Death Daily pct'] = full_df['Death Daily'] / full_df['Death'].shift(1) * 100
    full_df.fillna(value=0, inplace=True)
    
    return full_df