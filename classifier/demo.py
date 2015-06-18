"""
This is a demo about how to use LibLINEAR to do the prediction
==============================================================

Usage: python demo.py 

Author: Wenjun Wang
Date: June 18, 2015
"""
import pickle

from liblinearutil import *
from feature import convert_query

# Read training file
#y, x = svm_read_problem(path_to_training_file)
# Train and save model
#m = train(y, x, '-c 1 -s 1 -B 1 -e 0.01 -v 5 -q')
#save_model(name_of_model_file,m)
# Load the trained model, which is in the same directory as this script
m = load_model(path_to_saved_model)
# Load feature file, which is also in the same directory
infile = open(path_to_feature_file)
feature_list = pickle.load(infile)
# Class labels
y = [1,2,3,4,5]
# Example query
query = 'next entity'
# Convert query
x = convert_query(query, feature_list, 'test')
# Do the prediction
p_label, p_val = predict(y, x, m, '-b 0')
print p_label #predict class/label
print p_val #svm value for each class/label
