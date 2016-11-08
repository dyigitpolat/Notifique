# -*- coding: utf-8 -*-
import sys
import urllib2
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Save people's email addresses from already hier text file.
def saveEmails(filename, collection):
    people = []

    with open(filename, 'r') as f:
        for line in f:
            tokens = line.rstrip().split('\t')
            first_name = tokens[0]
            last_name = tokens[1]
            degree = tokens[2]
            email = tokens[3]
            first_name_latin = latinizeString(first_name)
            last_name_latin = latinizeString(last_name)

            obj = {"firstName": first_name, "lastName": last_name, "degree": degree,
                "email": email, "firstNameLatin": first_name_latin, "lastNameLatin": last_name_latin}

            people.append(obj)

    # Insert name, graduation level, and email address into DB.
    for person in people:
        dataid = collection.insert_one(person).inserted_id

# Could come in handy?
def latinizeString(s):
    s = s.replace("ö", "o")
    s = s.replace("Ö", "O")
    s = s.replace("Ç", "C")
    s = s.replace("ç", "c")
    s = s.replace("İ", "I")
    s = s.replace("ı", "i")
    s = s.replace("ü", "u")
    s = s.replace("Ü", "U")
    s = s.replace("Ş", "S")
    s = s.replace("ş", "s")
    s = s.replace("ğ", "g")
    s = s.replace("Ğ", "G")
    return s

host = 'localhost'
port = 27017

client = MongoClient(host, port)
db = client.notifique
collection299 = db['n20161cs299']
collection399 = db['n20161cs399']
# Delete previous records. This is to initialize the DB.
collection299.delete_many({})
collection399.delete_many({})
saveEmails('./students.txt', collection299)
saveEmails('./students.txt', collection399)


url2 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS299.htm'
url3 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS399.htm'

pages = []
people = []

# Two respective pages to read, for CS299 and CS399
pages.append(urllib2.urlopen(url2).read())
pages.append(urllib2.urlopen(url3).read())

count = 0

for page in pages:
    soup = BeautifulSoup(page, 'html.parser')
    trs = soup.findAll('tr')

    for i in xrange(len(trs)):
        tds = trs[i].findAll('td')
        try:
            # Parse the data
            num = int(tds[0].text.encode('utf-8'))
            first_name = str(tds[1].text.encode('utf-8')).rstrip().replace('\n', '').replace('\r', '').replace('  ', ' ')
            last_name = str(tds[2].text.encode('utf-8')).rstrip().replace('\n', '')
            professor = str(tds[3].text.encode('utf-8'))
            status = str(tds[4].text.encode('utf-8'))
            obj = {"firstName": first_name, "firstNameLatin": latinizeString(first_name),
                "lastNameLatin": latinizeString(last_name), "lastName": last_name,
                "professor": professor, "status": status}
            obj['courseInt'] = count
            people.append(obj)
        except:
            pass
    count += 1

for person in people:
    cur = person['courseInt']
    if cur == 0:
        collection299.update({'firstNameLatin': person['firstNameLatin'], 'lastNameLatin': person['lastNameLatin']}, {'$set': person})
    else:
        collection399.update({'firstNameLatin': person['firstNameLatin'], 'lastNameLatin': person['lastNameLatin']}, {'$set': person})
