import csv
from operator import add 

CSSE_FOLDER = "csse_covid_19_data"
CSSE_TIME_SERIES_FOLDER = "csse_covid_19_time_series"
CSSE_DAILY_REPORTS_FOLDER = "csse_covid_19_daily_reports"
CSSE_CASES_FILE = "time_series_19-covid-Confirmed.csv"
CSSE_DEATHS_FILE = "time_series_19-covid-Deaths.csv"
CSSE_RECOVERED_FILE = "time_series_19-covid-Recovered"

WHO_FOLDER = "who_covid_19_situation_reports"
WHO_TIME_SERIES_FOLDER = "who_covid_19_sit_rep_time_series"
WHO_TIME_SERIES_FILE = "who_covid_19_sit_rep_time_series.csv"

SLASH = "/"
COMMA = ","

PROVINCE_INDEX = 0
COUNTRY_INDEX = 1
LAT_INDEX = 2
LNG_INDEX = 3
DATE_START = 4
DATE_END = 60

csse_timeseries_cases_path = CSSE_FOLDER + SLASH + CSSE_TIME_SERIES_FOLDER + SLASH + CSSE_CASES_FILE
csse_timeseries_cases_file = open(csse_timeseries_cases_path, 'r')

line_count = 0

all_entities = {}
provinces_only = {}
countries_only = {}

with open(csse_timeseries_cases_path,'r') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	for row in csv_reader:
		if (line_count == 0):
			line_count = line_count + 1
			continue

		province_name = row[PROVINCE_INDEX]
		country_name = row[COUNTRY_INDEX]
		time_series_data = row[DATE_START:DATE_END]
		time_series_data = list(map(int, time_series_data)) 
		province_country_name = country_name

		if (province_name != ""):
			province_country_name = province_name + COMMA + province_country_name

		provinces_only[province_country_name] = time_series_data

		if country_name in countries_only:
			countries_only[country_name] = list(map(add, countries_only[country_name], time_series_data))
		else:
			countries_only[country_name] = time_series_data

csse_timeseries_cases_file.close()

