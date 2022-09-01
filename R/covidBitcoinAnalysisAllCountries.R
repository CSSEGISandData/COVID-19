#
# bitcoin and COVID regression analysis
# data dictionary is here: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data 

# Instructions: run readCovidRDSAllCountries.R before running this script

df <- readRDS("./rdsData/covidAndBitcoinAllCountries.rds")
library(lubridate)
library(tidyverse)

# create "daily" variables and time series
df %>% 
  mutate(time = Date - mdy("01/21/2020"),
         month = month(Date),
         year = year(Date),
         dailyActive = if_else(Date == mdy("01/22/2020"),Active,Active - lag(Active)),
         dailyConfirmed = if_else(Date == mdy("01/22/2020"),Confirmed,Confirmed - lag(Confirmed)),
         dailyDeaths = if_else(Date == mdy("01/22/2020"),Deaths,Deaths - lag(Deaths))) %>%
  select(Date,dailyActive,dailyConfirmed,dailyDeaths,time,month,year) -> covidBitcoin

library(corrgram)


aModel <- lm(Close ~ dailyActive + dailyConfirmed + dailyDeaths + time ,data = covidBitcoin)
summary(aModel)

library(lessR)
aModel <- Regression(Close ~ dailyActive + dailyConfirmed + dailyDeaths + dailyRecovered + time + Country_Region,data = covidBitcoin)
summary(aModel)

