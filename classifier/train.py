import pickle
import time

from feature import *

class Train(object):
    def __init__(self, train_file, stpfile, features, feature_file, options=''):
        self.stopwords = stopword(stpfile)
        self.feature_arg = parse_options(options)
        self.train_file = train_file
        self.features = features
        self.feature_file = feature_file
        self.feature_list = self._train_feature()

    def _train_feature(self):
        feature_set = set()
        output = open(self.features, 'w')
        for line in open(self.train_file):
            label, query = line.split('\t')
            features = feature_generator(query, self.stopwords, self.feature_arg)
            feature_set |= features

        feature_list = list(feature_set)
        pickle.dump(feature_list, output)

        return feature_list

    def convert_file(self):
        """Transform original training file to the format required by LibLINEAR

        Need:
            self.train_file: the name of the original training file
            self.feature_list: a list of unique features generated by function _train_feature
            self.feature_file: the name of the final transformed file

        Return:
            no return, create a new file, the transformed file
        """
        to_write = []
        for line in open(self.train_file):
            label,query = line.split('\t')
            feature_string = self._convert_query_to_string(query)
            feature_string = label + feature_string + '\n'
            to_write.append(feature_string)
        to_write_string = ''.join(to_write)

        output = open(self.feature_file, 'w')
        output.write(to_write_string)
        output.close()

    def _convert_query_to_string(self, query):
        """Convert each query in the training file to the format required by LibLINEAR

        Args and Need: 
            query: the raw query, like 'What do people think of ?'
            self.feature_list: a list of unique features generated by function _train_feature
    
        Return:
            Transformed query in string format
        """
        features = feature_generator(query, self.stopwords, self.feature_arg)
        onerow = set()
        for f in features:
            onerow.add(' %s:%s' % (str(self.feature_list.index(f)+1), str(1)))
        onerow = list(onerow)
        onerow.sort(key=lambda feature:int(feature.split(':')[0]))
        feature_string = ''.join(onerow)
    
        return feature_string
