"""
This is a demo about how to use LibLINEAR to do the prediction
"""
from classify import Classifier

# Example query
query = "Inside Out"
# Do the prediction
test = Classifier()
plausible = set([7])
p_label = test.action_info(query,plausible)
print p_label