# demoTable_BC <- function(df_r, varname_vec, varlabel_vec, caption = "Demographic characteristics",html_out){
#   #browser()
#   table_data<-list()
#   
#   #index = which(names(df_r) %in% varname_vec)
#   for (i in 1:length(varname_vec))
#   {
#     index = which(names(df_r) %in% varname_vec[i])
#     if(is.factor(df_r[,index]) | is.character(df_r[,index])){
#       # table_data[[i]]<- getT1Stat_1(df_r, varname = names(df_r)[index],varlabel_vec[[i]],1,html_out)
#       # names(table_data)[[i]] <- varlabel_vec[[i]]
#       fst <- getT1Stat_1(df_r, varname = names(df_r)[index],varlabel_vec[[i]],1,html_out)
#       
#       modl <- coxph(as.formula(paste('Surv(time_to_event_years, censoring) ~ ',names(df_r)[index])), data=df_r)
#       
#       tmodl <- broom::tidy(modl, exponentiate = TRUE, conf.int=TRUE) %>% mutate(ci=paste0(sprintf("%1.2f",estimate),' (',sprintf("%1.2f",conf.low),'-',sprintf("%1.2f",conf.high),')'), term=gsub(names(df_r)[index],'',term)) %>% select(term, ci)
#       
#       gmodl <- broom::glance(modl, exponentiate = TRUE, conf.int=TRUE) %>% pull(p.value.log) %>% sprintf("%1.3f",.)
#       
#       snd <- bind_rows(tibble(term = setdiff(unique(df_r[,names(df_r)[index]]), gsub(names(df_r)[index],'',tmodl$term)), ci='1', P=gmodl), tmodl) %>% as.matrix()
#       
#       lst<-attr(fst,'dimnames')
#       
#       lst[[2]]<-c('Hazard ratio (95%CI)','P','value')
#       
#       res <- matrix(c(snd[,setdiff(colnames(snd), 'term')], fst), ncol = 3, nrow = nrow(fst))
#       
#       attr(res,'dimnames') <-lst
#       
#       table_data[[i]] <- res
#       
#       names(table_data)[[i]] <- varlabel_vec[[i]]
#     }
#     if(is.numeric(df_r[,index])){
#       #table_data[[i]]<- getT1Stat_1(df_r, varname = names(df_r)[index], varlabel_vec[[i]],1,html_out)
#       #names(table_data)[[i]] <- varlabel_vec[[i]]
#       
#       fst <- getT1Stat_1(df_r, varname = names(df_r)[index], varlabel_vec[[i]],1,html_out)
#       
#       modl <- coxph(as.formula(paste('Surv(time_to_event_years, censoring) ~ ',names(df_r)[index])), data=df_r) 
#       
#       
#       snd <- bind_cols(
#                        modl %>% broom::tidy( exponentiate = TRUE,conf.int=TRUE) %>% mutate(ci=paste0(sprintf("%1.2f",estimate),' (',sprintf("%1.2f",conf.low),'-',sprintf("%1.2f",conf.high),')')) %>% select(ci), 
#                        P=modl %>% broom::glance() %>% pull(p.value.log) %>% sprintf("%1.3f",.)) %>%
#             as.matrix()
#       
#       lst<-attr(fst,'dimnames')
#       
#       lst[[2]]<-c('Hazard ratio (95%CI)','P',lst[[2]])
#       
#       res <- matrix(c(snd,fst), ncol = 3, nrow = 1)
#       
#       attr(res,'dimnames') <-lst
#       
#       table_data[[i]] <- res
#       
#       names(table_data)[[i]] <- varlabel_vec[[i]]
#     }
#     
#   }
#   #names(table_data)<- varlabel_vec
#   rgroup <- c()
#   n.rgroup <- c()
#   output_data <- NULL
#   for (varlabel in names(table_data)){
#     output_data <- rbind(output_data, table_data[[varlabel]])
#     rgroup <- c(rgroup, varlabel)
#     n.rgroup <- c(n.rgroup, nrow(table_data[[varlabel]]))
#   }
#   
#   
#   if(html_out){ 
#     #Replace >= and <= with HTML tags
#     row.names(output_data)<-gsub('<=|\u2264','&le;',row.names(output_data))
#     row.names(output_data)<-gsub('>=|\u2265','&ge;',row.names(output_data))
#     htmlTable(x = output_data,
#               align="lcc",
#               rgroup= rgroup ,
#               n.rgroup= n.rgroup,
#               rgroupCSSseparator="  ",
#               rowlabel="Variables",
#               caption=caption,
#               ctable=FALSE,escape.html = FALSE)
#   }
#   else{  
#     colnames(output_data) <- c("N (Percenatge)")
#     zt=ztable(x = output_data,align="lc",caption=caption,size=5, tablewidth = 0.4)
#     zt=addrgroup(zt,rgroup= rgroup,n.rgroup= n.rgroup)
#     zt
#   }
# }


#This function turns s3$surv=0.9471551, s3$lower=0.9299309, and s3$upper=0.9646984 where s3 is of class "summary.survfit" to "95% (95%CI; 93%-96%)"   
percent_cln <- function(x,y,z) sprintf("%.0f%% (95%%CI; %.0f%%-%.0f%%)", x*100, y*100, z*100)

#This function creats a 5, 3 years survival table from a "survfit" object
survyears_table = function(fit, yrs){
  #browser()
  smr <- summary(fit, time=yrs)
  df_out <- data.frame('Strata'=smr$strata, '5 years survival'=percent_cln(smr$surv, smr$lower, smr$upper), check.names = FALSE)
  return(df_out)
}
