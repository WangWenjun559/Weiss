import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages")
import imdb

ia = imdb.IMDb()
source = 'imdb'

def _getId(release_date, pageId):
    print "getting ID" , pageId
    return ia.get_movie_id(release_date, pageId)['data']['id']

def _getIdAdv(query, pageId):
    print "getting ID" , pageId
    return ia.get_movie_id_adv(query, pageId)['data']['id']



def get_movie_id(release_date):
    data = ia.get_movie_id(release_date, 0)['data']
    if (data.has_key('amount') and data['amount'][0].has_key('amount')):
        numMovies = int(data['amount'][0]['amount'])  # ID at IMDB is 1-indexed
        print "There are", numMovies, "IDs"
        numPages = numMovies / 50 + 1   ## each page has at most 50 IDs
        listOfListOfIds = map(lambda i: _getId(release_date, 1 + 50*i), xrange(numPages))  ## +1 needed , since 1 indexed
        return map(lambda x: x['id'], [ID for listOfIds in listOfListOfIds for ID in listOfIds])
    else:
        return []

def get_movie_id_adv(query):
    data = ia.get_movie_id_adv(query, 0)['data']
    if (data.has_key('amount') and data['amount'][0].has_key('amount')):
        numMovies = int(data['amount'][0]['amount'])  # ID at IMDB is 1-indexed
        print "There are", numMovies, "IDs"
        numPages = numMovies / 50 + 1   ## each page has at most 50 IDs
        listOfListOfIds = map(lambda i: _getIdAdv(query, 1 + 50*i), xrange(numPages))  ## +1 needed , since 1 indexed
        print listOfListOfIds
        return map(lambda x: x['id'], [ID for listOfIds in listOfListOfIds for ID in listOfIds])
    else:
        return []




def _addMetaData(entry, movieId):
    entry['id'] = movieId
    entry['source'] = source
    return entry

def _getReview(movieId, pageId):
    print "getting reviews", movieId, pageId
    a = ia.get_movie_user_reviews(movieId, pageId)['data']
    if (a.has_key("reviews")):
        return map(lambda x: _addMetaData(x, movieId), a['reviews'])
    else:
        return []

def get_movie_reviews(IDandNum):
    ID, numRvws = IDandNum
    #data = ia.get_movie_user_reviews(ID, 0)['data']
    #numRvws = int(data['amount'][0]['amount'])
    #print ID, "has", numRvws, "reviews"
    #if (numRvws == 0):
    #    return []
    print "Getting", numRvws, "Reviews at", ID
    numPages = (numRvws-1) / 10 + 1   ## each page has at most 10 reviews  - 1 # -1 needed, since 0-indexed
    listOfListOfRvws = map(lambda i: _getReview(ID, 10*i), xrange(numPages))
    return [rvw for listOfRvws in listOfListOfRvws for rvw in listOfRvws][:numRvws]

def get_review_amount(ID):
    data = ia.get_movie_user_reviews(ID, 0)['data']
    if (data.has_key('amount') and data['amount'][0].has_key('amount')):
        numRvws = int(data['amount'][0]['amount'])
        print ID, "has", numRvws, "reviews"
        return numRvws
    else:
        print ID, 'has 0 review.'
        return 0


def get_movie_infos(ID):
    '''
    id, source, name, tid, description, url
    '''
    print "getting movie info of", ID
    data = ia.get_movie(ID)
    res = {}
    res['id'] = ID
    res['source'] = source
    res['name'] = data['title']
    res['tid'] = 3  # imdb has type id 3
    res['description'] = data.summary()
    res['url'] = ia.urls['movie_main'] % ID
    return res



