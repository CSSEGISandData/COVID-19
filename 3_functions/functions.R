fun1 <- function(df)
{ 
  df = read_csv(file.path(path_data,df))
  df = df %>% rename(country = contains("country"), date_old = contains("Update")) 
  frmt_vec = unique(names(guess_formats(df$date_old, c("mdy_HM", "dmy_HMS", "ymd_HMS"), print_matches = FALSE)))
  df = list(df,frmt_vec )
}

#######################

fun2 <- function(df)
{
  if(any(df[[2]] %in% c("OmdyHM", "mdyHM")))
  {df1 = df[[1]] %>% mutate(date_new = floor_date(mdy_hm(date_old), "day")) %>% group_by_at(.vars = c("country","date_new")) %>%              summarise(Confirmed_cum = sum(Confirmed, na.rm = TRUE), Death_cum = sum(Deaths, na.rm = TRUE), Recovered_cum = sum(Recovered, na.rm = TRUE)) %>% ungroup()
  }
  else{
    if(any(df[[2]] %in% c("yOmdHMS", "ymdHMS"))){df1 = df[[1]] %>% mutate(date_new = floor_date(ymd_hms(date_old), "day")) %>% group_by_at(.vars = c("country","date_new")) %>% summarise(Confirmed_cum = sum(Confirmed, na.rm = TRUE), Death_cum = sum(Deaths, na.rm = TRUE), Recovered_cum = sum(Recovered, na.rm = TRUE)) %>% ungroup()} else{"ERROR"}
    
  }
  
}


fun2.temp <- function(df)
{
  if(any(df[[2]] %in% c("OmdyHM", "mdyHM")))
  {df1 = df[[1]] %>% mutate(date_new = date_old) %>% group_by_at(.vars = c("country","date_new")) %>% summarise(Confirmed_cum = sum(Confirmed, na.rm = TRUE), Death_cum = sum(Deaths, na.rm = TRUE), Recovered_cum = sum(Recovered, na.rm = TRUE)) %>% mutate(date_new = as.character(date_new)) %>% ungroup()
  }
  else{
    if(any(df[[2]] %in% c("yOmdHMS", "ymdHMS"))){df1 = df[[1]] %>% mutate(date_new = date_old) %>% group_by_at(.vars = c("country","date_new")) %>% summarise(Confirmed_cum = sum(Confirmed, na.rm = TRUE), Death_cum = sum(Deaths, na.rm = TRUE), Recovered_cum = sum(Recovered, na.rm = TRUE)) %>% mutate(date_new = as.character(date_new)) %>% ungroup()} else{"ERROR"}
    
  }

}