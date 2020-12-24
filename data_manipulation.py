import numpy as np
from pathlib import Path
import pandas as pd
from datetime import date, timedelta, datetime

start_date = date(2020, 12, 7)
end_date = date(2020, 12, 8)

delta = end_date - start_date

#dates = ["12-07-2020.csv", "12-08-2020.csv"]

for day in range(delta.days + 1):
    date = start_date + timedelta(days=day)
    print(date)
    print(type(date))
    date_string = date.strftime("%m-%d-%Y") + ".csv"
    print(date_string)
    print(type(date_string))
