"""
A scrpit to load entity into Database
Author: Ming
Usage:
python load_entities.py -source source -from 2015-01-01 -to 2016-01-01 -user username -pass password
"""

import MySQLdb as mdb
from datetime import date
from datetime import datetime
from dateutil.rrule import rrule, DAILY
import sys
import json
import argparse

datadir = '/home/mingf/data/'
source = 'imdb'
homedir = '/home/mingf/Weiss/'
module = 'mysql/'
start = date(2015, 1, 1)
end = date(2016, 1, 1)
release_date = ''
cfile = ''
efile = ''
dbname = ''

dbh = None
c = None
def _dict2tuple(entry):
    return (entry['id'],
            entry['source'],
            entry['description'],
            entry['url'],
            entry['tid'],
            entry['name']
            )


def run():
    with open(efile, 'r') as f:
        data = json.load(f)
    print "About to load", thisdate, "with", len(data), "entities"
    if (len(data) == 0):
        return
    c.executemany(
        """INSERT INTO entity (id, source, description, url, tid, name)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        map(_dict2tuple, data)
    )
    dbh.commit()

def _arg_parser():
    parser = argparse.ArgumentParser(description='A script to load entity info into database.\nEx: python load_entities.py --source=imdb --start=2015-01-01 --end=2015-01-01 --user=ming --passwd=fang --db=test')
    parser.add_argument('--source', dest='source', action='store', help='The source info, which would be used when openning cooresponding json file')
    parser.add_argument('--start', dest='start', action='store', help='The start date, in form of YYYY-MM-DD')
    parser.add_argument('--end', dest='end', action='store', help='The end date, in form of YYYY-MM-DD, The range is inclusive')
    parser.add_argument('--user', dest='user', action='store', help='The user name of database')
    parser.add_argument('--passwd', dest='passwd', action='store', help='The password of database')
    parser.add_argument('--db', dest='dbname', action='store', help='The name of database')

    results = parser.parse_args()

    user = results.user
    passwd = results.passwd
    source = results.source
    start = datetime.strptime(results.start, '%Y-%m-%d').date()
    end = datetime.strptime(results.end, '%Y-%m-%d').date()
    return


if __name__ == '__main__':
    _arg_parser()

    dbh = mdb.connect(host="localhost",
                   user=user,
                   passwd=passwd,
                   db=dbname)
    c = dbh.cursor()

    for dt in rrule(DAILY, dtstart = start, until = end):
        thisdate = dt.strftime('%Y-%m-%d')
        release_date = '%s,%s' % (thisdate, thisdate)  ## the release date range to crawl
        cfile = '%s%s_comments_%s.json' % (datadir, source, thisdate)
        efile = '%s%s_entities_%s.json' % (datadir, source, thisdate)
        run()

    dbh.close()
