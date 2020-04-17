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