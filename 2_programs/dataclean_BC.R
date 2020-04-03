###############
#Libraries#####
###############
library(tidyverse)
library(readxl)
library(lubridate)
###############
#PATH##########
###############
#path = 'C:/Abubaker/2_Research/project28_Breast cancer_Yusra/'

###################
#Read Data Sets####
###################
sheet1 <- read_excel(paste0('1_data/2_new/df_BC_v2.0.xls'), sheet = "Sheet1")
sheet2 <- read_excel(paste0('1_data/2_new/df_BC_v2.0.xls'), sheet = "with treatment")
sheet3 <- read_excel(paste0('1_data/2_new/df_BC_v2.0.xls'), sheet = "Updated last contact")



#######################
#Process Data Sets#####
#######################
#1. Get patients who have one incidence of Cancer
sh1_NonDup <- sheet1 %>% group_by(MRN) %>% filter(n()==1) %>% arrange(MRN) 

sh3_NonDup <- sheet3 %>% group_by(MRN) %>% distinct() %>% filter(n()==1) %>% arrange(MRN) %>% select(MRN, updated_DOLC, updated_vital_status)

#2. Merge sheet1 with sheet3 
sh13_NonDup_pry <- sh1_NonDup %>% left_join(sh3_NonDup, by='MRN') %>% select(-matches('state_.*|FR{1,2}')) %>% select(MRN, sort(names(.))) %>% ungroup()

#######################
#Clean variables####### 
#######################
#####################################
#1. Date of 1st Contact (DOF_contact)
#####################################

#sh13_NonDup_pry %>% mutate(DOF_contact_mod = dmy(DOF_contact)) %>% filter(is.na(DOF_contact_mod)) %>% mutate(DOF_contact_mod1 = dmy(sub('(99)(.*)','15\\2',DOF_contact)))%>% select(MRN,sort(names(.))) %>%  View

sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(DOF_contact_final = dmy(sub('(99)(.*)','15\\2',DOF_contact)))

#################################################
#2. Date First Course RX - COC (DOF_courseRX_COC)
#################################################

#sh13_NonDup_pry %>% mutate(DOF_courseRX_COC_mod = ymd(DOF_courseRX_COC)) %>% filter(is.na(DOF_courseRX_COC_mod) & DOF_courseRX_COC!=0 & !is.na(DOF_courseRX_COC)) %>% select(MRN,DOF_courseRX_COC,DOF_courseRX_COC_mod) %>%mutate(flag=ymd(sub('(.*)(99)','\\101',DOF_courseRX_COC))) %>% filter(!is.na(flag))

sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(DOF_courseRX_COC_final = ymd(sub('(.*)(99)','\\115',DOF_courseRX_COC)))

####################################
#3. Date of Initial Diagnosis (DOID)
####################################

#sh13_NonDup_pry %>% mutate(DOID_mod = dmy(DOID)) %>% filter(is.na(DOID_mod)) %>% select(MRN,DOID, DOID_mod) %>% mutate(flag=dmy(sub('(99)(.*)','01\\2',DOID)))

sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(DOID_final = dmy(sub('(99)(.*)','15\\2',DOID)))

#CSG
sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(CSG_final=ifelse(is.na(CSG) | grepl('99|88',CSG), NA, CSG))


#####################################################
#4. Diagnostic Confirmation (diagnostic_confirmation)
#####################################################

#sh13_NonDup_pry %>% ungroup() %>% count(diagnostic_confirmation)
sh13_NonDup_pry  <- sh13_NonDup_pry %>% mutate(diagnostic_confirmation_final = ifelse(grepl('9',diagnostic_confirmation), NA, diagnostic_confirmation))

#################################
#5. Grade/Differentiation (grade)
#################################

#sh13_NonDup_pry %>% ungroup() %>% count(grade)
sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(grade_final = ifelse(grepl('9',grade), NA, grade))

###################################
#6. Histo/Behavior ICD-O-3 (HB_ICD) 
###################################
# No NAs

sh13_NonDup_pry <- sh13_NonDup_pry %>%  mutate(HB_ICD_final = HB_ICD)

###########################
#7. Laterality (laterality)
###########################
#Change 9 Paired site, but no information concerning laterality To NA
#sh13_NonDup_pry %>% ungroup() %>% count(laterality) %>% View
sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(laterality_final = ifelse(grepl('9',laterality), NA, laterality))

