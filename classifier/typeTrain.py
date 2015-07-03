import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
import nltk
import MySQLdb
import ConfigParser
from feature import hashit, list2Vec
import time

class TypeTrain():
    def __init__(self,model_save_path='/',dictionary_size=1000):
        self.cursor = self._initDB()
        self.dictionary_size = dictionary_size
        self.path = model_save_path
        self.date = time.strftime('%Y-%m-%d')
    

    def _initDB(self):
        '''
        Initializes connection to the DB
        '''
        ## Read config file
        config = ConfigParser.ConfigParser()
        config.read("config.ini")

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

        return cursor


    def sql2list(self,list_sql_queries):
        '''
        Takes a list of sql queries and returns results in a form of list of lists.
        Each sublist contains text belonging to the same class.
        '''
        texts = []

        for q in list_sql_queries:
            cursor = self.cursor
            cursor.execute(q)
            n = cursor.fetchall()

            classes = []
            for text in n:
                classes.append(text[0])

            texts.append(classes)

        return texts


    def featureMatrix(self,list_text):
        '''
        Creates a matrix where each sublist represents rows.
        '''
        x = []
        y = []
        label = 1
        for comments in list_text:
            for comment in comments:
                x_i = hashit(comment)
                y.append(label)
                x.append(x_i)
            label += 1

        return x, y


    def train(self):
        '''
        ## -- How to predict -- ##
        Wenjun start prediction
            query = "blah blah"
            q = list2vec(hashit(q)) 
            clf2 = joblib.load('nb')
            print(clf2.predict(q)) # <--- returns type id
        '''
        cursor = self.cursor

        limit = 100
        sqls = ["SELECT body FROM comment JOIN entity ON comment.eid = entity.eid WHERE entity.tid=1 ORDER BY time DESC LIMIT " + str(limit),
            "SELECT body FROM comment JOIN entity ON comment.eid = entity.eid WHERE entity.tid=2 ORDER BY time DESC LIMIT " + str(limit),
            "SELECT body FROM comment JOIN entity ON comment.eid = entity.eid WHERE entity.tid=3 ORDER BY time DESC LIMIT " + str(limit)]

        print "training model"
        comments = self.sql2list(sqls)
        x, y = self.featureMatrix(comments)
        X = list2Vec(x)
        Y = list2Vec(y)

        q = "Let's talk about food."
        q_vec = list2Vec(hashit(q))

        ## Precicting
        print "Classifying"
        clf = MultinomialNB(alpha=1.0, class_prior=None, fit_prior=True)
        clf.fit(X, Y)
        joblib.dump(clf,'models/type_model_' + self.date ,compress=9)
        




