#
# readCovidRDS.R
# 
# read the COVID data after the files have been combined into
# a single data frame and saved to disk

# depends on: readDailyReportsData.R 
if(!file.exists("./rdsData/covidData.rds")) source("./R/readDailyReportsData.R")

system.time(data <- readRDS("./rdsData/covidData.rds"))
library(tidyverse)
library(lubridate)
max(data$date)
countries <- as.data.frame(table(data$Country_Region))

# clean the country names
data$Country_Region <- sub(" Azer","Azer",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub(", The","",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Dominica$","Dominican Republic",data$Country_Region)
data$Country_Region <- sub("g SAR","g",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub(" (Islamic Republic of)","",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Macao SAR","Macau",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Mainland ","",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("occupied Palestinian territory","Israel",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("West Bank and Gaza","Israel",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Palestine","Israel",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Republic of the Congo","Congo (Kinshasa)",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Republic of Korea","Korea, South",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Northern Ireland","Ireland",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Republic of ","",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Diamond Princess","Cruise Ship",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Russian Federation","Russia",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("South Korea","Korea, South",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("South Sudan","Sudan",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Summer Olympics 2020","Japan",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Taiwan*","Taiwan",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("The Gambia","Gambia",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("The Bahamas","Bahamas",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Taipei and environs","Taiwan",data$Country_Region,fixed = TRUE)
data$Country_Region <- sub("Winter Olympics 2022","China",data$Country_Region,fixed = TRUE)

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