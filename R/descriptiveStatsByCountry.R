#
# descriptivesByCountry.R
#
# descriptive stats for COVID-19 data by country, so we can see
# percentage contributions of countries 

df <- readRDS("./rdsData/covidData.rds")
library(lubridate)
library(tidyverse)

max(df$date)
min(df$date)

df %>%
     rename(Date = date) %>%
     # summarize by country and day
     group_by(Country_Region,Date) %>%
     summarise(Deaths = sum(Deaths,na.rm=TRUE),
               Confirmed = sum(Confirmed,na.rm = TRUE),
               Records = n()) %>%
     mutate(Deaths = Deaths - lag(Deaths),
            Confirmed = Confirmed - lag(Confirmed)) %>% 
     # summarize daily stats by country 
     group_by(Country_Region) %>% 
     summarise(Deaths = sum(Deaths,na.rm=TRUE),
               Confirmed = sum(Confirmed,na.rm = TRUE),
               Records = sum(Records),
               Date = max(Date)) %>% 
     ungroup(.) %>%
     mutate(pct_Records = 100 * Records / sum(Records), 
            pct_Deaths = 100 * Deaths / sum(Deaths),
            pct_Confirmed = 100 * Confirmed / sum(Confirmed))-> countrySummary


# note that based on 2023 population stats, China has 18.47% of the world's
# population, but contributes only 7.2% of the confirmed cases. Therefore, 
# the country-specific data is not accurate enough to make cross-country
# comparisons. Does anyone really believe that China only had 4 million confirmed
# cases. 

# see also:
# https://www.economist.com/graphic-detail/2021/05/30/covid-19-deaths-in-wuhan-seem-far-higher-than-the-official-count 
# https://time.com/5811222/wuhan-coronavirus-death-toll/ 
# https://www.ctvnews.ca/health/coronavirus/true-toll-of-wuhan-infections-may-be-nearly-10-times-official-number-chinese-researchers-say-1.5247063 


# calculate most recent date each country contributed data
df %>%
     rename(Date = date) %>%
     group_by(Country_Region) %>%
     summarize(lastUpdateDate = max(Date)) -> df2

# since data is cumulative, use most recent data as a cross check
# to confirm the daily data was aggregated correctly 

df %>%
     rename(Date = date) %>%
     group_by(Country_Region) %>%
     filter(Date == max(Date)) %>% 
     summarise(Deaths = sum(Deaths,na.rm=TRUE),
               Confirmed = sum(Confirmed,na.rm = TRUE),
               Date = max(Date)) %>% 
     ungroup(.) %>%
     mutate(pct_Deaths = 100 * Deaths / sum(Deaths),
            pct_Confirmed = 100 * Confirmed / sum(Confirmed))-> countrySummary2

     

