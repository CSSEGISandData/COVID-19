country_codes=`readlink -f data/country_codes.csv`
country_synonyms=`readlink -f data/country_synonyms.csv`
removed_country_codes=`readlink -f data/removed_country_codes.csv`
m49=`readlink -f data/m49.csv`

# Annotate daily reports for January and February
for report in ../csse_covid_19_daily_reports/{01,02}-*-2020.csv; do
    filetype=`file $report`
    trailing=`tail -c 1 $report`
    report=`readlink -f $report`

    cat daily-report-v1.sql \
        | sed -e "s|:report|$report|" \
        | sed -e "s|:country_codes|$country_codes|" \
        | sed -e "s|:country_synonyms|$country_synonyms|" \
        | sed -e "s|:removed_country_codes|$removed_country_codes|" \
        | sed -e "s|:m49|$m49|" \
        | psql -q

    # Restore Windows line-endings if present in original file
    echo $filetype | grep -q "CRLF" && unix2dos -q $report

    # Restore Unicode BOM if present in original file
    echo $filetype | grep -q "BOM" && unix2dos -q -m $report
done

# Annotate daily reports for March (slightly updated format)
for report in ../csse_covid_19_daily_reports/03-*-2020.csv; do
    filetype=`file $report`
    trailing=`tail -c 1 $report`
    report=`readlink -f $report`

    cat daily-report-v2.sql \
        | sed -e "s|:report|$report|" \
        | sed -e "s|:country_codes|$country_codes|" \
        | sed -e "s|:country_synonyms|$country_synonyms|" \
        | sed -e "s|:removed_country_codes|$removed_country_codes|" \
        | sed -e "s|:m49|$m49|" \
        | psql -q

    # Restore Windows line-endings if present in original file
    echo $filetype | grep -q "CRLF" && unix2dos -q $report

    # Restore Unicode BOM if present in original file
    echo $filetype | grep -q "BOM" && unix2dos -q -m $report
done
