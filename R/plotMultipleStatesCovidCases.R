#
# plot multiple states & render in combined chart
# 
# date       author
# ==================================================================
# 2020-04-18 lgreski

source("./R/readDailyReportsData.R")
source("./R/plotCovidUSCounties.R")
source("./R/multiplot.R")
# GA
gaCounties <- c("Cobb","Fulton","Cherokee","DeKalb","Gwinnett")
p1 <- plotCovidUSCounties(data,"Georgia",gaCounties,yLimit=c(0,20000))

# IL
ilCounties<- c("Cook","Lake","Will","McHenry","DuPage","Kane")
p3 <- plotCovidUSCounties(data,"Illinois",ilCounties,yLimit=c(0,100000))

# CO
coCounties <- c("Denver","Arapahoe","Jefferson","Douglas","Adams")
p2 <- plotCovidUSCounties(data,"Colorado",coCounties,yLimit=c(0,20000))

# print combined plot
multiplot(p1,p2,cols = 1)

# plot fatality rates
gaCounties <- c("Cobb","Fulton","Cherokee","DeKalb","Gwinnett")
plotCovidFatalityRateUSCounties(data,"Georgia",gaCounties,yLimit=c(0,10))

ilCounties<- c("Cook","Lake","Will","McHenry","DuPage","Kane")
plotCovidFatalityRateUSCounties(data,"Illinois",ilCounties,yLimit=c(0,10))

coCounties <- c("Denver","Arapahoe","Jefferson","Douglas","Adams")
plotCovidFatalityRateUSCounties(data,"Colorado",coCounties,yLimit=c(0,10))

# state level fatality rates
theStates <- c("Georgia","Florida","Texas","New York")
plotCovidFatalityRateUSStates(data,theStates,yLimit=c(0,10000))
