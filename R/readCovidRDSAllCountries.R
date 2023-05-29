#
# readCovidRDS.R
# 
# read the COVID data after the files have been combined into
# a single data frame and saved to disk
#
# (c) 2020 - 2023 Leonard Greski
# copying permitted with attribution 

# 2023-05-28 moved code to standardize country names to readDailyReportsData.R 


# depends on: readDailyReportsData.R 
if(!file.exists("./rdsData/covidData.rds")) source("./R/readDailyReportsData.R")

system.time(data <- readRDS("./rdsData/covidData.rds"))
library(tidyverse)
library(lubridate)
max(data$date)
countries <- as.data.frame(table(data$Country_Region))

countries <- as.data.frame(table(data$Country_Region))
countries$pct <- round(100 * countries$Freq / sum(countries$Freq), digits = 4) 

# read bitcoin data 
source("./R/readBitcoinPrices.R")

subsetCovidData <- data %>%
     filter(date > mdy("01/01/2020") & date < mdy("09/01/2022")) %>%
     rename(Date = date) %>%
     # use base R ifelse() to avoid typing problem with if_else() 
     mutate(Confirmed = ifelse(is.na(Confirmed),0,Confirmed),
            Active = ifelse(is.na(Active),0,Active),
            Deaths = ifelse(is.na(Deaths),0,Deaths),
            Incident_Rate = ifelse(is.na(Incident_Rate),0,Incident_Rate),
            Recovered = ifelse(is.na(Recovered),0,Recovered),
            Country_Region = case_when(Country_Region == "Mainland China" ~ "China",
                                       TRUE ~ Country_Region)) %>%
     # code to summarise() up to one row per country per day
     group_by(Country_Region,Date) %>% 
     summarise(Fatality_Rate = sum(Deaths) / sum(Confirmed) * 100,
               Confirmed = sum(Confirmed),
               Deaths = sum(Deaths),
               Incident_Rate = sum(Incident_Rate)) %>% 
     full_join(.,btcData) %>% filter(!is.na(Confirmed))

saveRDS(subsetCovidData,"./rdsData/covidAndBitcoinAllCountries.rds")