#
# Analyze column names in JHU covid-19 data files 
# 

directory <- "./csse_covid_19_data/csse_covid_19_daily_reports"
theFiles <- list.files(path=directory,pattern="*.csv",full.names = TRUE)
filenames <- list.files(path=directory,pattern="*.csv")
# read data 
dataList <- lapply(1:length(theFiles),function(x){
  y <-read.csv(theFiles[x],stringsAsFactors=FALSE)
  # add date from file names to mitigate coding errors in raw data
  y$date <- substr(filenames[x],1,10)
  y
})

# generate data dictionary day by day 

namesList <- lapply(dataList,function(x){
  columnName <- names(x)
  theDate <- x[1,"date"]
  data.frame(date = rep(theDate,length(columnName)),columnName,stringsAsFactors = FALSE)
})

namesData <- do.call(rbind,namesList)

library(dplyr)

namesData %>% group_by(columnName) %>%
  summarise(firstUsed = min(date), lastUsed = max(date)) -> summarisedNames

# print column names so we can see where changes occurred over time
summarisedNames 