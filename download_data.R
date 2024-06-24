library(readr)
library(dplyr)
library(maps)
library(usmap)
library(ggplot2)
library(tidyverse)


setwd("~/Dropbox/R coding/R coding practice/Covid-19/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us")
files <- list.files(path = "~/Dropbox/R coding/R coding practice/Covid-19/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us", pattern = "*.csv", full.names = T)
tbl <- sapply(files, read_csv, simplify=FALSE) %>%
bind_rows(.id = "id")

map("state")
with(tbl[1,8], points(tbl[1,6], tbl[1,5]))
with(tbl[4,8], points(tbl[4,6], tbl[4,5]))

alabama <- filter(tbl, Province_State == "Alabama")
max(alabama$Deaths)

deathsPerState <- aggregate(tbl$Deaths, by = list(tbl$Province_State), max)
colnames(deathsPerState) <- c("State", "Deaths")

states <- unique(tbl[, c(2,5,6)])

tbl <- arrange(tbl, Province_State)

deaths_location <- merge(deathsPerState, states, by.x = "State", by.y = "Province_State")
deaths_location <- deaths_location[-c(3,4,5,12,13,16,17,42,43,47,49,50,58),]
deaths_location <- cbind(deaths_location, state.abb)
state_deaths <- deaths_location[, c(5,2)]
fips <- 01:50
state_deaths <- cbind(fips, state_deaths)


plot_usmap(data = state_deaths, values = "Deaths", color = "red") + 
        scale_fill_continuous(low = "white", high = "red", name = "Deaths by State", label = scales::comma) +
        theme(legend.position = "right")

















