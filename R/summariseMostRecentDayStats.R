#
#
# aggregate covid data by Country_Region for most recent date

library(tidyverse)

data %>% 
  filter(date == max(date)) %>%
  group_by(Country_Region) %>% 
  summarise(Confirmed = sum(Confirmed),
            Deaths = sum(Deaths)) %>%
  mutate(pct_cases = 100 * Confirmed / sum(Confirmed),
         pct_deaths = 100 * Deaths / sum(Deaths),
         Death_Rate = 100 * Deaths / Confirmed ) -> summedData 

