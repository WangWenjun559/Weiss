"""
This is a demo about how to use LibLINEAR to do the prediction
"""
from liblinearutil import *

#y, x = svm_read_problem('../training_file')
#m = train(y, x, '-c 1 -s 1 -B 1 -e 0.01 -v 5 -q')
#save_model('model',m)
m = load_model('model')
y, x = [1,2,3,4,5], [{24:1, 50:1, 71:1, 62:1, 87:1, 96:1}]
p_label, p_val = predict(y, x, m, '-b 0')
print p_label
print p_val