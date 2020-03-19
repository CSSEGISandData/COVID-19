# Covid data analysis

library(tidyverse)
library(lubridate)

# read the data
ts_recovered <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv") %>%
    mutate(status = "recovered")
ts_deaths <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-deaths.csv") %>%
    mutate(status = "deaths")
ts_confirmed <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-confirmed.csv") %>%
    mutate(status = "confirmed")
daily <- read_csv("csse_covid_19_data/csse_covid_19_daily_reports/03-18-2020.csv")

us_data <- bind_rows(ts_recovered,
                     ts_deaths,
                     ts_confirmed) %>%
    filter(`Country/Region` == "US")

country_wide <- us_data %>%
    pivot_longer(cols = 5:61, names_to = "date") %>%
    group_by(status, date) %>%
    summarize(daily_total = sum(value))

country_wide$date <- mdy(country_wide$date)

country_wide <- arrange(country_wide, date)

g <- ggplot(country_wide, aes(x = date, y = daily_total, col = status)) +
    geom_line() +
    geom_smooth() +
    theme_bw()

us_confirmed <- country_wide %>% filter(status == "confirmed")
us_confirmed$d_confirmed <- c(0, diff(us_confirmed$daily_total))

h <- ggplot(us_confirmed, aes(x = date, y = d_confirmed)) +
    geom_line() +
    geom_smooth() +
    theme_bw()