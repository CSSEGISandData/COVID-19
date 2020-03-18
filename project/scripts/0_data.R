library(tidyverse)
library(tidylog)

ts_cv_conf<- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
ts_cv_deaths<- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv")
ts_cv_rec <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv")
