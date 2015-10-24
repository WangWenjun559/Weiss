#!/bin/bash
##################################################################
#
# This script assumes that there is another shell script that 
# takes care of the database name and password in the same directory
# 
# Author: Ming Fang
##################################################################
today="$(date +'%Y-%m-%d')"
shell="bash"
#today="2015-06-03"
scrdir="/home/mingf/Weiss"
source=$1
logdir="/home/mingf/data/log"
syslog="$logdir/syslog"
sourcelog="$logdir/${source}_log_${today}" 


source $scrdir/configure.sh # source the db and passwd variables

echo "" > $sourcelog

exec > >(tee -a $sourcelog) 2>&1

CheckExitCode() {
    #local ret=${pipestatus[0]}
    local ret=$?
    if [[ $ret == 0 ]]; then
            echo "success: $ret"
        else
            echo "failure: $ret"
            exit
    fi
}

# Daily Scraping
case "$source" in
    "imdb" )
        python $scrdir/scrapers/imdb/imdb_daily_crawler.py
        CheckExitCode
        ;;
    "MF" )
        /usr/bin/java -jar /home/yaozhou/Weiss/scrapers/MetaFilter/bin/Crawler.jar --mode=daily
        CheckExitCode
        ;;
    "GMA1"|"GMA2"|"GMA3"|"GMA4")
        /usr/bin/java -jar /home/yaozhou/Weiss/scrapers/GMA/GMA.jar
        CheckExitCode
        ;;
    "zomato" )
        python $scrdir/scrapers/urbanspoon/zomato.py    
        CheckExitCode
	    ;;
    *)
        echo "Invaild source"
        exit
        ;;
esac
echo "Finished $source daily crawler for $today"

# Loading entities
python $scrdir/mysql/load_entities.py --source=$source --start=$today --end=$today --user=$db --passwd=$passwd --db=$db
CheckExitCode
echo "Finished $source loading entities for $today"

# Computing sentiments
$shell $scrdir/sentiment/sentiment.sh $source $today 1 
CheckExitCode
echo "Finished $source computing sentiment for $today"

# Getting eid
python $scrdir/sentiment/geteid.py $db $db $passwd $source $today $today
CheckExitCode
echo "Finished $source finding eid for $today"

# Loading comments
python $scrdir/mysql/load_comments.py --source=$source --start=$today --end=$today --user=$db --passwd=$passwd --db=$db
CheckExitCode
echo "Finished $source loading comments for $today"