###############################
#8. Primary Site (primary_site) 
###############################
#No NAs

#sh13_NonDup_pry %>% ungroup() %>% count(primary_site) %>% View

sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(primary_site_final = primary_site)

################################
#9. Pathologic Stage Group (PSG) 
################################
#256 NAs
#sh13_NonDup_pry %>% count(PSG) %>% View
sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(PSG_final=ifelse(is.na(PSG) | grepl('99|88',PSG), NA, PSG))

#########################################################
#10. Updated last contact.Date of Last Contact (Updated DOLC) 
#########################################################
#Get values are missed in updated DOLC from DOLC
#sh13_NonDup_pry %>% mutate(updated_DOLC_mod = dmy(updated_DOLC)) %>% filter(is.na(updated_DOLC)) %>% select(MRN, DOLC, updated_DOLC, updated_DOLC_mod, vital_status, updated_vital_status)
sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(updated_DOLC_final = if_else(!is.na(updated_DOLC),dmy(updated_DOLC), dmy(DOLC)))

#############################################################
#11. Updated last contact.Vital Status (updated_vital_status)
#############################################################
#Get values are missed in updated_vital_status from vital_status
sh13_NonDup_pry <- sh13_NonDup_pry %>% mutate(updated_vital_status_final = if_else(!is.na(updated_vital_status),updated_vital_status,vital_status))

#################################################
#Primary Final Data set
#################################################
sh13_NonDup_scy <- sh13_NonDup_pry %>% select(MRN, sex, age, nationality,DOLC, updated_DOLC, updated_DOLC_final, vital_status, updated_vital_status, updated_vital_status_final, ends_with('final'))


#############################
#Get what available in Sheet2
#############################
nms <- c("CSG", "diagnostic_confirmation", "DOF_contact", "DOF_courseRX_COC", 
         "DOID", "grade", "HB_ICD", "primary_site", "PSG")

pids <- c("10101691", "10136216", "10180835", "10075575", "AFRA", "10073668", 
          "10176269", "10053028", "10060777", "10135551", "10077298", "10101111", 
          "10134740", "10134277", "10059957", "10064978")

##########################################
#Get missing values in Sheet1 from Sheet2 
##########################################
# 2 for CSG, 1 for diagnostic_confirmation, 1 for grade, 2 for PSG
sh13_NonDup_scy <- sh13_NonDup_scy %>% 
  left_join( sheet2 %>% select(MRN, nms) %>% filter(MRN %in% pids) %>% mutate(PSG=ifelse(grepl('99',PSG),NA,PSG)), 
             by='MRN') %>% 
  mutate(CSG_final=ifelse(is.na(CSG_final) & !is.na(CSG),CSG,CSG_final),
         diagnostic_confirmation_final=ifelse(is.na(diagnostic_confirmation_final) & !is.na(diagnostic_confirmation), diagnostic_confirmation, diagnostic_confirmation_final),
         grade_final=ifelse(is.na(grade_final) & !is.na(grade), grade, grade_final),
         PSG_final=ifelse(is.na(PSG_final) & !is.na(PSG), PSG, PSG_final)) %>% 
  select(-nms)



#################################################
#Import FCourseRx_summary from Sheet2
#################################################

sh13_NonDup_scy <- sh13_NonDup_scy %>% 
  left_join( sheet2 %>% select(MRN, FCourseRx_summary_final=FCourseRx_summary), 
             by="MRN")


#############################################################
#Get 19 Date First Course RX - COC from Maria's updated sheet
############################################################
df <- read_excel(paste0('1_data/2_new/Yusra.xlsx'), sheet = "rx") %>% 
  select(MRN=MRN__1, DOF=`Date First Course RX - COC`)

df <- df %>% mutate(flag=if_else(is.na(DOF) | grepl('/',DOF), 1, 2)) %>% split(.$flag) %>% map(., function(x) {
  if(x$flag[1]==1){
    x %>% mutate(DOF_mod = dmy(gsub('(99)(.*)','15\\2',x$DOF)))
  } else{
    x%>%mutate(DOF_mod = as.Date(as.numeric(DOF), origin="1899-12-30"))
  }
}) %>% bind_rows() %>% select(-flag) %>% filter(!is.na(DOF_mod))


