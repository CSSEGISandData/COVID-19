## Daily reports (csse_covid_19_daily_reports)

### Fields

Some field names had previously called differently,
the list below shows the previous label follows by the current label:

- "Province/State" -> "Province_State"
- "Country/Region" -> "Country_Region"
- "Last Update" -> "Last_Update"
- "Latitude" -> "Lat"
- "Longitude" -> "Long_"
- "Incidence_Rate" -> "Incident_Rate"
- "Case-Fatality_Ratio" -> "Case_Fatality_Ratio"

### Datetime format

- 22 Jan 2020 to 1 Feb 2020: `m/d/yyyy HH:MM` (e.g. 2/1/2020 11:03)
- 2 Feb 2020 to 21 Mar 2020: `yyyy-mm-ddTHH:MM:SS` (e.g. 2020-03-21T22:43:04)
- 22 Mar, 28-30 Mar, 2 Apr, 4 Apr, 6 Apr 2020: `m/d/yy HH:MM` (e.g. 3/22/20 23:45)
- 23-27 Mar, 1 Apr, 3 Apr, 5 Apr 2020, and since 7 Apr 2020: `yyyy-mm-dd HH:MM:SS` (e.g. 2020-03-23 23:19:34)

If time is not required, using the date from filename can be more convenient.
