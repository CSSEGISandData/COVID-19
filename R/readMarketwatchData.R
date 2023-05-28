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
             "Nikkei","Oil","SandP500","VIX")

indexesList <- lapply(indexes,function(x){
  theFiles <- list.files("./financial_data",
                         pattern = x,
                         full.names = TRUE)
  do.call(rbind,lapply(theFiles,function(y){
    df <- read.csv(y)
    df$symbol <- x
    df
  }))
})

indexData <- do.call(rbind,indexesList)

table(indexData$symbol)
