"""
This is a demo about how to use LibLINEAR to do the prediction
"""
import pickle

from liblinearutil import *
from feature import convert_query

# Load the trained model, which is in the same directory as this script
m = load_model('model')
# Load feature file, which is also in the same directory
infile = open('features')
feature_list = pickle.load(infile)
# Class labels
y = [1,2,3,4,5]
# Example query
query = 'What do people think of ?'
# Convert query
x = convert_query(query, feature_list, 'test')
# Do the prediction
p_label, p_val = predict(y, x, m, '-b 0')
print p_label
print p_val