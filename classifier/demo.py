"""
This is a demo about how to use LibLINEAR to do the prediction
"""
from classify import Classifier

# Example query
query = "Let's talk about action movies"
# Do the prediction
test = Classifier()
p_label = test.action_info(query)
print p_label