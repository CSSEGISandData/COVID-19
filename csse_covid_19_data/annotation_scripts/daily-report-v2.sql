-- Import data tables from local filesystem via psql \copy
create temporary table report (province text, region text, updated text, confirmed int, deaths int, recovered int, latitude text, longitude text);
\copy report from :report with csv header

alter table report add column index serial;

create temporary table country_codes (country text, alpha2 char(2), alpha3 char(3));
\copy country_codes from :country_codes with csv header

create temporary table removed_country_codes (country text, alpha2 char(2));
\copy removed_country_codes from :removed_country_codes with csv header

alter table removed_country_codes add column alpha3 char(3);
update removed_country_codes as r
set alpha3 = c.alpha3
from country_codes as c
where c.alpha2 = r.alpha2;

create temporary table country_synonyms (synonym text, country text);
\copy country_synonyms from :country_synonyms with csv header

create temporary table m49 (global int, global_name text, region int, region_name text, subregion int, subregion_name text, intermediate_region int, intermediate_region_name text, country text, m49 int, alpha3 char(3), ldc text, lldc text, ddc text, foo text);
\copy m49 from :m49 with csv header

create temporary table output as
with country_code as (
    select
        -- Output all fields from the original report data
        r.*,

        -- Pick alpha2, alpha3 fields in match rank order
        coalesce(c.alpha2, rc.alpha2, fc.alpha2, sc.alpha2) as alpha2,
        coalesce(c.alpha3, rc.alpha3, fc.alpha3, sc.alpha3) as alpha3,

        -- Use row_number to output the match rank for each candidate
        row_number() over (
            partition by r.index
            order by
                case when c.alpha2 is not null then 0
                else case when sc.alpha2 is not null then 1
                else case when rc.alpha2 is not null then 2
                else case when fc.alpha2 is not null then 3
                else 3
            end end end end
        ) as rn
    from report as r

    -- direct name matches
    left join country_codes as c on c.country = r.region

    -- country synonym matches (manually curated)
    left join country_synonyms as cs on cs.synonym = r.region
    left join country_codes as sc on sc.country = cs.country

    -- previously-removed JHSSE country names
    -- sourced from https://github.com/AnthonyEbert/COVID-19_ISO-3166/blob/97683e0c3972ff7acb30a8065df3150583657929/removed_countries.txt
    left join removed_country_codes as rc on rc.country = r.region

    -- fallback match on first-word-equals-country-name
    left join country_codes as fc on split_part(fc.country, ' ', 1) = r.region
)
select
    -- Output fields using the same column titles as the report CSV
    c.province as "Province/State",
    c.region as "Country/Region",
    c.alpha2 as "CountryAlpha2",
    c.alpha3 as "CountryAlpha3",
    m49.region_name as "M49Region",
    m49.subregion_name as "M49SubRegion",
    c.updated as "Last Update",
    c.confirmed as "Confirmed",
    c.deaths as "Deaths",
    c.recovered as "Recovered",
    c.latitude as "Latitude",
    c.longitude as "Longitude"
from country_code as c
left join m49 on m49.alpha3 = c.alpha3
where c.rn = 1
order by c.index;

\copy output to :report with csv header
