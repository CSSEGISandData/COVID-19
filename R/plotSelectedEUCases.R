#
# plot covid-19 cases for selected countries in Europe
#

data$Country_Region[data$Country_Region == "UK"] <- "United Kingdom"
library(dplyr)
library(ggplot2)
library(ggeasy)
countryList <- c("United Kingdom", "Ireland", "France","Germany", 
                 "Italy","Spain","Belgium","Netherlands")

europe <- data %>% filter(Country_Region %in% countryList & date > "02-21-2020") %>% 
  group_by(Country_Region, date) %>%
  summarise(Confirmed = sum(Confirmed)) %>% rename(Country = Country_Region)

europe$date <- mdy(europe$date)
asOfDate <- max(europe$date)
message("data as of ", asOfDate)
ggplot(europe, aes(date,Confirmed, group = Country)) + 
  geom_line(aes(group = Country), color = "grey80") +
  geom_point(aes(color = Country)) + scale_x_date(date_breaks = "2 days") +
  easy_rotate_x_labels(angle = 45, side = "right")  +
  labs(x = "Date",
       y = "Confirmed Cases", 
       title = paste("COVID-19 Cases for Selected Countries as of",asOfDate) )



#
# get list of country names
library(sqldf)
sqlStmt <- paste("select Country_Region, count(*) from data group by Country_Region",
                 "order by Country_Region")
sqldf(sqlStmt)






