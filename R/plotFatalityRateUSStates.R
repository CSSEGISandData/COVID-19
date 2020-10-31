#
#

plotCovidFatalityRateUSStates <- function(data,states,yLimits=NULL){
  require(ggplot2)
  require(dplyr)
  require(ggeasy)
  require(lubridate)
  df <- data[data$Province_State %in% states & data$date > "04-01-2020",]
  df <- rename(df,State = Province_State)
  asOfDate <- max(df$date)
  ggplot(df, aes(date,Mortality_Rate, group = State)) + 
    geom_line(aes(group = State), color = "grey80") +
    geom_point(aes(color = State)) + scale_x_date(date_breaks = "2 days") +
    easy_rotate_x_labels(angle = 45, side = "right")  +
    scale_y_continuous(limits = yLimits) + 
    labs(x = "Date",
         y = "Fatalities per 100 Confirmed Cases", 
         title = paste("COVID-19 Fatality Rates for Selected US States as of",asOfDate) )
}

plotCovidDailyCasesUSStates <- function(data,states,yLimits=NULL){
  require(ggplot2)
  require(dplyr)
  require(ggeasy)
  require(lubridate)
  df <- data[data$Province_State %in% states & data$date > "04-01-2020",]
  df <- rename(df,State = Province_State)
  asOfDate <- max(df$date)
  ggplot(df, aes(date,Daily_Cases, group = State)) + 
    geom_line(aes(group = State), color = "grey80") +
    geom_point(aes(color = State)) + scale_x_date(date_breaks = "2 days") +
    easy_rotate_x_labels(angle = 45, side = "right")  +
    scale_y_continuous(limits = yLimits) + 
    labs(x = "Date",
         y = "Cases Reported Each Day", 
         title = paste("COVID-19 Daily Cases for Selected US States as of",asOfDate) )
}

