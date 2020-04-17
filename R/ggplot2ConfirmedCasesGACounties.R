#
# COVID-19 Confirmed Cases for selected Georgia USA Counties
# 
# 2020-04-17 lgreski
# 
# dependencies: load & clean data with ./R/ReadDailyReportsData.R 

library(lubridate)
library(ggplot2)
georgia <- data[data$Province_State == "Georgia",]
countyList <- c("Cobb","Fulton","Cherokee","DeKalb","Gwinnett")
gaCounties <- georgia[georgia$Admin2 %in% countyList,]
colnames(gaCounties) <- sub("Admin2","County",colnames(gaCounties))
gaCounties$date <- mdy(gaCounties$date)
asOfDate <- max(gaCounties$date)
message("data as of ", asOfDate)
ggplot(gaCounties, aes(date,Confirmed, group = County)) + 
  geom_line(aes(group = County), color = "grey80") +
  geom_point(aes(color = County)) + 
  labs(x = "Date",
       y = "Confirmed Cases", 
       title = paste("COVID-19 Cases for Selected Counties in Georgia, USA as of",asOfDate) )