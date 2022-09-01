#
# readCovidRDS.R
# 
# read the COVID data after the files have been combined into
# a single data frame and saved to disk

system.time(data <- readRDS("./rdsData/covidData.rds"))
library(tidyverse)
library(lubridate)

countries <- as.data.frame(table(data$Country_Region))

# read bitcoin data 
source("./R/readBitcoinPrices.R")

subsetCovidData <- data %>%
     filter(date > mdy("01/01/2020") & date < mdy("09/01/2022")) %>%
     rename(Date = date) %>%
     # use base R ifelse() to avoid typing problem with if_else() 
     mutate(Confirmed = ifelse(is.na(Confirmed),0,Confirmed),
            Active = ifelse(is.na(Active),0,Active),
            Deaths = ifelse(is.na(Deaths),0,Deaths),
            Recovered = ifelse(is.na(Recovered),0,Recovered),
            Country_Region = case_when(Country_Region == "Mainland China" ~ "China",
                                       TRUE ~ Country_Region)) %>%
     # code to summarise() up to one row per country per day
     group_by(Country_Region,Date) %>% 
     summarise(Confirmed = sum(Confirmed),
               Active = sum(Active),
               Deaths = sum(Deaths),
               Recovered = sum(Recovered)) %>% 
     full_join(.,btcData) %>% filter(!is.na(Confirmed))

saveRDS(subsetCovidData,"./rdsData/covidAndBitcoinAllCountries.rds")