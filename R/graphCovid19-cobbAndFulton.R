#
# graph covid-19 confirmed cases
# 2020-04-17 lgreski
#

# dependency: run ./R/readDailyReportsData.R from console to create input data frame 

library(lubridate)
georgia <- data[data$Province_State == "Georgia",]
cobb <- georgia[georgia$Admin2 %in% c("Cobb"),]
cobb$date <- mdy(cobb$date)

plot(cobb$date,cobb$Confirmed,type = "h",cex = .5,ylim=c(0,2000),
     main="Cobb County GA - COVID-19 Confirmed Cases",
     xlab = "Date",ylab = "Confirmed Cases")

fulton <- georgia[georgia$Admin2 %in% c("Fulton"),]
fulton$date <- mdy(fulton$date)

plot(fulton$date,fulton$Confirmed,type = "h",cex = .5,ylim=c(0,2000),
     main="Fulton County GA - COVID-19 Confirmed Cases",
     xlab = "Date",ylab = "Confirmed Cases")


library(sqldf)
sqldf("select distinct Admin2 from georgia order by Admin2")

library(lubridate)
library(ggplot2)
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