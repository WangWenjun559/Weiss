: '
This file will go through all comments file of a certain source,
run comment.js to calculate sentiment score for each comment.

Usage: ./sentiment.sh source startdate #ofdays
        source could be: imdb, MF
        startdate in the form like: 2015-01-01
        #ofdays like: 2, so it will run file source_comments_2015-01-01.json
                      and source_comments_2015-01-02.json

Note: make sure that all comments are under folder /home/mingf/data

Author: Wenjun Wang
Date: May 28, 2015
'
#!/bin/bash
dash_date=${2:-$(date +%y-%m-%d)}
date=${dash_date//_/-}
num=$3
num=$((num-1))
FILES=/home/mingf/data/

for days in $(seq 0 $num);do
  day="`date -d "$date + $days days" +%Y-%m-%d`"
  f=$FILES$1_comments_$day.json
  echo $f
  node comment.js $f
done
