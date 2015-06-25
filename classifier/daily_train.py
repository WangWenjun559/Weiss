"""
This file builds a model from training data, which can be incorporated into daily pipeline.
===========================================================================================

TODO(wenjunw@cs.cmu.edu):
- change the path of training file, its transformed feature file, and the model file
  currently these files are in the same directory as this python script.
- In the feature, the parameter values of the SVM classifier may be modified

Usage: python daily_train.py 

Author: Wenjun Wang
Date: June 18, 2015
"""
from feature import feature_generator
from feature import convert_file
from liblinearutil import *

import time

def main():
	# Create appropriate input file for LibLINEAR (SVM)
    train_file = 'training' # name of original training file
    feature_file = 'training_file' # name of transformed training file
    feature_output = 'features' # name of feature file
    feature_list = feature_generator(train_file, feature_output)
    convert_file(train_file, feature_list, feature_file)
    # Use LibLINEAR to train the model
    y, x = svm_read_problem('training_file')
    m = train(y, x, '-c 2 -s 5 -B 1 -e 0.01 -v 5 -q')
    date = time.strftime("%Y-%m-%d")
    save_model('model_'+date, m)

if __name__ == '__main__':
    main()
