#
# read US daily reports
#

directory <- "./csse_covid_19_data/csse_covid_19_daily_reports_us/"

data <- read.csv(paste0(directory,"05-15-2020.csv"),header = TRUE)

summary(data$Recovered)

