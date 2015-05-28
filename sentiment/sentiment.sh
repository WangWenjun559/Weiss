#!/bin/bash
FILES=/home/mingf/data/$1_comments_*.json
for f in $FILES
do
  echo $f
  node comment.js $f
done
