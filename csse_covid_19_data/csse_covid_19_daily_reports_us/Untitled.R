library(readr)
library(plyr)
library(tidyverse)

setwd("/Users/coreyneff/Desktop/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us/")

files <- list.files()
states_csv <- ldply(files, read_csv)

new <- separate(states_csv, col = "Last_Update", 
        into = c("Date", "Time"), 
        sep = " ", convert = T, )

new <- select(new, -"Time")
new$Date <- as.POSIXct(new$Date)
class(new$Date)

#Deaths per day in U.S.

complete <- new[which(new$Province_State != "Recovered"),]

complete <- aggregate(complete$Deaths, list(complete$Date), sum) 
ggplot() +
  geom_line(aes(as.POSIXct(Group.1),x)) +
  geom_smooth(aes(as.POSIXct(Group.1),x))

#Deths per day by region
complete <- new[which(new$Province_State != "Recovered"),]
data(state)
state.name[51] <- "District of Columbia"
state.region[51] <- "Northeast"
complete$Country_Region<- sapply(complete$Province_State, function(x) state.region[which(state.name==x)])
complete$Country_Region <- factor(complete$Country_Region, levels = c(1:4), labels = c("Northeast", "South", "Midwest", "West"))
complete_region <- data.frame(aggregate(complete$Deaths, list(complete$Date, complete$Country_Region), sum))
names(complete_region) <- c("Date", "Region", "Deaths")
complete_region$Region <- as.character(complete_region$Region)
complete_region$Population[1:80] <- 55982803
complete_region$Population[81:160] <- 125580448
complete_region$Population[161:240] <- 68329004
complete_region$Population[241:320] <- 78347268

ggplot(complete_region) +
  geom_line(aes(Date,Deaths/Population*1000, col = Region)) +
  geom_smooth(aes(Date,Deaths/Population*1000, col = Region), method = "loess")

#Incidence rate by region
aggregate(complete$Incident_Rate, list(complete$Date, complete$Country_Region), sum) %>%
  ggplot() +
  geom_line(aes(Group.1, x, col = Group.2)) +
  geom_smooth(aes(Group.1, x, col = Group.2))

ggplot(complete, aes(x=date)) + 
  geom_area(aes(y=psavert+uempmed, fill="psavert"))

#Pie chart of deaths per state (top 10) so far
bar <- aggregate(complete$Deaths, list(complete$Province_State), sum)
#c <- c("All Other", sum(bar$x[-1:-5]))
#bar <- rbind(bar,c)
c <- bar
bar$x <- as.numeric(bar$x)
bar <- arrange(bar,desc(bar$x))
ybreaks <- cumsum(bar$Deaths) - bar$Deaths/2
bar <- bar[1:5,] 
ggplot(bar,(aes(fill=State))) +
  geom_bar(aes(x="", y=Deaths), width = 1, stat = "identity", color = "black") +
  coord_polar("y", start = 0) +
  geom_text(aes(x="", y=Deaths, label = paste(round(Deaths / sum(Deaths) * 100, 1), "%")), position = position_stack(vjust = 0.5)) +
  labs(x = NULL, y = NULL) + 
  ggtitle("Percentage of Deaths from Top 5 States") +
  scale_fill_manual(values = c("#0072B2", "#D55E00", "#CC79A7","#56B4E9", "#009E73"))+
  theme(axis.ticks=element_blank(),  # the axis ticks
        axis.title=element_blank(),  # the axis labels
        axis.text.y=element_blank(),
        axis.text.x=element_text(color='black'),
        legend.position = "none",
        panel.background = element_rect(fill = "white")) +
  scale_y_continuous(
    breaks=ybreaks,  
    labels=bar$State) 


  
      

