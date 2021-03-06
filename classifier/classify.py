"""
This script does action classification and extract keywords from the incoming query.
====================================================================================

TODO(wenjunw@cs.cmu.edu):
- Reconsider the type words
- Consider action 6,7,8 in one query
- log force change of aid
- update _type_recognition function

Usage: refer to demo.py

Author: Wenjun Wang<wenjunw@cs.cmu.edu>
Date: July 1, 2015

"""
import pickle
import datetime
import nltk

from feature import *
from liblinearutil import *
from sklearn.externals import joblib

class Classifier(object):
    def __init__(self):
        """
        All variables which would be used by every query classification and parsing are listed here.
        Only need to create Classifier object once, i.e. initialize once
        """    
        self.action_model, self.type_model = self._get_model()
        self.stopwords = stopword('english.stp')
        self.feature_arg = parse_options('-uni -pos2 -stem -stprm')
        self.feature_list = self._get_feature_list()
        self.type_words = self._set_type_words()
        self.labels = [21,22,23,24,5,6,7]

    def _get_model(self):
        """Load model

        This function is called during initialization

        Return: models, action model and type model
        """
        date = str(datetime.date.today())
        m1 = load_model('models/model_'+date)
        if m1 == None:
            date = str(datetime.date.fromordinal(datetime.date.today().toordinal()-1))
            m1 = load_model('models/model_'+date)
        m2 = joblib.load('models/type_model_'+date)

        return m1, m2

    def _get_feature_list(self):
        """Load feature file

        This function is called during initialization

        Return: Feature list
        """
        date = str(datetime.date.today())
        try:
            infile = open('models/features_'+date)
        except IOError:
            date = str(datetime.date.fromordinal(datetime.date.today().toordinal()-1))
            infile = open('models/features_'+date)

        feature_list = pickle.load(infile)
        return feature_list

    def _convert_query_to_dictionary(self, query):
        """Convert each user query to the format (refer to train.py) required by LibLINEAR

        This function is called by self._classify(query)

        Args and Need: 
            query: the raw query, like 'What do people think of ?'
            self.feature_list: a list of unique features generated by function feature_generator
    
        Return:
            Convert user's query: store information in a dictionary, 
            which is a member of a list. 
        """
        features = feature_generator(query, self.stopwords, self.feature_arg)
        onerow = {}
        for f in features:
            try:
                onerow[self.feature_list.index(f)+1] = 1
            except ValueError:
                pass

        return [onerow]

    def _classify(self, query):
        """Does query classification, which decides which action need to be taken

        This function is called by self.action_info

        Return: Action id
        """
        x = self._convert_query_to_dictionary(query)
        p_label, p_val = predict(self.labels, x, self.action_model, '-b 0')
        # print p_val
        if p_val[0][int(p_label[0])-1] == 0:
            p_label[0] = -1

        return int(p_label[0])

    def action_info(self, query, plausible):
        """API function in this script. Gives all info of an action

        This is the only function which will be called outside this script.

        Args:
            query: query need to classify and parse
            plausible: a set of plausible actions at current step

        Return:
            arguments: a dictionary contains all the info needed by calling function

        """
        arguments = {}
        temp = -1
        self._type_recognition(query, arguments)
        if arguments['aid'] == 8:
            temp = 8
        # State System Initiative and State Type Selected
        if plausible <= set([5,7,8]):
            q = list2Vec(hashit(query))
            arguments['tid'] = self.type_model.predict(q)[0]
            self._entity_recognition(query,arguments)
            if 'keywords' in arguments:
                arguments['aid'] = 7
            else:
                if temp != 8:
                    if 5 in plausible:
                        arguments['aid'] = 5
                    else:
                        arguments['aid'] = -1
        # State Entity Selected and State All Selected
        else:
            arguments['aid'] = self._classify(query)
            if arguments['aid'] == 7:
                if temp == -1:
                    q = list2Vec(hashit(query))
                    arguments['tid'] = self.type_model.predict(q)[0]
                self._entity_recognition(query,arguments)
                if 'keywords' not in arguments:
                    if temp == -1:
                        arguments['aid'] = 5
                    else:
                        arguments['aid'] = 8
            if arguments['aid'] == 2 and 2 not in plausible:
                arguments['aid'] = 1

        return arguments

    def _entity_recognition(self, query, arguments):
        """Parse query and extract keywords

        This function is called by self.action_info

        Args:
            query: query needs to be parsed
            arguments: info needs to be updated
        """
        tokens = nltk.word_tokenize(query)
        tags = nltk.pos_tag(tokens)
        entities = nltk.chunk.ne_chunk(tags)
        if 'aid' not in arguments:
            arguments['aid'] = 7
        #print entities

        tuples = []
        trees = []
        for i in entities:
            if isinstance(i,tuple):
                if ((i[1][:2] == 'NN' or i[1][:2] == 'JJ')
                    and i[0].lower() not in self.stopwords 
                    and i[0].rstrip('s') not in self.type_words['movie']
                    and i[0].rstrip('s') not in self.type_words['article'] 
                    and i[0].rstrip('s') not in self.type_words['restaurant']):
                    tuples.append(i[0])
            elif isinstance(i,nltk.tree.Tree):
                phrase = []
                for element in i:
                    if element[0].lower() not in self.stopwords:
                        phrase.append(element[0])
                if len(phrase) > 0:
                    trees.append(' '.join(phrase))

        if len(trees) > 0:
            arguments['keywords'] = '#'.join(trees).strip('#')
        elif len(tuples) > 0:
            arguments['keywords'] = '#'.join(tuples).strip('#')
    
    def _set_type_words(self):
        """Initialize synonymy words of movie, article and restaurant

        This function is called during initialization

        Return: A dictionary, key: movie, article, restaurant, value: their synonymy words
        """
        topic = {}
        topic['movie'] = set(['cinema','show','film','picture','cinematograph',
            'videotape','flick','pic','cine','cinematics','photodrama',
            'photoplay','talkie','flicker','DVD','movie'])
        topic['article'] = set(['report','announcement','story','account',
            'newscast','headlines','press','communication','talk','word',
            'communique','bulletin','message','dispatch','broadcast',
            'statement','intelligence','disclosure','revelation',
            'gossip','dispatch','news','article'])
        topic['restaurant'] = set(['bar','cafeteria','diner','dining','saloon','coffeehouse',
            'canteen','chophouse','drive-in','eatery','grill','lunchroom','inn','food',
            'pizzeria','hideaway','cafe','charcuterie','deli','restaurant'])
        return topic

    def _type_recognition(self, query, arguments):
        """Identity the type of the topic: movie, article or restaurant

        This is called by self.action_info

        Args:
            query: query needs to be parsed
            arguments: info needs to be updated

        """
        tokens = nltk.word_tokenize(query)
        arguments['aid'] = 8
        for i in xrange(0,len(tokens)):
            if tokens[i] in self.type_words['article']:
                arguments['tid'] = 1
                break
            if tokens[i] in self.type_words['restaurant']:
                arguments['tid'] = 2
                break
            if tokens[i] in self.type_words['movie']:
                arguments['tid'] = 3
                break
        if 'tid' not in arguments:
            arguments['aid'] = -1
