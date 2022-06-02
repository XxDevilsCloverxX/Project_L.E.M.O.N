import csv

"""
This will read resources from a formatted csv and create a dictionary that
holds 'topic: resources' key-value pairs.
"""

manuals = {}
with open("resources.csv",'r') as foo:
    reader = csv.reader(foo)
    next(reader)    #skip labels
    for value in reader:
        key = value.pop(0)
        manuals[key] = value
