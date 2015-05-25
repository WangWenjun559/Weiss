import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages")
import imdb

ia = imdb.IMDb()
source = 'imdb'

def _getId(release_date, pageId):
    print "getting ID" , pageId
    return ia.get_movie_id(release_date, pageId)['data']['id']


def get_movie_id(release_date):
    data = ia.get_movie_id(release_date, 0)['data']
    numMovies = int(data['amount'][0]['amount'])  # ID at IMDB is 1-indexed
    numPages = numMovies / 50 + 1   ## each page has at most 50 IDs
    listOfListOfIds = map(lambda i: _getId(release_date, 1 + 50*i), xrange(numPages))  ## +1 needed , since 1 indexed
    return map(lambda x: x['id'], [ID for listOfIds in listOfListOfIds for ID in listOfIds])


def _addMetaData(entry, movieId):
    entry['eid'] = movieId
    entry['source'] = source
    return entry

def _getReview(movieId, pageId):
    print "getting reviews", movieId, pageId
    a = ia.get_movie_user_reviews(movieId, pageId)['data']
    if (a.has_key("reviews")):
        return map(lambda x: _addMetaData(x, movieId), a['reviews'])
    else:
        return []


def get_movie_reviews(ID):
    data = ia.get_movie_user_reviews(ID, 0)['data']
    numRvws = int(data['amount'][0]['amount']) - 1 # -1 needed, since 0-indexed
    if (numRvws == -1) return []
    numPages = numRvws / 10 + 1   ## each page has at most 10 reviews
    print ID, "has", numRvws, "reviews"
    listOfListOfRvws = map(lambda i: _getReview(ID, 10*i), xrange(numPages))
    return [rvw for listOfRvws in listOfListOfRvws for rvw in listOfRvws]
