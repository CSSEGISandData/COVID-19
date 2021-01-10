# that extracts the data from the daily covid reports in the Johns Hopkins repo and produces a numpy array where each entry is a numpy array containing: (latitude, longitude, cumulative confirmed cases, number of days since covid hit the US).
import numpy as np
from pathlib import Path
import pandas as pd
from datetime import date, timedelta, datetime
from sklearn.preprocessing import normalize
import operator

data_folder = Path("csse_covid_19_data/csse_covid_19_daily_reports/")

# make days array based on inputs
pandemic_start = date(2020, 1, 22)

# don't do 3-21 or earlier
start_date = date(2020, 3, 22)
end_date = date(2020, 4, 20)

delete_location = False
delete_unassigned = True
normalize_data = True
sort_by_location = True

delta = end_date - start_date

for day in range(delta.days + 1):
    # get the day
    date = start_date + timedelta(days=day)
    # convert to string/file name
    day_file = date.strftime("%m-%d-%Y") + ".csv"

    file_to_open = data_folder / day_file
    raw_data = pd.read_csv(file_to_open, header=0, delimiter=',', encoding=None, usecols=(
        "Admin2", "Province_State", "Country_Region", "Lat", "Long_", "Confirmed"))

    # calculating days since covid hit US
    days_since_start = date - pandemic_start

    # adding another column with days since covid hit the US
    raw_data['Days since start'] = days_since_start.days  # number of days
    raw_data['Date'] = date.strftime("%m-%d-%Y")

    raw_data = raw_data[raw_data['Lat'].notna()]
    raw_data = raw_data[raw_data['Long_'].notna()]
    raw_data = raw_data.fillna(value="N/A")

    if day == 0:
        final_array = raw_data.copy(deep=False)  # make shallow copy
    else:
        final_array = final_array.append(raw_data)
        # print(final_array.iloc[-1])

final_array.drop(
    final_array[final_array['Country_Region'] != "US"].index, inplace=True)

if delete_unassigned:
    final_array.drop(
        final_array[final_array['Admin2'] == "Unassigned"].index, inplace=True)
    final_array.drop(
        final_array[final_array.Admin2.str.contains("Out of")].index, inplace=True)

if sort_by_location:
    final_array = final_array.sort_values(['Province_State', 'Admin2'])

if delete_location:
    final_array = final_array.drop(
        columns=["Admin2", "Province_State", "Country_Region", "Date"])
    final_array = final_array.to_numpy()

    if normalize_data:
        # normalize the columns (axis = 0)
        normed_matrix = normalize(final_array, axis=0, norm='l2')
        #normed_matrix1 = normed_matrix.tolist()
        # with open('yaydata.csv', 'w') as f:
        #     for item in normed_matrix:
        #         f.write("%s\n" % item)
        np.savetxt("yaydata.txt", normed_matrix, delimiter=",")
    else:
        with open('yaydata.txt', 'w') as f:
            for item in final_array:
                f.write("%s\n" % item)

else:
    print("here")
    final_array = final_array.to_numpy()
    with open('yaydata.txt', 'w') as f:
        for item in final_array:
            f.write("%s\n" % item)
