#
# read US state level daily reports
#

directory <- "./csse_covid_19_data/csse_covid_19_daily_reports_us/"
theFiles <- list.files(path=directory,pattern="*.csv",full.names = TRUE)
filenames <- list.files(path=directory,pattern="*.csv")

library(lubridate)

dataList <- lapply(1:length(theFiles),function(x){
  y <-read.csv(theFiles[x],stringsAsFactors=FALSE)
  # clean column names and add missing columns 
  y$date <- mdy(substr(filenames[x],1,10))
  
  # common processing across all files
  colnames(y) <- gsub("\\.","_",colnames(y))
  colnames(y) <- sub("ï__","",colnames(y)) 
  y
}) 

# check number of columns, should be 19 for all files 
table(unlist(lapply(1:length(theFiles),function(x) length(names(dataList[[x]])))))

data <- do.call(rbind,dataList)
# add daily calculations
library(dplyr)
dailyData <- data %>% group_by(Province_State) %>%
  arrange(.,Province_State,date,.by_group=TRUE) %>% 
  mutate(Daily_Deaths = Deaths - lag(Deaths),
         Daily_Cases = Confirmed - lag(Confirmed),
         Daily_Tests = People_Tested - lag(People_Tested))

cols <- (c("date","Province_State","Confirmed","Daily_Cases","Deaths","Daily_Deaths"))
dailyData[,cols]
source("./R/plotFatalityRateUSStates.R")
# state level fatality rates
theStates <- c("Georgia","Florida","Texas","New York","California")
plotCovidFatalityRateUSStates(data,theStates,yLimits=c(0,10))
plotCovidDailyCasesUSStates(dailyData,theStates,yLimits=c(-200,18000))
aModel <- lm(Daily_Cases ~  Daily_Tests,data = dailyData)
summary(aModel)
