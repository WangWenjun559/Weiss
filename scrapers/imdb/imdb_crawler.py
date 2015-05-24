import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages")
import imdb
from sets import Set
import json

historyfile = 'crawled.txt'    ## file that stores the movie id crawled
release_date = '2015-01-01,2016-01-01'  ## the release date range to crawl
reviewfile = 'reviews.json'

ia = imdb.IMDb()   ## crawler handler

def getToCrawl():
    with open(historyfile, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    crawled = Set(lines)

    toCrawlDicts = ia.get_movie_id(release_date, 0)['data']['id']
    toCrawlList = map(lambda x : x['id'], toCrawlDicts)
    res = filter(lambda x : x not in crawled, toCrawlList)

    with open(historyfile, 'w') as f:
        for s in res:
            f.write(s + '\n')

    return res[:10]



def getReview(movieId):
    print movieId
    a = ia.get_movie_user_reviews(movieId, 0)['data']
    if (a.has_key("reviews")):
        return a['reviews']
    else:
        return None


def getReviews():
    toCrawl = getToCrawl()
    data = map(getReview, toCrawl)
    data = filter(lambda x : x is not None, data)
    with open(reviewfile, 'w') as f:
        json.dump(data, f)


if __name__ == "__main__":
    getReviews()

