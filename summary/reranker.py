# -*- coding: utf8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from operator import attrgetter

import nltk


def stemming(sentences):
    snowball = nltk.SnowballStemmer("english")
    stemmed_sentences = []
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence.sentence)
        stemmed_tokens = [snowball.stem(t) for t in tokens]
        stemmed_sentences.append(' '.join(stemmed_tokens))
    return stemmed_sentences


def MMR(docs):
    """Use Maximal Marginal Relevance to rerank the comments

    This funtion assumes that the old scores are normalized to [0,1]
    This function assumes that the current scores represent the relevance
    measure of the sentences. For every sentence, the function iterates
    through all sentences with higher scores and computes the similarity
    measure using the provided similarity function. The new score for
    every sentence is computed as follows:
 
    new_score = relevance_weight * relevance - (1-relevance_weight) * similarity
    where
    relevance  = old_score
    similarity = maximum similarity between current sentence and sentences with
                 higher scores

    Args:
        docs: a list of comments

    Return:
        select_lst: a list of reranked comments
    """
    # Setup
    half = (len(docs)+1)/2
    select_lst = [docs.pop(0)]
    candidates = []
    tfidf_vectorizer = TfidfVectorizer()
    relevance_weight = 0.9

    # Start recalculating scores
    while len(select_lst) != half:
        for candidate in docs:
            old_score = candidate.rating

            stemmed_sen = stemming([candidate])
            stemmed_lst = stemming(select_lst)
            tfidf_matrix = tfidf_vectorizer.fit_transform(stemmed_lst)
            target = tfidf_vectorizer.transform(stemmed_sen)
            similarities = cosine_similarity(target,tfidf_matrix).flatten()
            similarities.sort()
            similarity = similarities[-1]
            
            new_score = old_score * relevance_weight - similarity * (1 - relevance_weight)
            candidate.rating = new_score
            
        docs = sorted(docs, key=attrgetter("rating"), reverse=True)
        select_lst.append(docs.pop(0))

    return select_lst
