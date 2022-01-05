import csv
import json
import datetime
from pathlib import Path
# import requests
from os import listdir
from os.path import isfile, join
def convert_csv_to_json(csv_path, csv_date):
    headers = []
    liste = []
    csv_version = 1 # csv version
    with open(csv_path, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',)
        for row in spamreader:
            # print (row[0])
            if (row[0].encode('ascii', 'ignore')).decode("utf-8") == 'Province/State':
                headers = [x.encode('ascii', 'ignore').decode("utf-8") for x in row[0: 6]]
                # print (headers)
                # print("version 1")
            else:
                # headers = row[2: 5] + row[7: 10]
                headers = ['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']
                # print (headers)
                # print("version 2")
                csv_version = 2
            break
        for row in spamreader:
            if csv_version == 1:
                row = row[0: 6]              # get rid if useless info
            if csv_version == 2:
                row = row[2: 5] + row[7: 10] # remap to old format
            val = {}
            # print (row)
            for i, j in enumerate(row):
                if headers[i] == 'Confirmed' or headers[i] == 'Deaths' or headers[i] == 'Recovered':
                    if j:
                        val[headers[i]] = int(j)
                    else:
                        val[headers[i]] = 0
                elif headers[i] == 'Last Update':
                    try:
                        x = datetime.datetime.strptime(j.replace('/20 ', '/2020 '), '%m/%d/%Y %H:%M')
                        j = x.strftime("%Y-%m-%d %H:%M:%S")
                        # print(j)  
                    except:
                        pass
                    # 2/1/2020 15:23
                    # dates.ZonedDateTime.parseDateTime(d, "yyyy-MM-dd'T'HH:mm:ss");
                    # dates.ZonedDateTime.parseDateTime(d, "yyyy-MM-dd' 'HH:mm:ss");
                    x_date = datetime.datetime.strptime(j, "%Y-%m-%d %H:%M:%S").date()
                    # print(str(csv_date) + '  -  ' + str(x_date))
                    delta_days = (x_date - csv_date).days
                    if delta_days > 0: # LastUpdate field date is > csv date
                        # print (delta_days)
                        # print (csv_path)
                        # print (row)
                        # x = x - datetime.timedelta(days=1)
                        j = (x_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                    val[headers[i]] = j
                else:
                    val[headers[i]] = j
            liste.append(val)
        # print(liste)
    return liste

def filter_spain_data(json_info):
    spain_data = [
        province for province in json_info
        if (province["Country/Region"] == "Spain" and province["Province/State"] != "Unknown")
    ]

    return spain_data

# TODO
# list folder
#  if mm-dd-yyyy.json exists do nothing
#  else use mm-dd-yyyy.csv to create it
INPUT_DIR = Path("./csse_covid_19_data/csse_covid_19_daily_reports").absolute()
OUTPUT_DIR_ES = Path("./csse_covid_19_data/csse_covid_19_daily_reports_es").absolute()
today = datetime.date.today()
delta = today - datetime.timedelta(days=7)
for f in [f_ for f_ in listdir(str(INPUT_DIR)) if isfile(join(str(INPUT_DIR), f_))]:
    if f.endswith('.csv'):
        date = datetime.datetime.strptime(f.replace('.csv', ''), '%m-%d-%Y').date()
        if delta > date:
            continue
        full_path = join(str(INPUT_DIR), f)
        full_new_path = join(str(INPUT_DIR), f.replace('.csv', '.json'))

        full_path_es = join(str(OUTPUT_DIR_ES), f)
        full_new_path_es = join(str(OUTPUT_DIR_ES), f.replace('.csv', '.json'))

        print (f)
        json_info = convert_csv_to_json(full_path, date)
        json_info_es = filter_spain_data(json_info)

        with open(full_new_path, 'w') as outfile:
            json.dump(json_info, outfile)

        with open(full_new_path_es, 'w') as outfile_es:
            json.dump(json_info_es, outfile_es)