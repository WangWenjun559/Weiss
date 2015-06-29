"""
This is a demo about how to use LibLINEAR to do the prediction
"""
from classify import Classifier

# Create an object first, use this object all the time
test = Classifier()
# When a query comes, Example query
query = "Inside Out"
# Do the prediction and get information
plausible = set([7])
p_label = test.action_info(query,plausible)
print p_label