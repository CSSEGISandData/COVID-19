library(ggplot2)
library(dplyr)
library(tidyr)
library(lubridate)
library(ggthemes)

summary(mydata)

names(mydata)
mydata<-rename(mydata, Prov_State=Province_State, Country_Region="Country/Region", Last_Update="Last Update")
names(mydata)

#looking at country totals as of 18 Mar
country<- mydata %>% select(Country_Region, Confirmed, Deaths, Recovered, Latitude, Longitude)
c_totals<-country %>% group_by(Country_Region) %>% summarize(total_confirmed=sum(Confirmed), total_deaths=sum(Deaths), total_recovered=sum(Recovered))

p<-ggplot(c_totals, aes(Country_Region,total_confirmed))
p+geom_bar(stat="identity")+ coord_flip()

#US time series
confirm <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
names(confirm)
us<-confirm %>% filter(`Country/Region`=="US")
head(us)
md<-us %>% filter(`Province/State`=="Maryland")
#mdata<-melt(md, id=c(md$`Province/State`, md$`Country/Region`))

#reshaping wide Cartesian view into long indexed view
md<-md[,-c(2:4)] #removing country, lat, long
names(md)[1]<-"State" 
md_short<-md %>% gather(Date, Confirmed, "1/22/20":"3/18/20")
head(md_short)
md_short$Date<-as.Date(md_short$Date, "%m/%d/%y")#turning from char to date 
p<-ggplot(md_short, aes(Date,Confirmed))
p<-p+geom_bar(stat="identity")
#realizing don't need half the dates in the data
drama<-p + xlim("3/1/20","3/18/20") #big change here
p_short<-p + xlim(as.Date(c("2020-03-01", "2020-03-20"), format="%Y-%m-%d")) #only showing time since infection started
p_titles<-p_short + labs(x=NULL, y="Infected People", title="Confirmed COVID-19 Cases in Maryland", subtitle = "github.com/mkinlan/COVID-19.git")
p_titles + theme_economist()

##################################
#World map

library(ggplot2)
library(dplyr) #for filtering & selecting 
library(ggmap)#for scatterplot map
library(maps)#for bubblemap
library(readr) #to read CSV
library(viridis) #for colors

daily<-read.csv2("C:/Users/Morganak/Documents/R/COVID_Project/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/03-22-2020.csv", header=TRUE, sep=",", stringsAsFactors=FALSE)

str(daily)
names(daily)
colnames(daily)<-c('State','Country','Date','Confirmed', 'Deaths', 'Recover', 'Lat', 'Long')

#Filtering to only US confirmed cases in the 50 states
us_only<-daily %>% dplyr::filter(Country=="US") %>% dplyr::select('State','Confirmed','Lat', 'Long')
states<-read.csv2("C:/Users/Morganak/Documents/R/COVID_Project/COVID-19/states.csv")

s<-states[,"State"] #vector of state names

us_only<-filter(us_only, State %in% s) #filtering out locations not in the state name vector


us_only<-us_only%>% dplyr::select('Confirmed','Lat', 'Long')#selecting only needed cols
us_only$Lat<-as.numeric(us_only$Lat)
us_only$Long<-as.numeric(us_only$Long)


#Scatterplot overlaid on map
m<-get_map(location = 'US', zoom=4, maptype = "roadmap")#Getting a map of the United States
#Adding points for confirmed cases
us_point<-ggmap(m) + geom_point(data=us_only, aes(x=Long, y=Lat), size=2, alpha=.5)
us_point

#Bubble maps 
map2<-map_data("world") %>% filter(region=="USA") #getting boundaries of world (as polygon) and extracting US
ggplot() + geom_polygon(data = map2, aes(x=long, y=lat, group=group), fill="grey", alpha=.3)
  test<-map2 %>% group_by(subregion) %>% tally()#trying to find where Alaska is listed so I can remove it b/c it's huge  

#Nice US map (including Alaska and Hawaii), no add'l data
map<-map_data("world") %>% filter(region=="USA") #map data

p1<-ggplot() + geom_polygon(data = map, aes(x=long, y=lat, group=group), fill=NA, colour = "darkgray", size=0.5) +
  ylim(15,75) + xlim(-180,-60)
  
#Bubble map CONUS
#warning "Removed 2 rows containing missing values" refers to Alaska and Hawaii, which are still in dataset

us_only<-us_only %>% arrange(desc(Confirmed))#arranging confirmed desc. so that points representing larger confirmed cases will be in the background

p<-ggplot() +
  geom_polygon(data = map, aes(x=long, y=lat, group=group), fill="gray", colour = "darkgray", size=0.5) + #setting line color, fill color, line size
  ylim(23,50) + xlim(-125,-60) + #resizing to just CONUS
  geom_point(data=us_only, aes(x=Long, y=Lat, color=us_only$Confirmed, size=us_only$Confirmed, alpha=0.5)) +
  theme_void() + #gets rid of axes
  coord_map() + #plotting with correct mercator projection (prior plot was cartesian coordinates)
  scale_color_viridis() +
  #theme(legend.position="none") +
  ggtitle("Confirmed COVID-19 Cases in the U.S.") 

p<-ggplot(us_only,aes(x=Long, y=Lat, size=Confirmed)) +
  geom_polygon(data = map, aes(x=long, y=lat, group=group), fill="gray", colour = "darkgray", size=0.5) + #setting line color, fill color, line size
  ylim(23,50) + xlim(-125,-60) + #resizing to just CONUS
  geom_point(alpha=0.5, color="darkgreen") + #everything inside aes appears in legend
  theme_void() + #gets rid of axes
  coord_map() + #plotting with correct mercator projection (prior plot was cartesian coordinates)
  ggtitle("Confirmed COVID-19 Cases in the U.S.") 
  

p<-ggplot() +
  geom_polygon(data = map, aes(x=long, y=lat, group=group), fill="lightgray", colour = "darkgray", size=0.5) + #setting line color, fill color, line size
  ylim(23,50) + xlim(-125,-60) + #resizing to just CONUS
  geom_point(data=us_only, aes(x=Long, y=Lat, alpha=Confirmed, color=Confirmed, size=Confirmed)) + #everything inside aes appears in legend
  coord_map() + #plotting with correct mercator projection (prior plot was cartesian coordinates)
  ggtitle("Confirmed COVID-19 Cases in the U.S.") +
  guides( colour = guide_legend()) +
  theme_void()  #gets rid of axes
  #theme(plot.background = element_rect(fill="black")) #changes to only show one legend
          
          
          # Gradient between n colors
          sp3+scale_color_gradientn(colours = rainbow(5))          
          

