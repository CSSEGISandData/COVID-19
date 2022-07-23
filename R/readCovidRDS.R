#
# readCovidRDS.R
# 
# read the COVID data after the files have been combined into
# a single data frame and saved to disk

system.time(data <- readRDS("./rdsData/covidData.rds"))
library(tidyverse)
library(lubridate)
data$date <- mdy(data$date)

countries <- as.data.frame(table(data$Country_Region))

# read bitcoin data 
source("./R/readBitcoinPrices.R")

subsetCovidData <- data %>%
     filter(date > mdy("01/01/2020") & date < mdy("06/01/2022")) %>%
     rename(Date = date) %>%
     # code to summarise() up to one row per country per day
     group_by(Country_Region,Date) %>% 
     summarise(Confirmed = sum(Confirmed),
               Active = sum(Active),
               Deaths = sum(Deaths),
               Recovered = sum(Recovered)) %>% 
     full_join(.,btcData)

# subset to China data

chinaData <- subsetCovidData %>%
     filter(Country_Region %in% c("Mainland China","China"))