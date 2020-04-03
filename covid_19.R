# refs:
# https://datasharkie.com/covid-19-daily-statistics-updates/?fbclid=IwAR0EwXLIH_AiwEmU7KxOMyfgE83nmdLH34Dj5QCtOdFA78pTHRsdf2KRguQ
# https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
# https://github.com/CSSEGISandData/COVID-19


# library bank ----

library(readxl)
library(httr)
library(tidyverse)
library(data.table)
library(scales)
library(directlabels)

# ecd data ----

# as.Date("2020-01-22"):Sys.Date()
# 
# covid_dates <- seq(as.Date("2020-03-16"), Sys.Date(), by="days")
# covid_dates
# 
# codiv_edc <- map(covid_dates,
#                  function(x) {
#                    
#                    # create the URL where the dataset is stored with automatic updates every day
#                    url <- paste("https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-", x, ".xlsx", sep = "")
#                    
#                    # download the dataset from the website to a local temporary file
#                    
#                    GET(url, authenticate(":", ":", type="ntlm"), write_disk(tf <- tempfile(fileext = ".xlsx")))
#                    
#                    #read the Dataset sheet into “R”
#                    
#                    data <- read_excel(tf)
#                    
#                  })


# john hopskins data ----

# list all the files in the path
covid_files <- list.files(path = "csse_covid_19_data/csse_covid_19_daily_reports", pattern = ".csv", full.names = T)
basename(covid_files)

covid_data <- map(covid_files,
                  function(x) {
                    fread(x, na = "") %>% mutate(Date = as.Date(gsub(".csv", "", basename(x)), format = "%m-%d-%Y"))
                    }) %>% bind_rows() %>% rename_all(.funs = ~gsub("/| ", "_", .)) %>% mutate(Country_Region = gsub("Mainland China", "China", Country_Region))


# world analysis ----

covid_world <- covid_data %>%
  group_by(Date) %>%
  summarize(Confirmed = sum(Confirmed),
            Deaths = sum(Deaths),
            Recovered = sum(Recovered)) %>% 
  gather(key = "Outcome", value = "Total", -Date) %>% 
  filter(!is.na(Total))

# line graph
covid_world %>% 
  ggplot(aes(x = Date, y = Total, color = Outcome)) +
    geom_line() +
    scale_y_continuous(labels = comma) +
    scale_colour_discrete(guide = 'none') +
    scale_x_date(breaks = pretty_breaks(10), expand = c(0, 5)) +
    geom_dl(aes(label = Outcome), method = list(dl.trans(x = x + 0.2), "last.points", cex = 0.8)) +
    coord_cartesian(clip = 'off') +
    theme_bw() +
    ggtitle("Covid19 Cases in The World")

# stacked area graph
covid_world %>% 
  ggplot(aes(x = Date, y = Total, fill = Outcome)) +
    geom_area(position="fill", stat="identity", alpha=0.6) +
    scale_x_date(breaks = pretty_breaks(10)) +
    theme_bw()

# country analysis ----

# group by country and dates
cntry_tots <- covid_data %>%
  group_by(Country_Region, Date) %>%
  summarize(Confirmed = sum(Confirmed), Deaths = sum(Deaths), Recovered = sum(Recovered))

# top 10% of contries
top_cntry <- cntry_tots %>% 
  group_by(Country_Region) %>% 
  summarize(Confirmed = sum(Confirmed, na.rm = T),
            Deaths = sum(Deaths, na.rm = T),
            Recovered = sum(Recovered, na.rm = T)) %>% 
  # gather(key = "Outcome", value = "Total", -Country_Region) %>% 
  filter(!is.na(Confirmed)) %>% 
  top_frac(n = 0.1, wt = Confirmed)

# top confirmed cases
top_cntry %>% 
  ggplot(aes(x = reorder(Country_Region, Confirmed), y = Confirmed)) +
    geom_bar(position = "dodge", stat = "identity") +
    scale_y_continuous(labels = comma) +
    coord_flip() +
    theme_bw() +
    theme(axis.title.y = element_blank()) +
    ggtitle("Countries with Top 10% of Confirmed Cases")

# top confirmed cases deaths
top_cntry %>% 
  ggplot(aes(x = reorder(Country_Region, Confirmed), y = Deaths)) +
    geom_bar(position = "dodge", stat = "identity") +
    scale_y_continuous(labels = comma) +
    coord_flip() +
    theme_bw() +
    theme(axis.title.y = element_blank()) +
    ggtitle("Deaths in Countries with Top 10% of Confirmed Cases")

# top confirmed cases
top_cntry %>% 
  ggplot(aes(x = reorder(Country_Region, Confirmed), y = Recovered)) +
  geom_bar(position = "dodge", stat = "identity") +
  scale_y_continuous(labels = comma) +
  coord_flip() +
  theme_bw() +
  theme(axis.title.y = element_blank()) +
  ggtitle("Recoveries in Countries with Top 10% of Confirmed Cases")

top_cntry %>% 
  gather(key = "Outcome", value = "Total", -Country_Region) %>% 
  filter(!is.na(Total)) %>% 
  ggplot(aes(x = Country_Region, y = Total, fill = Outcome)) +
  geom_bar(position="fill", stat="identity", alpha=0.6) +
  coord_flip()

cntry_tots %>%
  filter(Country_Region %in% (cntry_tots %>% 
                                group_by(Country_Region) %>% 
                                summarize(Confirmed = sum(Confirmed, na.rm = T)) %>% 
                                top_n(n = 7, wt = Confirmed) %>% 
                                unlist())) %>% 
  gather(key = "Outcome", value = "Total", -c(Date, Country_Region)) %>% 
  filter(!is.na(Total)) %>% 
  ggplot(aes(x = Date, y = Total, color = Country_Region)) +
  geom_line() +
  # scale_y_continuous(labels = comma) +
  # scale_colour_discrete(guide = 'none') +
  # scale_x_date(breaks = pretty_breaks(10), expand = c(0, 5)) +
  # geom_dl(aes(label = Country_Region), method = list(dl.trans(x = x + 0.2), "last.points", cex = 0.8)) +
  # coord_cartesian(clip = 'off') +
  # theme_bw() +
  ggtitle("Top 10 Countries over time") +
  facet_grid(Outcome ~ .)

    