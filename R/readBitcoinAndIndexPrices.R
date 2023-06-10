#
# readBitcoinAndIndexPrices.R 
#
# read a set of US and global stock indices along w/ btc price in USD 
# 
# alternate source for index data
# https://www.marketwatch.com/investing/index/ukx/download-data?startDate=04/27/2020&endDate=04/27/2023&countryCode=uk 
#
#
# (c) 2020 - 2023 Leonard Greski
# copying permitted with attribution 

library(quantmod)
library(lubridate)

symbols = c('BTC-USD','^GSPC','^FTSE','^VIX','^DJI')
start = as.Date("2020-01-01")
until = today() - 1 # get data through yesterday 

stocks = lapply(symbols, function(symbol) {
     aStock = as.data.frame(getSymbols(symbol,src='yahoo', from = start, to = until, 
                                       auto.assign = FALSE))
     colnames(aStock) <- c("Open","High","Low","Close","Volume","Adjusted")
     aStock$Symbol <- symbol
     aStock$Date <- as.Date(rownames(aStock),"%Y-%m-%d")
     aStock
})
btcData <- do.call(rbind,stocks)

# see min / max dates by symbol
library(tidyverse)
btcData %>%
     group_by(Symbol) %>%
     summarise(min_date = min(Date),
               max_date = max(Date),
               count = n())

# remove caret from Symbol name
btcData$Symbol <- sub("^","",btcData$Symbol,fixed = TRUE)
btcData$Symbol <- sub("-","_",btcData$Symbol,fixed = TRUE)
# refactor to one row per date, columns are symbol close data



btcData %>%
     select(Close,Volume,Symbol,Date) %>%
     pivot_wider(id_cols = Date,
                 names_from = Symbol,
                 values_from = c("Volume","Close"),
                 names_glue = "{Symbol}.{.value}")
     

