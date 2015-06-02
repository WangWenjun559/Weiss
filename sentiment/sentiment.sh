:'
This file will go through all comments file of a certain source,
run comment.js to calculate sentiment score for each comment.

Usage: ./sentiment.sh source
        source could be: imdb, MF

Note: make sure that all comments are under folder /home/mingf/data

Author: Wenjun Wang
Date: May 28, 2015
'
#!/bin/bash
FILES=/home/mingf/data/$1_comments_*.json
for f in $FILES
do
  echo $f
  node comment.js $f
done
