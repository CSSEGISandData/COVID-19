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