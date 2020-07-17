#
#

plotCovidFatalityRateUSStates <- function(data,states,yLimits=NULL){
  require(ggplot2)
  require(dplyr)
  require(ggeasy)
  require(lubridate)
  aSubset <- data[data$Province_State %in% states & data$date > "04-01-2020",]
  aSubset %>% group_by(.,Province_State,date) %>%
    summarise(., Confirmed = sum(Confirmed),
              Deaths = sum(Deaths),
              Case_Fatality_Ratio = Deaths * 100000 / (Confirmed) ) %>%
    rename(.,State = Province_State) -> df
  df$date <- mdy(df$date)
  asOfDate <- max(df$date)
  ggplot(df, aes(date,Case_Fatality_Ratio, group = State)) + 
    geom_line(aes(group = State), color = "grey80") +
    geom_point(aes(color = State)) + scale_x_date(date_breaks = "2 days") +
    easy_rotate_x_labels(angle = 45, side = "right")  +
    scale_y_continuous(limits = yLimits) + 
    labs(x = "Date",
         y = "Fatalities per 100,000 Confirmed Cases", 
         title = paste("COVID-19 Fatality Rates for Selected US States as of",asOfDate) )
}

