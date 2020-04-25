# JHU CSSE COVID-19 Dataset

## Table of contents

 * [Daily reports (csse_covid_19_daily_reports)](#daily-reports-csse_covid_19_daily_reports)
 * [USA daily state reports (csse_covid_19_daily_reports_us)](#usa-daily-state-reports-csse_covid_19_daily_reports_us)
 * [Time series summary (csse_covid_19_time_series)](#time-series-summary-csse_covid_19_time_series)
 * [Data modification records](#data-modification-records)
 * [UID Lookup Table Logic](#uid-lookup-table-logic)
---

## [Daily reports (csse_covid_19_daily_reports)](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

This folder contains daily case reports. All timestamps are in UTC (GMT+0).

### File naming convention
MM-DD-YYYY.csv in UTC.

### Field description
* <b>FIPS</b>: US only. Federal Information Processing Standards code that uniquely identifies counties within the USA.
* <b>Admin2</b>: County name. US only.
* <b>Province_State</b>: Province, state or dependency name.
* <b>Country_Region</b>: Country, region or sovereignty name. The names of locations included on the Website correspond with the official designations used by the U.S. Department of State.
* <b>Last Update</b>: MM/DD/YYYY HH:mm:ss  (24 hour format, in UTC).
* <b>Lat</b> and <b>Long_</b>: Dot locatoins on the dashboard. All points (except for Australia) shown on the map are based on geographic centroids, and are not representative of a specific address, building or any location at a spatial scale finer than a province/state. Australian dots are located at the centroid of the largest city in each state.
* <b>Confirmed</b>: Confirmed cases include presumptive positive cases.
* <b>Deaths</b>: Death totals in the US include confirmed and probable, in accordance with [CDC](https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/cases-in-us.html) guidelines as of April 14.
* <b>Recovered</b>: Recovered cases outside China are estimates based on local media reports, and state and local reporting when available, and therefore may be substantially lower than the true number.
* <b>Active:</b> Active cases = total confirmed - total recovered - total deaths.
* <b>Combined_Key</b>: Admin2 + Province_State + Country_Region.

### Update frequency
* Files on and after April 23, once per day between 03:30 and 04:00 UTC.
* Files from February 2 to April 22: once per day around 23:59 UTC.
* Files on and before February 1: the last updated files before 23:59 UTC. Sources: [archived_data](https://github.com/CSSEGISandData/COVID-19/tree/master/archived_data) and dashboard.

### Data sources
Refer to the [mainpage](https://github.com/CSSEGISandData/COVID-19).

### Why create this new folder?
1. Unifying all timestamps to UTC, including the file name and the "Last Update" field.
2. Pushing only one file every day.
3. All historic data is archived in [archived_data](https://github.com/CSSEGISandData/COVID-19/tree/master/archived_data).

---
## [USA daily state reports (csse_covid_19_daily_reports_us)](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports_us)

This table contains an aggregation of each USA State level data.

### File naming convention
MM-DD-YYYY.csv in UTC.

### Field description
* <b>Province_State</b> - The name of the State within the USA.
* <b>Country_Region</b> - The name of the Country (US).
* <b>Last_Update</b> - The most recent date the file was pushed.
* <b>Lat</b> - Latitude.
* <b>Long_</b> - Longitude.
* <b>Confirmed</b> - Aggregated confirmed case count for the state.
* <b>Deaths</b> - Aggregated Death case count for the state.
* <b>Recovered</b> - Aggregated Recovered case count for the state.
* <b>Active</b> - Aggregated confirmed cases that have not been resolved (Active = Confirmed - Recovered - Deaths).
* <b>FIPS</b> - Federal Information Processing Standards code that uniquely identifies counties within the USA.
* <b>Incident_Rate</b> - confirmed cases per 100,000 persons.
* <b>People_Tested</b> - Total number of people who have been tested.
* <b>People_Hospitalized</b> - Total number of people hospitalized.
* <b>Mortality_Rate</b> - Number recorded deaths * 100/ Number confirmed cases.
* <b>UID</b> - Unique Identifier for each row entry. 
* <b>ISO3</b> - Officialy assigned country code identifiers.
* <b>Testing_Rate</b> - Total number of people tested per 100,000 persons.
* <b>Hospitalization_Rate</b> - Total number of people hospitalized * 100/ Number of confirmed cases.

### Update frequency
* Once per day between 03:30 and 04:00 UTC.

### Data sources
Refer to the [mainpage](https://github.com/CSSEGISandData/COVID-19).

---
## [Time series summary (csse_covid_19_time_series)](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)

See [here](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/README.md).

---
## Data modification records
We are also monitoring the curve change. Any errors made by us will be corrected in the dataset. Any possible errors from the original data sources will be listed here as a reference.
* NHC 2/14: Hubei Province deducted 108 prior deaths from the death toll due to double counting.
* For Hubei Province: from Feb 13 (GMT +8), we report both clinically diagnosed and lab-confirmed cases. For lab-confirmed cases only (Before Feb 17), please refer to [who_covid_19_situation_reports](https://github.com/CSSEGISandData/COVID-19/tree/master/who_covid_19_situation_reports). 
* On Feb 27 Italy made a change in their testing protocols, to limit coronavirus testing to at-risk people showing symptoms of COVID-19. ([Source](https://apnews.com/6c7e40fbec09858a3b4dbd65fe0f14f5))
* About DP 3/1: All cases of COVID-19 in repatriated US citizens from the Diamond Princess are grouped together, and their location is currently designated at the ship’s port location off the coast of Japan. These individuals have been assigned to various quarantine locations (in military bases and hospitals) around the US. This grouping is consistent with the CDC.
* Hainan Province active cases update (4/13): We responded to the error from 3/24 to 4/1 we had incorrect data for Hainan Province.  We had -6 active cases (168 6 168 -6). We applied the correction (168 6 162 0) that was applied on 4/2 for this period (3/24 to 4/1).
* Florida in the daily report US (4/13): Source data error. Correction 123,019 -> 21,019.
* Okaloosa, Florida in the dail report (4/13): Source data error. Correction 102,103 -> 103.
* The death toll in Wuhan was revised from 2579 to 3869 (4/17). ([Source1](http://www.china.org.cn/china/Off_the_Wire/2020-04/17/content_75943843.htm), [Source2](http://www.nhc.gov.cn/yjb/s7860/202004/51706a79b1af4349b99264420f2cee54.shtml))
* About France confirmed cases (4/16): after communicating with solidarites-sante.gouv.fr, we decided to make these adjustments based on public available information. From April 4 to April 11, only "cas confirmés" are counted as confirmed cases in our dashboard. Starting from April 12, both "cas confirmés" and "cas possibles en ESMS" (probable cases from ESMS) are counted into confirmed cases in our dashboard. ([More details](https://github.com/CSSEGISandData/COVID-19/issues/2094))
* Benton and Franklin, WA on April 21 and 22. Data were adjusted/added to match the WA DOH report. See [errata](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/Errata.csv) for details.

---
## [UID Lookup Table Logic](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv)

1.	All countries without dependencies (entries with only Admin0).
  *	None cruise ship Admin0: UID = code3. (e.g., Afghanistan, UID = code3 = 4)
  *	Cruise ships in Admin0: Diamond Princess UID = 9999, MS Zaandam UID = 8888.
2.	All countries with only state-level dependencies (entries with Admin0 and Admin1).
  *	Demark, France, Netherlands: mother countries and their dependencies have different code3, therefore UID = code 3. (e.g., Faroe Islands, Denmark, UID = code3 = 234; Denmark UID = 208)
  *	United Kingdom: the mother country and dependencies have different code3s, therefore UID = code 3. One exception: Channel Islands is using the same code3 as the mother country (826), and its artificial UID = 8261.
  *	Australia: alphabetically ordered all states, and their UIDs are from 3601 to 3608. Australia itself is 36.
  *	Canada: alphabetically ordered all provinces (including cruise ships and recovered entry), and their UIDs are from 12401 to 12415. Canada itself is 124.
  *	China: alphabetically ordered all provinces, and their UIDs are from 15601 to 15631. China itself is 156. Hong Kong and Macau have their own code3.
3.	The US (most entries with Admin0, Admin1 and Admin2).
  *	US by itself is 840 (UID = code3).
  *	US dependencies, American Samoa, Guam, Northern Mariana Islands, Virgin Islands and Puerto Rico, UID = code3. Their FIPS codes are different from code3.
  *	US states: UID = 840 (country code3) + 000XX (state FIPS code). Ranging from 8400001 to 84000056.
  *	Out of [State], US: UID = 840 (country code3) + 800XX (state FIPS code). Ranging from 8408001 to 84080056.
  *	Unassigned, US: UID = 840 (country code3) + 900XX (state FIPS code). Ranging from 8409001 to 84090056.
  *	US counties: UID = 840 (country code3) + XXXXX (5-digit FIPS code).
  *	Exception type 1, such as recovered and Kansas City, ranging from 8407001 to 8407999.
  *	Exception type 2, only the New York City, which is replacing New York County and its FIPS code.
  *	Exception type 3, Diamond Princess, US: 84088888; Grand Princess, US: 84099999.
