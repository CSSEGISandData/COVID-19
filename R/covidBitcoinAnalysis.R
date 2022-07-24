#
# bitcoin and COVID regression analysis

df <- readRDS("./rdsData/covidAndBitcoin.rds")
library(lubridate)

# add time series variables 
df$time <- df$Date - mdy("01/20/2020")
df$month <- month(df$Date)
df$year <- year(df$Date)

# create "daily" variables
df %>% 
  mutate(time = Date - mdy("01/21/2020"),
         month = month(Date),
         year = year(Date),
         dailyActive = if_else(Date == mdy("01/22/2020"),Active,Active - lag(Active)),
         dailyConfirmed = if_else(Date == mdy("01/22/2020"),Confirmed,Confirmed - lag(Confirmed)),
         dailyDeaths = if_else(Date == mdy("01/22/2020"),Deaths,Deaths - lag(Deaths)),
         dailyRecovered = if_else(Date == mdy("01/22/2020"),Recovered,Recovered - lag(Recovered))) -> covidBitcoin

aModel <- lm(Close ~ dailyActive + dailyConfirmed + dailyDeaths + dailyRecovered + time + Country_Region,data = covidBitcoin)
summary(aModel)

library(lessR)
aModel <- Regression(Close ~ dailyActive + dailyConfirmed + dailyDeaths + dailyRecovered + time + Country_Region,data = covidBitcoin)
summary(aModel)

