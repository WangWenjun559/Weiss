'''
This script takes a list of comments, finds the word overlap between comments and builds
a graph based on the overlaps. The pagerank of the graph is then calculated, and the
comment with the highest pagerank is chosen as the most important comment.

Author: Austin
Date: 6/5/15

'''

from igraph import *
import nltk
from nltk.corpus import stopwords
import re

text1 = '''An off day on the lunch buffet?. I usually like the buffet here \
(not a frequent visitor, but I've had it before), and today it just \
wasn't the best. The first pizzas that were put out were fresh and good, \
but the third one that was brought out was really dark, and it tasted like \
yesterday's leftovers reheated... I couldn't even eat it... it was horrible. \
The deep fried zucchini was O.K., but it was kinda dry, so I put a little red \
sauce on it that I took from the rigatoni pasta on the buffet. The marinara \
sauce wasn't brought out until the zucchini plate was already empty, and then \
they replaced the empty plate with deep fried mushrooms, and some of the \
mushrooms were still cold on the inside. It took 45 minutes before any Italian \
hoagies arrived on the buffet, and I was sadly disappointed because they were \
cold and not cooked enough on the inside, and just didn't taste good. I also \
should mention that there were some dirty plates on the buffet too, like somebody \
didn't wash them properly. Also, I was hoping for maybe some wedding soup on the \
buffet, but they didn't have any. And lastly, the pieces of garlic bread were \
too big... I think they should be cut into smaller pieces. I ended up getting \
two big pieces because they weren't cut properly and stuck together, which was \
about 3/4ths more bread than I wanted. I'll come back again some day, but I \
really hope they step it up a bit, since today was kind of an off-day. At least \
the cost wasn't too bad... $9.00 for all you can eat.'''

text2 = '''On a quest for the BEST!. The numbers on this place are awesome (a 90%+). \
I guess I can understand it for some people, but not for me. The food was adequate, \
it came hot and quick. The cost was not offensive, the waiter was nice, it was clean \
(albeit a bit out dated). I have nothing to complain about, it was o.k. Obviously, \
people like the place. It's just not for ME. To me it's like every other Italian \
restaurant on every corner, in every neighborhood in Pittsburgh. Italian restaurants \
are to Pittsburgh what Chinese restaurants are to San Francisco, there a scads of them \
and they are all "O.K." To me, Juliano's is not bad, it's just O.K.. Congrats to you \
Juliano's for finding your niche audience, I am just not one of them. I wish you \
continued success. I am going to continue my quest for the BEST. '''

text3 = '''Family enviroment. My lady and I went there on a Saturday night because I \
have heard good things. Just a forewarning, this is not a quiet little Italian bistro... \
It's loud, full of noisy kids and large families. We were seated next to the fountain \
drink machine. My silverware was kind of dirty. I guess I was expecting something with \
a little more comfortable environment. Overall the food and service were good, just \
far from classy or romantic. '''

texts = [text1, text2, text3]

class prChoice():
    def two():
        return 2

def bestComment(comment_list):
    commentList = []

    for comment in comment_list:
        wordList = tokenize(comment)
        noStop = removeStopWords(wordList)
        noNums = removeNumbers(noStop)

        commentList.append(noNums)

    g = createGraph(commentList)

    commentChoice = importantNode(g)
    return commentChoice

def tokenize(text, replace_chars = [',','.','"','\'','(',')','$','?','<','>','=','/']):
    # iterate over list of chars being replaces
    for char in replace_chars:
        text = text.replace(char,'')

    text = text.lower().split(' ')

    return text


def splitSentence(text):
    return text.split('. ')

def splitWord(sentence):
    return sentence.lower().split(' ')

def cleanWord(word):
    table = string.maketrans("","")
    return word.translate(table, string.punctuation)

def removeStopWords(wordList):
    newWordList = []

    for word in wordList:
        if not word in stopwords.words('english'):
            newWordList.append(word)

    return list(set(newWordList))

def removeNumbers(wordList):
    newWordList = []

    for word in wordList:
        if not re.search('\d+', word):
            newWordList.append(word)

    return list(set(newWordList))

def intersection(list1, list2):
    overlap = list(set(list1) & set(list2))
    return overlap

def createGraph(commentList):
    g = Graph()

    g.add_vertices(len(commentList))

    ## add edges
    for i in range(len(commentList)):
        for j in range(len(commentList)):
            if not i == j and g.are_connected(i,j) is False:
                intersect = intersection(commentList[i],commentList[j])
                if len(intersect) > 5:
                    g.add_edge(i,j)

    return g

def importantNode(graph):
    pageRank = graph.pagerank()
    maxPR = max(pageRank)
    node = pageRank.index(maxPR)

    return node

print bestComment(texts)