sh13_NonDup_scy <- sh13_NonDup_scy %>% left_join(df,by='MRN') %>% mutate(DOF_courseRX_COC_final= if_else(!is.na(DOF_mod) & is.na(DOF_courseRX_COC_final),DOF_mod, DOF_courseRX_COC_final)) %>% select(-DOF,-DOF_mod)

#################################################
#DF FINAL#######################################
#################################################
df_final <- sh13_NonDup_scy %>% rename_at(vars(matches('^[^u].*final')), list(~sub('_final','',.))) %>% filter(sex=="2  Female") 


#Rename DOF_contact to DOF_contact_tawam
df_final <- df_final %>% rename(DOF_contact_tawam=DOF_contact)

#Create Survival time "time to event" (Days, months, years) and Censoring "1 Dead, 0 non NA, NA", delay in treatment (Days and Category)
df_final <- df_final %>% mutate(time_to_event_days=updated_DOLC_final - DOID,
                                time_to_event_months=time_to_event_days/30,
                                time_to_event_years=time_to_event_days/365.25,
                                censoring=case_when(
                                  grepl('Dead',updated_vital_status_final) ~ 1,
                                  !is.na(updated_vital_status_final) ~ 0,
                                  TRUE ~ NA_real_),
                                time_to_event_treat_days=updated_DOLC_final - DOF_courseRX_COC,
                                time_to_event_treat_months=time_to_event_treat_days/30,
                                time_to_event_treat_years=time_to_event_treat_days/365.25,
                                delay_treatment_days = DOF_courseRX_COC - DOID,
                                delay_treatment_days_cat = case_when(delay_treatment_days<=30 ~ '<= 30 days',
                                                                     between(delay_treatment_days,31,150) ~ '30-150 days',
                                                                     delay_treatment_days>=151 ~ '>=151 days',
                                                                     TRUE ~ NA_character_),
                                age = as.numeric(age),
                                age_cat = case_when(age <= 35 ~ '<=35 years',
                                                    between(age,36,49) ~ '36-49 years',
                                                    between(age,50,64) ~ '50-64 years',
                                                    age >= 65 ~ '>=65 years',
                                                    TRUE ~ NA_character_)
                                )

#Create re-categorizing primary_site variable
df_final <- df_final %>% mutate(primary_site_mod = case_when(str_detect(primary_site,'50[01]') ~ 'C5001',
                                                             str_detect(primary_site,'50[246]') ~ 'C50246',
                                                             str_detect(primary_site,'50[35]') ~ 'C5035',
                                                             !is.na(primary_site) ~ str_extract(primary_site,'C\\d+'),
                                                             TRUE ~ NA_character_))

#Create re-categorizing HB_ICD variable
HB_ICD.df <- read_excel(paste0('1_data/2_new/primary_site_HB_ICD_FCRx_summary_recatg.xlsx'), sheet = "HB_ICD_Cat") %>% separate_rows(Var1, sep = '\\s\\|\\s') %>% select(HB_id = Var1, HB_ICD_mod = Category_HB)

df_final <- df_final %>% mutate(HB_ICD = gsub('(\\d+)\\s{2}(.*)','\\1 \\2',HB_ICD),
                                HB_id = HB_ICD) %>% left_join(HB_ICD.df , by="HB_id") 
#%>% select(MRN,HB_ICD,HB_id,Var1) %>% filter(is.na(Var1)) %>% mutate(id=str_extract(HB_id,'\\d+')) %>% arrange(id)


#######################################################################################################
#WARNING: FILTERING START  FROM THIS POINT ############################################################
#######################################################################################################

#Filter Non NAs in time_to_event_days, censoring, and delay_treatment
df_final <- df_final %>% filter(!is.na(time_to_event_days) & !is.na(censoring) & !is.na(delay_treatment_days))

#Create Stage, Tumor size, Lymphnode involvement, and Metastasis
#1. Select one case for those with mutiple cases
#E.g gsub('(.*?);.*','\\1','aa; bb; cc'), gsub('(.*?);.*','\\1','aa')
df_final$PSG_mod <- gsub('(.*?);.*','\\1',df_final$PSG)

