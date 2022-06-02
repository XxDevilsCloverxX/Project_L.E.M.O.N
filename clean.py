import csv

"""
This program will clean a csv file of repeated terms, and return a .txt file of the unique terms
"""

word_set= set()

with open('Terms-to-Block.csv', "r") as csvfile:
    with open('cleaned.txt', 'w') as output:
        #create csvreader
        csvreader = csv.reader(csvfile)
        #get the rows from the reader
        for row in csvreader:
            #strip the commas from the csv and access the words, update word to the set of slurs
            word_set.update([row[0].replace(',', "").replace(" ", "").lower()])
        for slur in word_set:
            output.write(f"{slur},\n")
print("cleaned.txt is written")
csvfile.close()
output.close()
