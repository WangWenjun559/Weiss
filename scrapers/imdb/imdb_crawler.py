import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages")
from sets import Set
import json
import helpers


historyfile = 'crawled.txt'    ## file that stores the movie id crawled
release_date = '2015-01-01,2015-01-01'  ## the release date range to crawl
reviewfile = 'reviews.json'
source = 'imdb'


def getToCrawl():
    with open(historyfile, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    crawled = Set(lines)

    toCrawlList = helpers.get_movie_id(release_date)
    toCrawl = filter(lambda x : x not in crawled, toCrawlList)

    with open(historyfile, 'a') as f:
        for s in toCrawl:
            f.write(s + '\n')

    return toCrawl


def getReviews():
    toCrawl = getToCrawl()
    print "About to get Reviews", len(toCrawl), 'IDs in total'
    data = map(helpers.get_movie_reviews, toCrawl)
    data = filter(lambda x : x != [], data)
    with open(reviewfile, 'w') as f:
        json.dump(data, f)


if __name__ == "__main__":
    getReviews()
