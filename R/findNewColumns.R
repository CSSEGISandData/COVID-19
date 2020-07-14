#
# findNewColumns.R
# find the new columns as JHU changes the data over time 

colnamesList <- lapply(dataList,function(x){
  name <- colnames(x)
  id <- 1:length(name)
  date <- rep(min(x$date),length(name))
  data.frame(id,date,name)
})

cols <- do.call(rbind,colnamesList)
table(cols$name)
