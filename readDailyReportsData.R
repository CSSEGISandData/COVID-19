#
# read JHU covid-19 data
#

data <- read.csv('./csse_covid_19_data/csse_covid_19_daily_reports/03-03-2020.csv',
                 stringsAsFactors=FALSE)

country <- table(data$Country_Region)
country[country > 1]

# georgia data

georgia <- data[data$Province_State == "Georgia",]

# read all files in directory
directory <- "./csse_covid_19_data/csse_covid_19_daily_reports"
theFiles <- list.files(path=directory,pattern="*.csv",full.names = TRUE)
filenames <- list.files(path=directory,pattern="*.csv")

columnList <- c("Province_State","Country_Region","Last_Update","Confirmed",
                "Deaths","Recovered","date")                
dataList <- lapply(1:length(theFiles),function(x){
  y <-read.csv(theFiles[x],stringsAsFactors=FALSE)
  # replace '.' with '_' in column names so we can rbind() without error
  colnames(y) <- sub("\\.","_",colnames(y))
  y$date <- substr(filenames[x],1,10)
  y[,columnList]
  })

# discovered that March 1, added lat long data
# discovered that March 22, added 4 columns, changed '.' to '_' in names

# data from Johns Hopkins University Center for Systems Science and Engineering
# on GitHub at https://github.com/CSSEGISandData/COVID-19
# 
directory <- "./csse_covid_19_data/csse_covid_19_daily_reports"
theFiles <- list.files(path=directory,pattern="*.csv",full.names = TRUE)
filenames <- list.files(path=directory,pattern="*.csv")
# read data as of March 22
dataList <- lapply(61:85,function(x){
  y <-read.csv(theFiles[x],stringsAsFactors=FALSE)
  # add date from file names to mitigate coding errors in raw data
  y$date <- substr(filenames[x],1,10)
  y
})

data <- do.call(rbind,dataList)
library(lubridate)
georgia <- data[data$Province_State == "Georgia",]
cobb <- georgia[georgia$Admin2 %in% c("Cobb"),]
cobb$date <- mdy(cobb$date)

plot(cobb$date,cobb$Confirmed,type = "h",cex = .5,
     main="Cobb County GA - COVID-19 Confirmed Cases",
     xlab = "Date",ylab = "Confirmed Cases")

fulton <- georgia[georgia$Admin2 %in% c("Fulton"),]
fulton$date <- mdy(fulton$date)

plot(fulton$date,fulton$Confirmed,type = "h",cex = .5,
     main="Fulton County GA - COVID-19 Confirmed Cases",
     xlab = "Date",ylab = "Confirmed Cases")
