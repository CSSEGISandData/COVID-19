## Time series summary (csse_covid_19_time_series)

This folder contains daily time series summary tables, including confirmed, deaths and recovered. All data is read in from the daily case report. The time series tables are subject to be updated if inaccuracies are identified in our historical data. The daily reports will not be adjusted in these instances to maintain a record of raw data. 

Two time series tables are for the US confirmed cases and deaths, reported at the county level. They are named `time_series_covid19_confirmed_US.csv`, `time_series_covid19_deaths_US.csv`, respectively.

Three time series tables are for the global confirmed cases, recovered cases and deaths. Australia, Canada and China are reported at the province/state level. Dependencies of the Netherlands, the UK, France and Denmark are listed under the province/state level. The US and other countries are at the country level. The tables are renamed  `time_series_covid19_confirmed_global.csv` and `time_series_covid19_deaths_global.csv`, and `time_series_covid19_recovered_global.csv`, respectively.

### Update frequency

* Once a day around 23:59 (UTC).

###  Deprecated warning
The files below were archived [here](https://github.com/CSSEGISandData/COVID-19/tree/master/archived_data/archived_time_series), and will no longer be updated. With the release of the new data structure, we are updating our time series tables to reflect these changes. Please reference `time_series_covid19_confirmed_global.csv` and `time_series_covid19_deaths_global.csv` for the latest time series data. 

* `time_series_19-covid-Confirmed.csv`
* `time_series_19-covid-Deaths.csv`	
* `time_series_19-covid-Recovered.csv`
