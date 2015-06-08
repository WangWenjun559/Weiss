'''
A python package which contains different methods for chooseing a 
representative comment from a list of comments.

Current Methods:
    randomComment   - chooses a random comment
    leadComment     - chooses the first/lead comment
    walkThrough     - ??
    pageRankComment - creates a graph from similar words within comments and then 
                        runs page rank. Chooses comment with highest page rank.

Author: Austin Ankney & Wenjun Wang
Date 6/7/2015

Usage:
import the package (commentChooser) and choose the specifc method 
(listed above) you would like to use.
'''

## Import list
#import _commentChooser
import nltk
from igraph import *
import nltk
from nltk.corpus import stopwords
import re
import random

## Chooses random comment
def randomComment(comment_list):
    num_comments = len(comment_list)
    comment_index = random.randint(0,num_comments-1)

    return comment_list[comment_index]


## Chooses first/lead comment
def leadComment(comment_list):
    return comment_list[0]


## Choose comment based on page rank of comment graph
def pageRankComment(comment_list):
    commentList = []

    for text in comment_list:
        wordList = tokenize(text)
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

