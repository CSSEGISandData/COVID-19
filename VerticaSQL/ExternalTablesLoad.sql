drop TABLE public.COVID19_EXT ;

CREATE external TABLE public.COVID19_EXT 
(  -- c3 as CURRENT_LOAD_SOURCE()
    ProvinceState varchar(50) ,
    CountryRegion varchar(50) ,
    LastUpdate varchar(50) ,
    Confirmed int ,
    Deaths int ,
    Recovered int ,
    Latitude numeric(37,15) ,
    Longitude numeric(37,15) 
)
as copy
from '/vertica/data/raw/covid19/csse_covid_19_data/csse_covid_19_daily_reports/*.csv' on v_vmart_node0001 
delimiter as ',' enclosed by '"' skip 1 TRAILING NULLCOLS;

select * from public.COVID19_EXT;

CREATE external TABLE public.COVID19_20200323_EXT 
(   FIPS  varchar(10),
    cnty  varchar(100),
    ProvinceState varchar(50) ,
    CountryRegion varchar(50) ,
    LastUpdate varchar(50) ,
    Latitude numeric(37,15) ,
    Longitude numeric(37,15),
    Confirmed int ,
    Deaths int ,
    Recovered int ,
    active int ,
    combkey varchar(200)
)
as copy
from '/vertica/data/raw/covid19/csse_covid_19_data/csse_covid_19_daily_reports_20200322/*.csv' on v_vmart_node0001 
delimiter as ',' enclosed by '"' skip 1 TRAILING NULLCOLS;


select * from public.COVID19_20200323_EXT;


CREATE external TABLE public.UID_ISO_FIPS_Lookup 
(   UID int,
    iso2 varchar(2),
    iso3 varchar(3) ,
    code3 int,
    FIPS int,
    admin2 varchar(100),
    provincestate varchar(100),
    CountryRegion varchar(50) ,
    Latitude numeric(37,15) ,
    Longitude numeric(37,15),
    combkey varchar(200)
)
as copy
from '/vertica/data/raw/covid19/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv' on v_vmart_node0001 
delimiter as ',' enclosed by '"' skip 1 TRAILING NULLCOLS;


select * from public.UID_ISO_FIPS_Lookup
where iso2 = 'US';

