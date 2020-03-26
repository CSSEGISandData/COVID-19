#
# read covid-19 case data
# https://stackoverflow.com/questions/60823499/read-csv-in-r-no-lines-available-in-input-error

theFiles <- list.files("./csse_covid_19_data/csse_covid_19_daily_reports",pattern="*.csv",full.names = TRUE)

dataList <- lapply(theFiles[1:2],function(x){
  read.csv(x,stringsAsFactors=FALSE)
})

dataList <- lapply(theFiles,read.csv,stringsAsFactors=FALSE)

# 
# archived days data
# 
theFiles <- list.files("./archived_data/archived_daily_case_updates",pattern="*.csv",full.names = TRUE)

dataList <- lapply(theFiles,read.csv,stringsAsFactors=FALSE)

head(dataList[[1]])

# show path names in list of files
head(theFiles)


# replicate original error
originalDirectory <- getwd()
path2 =paste0(originalDirectory, "/csse_covid_19_data/csse_covid_19_daily_reports")
setwd(path2)
daily_file_names<-list.files(path2)
daily_DAYS<-lapply(daily_file_names,read.csv,sep=",")

# use pattern = "*.csv"
daily_file_names<-list.files(path2,pattern = "*.csv")
daily_DAYS<-lapply(daily_file_names,read.csv,sep=",")
head(daily_DAYS[[1]])
