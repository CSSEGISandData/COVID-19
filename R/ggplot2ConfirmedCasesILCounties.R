#
# COVID-19 Confirmed Cases for selected Illinois USA Counties
# 
# 2020-04-17 lgreski
# 
# dependencies: load & clean data with ./R/ReadDailyReportsData.R 

library(lubridate)
library(ggplot2)
### edit state & counties to be plotted
theState <- "Illinois"
theCounties <- c("Cook","Lake","Will","McHenry","DuPage","Kane")
### 

state <- data[data$Province_State == theState,]
counties <- state[state$Admin2 %in% theCounties,]
colnames(counties) <- sub("Admin2","County",colnames(counties))
counties$date <- mdy(counties$date)
asOfDate <- max(counties$date)
message("data as of ", asOfDate)
ggplot(counties, aes(date,Confirmed, group = County)) + 
  geom_line(aes(group = County), color = "grey80") +
  geom_point(aes(color = County)) + 
  labs(x = "Date",
       y = "Confirmed Cases", 
       title = paste("COVID-19 Cases for Selected Counties in",theState,"USA as of",asOfDate) )

today <- counties[counties$date == asOfDate,]