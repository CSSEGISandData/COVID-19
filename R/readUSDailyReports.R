#
# read US daily reports
#

directory <- "./csse_covid_19_data/csse_covid_19_daily_reports_us/"
theFiles <- list.files(path=directory,pattern="*.csv",full.names = TRUE)
filenames <- list.files(path=directory,pattern="*.csv")

data <- read.csv(paste0(directory,"07-15-2020.csv"),header = TRUE)


dataList <- lapply(1:length(theFiles),function(x){
  y <-read.csv(theFiles[x],stringsAsFactors=FALSE)
  # clean column names and add missing columns 
  fileDate <- mdy(substr(filenames[x],1,10))
  
  # common processing across all files
  colnames(y) <- gsub("\\.","_",colnames(y))
  colnames(y) <- sub("ï__","",colnames(y)) 
  y
}) 

# check number of columns, should be 18 for all files 
table(unlist(lapply(1:length(theFiles),function(x) length(names(dataList[[x]])))))

data <- do.call(rbind,dataList)
