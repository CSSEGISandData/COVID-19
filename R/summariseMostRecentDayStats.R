#
#
# aggregate covid data by Country_Region for most recent date

library(tidyverse)

data %>% 
  filter(date == max(date)) %>%
  group_by(Country_Region) %>% 
  summarise(Confirmed = sum(Confirmed),
            Deaths = sum(Deaths)) -> summedData 