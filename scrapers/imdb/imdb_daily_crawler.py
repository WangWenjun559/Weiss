#!/usr/bin/python
import sys
from sets import Set
import json
import helpers
from datetime import date
from datetime import datetime
from dateutil.rrule import rrule, DAILY
from multiprocessing import Pool


datadir = '/home/mingf/data/'
source = 'imdb'
homedir = '/home/mingf/Weiss/'
module = 'scrapers/'
historyfile = homedir + module + source + '/crawled.txt'    ## file that stores the movie id crawled
start = datetime.now().date()
#start = date(2015, 6, 3)
end = start
release_date = ''
cfile = ''
efile = ''
query = "groups=now-playing-us&title_type=feature"
#query = "release_date=2015-01-01,2015-06-03&title_type=feature"


def getToCrawl():
    with open(historyfile, 'r') as f:
        crawled = json.load(f)
    crawledIDs = Set(crawled.keys())
    IDs = helpers.get_movie_id_adv(query)
    print "Num of ID in the query", len(IDs)
    pool = Pool(processes=6)
    nums = pool.map(helpers.get_review_amount, IDs)
    pool.close()
    pool.join()
    IDwithNum = dict(zip(IDs, nums))
    updates = {ID: num for ID, num in IDwithNum.iteritems() if num != 0 and ID in crawledIDs and num > crawled[ID]}
    news = {ID: num for ID, num in IDwithNum.iteritems() if num != 0 and ID not in crawledIDs}

    toCrawl = {ID: num - crawled[ID] for ID, num in updates.iteritems()}
    toCrawl.update(news)

    crawled.update(IDwithNum)

    with open(historyfile, 'w') as f:
        json.dump(crawled, f)

    return toCrawl, news.keys()   # return: movies that have new reviews, new movies

def run():
    toCrawl, newEntities = getToCrawl()
    print "About to get Reviews ", len(toCrawl), ' IDs in total'
    pool = Pool(processes=6)
    comments = pool.map(helpers.get_movie_reviews, toCrawl.iteritems())
    entities = pool.map(helpers.get_movie_infos, newEntities)
    pool.close()
    pool.join()
    #comments = filter(lambda x : x != [], comments)  #should not have any []
    with open(cfile, 'w') as f:
        json.dump(comments, f)
    with open(efile, 'w') as f:
        json.dump(entities, f)


if __name__ == "__main__":
    for dt in rrule(DAILY, dtstart = start, until = end):
        thisdate = dt.strftime('%Y-%m-%d')
        release_date = '%s,%s' % (thisdate, thisdate)  ## the release date range to crawl
        cfile = '%s%s_comments_%s.json' % (datadir, source, thisdate)
        efile = '%s%s_entities_%s.json' % (datadir, source, thisdate)
        print "About to crawl", thisdate
        run()
