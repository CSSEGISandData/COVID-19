#
# readCovidRDS.R
# 
# read the COVID data after the files have been combined into
# a single data frame and saved to disk

system.time(data <- readRDS("./rdsData/covidData.rds"))
library(tidyverse)
library(lubridate)
data$date <- mdy(data$date)

subsetCovidData <- data %>%
     filter(date > mdy("01/01/2020") & date < mdy("06/01/2022"))

aTable <- subsetCovidData %>% 
     group_by(date) %>% 
     summarise(dailyObservations = n())