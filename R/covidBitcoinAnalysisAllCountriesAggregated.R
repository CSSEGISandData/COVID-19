#
# bitcoin and COVID regression analysis
# data dictionary is here: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data 

# Instructions: run readCovidRDSAllCountries.R before running this script

df <- readRDS("./rdsData/covidAndBitcoinAllCountries.rds")
library(lubridate)
library(tidyverse)

# read bitcoin data 
source("./R/readBitcoinPrices.R")

# create "daily" variables and time series
df %>% 
     group_by(Date) %>%
     summarise(Confirmed = sum(Confirmed),
               Incident_Rate = mean(Incident_Rate),
               Deaths = sum(Deaths),
               Fatality_Ratio = sum(Deaths) / sum(Confirmed * 100)) %>% 
     full_join(.,btcData) %>% filter(!is.na(Confirmed)) %>%
     mutate(time = Date - mdy("01/21/2020"),
            month = month(Date),
            year = year(Date),
            dailyConfirmed = if_else(Date == mdy("01/22/2020"),Confirmed,Confirmed - lag(Confirmed)),
            dailyDeaths = if_else(Date == mdy("01/22/2020"),Deaths,Deaths - lag(Deaths))) -> covidBitcoin

library(corrgram)


aModel <- lm(Close ~ Incident_Rate + Fatality_Ratio + dailyConfirmed + dailyDeaths + time ,data = covidBitcoin)
summary(aModel)

library(lessR)
aModel <- lm(Close ~ dailyActive + dailyConfirmed + dailyDeaths + time + Country_Region,data = covidBitcoin)
summary(aModel)

