#
# readBitcoinPrices.R
#
# (c) 2000 - 2023 Leonard Greski
# copying permitted with attribution 


library(quantmod)
symbols <- c("BTC-USD",'^DJI','^VIX','^HSI','^FTSE','GC=F','^N225',"CL=F","^GSPC")
symbolNames <- c("Bitcoin","DJIA","Vix","Hang Seng Index","FTSE","Gold",
                 "Nikkei 225","Oil","S&P 500")
symbols = c('^GSPC')
start = as.Date("2020-01-01")
until = as.Date("2023-01-01")

# df <- getSymbols('BTC-USD',src='yahoo', from = start, to = until, 
#                  auto.assign = FALSE)

stocks = lapply(symbols, function(symbol) {
     aStock = as.data.frame(getSymbols(symbol,src='yahoo', from = start, to = until, 
                                       auto.assign = FALSE))
     colnames(aStock) <- c("Open","High","Low","Close","Volume","Adjusted")
     aStock$Symbol <- symbol
     aStock$Date <- as.Date(rownames(aStock),"%Y-%m-%d")
     aStock
})
btcData <- do.call(rbind,stocks)