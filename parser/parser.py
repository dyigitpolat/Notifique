# -*- coding: utf-8 -*-
import sys
import urllib2
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient

def saveEmails(filename):
    with open(filename, 'r') as f:
        for line in f:
            print line

def latinizeString(s):
    s = s.replace(u"ö", "o")
    s = s.replace(u"Ö", "O")
    s = s.replace(u"Ç", "C")
    s = s.replace(u"ç", "c")
    s = s.replace(u"İ", "I")
    s = s.replace(u"ı", "i")
    s = s.replace(u"ü", "u")
    s = s.replace(u"U", "U")
    s = s.replace(u"Ş", "S")
    s = s.replace(u"ş", "s")
    s = s.replace(u"ğ", "g")
    s = s.replace(u"Ğ", "G")

    return s

# saveEmails()
# sys.exit()

url2 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS299.htm'
url3 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS399.htm'

pages = []
cs299 = []
cs399 = []

pages.append(urllib2.urlopen(url2).read())

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
            obj = {"firstName": first_name, "lastName": last_name, "professor": professor, "status": status}
            if count == 0:
                obj['courseInt'] = 0
                cs299.append(obj)
            else:
                obj['courseInt'] = 1
                cs399.append(obj)
        except:
            # print i, "Fail", tds[0].text.encode('utf-8')
            pass
