
#Environment cleanup
rm(list=ls())

#Install Packages if needed:
pkgs <- c(
  "dplyr", # package for data manipulation
  "ggplot2",## Libraries for Plotting our Results
  "gridExtra",## Libraries for Plotting our Results
  "tidyverse", # Library for data cleaning
  "caret",## Library for preprocessing, train, confusion matrix, and many other functions
  "lubridate"
  )
missingpkgs <- lapply(pkgs, require, character.only = TRUE)
missingpkgs <- unlist(missingpkgs)
if (sum(!missingpkgs)) {
  install.packages(pkgs[!missingpkgs])
  lapply(pkgs[!missingpkgs], library, character.only = TRUE)
}


#Store URLs
directory <- "~/R/COVID-19-master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-"
confirmed_URL <- paste0(directory,"Confirmed.csv")
  #"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
deaths_URL <- paste0(directory,"Deaths.csv")
  #"https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
recovered_URL <- paste0(directory,"Recovered.csv")
  #"https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"

#Load Data
confirmedCases <- read.csv(confirmed_URL)
deaths <- read.csv(deaths_URL)
recovered <- read.csv(recovered_URL)

tidyConfirmedCases <- confirmedCases %>%
        pivot_longer(-c(Province.State, Country.Region, Lat, Long), names_to = "Date", values_to = "cumulativeCases") %>%
        mutate(Date = substring(Date, 2))%>%
        mutate(Date = mdy(Date,tz="UTC"))%>%
        select(Date,Country.Region, everything())%>%
        arrange(Date,Country.Region,Province.State)%>%
        rename(lat = Lat, )

#identify countries without provinces
noProvinces <- tidyConfirmedCases$Province.State==""

#convert provinces to character for ease of replacement
tidyConfirmedCases$Province.State <- tidyConfirmedCases$Province.State %>%
        as.character() 
 
#Replace empty province entries with country names       
tidyConfirmedCases$Province.State[noProvinces]<-tidyConfirmedCases$Country.Region[noProvinces]%>%
        as.character()

#Convert Province back to factor
tidyConfirmedCases$Province.State <- tidyConfirmedCases$Province.State %>%
        as.factor()

#Identify cumulative cases as of most recent download
current <- max(tidyConfirmedCases$Date)
currentCumulativeTotal <- filter(tidyConfirmedCases,Date==current)

#Create interactive map
currentCumulativeTotal %>%
        leaflet() %>%
        addTiles() %>%
        addCircleMarkers(
                weight = 1,
                color = "red",
                radius = 2*log(currentCumulativeTotal$cumulativeCases),
                #clusterOptions = markerClusterOptions(), 
                popup = currentCumulativeTotal$Province.State
                )# %>%

#Code for adding a date to the map
#        addCircleMarkers(lat = 75, lng = -120, label = today(),
#                   markerOptions(opacity = .001, radius = .01),
#                   labelOptions = labelOptions(noHide = T, textsize = "12px"))
