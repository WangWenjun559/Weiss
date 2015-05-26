import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages")
from sets import Set
import json
import helpers


historyfile = 'crawled.txt'    ## file that stores the movie id crawled
start = '2015-01-02'
end = '2015-01-02'
release_date = '%s,%s' % (start, end)  ## the release date range to crawl
cfile = 'comments_%s.json' % start
efile = 'entities_%s.json' % start
source = 'imdb'


def getToCrawl():
    with open(historyfile, 'r') as f:
        #lines = [line.rstrip('\n') for line in f]
        crawled = json.load(f)
    crawledIDs = Set(crawled.keys())
    IDs = helpers.get_movie_id(release_date)
    IDwithNum = {ID: helpers.get_review_amount(ID) for ID in IDs}
    updates = {ID: num for ID, num in IDwithNum.iteritems() if num != 0 and ID in crawledIDs and num > crawled[ID]}
    news = {ID: num for ID, num in IDwithNum.iteritems() if num != 0 and ID not in crawledIDs}

    toCrawl = {ID: num - crawled[ID] for ID, num in updates}
    toCrawl.update(news)

    crawled.update(IDwithNum)

    with open(historyfile, 'w') as f:
        json.dump(crawled, f)

    return toCrawl, news.keys()   # return: movies that have new reviews, new movies

def run():
    toCrawl, newEntities = getToCrawl()
    print "About to get Reviews", len(toCrawl), 'IDs in total'
    comments = map(helpers.get_movie_reviews, toCrawl.iteritems())
    #comments = filter(lambda x : x != [], comments)  #should not have any []
    entities = map(helpers.get_movie_infos, newEntities)
    with open(cfile, 'w') as f:
        json.dump(comments, f)
    with open(efile, 'w') as f:
        json.dump(entities, f)


if __name__ == "__main__":
    run()
