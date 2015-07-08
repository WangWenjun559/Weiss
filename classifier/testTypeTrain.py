from typeTrain import *
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from feature import hashit, list2Vec

query = "Let's talk about news"
q = list2Vec(hashit(query))

clf1 = joblib.load('models/type_model_d1000_l1000')
print(clf1.predict(q))

clf2 = joblib.load('models/type_model_d10000_l1000')
print(clf2.predict(q))

clf3 = joblib.load('models/type_model_d100000_l1000')
print(clf3.predict(q))

clf4 = joblib.load('models/type_model_d1000_l10000')
print(clf4.predict(q))

clf5 = joblib.load('models/type_model_d10000_l10000')
print(clf5.predict(q))

clf6 = joblib.load('models/type_model_d100000_l10000')
print(clf6.predict(q))