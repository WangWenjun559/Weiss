# -- coding: utf-8 --

from bs4 import BeautifulSoup
import re
import urllib2
import urllib
import csv
import json
import datetime
import MySQLdb
import ConfigParser

## Read config file
config = ConfigParser.ConfigParser()
config.read("/home/mingf/Weiss/scrapers/urbanspoon/config.ini")

## Grab values
host = config.get('mysql', 'host')
user = config.get('mysql', 'user')
passwd = config.get('mysql', 'password')
db = config.get('mysql', 'db')

## First grab a list of all entities and comments
# Connect to database
db = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db)

# Create cursor which is used later
cursor = db.cursor()

# Dicts to contain query results
all_entities = {}
entity_comments = []

# Grab all entity id's and eid's
cursor.execute("SELECT eid,id FROM entity WHERE tid=2")

# Add records which link eid's to id's
for item in cursor.fetchall():
    all_entities[item[1]] = int(item[0])


main_page = 'http://www.zomato.com'

restaurants = '/pittsburgh/best-restaurants'
path="/home/mingf/data/"
#path = ''

## Determine the starting page value to begin scraping on
# Finds todays date (also used to create json file name)
today = datetime.datetime.now()
weekday = today.weekday()
startPage = ( weekday * 20 ) + 1 # There are currently 148 pages of results. 7 days of 20 pages give us 140 pages.

## scrape numPages of search results starting on startPage
numPages = 20

## List that contains urls to each restaurant
placeList = []


## Iterate over the number of pages specified above. Each page has 30 restaurants on it.
for i in range(startPage, startPage + numPages):

    ## Changes page number for results
    pagination = "?page=" + str(i)

    ## Assemble url
    url = main_page + restaurants + pagination
    ## Send http request to url and receive response
    page = urllib2.urlopen(url)

    print "Collecting content from url: " + url

    ## Convert http response to text
    soup = BeautifulSoup(page)

    ## Isolate search results which are contained in <section class="restaurant-results">
    results = soup.findAll('article','search-result')

    for result in results:
        hrefs = result.findAll('a','result-title',href=True)

        for href in hrefs:
            placeList.append(href['href'].encode('utf-8'))


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

    ## Converts weird characters ir url to ascii, url safe characters
    safeUrl = urllib2.quote(place,':/')

    ## Try to send http request to url. Skips url if there are any problems
    try:
        restaurantURL = urllib2.urlopen(safeUrl)
    except:
        print "Problem with URL: " + safeUrl
        print "skipping to the next URL"
        continue

    soup2 = BeautifulSoup(restaurantURL)

    ## Tries to grab restaurant data and skips any restaurants where it runs into problems
    try:
        ## Grab food types served
        descText = "FoodType: "
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

        ## Get restaurant id, name, address
        entityID_val = soup2.find('div',{'itemprop':'ratingValue'})['data-res-id']
        entity_val = soup2.find('span',{'itemprop':'name'}).getText()
        entity_address = soup2.find('div',{'itemprop':'address'}).getText()
        entity_address = entity_address.replace('United States','').strip()

        descText += "Address: " + entity_address

        ## Send post request using entity_id
        response = postRequest('https://www.zomato.com/php/filter_reviews.php',entityID_val,200)

        reviews = response['html'].encode('utf-8')

        soup3 = BeautifulSoup(reviews)

        date_vals = soup3.findAll('time',{'itemprop':'datePublished'}) # grab value of key = datetime

        reviewID_vals = soup3.findAll('div','res-review-body clearfix') # grab value of key = data-review-id
        review_vals = soup3.findAll('div','rev-text')
        reviewTitle_vals = [None] * len(review_vals) # No title to review on Zomato
        author_vals = soup3.findAll('span','left mr5') # use .getText() to get text content of tag
    except:
        print "Problem processing content from URL: " + safeUrl
        print "skipping to the next URL"
        continue

    # Grab all csid's belonging to this entity
    cursor.execute("SELECT id FROM comment WHERE eid=" + entityID_val)

    # Add records which link eid's to id's
    for item in cursor.fetchall():
        entity_comments.append(int(item))


    for i in range(len(review_vals)):
        ## Attempts to grab review content, skips reviews where it runs into problems
        try:
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
        except:
            print "Problem with processing review from URL: " + safeUrl
            print "skipping to the next URL"
            continue

        if int(reviewID_vals[i]['data-review-id']) in entity_comments:
            print "review present - skipping to avoid duplicating"
        else:
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
        "source":source,"id":entityID[i],"time":date[i], \
        "csid":commentID[i]}
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
year = today.year
month = today.month
day = today.day


## Create date stamp string
dateStamp = str(year) + "-" + str("%02d" % (month)) + "-" + str("%02d" % (day))

## write comments json
with open(path + source + '_comments_' + dateStamp + '.json','w') as output1:
    json.dump(commentJSON, output1)

## Write entity json
with open(path + source + '_entities_' + dateStamp + '.json','w') as output1:
    json.dump(entityJSON, output1)
