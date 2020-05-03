import datetime
from datetime import timedelta

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