# -*- coding: utf-8 -*-
import sys
import urllib2
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient

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

    for person in people:
        dataid = collection.insert_one(person).inserted_id

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
db = client.notifique # Change the database name
collection = db['n20161']
collection.delete_many({})
saveEmails('./students.txt', collection)


url2 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS299.htm'
url3 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS399.htm'

pages = []
people = []

pages.append(urllib2.urlopen(url2).read())
pages.append(urllib2.urlopen(url3).read())

for page in pages:
    soup = BeautifulSoup(page, 'html.parser')
    # print soup

    trs = soup.findAll('tr')

    # sys.exit()
    for i in xrange(len(trs)):
        tds = trs[i].findAll('td')
        try:
            num = int(tds[0].text.encode('utf-8'))
            first_name = str(tds[1].text.encode('utf-8')).rstrip().replace('\n', '').replace('\r', '').replace('  ', ' ')
            last_name = str(tds[2].text.encode('utf-8')).rstrip().replace('\n', '')
            professor = str(tds[3].text.encode('utf-8'))
            status = str(tds[4].text.encode('utf-8'))
            count = num
            obj = {"firstName": first_name, "firstNameLatin": latinizeString(first_name),
                "lastNameLatin": latinizeString(last_name), "lastName": last_name,
                "professor": professor, "status": status}
            if count == 0:
                obj['courseInt'] = 0
                people.append(obj)
            else:
                obj['courseInt'] = 1
                people.append(obj)
        except:
            # print i, "Fail", tds[0].text.encode('utf-8')
            pass

print len(people)

for person in people:
    # print person
    found = collection.find({'firstNameLatin': person['firstNameLatin'], 'lastNameLatin': person['lastNameLatin']})
    print person['firstNameLatin'], person['lastNameLatin']

    dbobj = collection.update({'firstNameLatin': person['firstNameLatin']}, {'$set': person})
    # print dbobj[0]
