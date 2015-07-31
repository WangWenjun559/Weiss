# -*- coding: utf8 -*-
'''
A python package which contains different methods for chooseing a 
representative comment from a list of comments.

Current Methods:
    random - chooses a random comment
    sentiment   - chooses comment with highest/lowest sentiment score
    pageRankComment - creates a graph from similar words within comments and then 
                        runs page rank. Chooses comment with highest page rank.

Author: Wenjun Wang & Austin Ankney
Date: July 15, 2015

Usage:
import the package (comment_select) and choose the specific method 
(listed above) you would like to use.

TODO<wenjunw@cs.cmu.edu>:
Tune the pagerank thing, threshold for building edges 
(length normalization, tfidf similarity, cosine similarity)
'''

from igraph import *
from reranker import MMR
from operator import attrgetter
import nltk
import random
import string
import math


def random_comment(comment_list, num):
    """Choose random comments from a list of comment

    Args:
        comment_list: A list of comments
        num: number of comments to pick

    Return:
        random_list: A list of random selected comments
    """
    rnd_idx = set()
    random_lst = []
    num = min(num,len(comment_list))
    count = 0
    while count < num:
        rnd_num = random.randint(0,num_comments-1)
        if rnd_num not in rnd_idx:
            random_lst.append(comment_list[rnd_num])
            rnd_idx.add(rnd_num)
            count += 1
    return random_lst


def sentiment(sentiment, comment_list, num, rerank=True):
    """Choose comments based on their sentiment scores

    Args:
        sentiment: value can be 'positive' or 'negative'
        comment_list: A list of comments, each comment is a tuple
                      Format: (comment id, sentiment score, comment)
                      E.g: (1314,3,'I like it!')
        num: number of comments to pick

    Return:
        candidate_list: A list of selected comments
    """
    if rerank == True:
        num = min(int(num*1.5),len(comment_list))
    else:
        num = min(num,len(comment_list))
    candidate_list = []
    
    # Normalize sentiment score
    for comment in comment_list:
        length = len(nltk.word_tokenize(comment.sentence))
        comment.rating /= length
    
    if sentiment.lower()[:3] == 'pos':
        comment_list = sorted(comment_list, key=attrgetter('rating'),reverse=True)
    elif sentiment.lower()[:3] == 'neg':
        comment_list = sorted(comment_list, key=attrgetter('rating'))
    else:
        print "Please specify sentiment correctly, positive or negative?"
        raise ValueError
    
    candidate_list = comment_list[:num]
    if rerank == True:
        candidate_list = MMR(candidate_list)
    
    return candidate_list


def pagerank_comment(comment_list, num, rerank=True):
    """Choose comments based on pagerank of comment graph

    Args:
        comment_list: A list of comment
        num: number of comments to pick
    
    Return:
        candidate_list: A list of selected comments
    """
    if rerank == True:
        num = min(num*2,len(comment_list))
    else:
        num = min(num,len(comment_list))
    g = create_graph(comment_list)
    scorelist = pagerank_scores(g,num)
    for i in xrange(0,len(comment_list)):
        comment_list[i].rating = scorelist[i]
    candidate_list = comment_list[:num]
    if rerank == True:
        candidate_list = MMR(candidate_list)

    return candidate_list


def clean_word(comment):
    """Strip all the punctuations in a comment

    Arg:
        comment: original comment

    Return:
        comment with punctuation stripped
    """
    table = string.maketrans("","")
    return comment.translate(table, string.punctuation)


def remove_stop_words(wordlist):
    """Remove stopwords in a wordlist

    Arg:
        wordlist: A list of words

    Return:
        new_wordlist: A list of words without stopwords
    """
    new_wordlist = []

    for word in wordlist:
        if not word.decode('utf-8') in nltk.corpus.stopwords.words('english'):
            new_wordlist.append(word)

    return list(set(new_wordlist))


def remove_numbers(wordlist):
    """Remove numbers in the wordlist

    Arg:
        wordlist: a list of words

    Return:
        new_wordlist: a list of words without any number
    """
    new_wordlist = []

    for word in wordlist:
        if not re.search('\d+', word):
            new_wordlist.append(word)

    return list(set(new_wordlist))


def intersection(wordlist1, wordlist2):
    """Calculate number of intersection words between two comments

    Args:
        comment1, comment2: two wordlists

    Return:
        overlap: number of common words in both wordlists
    """
    snowball = nltk.SnowballStemmer("english")
    #wordlist1 = clean_word(comment1.sentence)
    #wordlist2 = clean_word(comment2.sentence)
    wordlist1 = nltk.word_tokenize(wordlist1.lower())
    wordlist2 = nltk.word_tokenize(wordlist2.lower())
    wordlist1 = remove_stop_words(wordlist1)
    wordlist2 = remove_stop_words(wordlist2)
    wordlist1 = [snowball.stem(t) for t in wordlist1]
    wordlist2 = [snowball.stem(t) for t in wordlist2]
    #wordlist1 = remove_numbers(wordlist1)
    #wordlist2 = remove_numbers(wordlist2)
    
    norm = math.log(len(wordlist1)) + math.log(len(wordlist2))
    overlap = len(list(set(wordlist1) & set(wordlist2)))/norm

    return overlap


def create_graph(commentList):
    """Build a graph of a list of comments

    Arg:
        commentList: a list of comments

    Return:
        g: the graph of the comments
    """
    print "------Create Graph------"
    g = Graph()
    g.add_vertices(len(commentList))

    ## add edges
    count = 1
    scores = []
    for i in xrange(len(commentList)):
        for j in xrange(len(commentList)):
            #print count
            count += 1
            if not i == j and g.are_connected(i,j) is False:
                intersect = intersection(commentList[i].sentence,commentList[j].sentence)
                scores.append(intersect)
                #if intersect > 0.15:
                    #g.add_edge(i,j)

    scores.sort()
    threshold = scores[int(1/3*len(scores))]
    for i in xrange(len(commentList)):
        for j in xrange(len(commentList)):
            #print count
            count += 1
            if not i == j and g.are_connected(i,j) is False:
                if intersect > threshold:
                    g.add_edge(i,j)

    return g


def pagerank_scores(graph, num):
    """Pick top (num) comments with highest pagerank scores

    Args:
        graph: a graph of comments
        num: number of comments to pick

    Return:
        nodes: a list of selected comments
    """
    print "------Run PageRank------"
    pageRank = graph.pagerank()
    return pageRank
