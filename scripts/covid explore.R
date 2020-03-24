# covid data

dth <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv")
str(dth)
names(dth)

cases <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")

rec <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv")


  # new series

cases <- read_csv("csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")




# US cases -------------------------------------------------------------------

str(cases)
names(cases)

frq(cases$`Province/State`)
frq(cases$`Country/Region`)

usC <- cases %>%
  filter(`Country/Region`=="US")

usC

byDay <- usC %>%
  pivot_longer(cols=5:65,
               names_to="day",
               values_to="cases") %>%
  select(-Lat, -Long) %>%
  group_by(day) %>%
  summarize(cases=sum(cases)) %>%
  mutate(day = as.POSIXct(strptime(day, format="%m/%d/%y")),
         log_cases = log(cases)) %>%
  arrange(day) %>%
  mutate(prcnt_grwth = (cases - lag(cases))/lag(cases)*100) %>%
  as.data.frame

head(byDay)
tail(byDay)
str(byDay)
frq(byDay$day)

ggplot(byDay, aes(day, cases)) +
  annotate("text", x=as.POSIXct("2020-02-08"), y=32200, label="33,272 cases") + 
  geom_point(size=1.5, color="darkblue", alpha=.8) + 
  stat_smooth(se=F, span=.2, color="blue", alpha=.2) + 
  scale_x_datetime(breaks=date_breaks("12 days"),
                   labels=date_format("%b-%d")) +
  scale_y_continuous(labels=comma) + 
  labs(x="",
       y="",
       title="U.S. COVID-19 cases\n22 Jan through 22 March, 2020") + 
  geom_hline(yintercept=33272, color="pink", alpha=.8, size=1) 

ggsave("viz/US cases 22 March 2020 no border.png",
       device="png",
       type="cairo",
       height=4,
       width=7)


ggplot(byDay, aes(day, prcnt_grwth/100)) + 
  #annotate("text", x=as.POSIXct("2020-03-08"), y=2, label="40 percent growth is\na doubling time of five days") + 
  geom_point(size=1.5, color="darkblue", alpha=.8) + 
  stat_smooth(se=F, color="blue", alpha=.2) + 
  scale_x_datetime(breaks=date_breaks("12 days"),
                   labels=date_format("%b-%d")) +
  scale_y_continuous(labels=percent) + 
  labs(x="",
       y="Daily percent growth",
       title="U.S. COVID-19 cases\n22 Jan through 22 March, 2020",
       caption="40 percent daily growth rate\nis a doubling time of two days") + 
  geom_hline(yintercept=.40, color="maroon", alpha=.6, size=1, linetype="dashed") 

ggsave("viz/growth rate in US cases 22 March 2020 no border.png",
       device="png",
       type="cairo",
       height=4,
       width=7)



# cases by country --------------------------------------------------------

head(cases[,1:5])

?ncol
ncol(byDay)

byDay <- cases %>%
  pivot_longer(cols=5:ncol(cases),
               names_to="day",
               values_to="cases") %>%
  select(-Lat, -Long) %>%
  group_by(country=`Country/Region`, day) %>%
  summarize(cases=sum(cases)) %>%
  mutate(day = as.POSIXct(strptime(day, format="%m/%d/%y"))) %>%
  filter(country == "China" | country == "France" | country == "Germany" | country == "Iran" | 
           country == "Italy" | country == "Spain" | country == "US") %>%
  arrange(desc(cases)) %>%
  as.data.frame 

head(byDay)
tail(byDay)
str(byDay)

describe(byDay$cases)
frq(byDay$country)

byDay <- byDay %>%
  mutate(label = ifelse(day==max(day), as.character(country), NA_character_),
         country2 = fct_reorder(country, cases, max))

frq(byDay$label)

?rank
rank(byDay$country)
frq(byDay$country2)

str(byDay)
head(byDay)
tail(byDay)

?distinct
lab <- byDay %>%
  distinct(label) %>%
  na.omit %>%
  unlist

lab

case_ends <- byDay %>%
  group_by(country) %>%
  top_n(1,cases) %>%
  pull(cases)

case_ends

tail(byDay)

ggplot(byDay, aes(day, cases, color=fct_rev(country2))) + 
  stat_smooth(size=1, alpha=.2, se=F, span=.1) + 
  scale_color_viridis_d() + 
  scale_x_datetime(limits=c(as.POSIXct("2020-02-25"), as.POSIXct("2020-03-23")),
                   breaks=date_breaks("12 days"),
                   labels=date_format("%b-%d")) +
  scale_y_continuous(limits=c(0,82000),
                     breaks=seq(0,80000,10000),
                     labels=comma) +
  labs(x="",
       y="",
       title="COVID-19 cases for hardest hit countries\n25 Feb through 23 March, 2020") +
  theme(legend.title=element_blank()) 

ggsave("viz/top country cases 23 March 2020.png",
       device="png",
       type="cairo",
       height=6,
       width=6)

  # with labels

ggplot(byDay, aes(day, cases, color=fct_rev(country2))) + 
  stat_smooth(size=1, alpha=.2, se=F, span=.1) + 
  scale_color_viridis_d() + 
  scale_x_datetime(limits=c(as.POSIXct("2020-02-25"), as.POSIXct("2020-03-23")),
                   breaks=date_breaks("6 days"),
                   labels=date_format("%b-%d")) +
  scale_y_continuous(limits=c(0,82000),
                     breaks=seq(0,80000,10000),
                     labels=comma,
                     sec.axis=sec_axis(~., 
                                       breaks=case_ends,
                                       labels=comma)) +
  labs(x="",
       y="",
       title="COVID-19 cases for hardest hit countries\n25 Feb through 23 March, 2020") +
  theme(legend.title=element_blank()) + 
  geom_label_repel(aes(label=label),
                   #nudge_x=10,
                   direction="both") + 
  spec +
  theme(legend.position="none",
        panel.border = element_blank(),
        axis.ticks=element_blank()) 

ggsave("viz/top country cases 23 March 2020 label.png",
       device="png",
       type="cairo",
       height=6,
       width=6)


  # with secondary y axis

ggplot(byDay, aes(day, cases, color=fct_rev(country2))) + 
  stat_smooth(size=1, alpha=.2, se=F, span=.1) + 
  scale_color_viridis_d() + 
  scale_x_datetime(limits=c(as.POSIXct("2020-02-25"), as.POSIXct("2020-03-23")),
                   breaks=date_breaks("6 days"),
                   labels=date_format("%b-%d")) +
  scale_y_continuous(limits=c(0,82000),
                     breaks=seq(0,80000,10000),
                     labels=comma,
                     sec.axis=sec_axis(~., 
                                       breaks=case_ends,
                                       labels=lab)) +
  labs(x="",
       y="",
       title="COVID-19 cases for hardest hit countries\n25 Feb through 23 March, 2020") +
  theme(legend.title=element_blank()) + 
  spec +
  theme(legend.position="none",
        panel.border = element_blank(),
        axis.ticks=element_blank()) 

ggsave("viz/top country cases 23 March 2020 sec.y.png",
       device="png",
       type="cairo",
       height=7,
       width=7)



  

# US locations ------------------------------------------------------------


