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
normalize_data = False

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
    # raw_data = raw_data.dropna()  # be careful b/c maybe too early
    raw_data = raw_data[raw_data['Lat'].notna()]
    raw_data = raw_data[raw_data['Long_'].notna()]
    raw_data = raw_data.fillna(value="N/A")
    raw_data.sort_values(['Province_State', 'Admin2'])
    np_raw_data = raw_data.to_numpy()

    rows_to_delete = []

    counter = 0
    current_state = ""
    unassigned_array = []
    # assigned_array = numpy.empty([1000, 3]) #1000 is just to be safe, used to store things to calculate center of mass
    assigned_array = []
    for i in np_raw_data:
        if i[2] != "US":  # hardcoded index for checking state/country
            rows_to_delete.append(counter)
        else:
            # save row numbers of
            if delete_unassigned:  # delete unassigned row if need be
                print("deleting unassigned")
                if i[0] == "Unassigned":  # hardcoded index for checking county
                    print("deleting unassigned")
                    rows_to_delete.append(counter)
                elif "Out of" in str(i[0]):
                    print("deleting unassigned")
                    rows_to_delete.append(counter)
            else:  # i.e. assign unassigned to center of mass
                if current_state != i[1]:  # i[1] is hardcoded index for state
                    current_state = i[1]
                    # center of mass calculation + attach to unassigned array
                    unassigned_array.clear()
                else:
                    # hardcoded index for slicing to get lat, long, cases
                    assigned_array.append(i[3:6])

                # save row numbers of those in a state with no coordinates in array
                # after getting thru the state, attach center of mass coordinates to those
                # clear array

        counter = counter + 1

    if day == 0:
        # 0 refers to deleting the rows
        final_array = np.delete(np_raw_data, rows_to_delete, 0)
    else:
        # 0 refers to deleting the rows
        selected_data = np.delete(np_raw_data, rows_to_delete, 0)
        final_array = np.vstack((final_array, selected_data))


# np.savetxt("yaydata.csv", final_array, delimiter=",") #problematic bc different dtypes

# with open('yaydata.txt', 'w') as f:
#     for item in final_array:
#         f.write("%s\n" % item)


if delete_location:
    selected_data1 = np.delete(final_array, [0, 1, 2], 1)  # deleting locations

    if normalize_data:
        normed_matrix = normalize(selected_data1, axis=1, norm='l1')
        #normed_matrix1 = normed_matrix.tolist()
        # with open('yaydata.csv', 'w') as f:
        #     for item in normed_matrix:
        #         f.write("%s\n" % item)
        np.savetxt("yaydata.txt", normed_matrix, delimiter=",")
    else:
        with open('yaydata.txt', 'w') as f:
            for item in selected_data1:
                f.write("%s\n" % item)

else:
    # final_array.sort(order=[1, 0])
    with open('yaydata1.txt', 'w') as f:
        for item in final_array:
            f.write("%s\n" % item)

# convert array back into floats
#convertedArray = r.astype(np.float)
