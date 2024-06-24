import datetime
from datetime import timedelta
import pandas as pd

def create_new_key(dt, days):
    """
    param dt (string formatted M/D/Y): current day 
    param days (int): number of days to go back
    
    returns: string (M/D/Y) days backwards in time
    """
    month, day, year = dt.split('/')
    if len(day) == 1:
        day = '0'+day
    if len(month) ==1:
        month = '0'+month
    old_datetime = datetime.datetime.strptime('/'.join((month,day,year)), '%m/%d/%y')
    new_datetime = old_datetime - timedelta(days=days)
    new_date = new_datetime.strftime('%m/%d/%y')
    month, day, year = new_date.split('/')
    if month[0] == '0':
        month = month[1]
    if day[0] == '0':
        day = day[1]
    return '/'.join((month, day, year))

def get_date_time_from_key(dt):
    month, day, year = dt.split('/')
    if len(day) == 1:
        day = '0'+day
    if len(month) ==1:
        month = '0'+month
    old_datetime = datetime.datetime.strptime('/'.join((month,day,year)), '%m/%d/%y')
    return old_datetime

def get_weekly_cases(case_data, start_date, end_date):
    
    current_date = start_date
    week_ending_cases={}

    while get_date_time_from_key(current_date)>get_date_time_from_key(end_date):
        date_cases = case_data[current_date]
        old_date = create_new_key(current_date, 7)
        old_date_cases = case_data[old_date]
        period_cases = date_cases - old_date_cases
        week_ending_cases[current_date] = sum(period_cases) 
        current_date = old_date
        
    week_ending_df = pd.DataFrame.from_dict({'Week Ending': list(week_ending_cases.keys())[::-1],
                                           'New Cases': list(week_ending_cases.values())[::-1]})
    return week_ending_df