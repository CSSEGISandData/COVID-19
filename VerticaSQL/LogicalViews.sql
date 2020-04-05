SELECT
    ProvinceState,
    CountryRegion,
    LastUpdate::DATE dt,
    SUM(Confirmed)   conf,
    SUM(Deaths)      dths,
    SUM(Recovered)   reco,
    MAX(Latitude)    lat,
    MAX(Longitude)   LONG
FROM
    COVID19_EXT
    --WHERE CountryRegion ilike '%France%'
GROUP BY
    ProvinceState,
    CountryRegion,
    LastUpdate::DATE
ORDER BY
    1,2 DESC;
    
    
SELECT
    LastUpdate::DATE dt,
    COUNT(1)
FROM
    COVID19_EXT
    --WHERE CountryRegion ilike '%France%'
GROUP BY
    LastUpdate::DATE
ORDER BY
    1,2 DESC;
    
SELECT
    ProvinceState,
    CountryRegion,
    case when CountryRegion = 'Mainland China' then 'China' else CountryRegion end CountryRegiondervd,
    LastUpdate,
    LastUpdate::date dt,
    Confirmed,
    Deaths,
    Recovered,
    Latitude,
    Longitude,
    max(Latitude) over (partition by ProvinceState, CountryRegion) latfill,
    max(Longitude) over (partition by ProvinceState, CountryRegion) longfill
FROM
    COVID19_EXT ;

create or replace view public.COVID19_VIEW as
with x as  (
SELECT null as cnty,
    ProvinceState,
    CountryRegion,
    case 
    when CountryRegion = 'Mainland China' then 'China' 
    when CountryRegion = 'Korea, South' then 'South Korea' 
    when CountryRegion = 'Republic of Korea' then 'South Korea' 
    when CountryRegion = 'UK' then 'United Kingdom' 
    else CountryRegion 
    end CountryRegiondervd,
    LastUpdate,
    LastUpdate::date reportdt,
    Confirmed,
    Deaths,
    Recovered,
    Latitude,
    Longitude,
    max(Latitude) over (partition by ProvinceState, CountryRegion) latfill,
    max(Longitude) over (partition by ProvinceState, CountryRegion) longfill,
    max(LastUpdate::date) over (partition by ProvinceState, CountryRegion) currentportdate
FROM
    COVID19_EXT
UNION ALL
SELECT cnty,
    ProvinceState,
    CountryRegion,
    case 
    when CountryRegion = 'Mainland China' then 'China' 
    when CountryRegion = 'Korea, South' then 'South Korea' 
    when CountryRegion = 'Republic of Korea' then 'South Korea' 
    when CountryRegion = 'UK' then 'United Kingdom' 
    else CountryRegion 
    end CountryRegiondervd,
    LastUpdate,
    LastUpdate::date reportdt,
    Confirmed,
    Deaths,
    Recovered,
    Latitude,
    Longitude,
    max(Latitude) over (partition by ProvinceState, CountryRegion) latfill,
    max(Longitude) over (partition by ProvinceState, CountryRegion) longfill,
    max(LastUpdate::date) over (partition by ProvinceState, CountryRegion) currentportdate
FROM
    COVID19_20200323_EXT
)
select cnty, ProvinceState,
    CountryRegiondervd CountryRegion,
    reportdt,
    latfill,
    longfill,
    sum(nvl(Confirmed,0)) confirmed,
    sum(nvl(Deaths,0)) deaths,
    sum(nvl(Recovered,0)) recovered
    from x
group by cnty, ProvinceState,
    CountryRegiondervd  ,
    reportdt,
    latfill,
    longfill
 ;


create or replace view public.COVID19_US_VIEW as
with us as (
select  *,
 trim(
 replace(substr(provincestate,instr(provincestate,',')+1),'(From Diamond Princess)','')
 ) usstate from public.COVID19_VIEW v
where CountryRegion = 'US' 
--and reportdt between'2020-03-03' and '2020-03-19'
)
,s as (select * from usstatescodes )
select     cnty,
    ProvinceState,
    CountryRegion,
    reportdt,
    latfill,
    longfill,
    confirmed,
    deaths,
    recovered,
--s.*,
nvl(statename,usstate) statename
  from us left join s on (statecode = usstate)
--group by provincestate
;

with x as (
select CountryRegion,statename,reportdt,
sum(confirmed) conf, sum(deaths) dths
from public.COVID19_US_VIEW
group by CountryRegion,statename,reportdt
)
select *--, dths/conf mortratio 
from x where CountryRegion = 'US'
order by reportdt desc,conf desc, dths desc ,CountryRegion
;

select * from public.COVID19_VIEW
--where CountryRegion ilike '%US%'
;

select * from public.COVID19_US_VIEW
--where CountryRegion ilike '%US%'
;
