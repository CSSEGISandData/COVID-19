# CSSE COVID-19 Dataset

## Daily reports (csse_covid_19_daily_reports)

This folder contains daily case reports. All timestamps are in UTC (GMT+0).

### File naming convention
MM-DD-YYYY.csv in UTC.

### Field description
* Province/State: China - province name; US/Canada/Australia/ - city name, state/province name; Others - name of the event (e.g., "Diamond Princess" cruise ship); other countries - blank.
* Country/Region: country/region name conforming to WHO (will be updated).
* Last Update: MM/DD/YYYY HH:mm  (24 hour format, in UTC).
* Confirmed: the number of confirmed cases. For Hubei Province: from Feb 13 (GMT +8), we report both clinically diagnosed and lab-confirmed cases. For lab-confirmed cases only (Before Feb 17), please refer to [who_covid_19_situation_reports](https://github.com/CSSEGISandData/COVID-19/tree/master/who_covid_19_situation_reports). For Italy, diagnosis standard might be changed since Feb 27 to "slow the growth of new case numbers." ([Source](https://apnews.com/6c7e40fbec09858a3b4dbd65fe0f14f5))
* Deaths: the number of deaths.
* Recovered: the number of recovered cases.

### Update frequency
* Files after Feb 1 (UTC): once a day around 23:59 (UTC).
* Files on and before Feb 1 (UTC): the last updated files before 23:59 (UTC). Sources: [archived_data](https://github.com/CSSEGISandData/COVID-19/tree/master/archived_data) and dashboard.

### Data sources
Refer to the [mainpage](https://github.com/CSSEGISandData/COVID-19).

### Why create this new folder?
1. Unifying all timestamps to UTC, including the file name and the "Last Update" field.
2. Pushing only one file every day.
3. All historic data is archived in [archived_data](https://github.com/CSSEGISandData/COVID-19/tree/master/archived_data).

---
## Time series summary (csse_covid_19_time_series)

This folder contains daily time series summary tables, including confirmed, deaths and recovered. All data are from the daily case report.

### Field descriptioin
* Province/State: same as above.
* Country/Region: same as above.
* Lat and Long: a coordinates reference for the user.
* Date fields: M/DD/YYYY (UTC), the same data as MM-DD-YYYY.csv file.

### Update frequency
* Once a day.

---
## Data modification records
We are also monitoring the curve change. Any errors made by us will be corrected in the dataset. Any possible errors from the original data sources will be listed here as a reference.
* NHC 2/14: Hubei Province deducted 108 prior deaths from the death toll due to double counting.
* About DP 3/1: All cases of COVID-19 in repatriated US citizens from the Diamond Princess are grouped together, and their location is currently designated at the ship’s port location off the coast of Japan. These individuals have been assigned to various quarantine locations (in military bases and hospitals) around the US. This grouping is consistent with the CDC.