#2. Modify PSG_mod 2 Stage II for MRN 70008616 to 2StageII
df_final$PSG_mod <- gsub('2  Stage II','2StageII',df_final$PSG_mod)

#3. Handle Any T and Any N 
#E.g gsub('(Any)\\s([TN])','\\2\\1','4 Any T N2 M1'), gsub('(Any)\\s([TN])','\\2\\1','4 Any T Any N M1'), gsub('(Any)\\s([TN])','\\2\\1','3C T1 N2 M1')
df_final$PSG_mod_upd <- gsub('(Any)\\s([TN])','\\2\\1',df_final$PSG_mod)

#4. Seperate PSG into four columns namely Stage, Tsize, LN, MS
df_final <- separate(df_final, col = PSG_mod_upd, into = c('Stage', 'Tsize', 'LN', 'MS'), sep = '\\s+',remove = FALSE)

#5. Collapse and clean Stgae, Tsize, and LN

df_final <- df_final %>% mutate(Stage_mod = case_when(str_detect(Stage,'0') ~ '0',
                                                      str_detect(Stage,'1') ~ '1',
                                                      str_detect(Stage,'2') ~ '2',
                                                      str_detect(Stage,'3') ~ '3',
                                                      str_detect(Stage,'4') ~ '4',
                                                      TRUE ~ NA_character_),
                                LN_mod = case_when(str_detect(LN,'N0') ~ 'N0',
                                                   str_detect(LN,'N1') ~ 'N1',
                                                   str_detect(LN,'N2') ~ 'N2',
                                                   str_detect(LN,'N3') ~ 'N3',
                                                   str_detect(LN,'NAny') ~ 'Not available',
                                                   TRUE ~ NA_character_),
                                TSize_mod = case_when(str_detect(Tsize,'T0') ~ 'T0',
                                                      str_detect(Tsize,'T1') ~ 'T1',
                                                      str_detect(Tsize,'T2') ~ 'T2',
                                                      str_detect(Tsize,'T3') ~ 'T3',
                                                      str_detect(Tsize,'T4') ~ 'T4',
                                                      str_detect(Tsize,'T') ~ 'Not available',
                                                      TRUE ~ NA_character_))

#Create clean variables for laterality and grade
df_final <- df_final %>% mutate(laterality_mod = case_when(str_detect(laterality,'0') ~ 'Not a paired site',
                                                           str_detect(laterality,'1') ~ 'Right',
                                                           str_detect(laterality,'2') ~ 'Left',
                                                           str_detect(laterality,'4') ~ 'Bilateral involvement, lateral origin unknown, stated to be single primary',
                                                           TRUE ~ NA_character_),
                                grade_mod = case_when(str_detect(grade,'1') ~ 'Grade I',
                                                      str_detect(grade,'2') ~ 'Grade II',
                                                      str_detect(grade,'3') ~ 'Grade III',
                                                      str_detect(grade,'4') ~ 'Grade IV',
                                                      str_detect(grade,'6') ~ 'B-cell, Pre-B, B-precursor: Lymphomas/Leukemias',
                                                      TRUE ~ NA_character_))


#Redefine Nationalty inot Emirati/Non-Emirati
df_final <- df_final %>% mutate(nationality_mod = case_when(str_detect(nationality,'United Arab Emirates') ~ 'Emirati',
                                                            !is.na(nationality) ~ 'Non-Emirati',
                                                            TRUE ~ NA_character_))


#########################################################
# Remove subject with NAs in PSG, LN, Tsize, or MS,
# will use MS as a proxy
#########################################################
df_final <- filter(df_final, !is.na(MS))

#########################################################
# Remove subject with NAs grade and laterality
#########################################################
df_final <- filter(df_final, !is.na(grade_mod) & !is.na(laterality_mod))

##########################################################################################
# Remove subject with grade_mod = GradeIV and 
#laterality = 'Bilateral involvement, lateral origin unknown, stated to be single primary'
##########################################################################################
df_final <- df_final %>% filter(grade_mod %in% c('Grade I','Grade II','Grade III') & laterality_mod %in% c('Left','Right'))


############################
#Write df_final to disk
###########################
write.csv(df_final,file = paste0('1_data/2_new/dfBC_clean.csv'), row.names = FALSE)


