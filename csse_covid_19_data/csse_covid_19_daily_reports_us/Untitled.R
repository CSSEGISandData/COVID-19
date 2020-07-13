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
complete <- new[complete.cases(new),] 
complete <- complete[which(complete$Province_State != "Recovered"),] 
aggregate(complete$Deaths, list(complete$Date), sum) %>%
ggplot() +
  geom_line(aes(as.POSIXct(Group.1),x)) +
  geom_smooth(aes(as.POSIXct(Group.1),x))

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
  
      

