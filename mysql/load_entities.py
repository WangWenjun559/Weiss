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

datadir = '/home/mingf/data/'
homedir = '/home/mingf/Weiss/'
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


def run():
    if (not os.path.exists(efile)):
        logging.info("No such file " +  efile)
        return
    with open(efile, 'r') as f:
        data = json.load(f)
    logging.info("About to load " + thisdate +  "with " + str(len(data)) + " entities")
    if (len(data) == 0):
        return
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

def initLogging():
    today = datetime.now().date().strftime("%Y-%m-%d")
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename="~/Weiss/log/" + sys.argv[0] + "-" + today + '.log'
        filemode='w')
    logging.info('logger initialzed.')


if __name__ == '__main__':
    initLogging()

    user, passwd, start, end, dbname, source = _arg_parser()

    dbh = mdb.connect(host="localhost",
                   user=user,
                   passwd=passwd,
                   db=dbname)
    dbc = dbh.cursor()

    dbh.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    for dt in rrule(DAILY, dtstart = start, until = end):
        thisdate = dt.strftime('%Y-%m-%d')
        release_date = '%s,%s' % (thisdate, thisdate)  ## the release date range to crawl
        efile = '%s%s_entities_%s.json' % (datadir, source, thisdate)
        run()

    dbh.close()
