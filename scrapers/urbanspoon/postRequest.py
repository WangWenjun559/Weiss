import urllib2
import urllib
import json
from bs4 import BeautifulSoup
import datetime

## Comment Fields
comment = []
rating = []
author = []
commentTitle = []
source = "urbanspoon"
commentID = []
date = []


## Post request to retreive comments on 
url = "https://www.zomato.com/php/filter_reviews.php"
values = {'res_id':'17041281','sort':'reviews-dd','limit':'3'}

data = urllib.urlencode(values)
request = urllib2.Request(url, data)
response = urllib2.urlopen(request)
result = response.read()


data = json.loads(result)

html = data['html'].encode('utf-8')

soup = BeautifulSoup(html)



date_vals = soup.findAll('time',{'itemprop':'datePublished'}) # grab value of key = datetime

reviewID_vals = soup.findAll('div','res-review-body clearfix') # grab value of key = data-review-id
review_vals = soup.findAll('div','rev-text')
reviewTitle_vals = [None] * len(review_vals) # No title to review on Zomato
author_vals = soup.findAll('span','left mr5') # use .getText() to get text content of tag

print str(len(review_vals)) + " Reviews"

ignore = ['Rated','POSITIVE','NEGATIVE']

for i in range(len(review_vals)):
    ## Comment Fields
    review = review_vals[i].getText().strip()
    comment.append()
    rating.append(None)
    author.append(author_vals[i].getText())
    commentTitle.append(None)
    commentID.append(reviewID_vals[i]['data-review-id'])

    datetimeStamp = date_vals[i]['datetime'].split(' ')
    dateStamp = datetimeStamp[0].split('-')
    year = int(dateStamp[0])
    month = int(dateStamp[1])
    day = int(dateStamp[2])
    dt = datetime.datetime(year,month,day) - datetime.datetime(1970,1,1)
    date.append(dt.total_seconds())

print comment


# html = '''
# <div class="rev-text">
#     <div class="left">
#         <div title="Poor" class="ttupper fs12px left bold zdhl2 tooltip icon-font-level-3" data-iconr="0">
#             Rated
#         </div>

#         &nbsp;&nbsp;

#     </div>

#     First Off: I'm From Marion County, West Virginia. Well, having let you know that in the title and if you know the Fairmont/Marion Country, WV hot dog scene, you know that you should NEVER put ketchup (let alone OFFER it) on a hot dog. And it should be hot dog SAUCE, never CHILI. All that being said, I found the friendly staff, the bun, the grilled hot dog itself, the hand chopped onions and the delicious french fries all very, VERY good. But not good enough to overcome the fact that there was ketchup offered that could be put on a hot dog and the fact that there was chili, ACTUAL FREAKING CHILI on my hot dog. Russell Yann would go in to cardiac arrest at this place! Bottom line: I'd go back for the fries and have the kielbasa instead.

# </div>'''

# soup = BeautifulSoup(html)

# a = soup.findAll('div','rev-text')

# for item in a:
#     print item
#     print item.find(text=True, recursive=False)


