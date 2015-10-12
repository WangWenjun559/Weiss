"""
A scrpit to load entity into Database
Author: Ming
Usage:
usage: load_entities.py [-h] [--source SOURCE] [--start START] [--end END]
                        [--user USER] [--passwd PASSWD] [--db DBNAME]

optional arguments:
-h, --help       show this help message and exit
--source SOURCE  The source info, which would be used when openning
cooresponding json file
--start START    The start date, in form of YYYY-MM-DD
--end END        The end date, in form of YYYY-MM-DD, The range is inclusive
--user USER      The user name of database
--passwd PASSWD  The password of database
--db DBNAME      The name of database

Example:
python load_entities.py --source=imdb --start=2015-01-01 --end=2015-01-01 --user=ming --passwd=fang --db=test')
"""

import MySQLdb as mdb
from datetime import date
from datetime import datetime
from dateutil.rrule import rrule, DAILY
import sys
import json
import argparse
import os.path
from sets import Set
from multiprocessing import Pool

datadir = '/home/mingf/data/'
homedir = '/home/mingf/Weiss/'
dbsetting = '/home/mingf/Weiss/scrapers/imdb/dbsetting.json'
module = 'mysql/'
release_date = ''
cfile = ''
efile = ''

dbh = None
dbc = None
def _dict2tuple(entry):
    return (entry['id'],
            entry['source'],
            entry['description'],
            entry['url'],
            entry['tid'],
            entry['name']
            )

def getHistory(source):
        with open(dbsetting, 'r') as f:
            setting = json.load(f)
        dbh = mdb.connect(host=setting['host'], user=setting['user'], passwd=setting['passed'], db=setting['db'])
        dbc = dbh.cursor()
        dbc.execute("select id from entity where source='%s'" % source)
        res = dbc.fetchall()
        IDs = map(lambda x: x[0], list(res))
        return Set(IDs)

def run(IDs):
    if (not os.path.exists(efile)):
        print "No such file", efile
        return
    with open(efile, 'r') as f:
        data = json.load(f)
    print "About to load",  thisdate, "with", len(data), "entities"
    if (len(data) == 0):
        return
    data = filter(lambda entry: entry['id'] not in IDs, data) # filter out duplicate entities
    print "After filtering,", len(data), "entities left"
    dbc.executemany(
        """INSERT INTO entity (id, source, description, url, tid, name)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        map(_dict2tuple, data)
    )
    dbh.commit()

def _arg_parser():
    parser = argparse.ArgumentParser(description='A script to load entity info into database.\nEx: python load_entities.py --source=imdb --start=2015-01-01 --end=2015-01-01 --user=ming --passwd=fang --db=test')
    parser.add_argument('--source', dest='source', action='store', help='The source info, which would be used when openning cooresponding json file', required=True)
    parser.add_argument('--start', dest='start', action='store', help='The start date, in form of YYYY-MM-DD', required=True)
    parser.add_argument('--end', dest='end', action='store', help='The end date, in form of YYYY-MM-DD, The range is inclusive', required=True)
    parser.add_argument('--user', dest='user', action='store', help='The user name of database', required=True)
    parser.add_argument('--passwd', dest='passwd', action='store', help='The password of database', required=True)
    parser.add_argument('--db', dest='dbname', action='store', help='The name of database', required=True)

    results = parser.parse_args()


    user = results.user
    passwd = results.passwd
    source = results.source
    dbname = results.dbname
    start = datetime.strptime(results.start, '%Y-%m-%d').date()
    end = datetime.strptime(results.end, '%Y-%m-%d').date()

    return (user, passwd, start, end, dbname, source)


if __name__ == '__main__':
    with open(dbsetting, 'r') as f:
        setting = json.load(f)
    dbh = mdb.connect(host=setting['host'], user=setting['user'], passwd=setting['passed'], db=setting['db'])

    dbc = dbh.cursor()

    dbh.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')


    for dt in rrule(DAILY, dtstart = start, until = end):
        IDs = getHistory(source)
        thisdate = dt.strftime('%Y-%m-%d')
        release_date = '%s,%s' % (thisdate, thisdate)  ## the release date range to crawl
        efile = '%s%s_entities_%s.json' % (datadir, source, thisdate)
        run(IDs)

    dbh.close()
