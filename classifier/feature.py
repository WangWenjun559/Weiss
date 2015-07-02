"""
This script extracts features from the query.
=============================================

Usage: 
This file cannot run standalone, the functions will be used in other scripts,
such as "train.py" and "classify.py"

TODO(wenjunw@cs.cmu.edu):
- Consider encoding issue

Author: Wenjun Wang
Date: June 28, 2015

"""
import nltk
import hashlib
import numpy as np

def stopword(stpfile):
    """Reads stopwords from a file and return a set of stopwords
    """
    stopwords = set()
    for line in open(stpfile):
        stopwords.add(line.strip())
    return stopwords

def parse_options(options=''):
    """parse feature options, i.e. which types of features need to extract

    Arg:
        options: a string of feature options in the format like: '-uni -pos2'

    Return:
        feature_arg: a dictionary of feature options, key: feature name, value: True/False
    """
    argv = options.split()
    feature_arg = {}
    feature_arg['unigram'] = False
    feature_arg['POS'] = False
    feature_arg['POSbigram'] = False
    feature_arg['stem'] = False
    feature_arg['stopword_removal'] = False
    for i in xrange(0,len(argv)):
        if argv[i].lower()[:4] == '-uni':
            feature_arg['unigram'] = True
        if argv[i].lower()[:6] == '-pos2':
            feature_arg['POSbigram'] = True
            feature_arg['POS'] = True
        if argv[i].lower()[:6] == '-stprm':
            feature_arg['stopword_removal'] = True
        if argv[i].lower() == '-stem':
            feature_arg['stem'] = True
    return feature_arg

def feature_generator(query, stopwords, feature_arg):
    """Generate a feature set from the query

    Args:
        query: the query need to extract features from
        stopwords: a set of stopwords
        feature_arg: returned by parse_options, 
            contains info of which types of features need to be extract
    Return:
        features: a set of features
    """
    features = set()

    token_list = nltk.word_tokenize(query.lower())
    if feature_arg['POS'] == True:
        token_list = nltk.pos_tag(token_list)
    if feature_arg['stopword_removal'] == True:
        token_list = _stopword_removal(token_list, stopwords)
    if feature_arg['stem'] == True:
        token_list = _stemming(token_list)

    if feature_arg['unigram'] == True:
        _ngram(1, token_list, features)
    if feature_arg['POSbigram'] == True:
        _POSngram(2, token_list, features)

    return features


def _ngram(n, token_list, features):
    """Extract ngram features
    Currently, only implements unigram

    This function is called by feature_generator

    Args:
        n: n=1 unigram, n=2 bigram, n=3 trigram
        token_list: a list of tokens of a query
        features: feature set need to update
    """
    if n == 1:
        for t in token_list:
            if isinstance(t,tuple):
                features |= set([t[0]])
            elif isinstance(t,str):
                features |= set([t])

def _POSngram(n, tag_list, features):
    """Extract POSngram features
    Currently, only implements POSbigram

    This function is called by feature_generator

    Args:
        n: n=1 POSunigram, n=2 POSbigram, n=3 POStrigram
        tag_list: a list of (token, POStag) tuples of the query
        features: feature set need to update
    """
    features |= set(['START_'+tag_list[0][1]])
    if n == 2:
        for i in xrange(0,len(tag_list)-1):
            features |= set([tag_list[i][1]+'_'+tag_list[i+1][1]])
        features |= set([tag_list[-1][1]+'_END'])

def _stemming(token_list):
    """Stem all words in the list

    Arg: 
        token_list: a list of tokens of a query 
            OR a list of (token, POStag) tuples of the query

    Return:
        stemmed_tokens: a list of stemmed tokens of a query
            OR a list of (stemmed_token, POStag) tuples of the query
    """
    porter = nltk.PorterStemmer()
    if isinstance(token_list[0],str):
        stemmed_tokens = [porter.stem(t) for t in token_list]
    elif isinstance(token_list[0],tuple):
        stemmed_tokens = [(porter.stem(t[0]),t[1]) for t in token_list]

    return stemmed_tokens

def _stopword_removal(token_list, stopwords):
    """Remove all stopwords in a sentence

    Arg:
        token_list: a list of tokens of a query 
            OR a list of (token, POStag) tuples of the query

    Return:
        clean_tokens: stopwords-removed version of original token_list
    """
    clean_tokens = []
    while len(token_list) > 0:
        if isinstance(token_list[0],str):
            target = token_list[0].lower()
        elif isinstance(token_list[0],tuple):
            target = token_list[0][0].lower()
        if target in stopwords:
            token_list.pop(0)
        else:
            clean_tokens.append(token_list.pop(0))
    return clean_tokens

def hashit(text, dictionary_size=1000):
        '''
        Takes a sentence, tokenizes it, stems each word, and hashes each word
        based on the dictionary size specified.
        '''
        stemmer = nltk.SnowballStemmer("english", ignore_stopwords=True)
        tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')

        tokens = tokenizer.tokenize(unicode(text, errors='ignore'))
        
        x_i = [0] * dictionary_size

        for token in tokens:
            stemmed = stemmer.stem(token.lower())
            if not stemmed in nltk.corpus.stopwords.words('english') and len(stemmed) > 1:
                hasher = hashlib.sha1()
                hasher.update(stemmed)
                index = int(hasher.hexdigest(), 16) % dictionary_size
                x_i[index] += 1

        return x_i

def list2Vec(word_list):
        '''
        Converts a list into a numpy vector/matrix
        '''
        a = np.array(word_list)
        return a