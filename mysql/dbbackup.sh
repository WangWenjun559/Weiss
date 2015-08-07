#/usr/bin/bash
# Back up database
# Usage:
# bash dbbackup.sh weiss
today="$(date +'%Y-%m-%d')"

srcdir="/home/mingf/Weiss"

source $srcdir/scrapers/configure.sh

mysqldump -u $1 -p${passwd} $1 > "/home/mingf/db_bak/$1_${today}.sql"
