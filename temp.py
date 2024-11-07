import json

FileLocation = '/Users/olavvanr/Documents/DVG_Model.bim'

with open(FileLocation, 'r') as file:
    data = json.load(file)
    print(data)
    