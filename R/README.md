# README for R Scripts 

The README file explains how to use the R scripts in the repository to analyze the Johns Hopkins
COVID-19 data. 

The scripts are organized into a few categories, including:

1. Scripts to read the CSV files provided by JHU and save them to RDS
2. Scripts to read the RDS files, combine with bitcoin data to analyze the relationship between COVID stats and bitcoin prices
3. Scripts to generate graphics of cases and deaths for selected geographic regions


The primary "starting" script is `readDailyReportsData.R`, which reads the files in the `./csse_covid_19_data/csse_covid_19_daily_reports/` subdirectory of the github project. 

Once data has been saved to `.\rdsData\covidData.rds`, other scripts can be used to analyze the data without having to read hundreds of data files and clean them. 

## Data Cleaning

The data read scripts account for the fact that over time Johns Hopkins University added and changed  columns representing the data they collected. Therefore, the data loader adds missing columns where necessary so that once all the data is read it can be combined into a single data frame. 

An example of some of this data cleaning code looks like this: 

    # processing specific to first batch of files
    if(fileDate < mdy("02/01/2020")) {
       y$Province_State <- NA
       y$Lat <- NA
       y$Long_ <- NA
       y$Active <- NA
       y$Admin2 <- NA
       y$FIPS <- NA 
       y$Combined_Key <- NA 
       y$Case_Fatality_Ratio <- NA
       y$Incident_Rate <- NA 
    }

COVID-19 field descriptions are accessible in the [../csse_covid_19_data/README.md](../csse_covid_19_data/README.md) file. 

# Financial Data

Market data accessed through the `quantmod` R package and its interface to Yahoo! Finance appeared to provide significantly fewer valid observations for symbols other than Bitcoin. To assess the validity of the data from Yahoo! Finance, we 
retrieved the following index data from the [Marketwatch](https://www.marketwatch.com/investing/index/djia/download-data?mod=mw_quote_tab) website as yearly downloads from their manual interface. 

* Bitcoin in USD
* CBOE Volatility Index (VIX)
* Crude Oil WTI Futures (NYM $/bbl) Front Month 
* DJIA
* FTSE 100 
* Gold Continuous Contract  
* Hang Seng
* Nikkei 225
* S&P 500 

A script to read the downloaded Marketwatch data, clean it, and save as an RDS file is located [here.](../R/readMarketwatchData.R)

### (c) 2000 - 2023 Leonard Greski
### copying permitted with attribution 