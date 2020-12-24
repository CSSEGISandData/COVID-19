# that extracts the data from the daily covid reports in the Johns Hopkins repo and produces a numpy array where each entry is a numpy array containing: (latitude, longitude, cumulative confirmed cases, number of days since covid hit the US).
import numpy as np
from pathlib import Path
import pandas as pd

data_folder = Path("csse_covid_19_data/csse_covid_19_daily_reports/")

# input: days wanted (and then get the corresponding files)

file_to_open = data_folder / "12-07-2020.csv"

# r = np.genfromtxt(file_to_open, delimiter=',',
#                   dtype=None, names=True, encoding=None, usecols=("Admin2", "Province_State", "Lat", "Long_", "Confirmed"))

r = np.genfromtxt(file_to_open, delimiter=',',
                  dtype=None, names=True, encoding=None)

# + new column: number of days since covid hit the US

rows_to_delete = []

counter = 0
for i in r:
    if i[1] != "Massachusetts":  # hardcoded index for checking state
        rows_to_delete.append(counter)
    counter = counter + 1

# 0 refers to deleting the rows
selected_data = np.delete(r, rows_to_delete, 0)
print(selected_data)
with open('gendata.txt', 'w') as f:
    for item in selected_data:
        f.write("%s\n" % item)

print(type(selected_data))
# print(shape(selected_data))
selected_data1 = np.delete(selected_data, [0, 1], 1)


# # convert array back into floats
# #convertedArray = r.astype(np.float)

# print(selected_data)
# with open('gendata.txt', 'w') as f:
#     for item in selected_data1:
#         f.write("%s\n" % item)
