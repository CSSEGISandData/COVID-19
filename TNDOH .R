library(tidyverse)
library(stringr)
library(lubridate)
library(stringr)
library(xlsx)
library(ggthemes)
setwd("/users/coreyneff/desktop/COVID-19/")
raw1 <- "https://www.tn.gov/content/dam/tn/health/documents/cedep/novel-coronavirus/datasets/Public-Dataset-Daily-Case-Info.XLSX"
download.file(url = raw1, destfile = "daily_data")


#Total Daily Data
classes1 <- as.vector("Date")
classes1[2:19] <- "numeric"
dailyraw <- read.xlsx2(file = "daily_data", sheetIndex = 1, colClasses = classes1)

dailyraw[-1,] %>%
ggplot() + 
  geom_col(aes(DATE, NEW_CASES), col = "#3CB371") +
  geom_smooth(aes(DATE, NEW_CASES), col = "red", method = "loess") +
  ggtitle("New Cases per Day") +
  labs(x = "Date", y ="# New Cases") +
  theme(plot.title = element_text(hjust = 0.5))


#County Data Function -- Input County
raw2 <- "https://www.tn.gov/content/dam/tn/health/documents/cedep/novel-coronavirus/datasets/Public-Dataset-Daily-County-Age-Group.XLSX"
download.file(url = raw2, destfile = )
classes2 <- as.vector("Date")
classes2[2:3] <- "character"
classes2[4] <- "numeric"
countysex <- read.xlsx2(file = "county_sex", sheetIndex = 1, colClasses = classes2)
countysex <- select

county <- function(X) {
    vname <- enquo(X)
    variable_name <- rlang::quo_name(vname)
    countysex %>%
    filter(COUNTY == variable_name  & AGE_GROUP != "Pending") %>%
    ggplot() + 
    #geom_point(aes(DATE, CASE_COUNT, col = AGE_GROUP)) +
    geom_smooth(aes(DATE, CASE_COUNT,  col = AGE_GROUP), method = "loess") +
    ggtitle(paste("New Cases per Day in", variable_name, "County by Age Group", sep = " ")) +
    labs(x = "Date", y ="# New Cases") +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme_few() +
    scale_fill_few()
}

compare <- function(X,Y) {
  
  vname1 <- enquo(X)
  variable_name1 <- rlang::quo_name(vname1)
  vname2 <- enquo(Y)
  variable_name2 <- rlang::quo_name(vname2)

    first <- countysex %>%  
    filter(COUNTY == variable_name1 | COUNTY == variable_name2) 
    aggregate(first$CASE_COUNT, list(first$COUNTY, first$DATE), FUN = sum) %>%
    ggplot() + 
    geom_point(aes(Group.2, x, col = Group.1)) +
    geom_smooth(aes(Group.2, x, col = Group.1)) +
    ggtitle(paste("New Cases per Day in", variable_name1, "and", variable_name2, "County", sep = " ")) +
    labs(x = "Date", y ="# New Cases") +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme_few() +
    scale_fill_few()
}



