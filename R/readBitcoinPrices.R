library(quantmod)
symbols = c('BTC-USD')
start = as.Date("2020-01-01")
until = today() - 1 # get data through yesterday 

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