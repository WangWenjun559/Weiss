from bs4 import BeautifulSoup
import re
import urllib2
import urllib
import csv
import json
import datetime

main_page = 'http://www.zomato.com'

restaurants = '/pittsburgh/restaurants?sort=best'

numPages = 1

## List that contains urls to each restaurant
placeList = []


## Iterate over the number of pages specified above. Each page has 15 results on it.
for i in range(numPages):

    print "Collecting content from url: " + restaurants

    ## Send http request to url and receive response
    page = urllib2.urlopen(main_page + restaurants)

    ## Convert http response to text
    soup = BeautifulSoup(page)

    ## Isolate search results which are contained in <section class="restaurant-results">
    results = soup.findAll('article','search-result')

    for result in results:
        hrefs = result.findAll('a','result-title',href=True)

        for href in hrefs:
            placeList.append(href['href'])

## Comment Fields
comment = []
rating = []
author = []
commentTitle = []
source = "zomato"
commentID = []
date = []

## Words to ignore at beginning of review
ignore = ['Rated','POSITIVE','NEGATIVE']


## Entity Fields
description = []
url = []
entityID = []
tid = 2
entity = []
placeCount = 1
totalPlaces = len(placeList)


def postRequest(url,restaurant_id,limit):
    params = {'res_id':restaurant_id,'sort':'reviews-dd','limit':limit}

    data = urllib.urlencode(params)
    request = urllib2.Request(url, data)
    response = urllib2.urlopen(request)
    result = response.read()

    data = json.loads(result)

    return data



## Iterate over each restaurant's URL in placeList (list of URLs) and collect reviews from each one
for place in placeList:

    print str(placeCount) + "/" + str(totalPlaces) + " Collecting Reviews from: " + place
    placeCount += 1

    restaurantURL = urllib2.urlopen(place)
    soup2 = BeautifulSoup(restaurantURL)

    ## Grab food types served
    descText = ""
    foodTypes = soup2.findAll('a',{'itemprop':"servesCuisine"})
    numTypes = len(foodTypes)
    counter = 1

    ## Get food types served at restaurant
    for food in foodTypes:
        foodType = food.getText()
        descText += foodType

        if counter < numTypes:
            descText += ", "

        counter += 1

    ## Get restaurant id and name
    entityID_val = soup2.find('div',{'itemprop':'ratingValue'})['data-res-id']
    entity_val = soup2.find('span',{'itemprop':'name'}).getText()

    ## Send post request using entity_id
    response = postRequest('https://www.zomato.com/php/filter_reviews.php',entityID_val,2)

    reviews = response['html'].encode('utf-8')

    soup3 = BeautifulSoup(reviews)

    date_vals = soup3.findAll('time',{'itemprop':'datePublished'}) # grab value of key = datetime

    reviewID_vals = soup3.findAll('div','res-review-body clearfix') # grab value of key = data-review-id
    review_vals = soup3.findAll('div','rev-text')
    reviewTitle_vals = [None] * len(review_vals) # No title to review on Zomato
    author_vals = soup3.findAll('span','left mr5') # use .getText() to get text content of tag


    for i in range(len(review_vals)):
        ## Comment Fields
        review = review_vals[i].getText().strip()

        ## deal with reviews beginning with unwanted content
        startingPhrase = -1
        counter = 0
        for word in ignore:
            if review.startswith(word,0,len(word)):
                startingPhrase = counter
            counter += 1

        if startingPhrase > -1:
            review = re.sub(ignore[startingPhrase] + '(.+)\n', '',review).strip()
        comment.append(review)
        rating.append(None)
        author.append(author_vals[i].getText())
        commentTitle.append(None)
        commentID.append(reviewID_vals[i]['data-review-id'])
        
        datetimeStamp = date_vals[i]['datetime'].split(' ')
        dateStamp = datetimeStamp[0]
        date.append(dateStamp)

        ## Entity Fields
        entityID.append(entityID_val)
        entity.append(entity_val)
        rating.append(-1)
        url.append(place)
        description.append(descText)


## Print out stats
print "Places " + str(len(placeList))
print "Reviews " + str(len(comment))


## Create json
commentJSON = []
commentByEntity = []
entityJSON = []

## Format comments
for i in range(len(date)):
    commentDict = {"body":comment[i],"rating":rating[i], \
        "author":author[i],"title":commentTitle[i], \
        "source":source,"id":entityID[i],"time":date[i]}
    commentByEntity.append(commentDict)

    if i+2 < len(entityID):
        if (entityID[i] != entityID[i+1]):
            commentJSON.append(commentByEntity)
            commentByEntity = []

## Format entities
uniqueEntities = set(entityID)
for nameID in uniqueEntities:
    index = entityID.index(nameID)
    entityDict = {"description":description[index],"url":url[index], \
        "id":nameID,"tid":2,"name":entity[index],"source":source}
    entityJSON.append(entityDict)

## Write the two jsons
today = datetime.datetime.now()
year = today.year
month = today.month
day = today.day

## Create date stamp string
dateStamp = str(year) + "-" + str("%02d" % (month)) + "-" + str("%02d" % (day))

## write comments json
with open('urbanspoon_comments_' + dateStamp + '.json','w') as output1:
    json.dump(commentJSON, output1)

## Write entity json
with open('urbanspoon_entities_' + dateStamp + '.json','w') as output1:
    json.dump(entityJSON, output1)