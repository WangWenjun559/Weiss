"""
This is a demo about how to use LibLINEAR to do the prediction
"""
from classify import Classifier

# Create an object first, use this object all the time
test = Classifier()
# When a query comes, Example query
query = "Let's talk about Jurassic Park"
# Do the prediction and get information
plausible = set([1,3,4,5,6,7,8])
p_label = test.action_info(query,plausible)
print p_label
