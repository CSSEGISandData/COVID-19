country_codes=`readlink -f data/country_codes.csv`
country_synonyms=`readlink -f data/country_synonyms.csv`
removed_country_codes=`readlink -f data/removed_country_codes.csv`
m49=`readlink -f data/m49.csv`

# Annotate daily reports for January and February
for report in ../csse_covid_19_daily_reports/*.csv; do
    columns=`head -n 1 $report | sed -e 's/,/\n/g' | wc -l`
    filetype=`file $report`
    trailing=`tail -c 1 $report`
    report=`readlink -f $report`

    if [ $columns -eq 6 ]; then
        sql="daily-report-v1.sql"
    elif [ $columns -eq 8 ]; then
        sql="daily-report-v2.sql"
    else
        continue
    fi

    cat $sql \
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
