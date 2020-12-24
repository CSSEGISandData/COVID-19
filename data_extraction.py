# that extracts the data from the daily covid reports in the Johns Hopkins repo and produces a numpy array where each entry is a numpy array containing: (latitude, longitude, cumulative confirmed cases, number of days since covid hit the US).
import numpy as np
from pathlib import Path
import pandas as pd
from datetime import date, timedelta, datetime
from sklearn.preprocessing import normalize

data_folder = Path("csse_covid_19_data/csse_covid_19_daily_reports/")

# make days array based on inputs
pandemic_start = date(2020, 1, 22)

# don't do 3-21 or earlier
start_date = date(2020, 3, 22)
end_date = date(2020, 4, 20)

delete_location = True
delete_unassigned = True
normalize_data = True

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
    raw_data = raw_data.dropna()  # be careful b/c maybe too early
    np_raw_data = raw_data.to_numpy()

    rows_to_delete = []

    counter = 0
    for i in np_raw_data:
        if i[2] != "US":  # hardcoded index for checking state
            rows_to_delete.append(counter)
        else:
            if delete_unassigned:  # delete unassigned row if need be
                if i[0] == "Unassigned":  # hardcoded index for checking county
                    rows_to_delete.append(counter)
                elif "Out of" in str(i[0]):
                    rows_to_delete.append(counter)
        counter = counter + 1

    if day == 0:
        # 0 refers to deleting the rows
        final_array = np.delete(np_raw_data, rows_to_delete, 0)
    else:
        # 0 refers to deleting the rows
        selected_data = np.delete(np_raw_data, rows_to_delete, 0)
        final_array = np.vstack((final_array, selected_data))


if delete_location:
    selected_data1 = np.delete(final_array, [0, 1, 2], 1)  # deleting locations

    if normalize_data:
        normed_matrix = normalize(selected_data1, axis=1, norm='l1')
        with open('yaydata.txt', 'w') as f:
            for item in normed_matrix:
                f.write("%s\n" % item)
    else:
        with open('yaydata.txt', 'w') as f:
            for item in selected_data1:
                f.write("%s\n" % item)

else:
    with open('yaydata.txt', 'w') as f:
        for item in final_array:
            f.write("%s\n" % item)

# convert array back into floats
#convertedArray = r.astype(np.float)
