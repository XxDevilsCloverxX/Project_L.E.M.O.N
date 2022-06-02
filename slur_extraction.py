import csv  #used to extract a csv of slurs and insults

slurs = set() #set of unique words that will be used for lookups to prevent misbehavior

#open a csv and store the data as a set:
with open('Terms-to-Block.csv', 'r') as csvfile:
    #create csvreader
    csvreader = csv.reader(csvfile)
    #get the rows from the reader
    for row in csvreader:
        #strip the commas from the csv and access the words, update word to the set of slurs
        slurs.update([row[0].strip(',').lower()])
