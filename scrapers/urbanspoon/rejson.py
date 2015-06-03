import json

with open('urbanspoon_entities_2015-5-29.json','rb') as jsonfile:
    d = json.load(jsonfile)

## Loop through json and add source field
for record in d:
    record['source'] = "urbanspoon"

with open('urbanspoon_entities_' + '2015-05-29' + '.json','w') as output1:
    json.dump(d, output1)