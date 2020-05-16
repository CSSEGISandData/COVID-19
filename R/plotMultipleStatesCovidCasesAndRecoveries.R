#
# plot multiple states & render in combined chart
# 
# date       author
# ==================================================================
# 2020-04-18 lgreski

source("./R/plotCovidUSCounties.R")
source("./R/multiplot.R")
# GA
gaCounties <- c("Cobb","Fulton","Cherokee","DeKalb","Gwinnett")
p1 <- plotCovidUSCounties(data,"Georgia",gaCounties,yLimit=c(0,4000))

p2 <- plotCovidRecoveriesUSCounties(data,"Georgia",gaCounties,yLimit=c(0,4000))

# print combined plot
multiplot(p1,p2,cols = 1)

# IL
ilCounties<- c("Cook","Lake","Will","McHenry","DuPage","Kane")
p3 <- plotCovidUSCounties(data,"Illinois",ilCounties,yLimit=c(0,3500))

# CO
coCounties <- c("Denver","Arapahoe","Jefferson","Douglas","Adams")
p2 <- plotCovidUSCounties(data,"Colorado",coCounties,yLimit=c(0,3500))

# print combined plot
multiplot(p1,p2,cols = 1)

recovered <- data[data$Recovered > 0,]
ga_data <- data[data$Province_State == "Georgia",]