"""
This is a demo about how to use LibLINEAR to do the prediction
"""
from test import Test

# Example query
query = 'What do people think of ?'
# Do the prediction
test = Test()
p_label = test.classify(query)
print p_label