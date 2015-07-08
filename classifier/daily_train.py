"""
This file builds a model from training data, which can be incorporated into daily pipeline.
===========================================================================================

TODO(wenjunw@cs.cmu.edu):
- change the path of training file, its transformed feature file, and the model file
  currently these files are in the same directory as this python script.
- In the feature, the parameter values of the SVM classifier may be modified

Usage: python daily_train.py 

Author: Wenjun Wang
Date: June 28, 2015
"""
from train import Train
from typeTrain import *
from liblinearutil import *
from sklearn.externals import joblib

import time

def main():
    ### Train Wenjun's classifier
    # Name of files needed when training a model
    date = time.strftime('%Y-%m-%d')
    train_file = 'training' # name of original training file
    feature_file = 'models/training_file_'+date # name of transformed training file
    feature_output = 'models/features_'+date # name of feature file
    stpfile = 'english.stp' # english stopwords file
    feature_arg = '-uni -pos2 -stem -stprm' # types of features need to extract

    log = open('models/training_log','a') # log file
    log.write('Feature Arguments: %s\n-------------------------------\n'% feature_arg)

    # Create appropriate input file for LibLINEAR (SVM)
    training = Train(train_file, stpfile, feature_output, feature_file, feature_arg)
    training.convert_file()
    # Use LibLINEAR to train the model and save the model
    y, x = svm_read_problem(feature_file)
    m = train(y, x, '-c 1 -s 1 -B 1 -e 0.01 -v 5 -q')
    save_model('models/model_'+date, m)

    ### Train Austin's classifier
    tt = TypeTrain('models/type_model_' + date)
    tt.train()


if __name__ == '__main__':
    main()
