from bs4 import BeautifulSoup
import re
import urllib2
import csv

main_page = 'http://www.urbanspoon.com'

restaurants = '/lb/23/best-restaurants-Pittsburgh'

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
    results = soup.findAll('section','restaurant-results')


    for result in results:
        hrefs = result.findAll('a',href=True)

        for href in hrefs:
            if '/lb/23/best-restaurants-Pittsburgh' in href['href']:
                restaurants = href['href']
            else:
                placeList.append(main_page + href['href'])

## Lists to hold comment data
date = []
author = []
entityID = []
entity = []
commentID = []
comment = []
commentTitle = []
sentiment = []

## Iterate over each restaurant's URL in placeList (list of URLs) and collect reviews from each one
for place in placeList:

    print "Collecting Reviews from: " + place

    restaurantURL = urllib2.urlopen(place)
    soup2 = BeautifulSoup(restaurantURL)
        
    reviews = soup2.findAll('li','comment review')

    for review in reviews:
        ## Grab unix timestampe from data-date attribute in <li class="comment review"
        date_val = review['data-date']

        ## 
        authorID = review['data-user']
        author_val = review.find('a',{'href':'/u/profile/' + authorID},text=True).getText()

        ## Get restaurant id and name
        entityID_val = re.findall(r'\d+',place)[1]
        getEntity = soup2.find('title').getText().split(' - ')[0].strip()
        entity_val = getEntity.encode('utf-8')

        ## Get Review information
        reviewID_val = review['data-comment'].strip()
        reviewTitle_val = review.find('div','title',text=True).getText().encode('utf-8')
        review_val = review.find('div','body').getText().encode('utf-8')

        ## Append data to lists
        date.append(date_val)
        author.append(author_val)
        entityID.append(entityID_val)
        entity.append(entity_val)
        commentID.append(reviewID_val)
        comment.append(review_val)
        commentTitle.append(reviewTitle_val)
        sentiment.append(None)


with open('reviews.csv','wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t')

    ## Write header
    csvwriter.writerow(['Date','Author','entityID','Entity Name','ReviewID','Review Title','Review','Sentiment'])

    for i in range(len(date)):
        csvwriter.writerow([date[i],author[i],entityID[i],entity[i],commentID[i],comment[i],commentTitle[i],sentiment[i]])



