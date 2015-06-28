"""
TODO(wenjunw@cs.cmu.edu):
- Consider encoding issue
"""
import nltk

def stopword(stpfile):
    stopwords = set()
    for line in open(stpfile):
        stopwords.add(line.strip())
    return stopwords

def parse_options(options=''):
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
    features = set()

    token_list = nltk.word_tokenize(query.lower())
    if feature_arg['POS'] == False:
        if feature_arg['stopword_removal'] == True:
            token_list = stopword_removal(token_list, stopwords)
        if feature_arg['stem'] == True:
            token_list = stemming(token_list)
    else:
        tag_list = nltk.pos_tag(token_list)
        if feature_arg['stopword_removal'] == True:
            tag_list = stopword_removal(tag_list, stopwords)

    if feature_arg['unigram'] == True:
        _ngram(1, token_list, features)
    if feature_arg['POSbigram'] == True:
        _POSngram(2, tag_list, features)

    return features

"""
Currently, only implements unigram
"""
def _ngram(n, token_list, features):
    if n == 1:
        for t in token_list:
            features |= set([t])

"""
Currently, only implements POSbigram
"""
def _POSngram(n, tag_list, features):
    features |= set(['START_'+tag_list[0][1]])
    for i in xrange(0,len(tag_list)-1):
        features |= set([tag_list[i][1]+'_'+tag_list[i+1][1]])
    features |= set([tag_list[-1][1]+'_END'])

def stemming(token_list):
    """Stem all words in the list

    Arg: 
        token_list: tokens of a query

    Return:
        stemmed_tokens: all tokens in the original query will be stemmed
    """
    porter = nltk.PorterStemmer()
    stemmed_tokens = [porter.stem(t) for t in token_list]

    return stemmed_tokens

def stopword_removal(token_list, stopwords):
    """Remove all stopwords in a sentence

    Arg:
        token_list: tokens of a query

    Return:
        clean_sentence: stopwords-removed sentence, string format    
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