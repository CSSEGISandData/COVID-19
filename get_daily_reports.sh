#!/bin/bash 
function oops {
	echo
	echo '*** oops, '$1' ***'
	echo
	exit 86
}

USER=CSSEGISandData
PROJECT=COVID-19
REMDIR=csse_covid_19_daily_reports
RELPATH=csse_covid_19_data/$REMDIR
BRANCH=master
LCLDIR=daily_reports
THE_DATE=`date '+%Y-%m-%d'`
THE_TIME=`date '+%H:%M:%S'`

if [ -e $LCLDIR ]; then
    mv $LCLDIR $LCLDIR.$THE_DATE.$THE_TIME
    if [ $? -ne 0 ]; then 
	    oops "Renaming $LCLDIR failed"
    fi
fi

svn export https://github.com/$USER/$PROJECT/branches/$BRANCH/$RELPATH
if [ $? -ne 0 ]; then 
    oops "svn export failed"
fi

mv $REMDIR $LCLDIR
if [ $? -ne 0 ]; then 
    oops "Renaming $REMDIR to $LCLDIR failed"
fi
