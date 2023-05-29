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

indexesList <- lapply(indexes,function(x){
  theFiles <- list.files("./financial_data",
                         pattern = x,
                         full.names = TRUE)
  do.call(rbind,lapply(theFiles,function(y){
    df <- read.csv(y)
    df$Symbol <- x
    df
  }))
})

indexData <- do.call(rbind,indexesList)
indexData$Source <- "Marketwatch"

# convert character strings to numerics
aList <- lapply(c("Open","High","Low","Close"),function(x){
  indexData[[x]] <- as.numeric(gsub(",","",indexData[[x]]))
})

df <- as.data.frame(do.call(cbind,aList)) 

# add dates and indicative columns
df <- cbind.data.frame(indexData$Source,indexData$Symbol,df)
colnames(df) <- c("Source","Symbol","Open","High","Low","Close")

table(df$Symbol)
# make directory & save the RDS
if(!dir.exists("./rdsData")) dir.create("./rdsData")
saveRDS(df,"./rdsData/marketwatchSymbolPrices.rds")


