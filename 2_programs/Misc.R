res_gr<-model.matrix(~grade_mod_fac, data=df)[,-1]
res_sg<-model.matrix(~Stage_mod_fac, data=df)[,-1]
res_tz<-model.matrix(~Tsize_g, data=df)[,-1]
res_ln<-model.matrix(~LN_g, data=df)[,-1]
res_ps<-model.matrix(~primary_site_mod, data=df)[,-1]

df_test <- bind_cols(df, data.frame(res_gr), data.frame(res_sg), data.frame(res_tz),  data.frame(res_ln), data.frame(res_ps))


cr <- smcure(Surv(time_to_event_years, censoring)~
               
               grade_mod_facGrade.II+grade_mod_facGrade.III+LN_gN1+LN_gNAny+MS_num, 
             
             cureform=~grade_mod_facGrade.II+grade_mod_facGrade.III+LN_gN1+LN_gNAny+MS_num, 
             data=df_test, model="ph", nboot=500, Var = TRUE)


+Tsize_gT3+Tsize_gTAny

+primary_site_modC50246+primary_site_modC5035+primary_site_modC508+primary_site_modC509

+Stage_mod_fac1+Stage_mod_fac2+Stage_mod_fac3+Stage_mod_fac4

+laterality_mod_num


#For grade_mod doesn't converage