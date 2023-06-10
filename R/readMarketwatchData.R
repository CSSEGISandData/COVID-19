#
# readMarketwatchData.R
#
# (c) 2023 lgreski
# copying permitted with attribution
#
# read data that was downlaoded from marketwatch.com for various stock indexes
# or commodities between 1 January 2020 and 26 May 2023.
# data source: https://www.marketwatch.com/investing/index/djia/download-data?mod=mw_quote_tab 

indexes <- c("FTSE","DJIA","Gold","HangSeng",
             "Nikkei","Oil","SandP500","VIX",
             "BTC-USD")

# use technique from https://stackoverflow.com/questions/25088144/how-to-load-df-with-1000-separator-in-r-as-numeric-class
# to read numbers with commas to numeric format
library(methods)
setClass("chr.w.commas", contains=numeric())
setAs("character", "chr.w.commas", function(from) 
  as.numeric(gsub("\\,", "",from )) )

theColClasses <- c("character","chr.w.commas","chr.w.commas","chr.w.commas","chr.w.commas")
indexesList <- lapply(indexes,function(x){
  theFiles <- list.files("./financial_data",
                         pattern = x,
                         full.names = TRUE)
  do.call(rbind,lapply(theFiles,function(y){
    df <- read.csv(y,colClasses = theColClasses)
    df$Symbol <- x
    df$Source <- "Marketwatch"
    df$Date <- as.Date(df$Date,"%m/%d/%Y") # use this because date format is ambiguous on read.csv()
    df
  }))
})

indexData <- do.call(rbind,indexesList)

table(indexData$Symbol)
# make directory & save the RDS
if(!dir.exists("./rdsData")) dir.create("./rdsData")
saveRDS(indexData,"./rdsData/marketwatchSymbolPrices.rds")


