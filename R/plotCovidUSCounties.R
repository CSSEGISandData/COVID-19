#
# plotCovidUSCounties
#
# generalized plot function 
#
# date       author
# -------------------------
# 2020-04-18 lgreski
#
# arguments
# -------------------------
# data      - data file to be subset and graphed 
# state     - the name of one state in the US 
# counties  - a list of counties for the state being graphed
# 
# dependencies: ggeasy, ggplot2, lubridate, input data frame from 
#               JHU CSSE COVID-19 daily reports, cleaned & standardized
#
plotCovidUSCounties <- function(data,state,counties,yLimits=NULL){
  require(ggplot2)
  require(ggeasy)
  require(lubridate)
  countyData <- data[data$Admin2 %in% counties & data$Province_State == state,]
  colnames(countyData) <- sub("Admin2","County",colnames(countyData))
  countyData$date <- mdy(countyData$date)
  asOfDate <- max(countyData$date)
  ggplot(countyData, aes(date,Confirmed, group = County)) + 
    geom_line(aes(group = County), color = "grey80") +
    geom_point(aes(color = County)) + scale_x_date(date_breaks = "2 days") +
    easy_rotate_x_labels(angle = 45, side = "right")  +
    scale_y_continuous(limits = yLimits) + 
    labs(x = "Date",
         y = "Confirmed Cases", 
         title = paste("COVID-19 Cases for Selected Counties in",state,"USA as of",asOfDate) )
}