# -*- coding: utf-8 -*-
import time
import sys
import urllib2
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import sendgrid
import hashlib, binascii
import re

def replaceHtmlParams(template, course, firstName, lastName, oldStatus, newStatus, unsubscribe):
    result = re.sub('\{\{course\}\}', course, template)
    result = re.sub('\{\{firstName\}\}', firstName, result)
    result = re.sub('\{\{lastName\}\}', lastName, result)
    result = re.sub('\{\{oldStatus\}\}', oldStatus, result)
    result = re.sub('\{\{newStatus\}\}', newStatus, result)
    result = re.sub('\{\{unLink\}\}', unsubscribe, result)
    return result

def getStatusString(s):
    d = { 'S': 'Satisfactory', 'U': 'Unsatisfactory', 'E': 'Under Evaluation', 'R': 'Requires Revision', 'F': 'Form from company has not arrived', 'N': 'Report has not been submitted'}

    tokens = map(str.strip, s.split('+'))

    res = ''
    for i in xrange(len(tokens) - 1):
        res += d[tokens[i]] + ' + '

    res += d[tokens[len(tokens) - 1]]

    return res

def sendMail(sg, to, subject, contentPlain, contentHtml, _from='notifique@cgds.me'):
    data = {
      "personalizations": [
        {
          "to": [
            {
              "email": to
            }
          ],
          "subject": subject
        }
      ],
      "from": {
        "email": _from
      },
      "content": [
        {
          "type": "text/plain",
          "value": contentPlain
        },
        {
          "type": "text/html",
           "value": contentHtml
        }
      ]
    }

    response = sg.client.mail.send.post(request_body=data)
    return response

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

def getToken():
    salt = ''.join(map(bin, bytearray(str(os.environ.get('SALT')))))
    timestamp = ''.join(map(bin,bytearray(str(time.time()))))
    dk = hashlib.pbkdf2_hmac('sha256', timestamp, salt, 100000)
    return str(binascii.hexlify(dk))

html_template = open('./email_template.html', 'r').read()
sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

host = 'localhost'
port = 27017
client = MongoClient(host, port)
db = client.notifique
collection = db['n20161'] # Application data
collectionU = db['u20161'] # List of people who unsubscribed
collectionT = db['t20161'] # List of email tokens

token = getToken()
firstName = 'Doğukan Yiğit'
lastName = 'Polat'
email = 'yigit.polat@ug.bilkent.edu.tr'
res = collectionU.find({'email': email})
if res.count() == 0:
    oldStatus = getStatusString('E')
    newStatus = getStatusString('R')
    unsub = {'email': email, 'token': token}
    # @TODO Insert token with email address to db.
    collectionT.insert_one({'email': email, 'token': token})
    url = 'http://cgds.me:5000/notifique?token='
    course = 'CS299'

    # yigit.polat@ug.bilkent.edu.tr
    # cagdas.oztekin@ug.bilkent.edu.tr
    html = replaceHtmlParams(html_template, course, firstName, lastName, oldStatus, newStatus, url + token)
    sendMail(sg, email, 'Your {0} report status changed!'.format(course), 'Greetings {0} {1},\nYour {2} report status changed from {3} to {4}'.format(firstName, lastName, course, oldStatus, newStatus), html)

sys.exit()

url2 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS299.htm'
url3 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS399.htm'

pages = []
people = []

while True:
    pages.append(urllib2.urlopen(url2).read())
    pages.append(urllib2.urlopen(url3).read())

    emails = []

    while len(pages) > 0:
        page = pages.pop()
        soup = BeautifulSoup(page, 'html.parser')

        trs = soup.findAll('tr')

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

    for person in people:
        old = collection.find({'firstNameLatin': person['firstNameLatin'], 'lastNameLatin': person['lastNameLatin']})
        oldStatus = old['status']
        newStatus = person['status']

        if newStatus != oldStatus:
            res = collectionU.find({'email': old['email']})
            if res.count() == 0:
                emails.append({'email': old['email'], 'course': old['courseInt'], 'oldStatus': oldStatus,
            'newStatus': newStatus, 'firstName': person['firstName'], 'lastName': person['lastName']})

        dbobj = collection.update({'firstNameLatin': person['firstNameLatin']}, {'$set': person})

    while len(emails) > 0:
        token = getToken()
        cur = emails.pop()

        firstName = cur['firstName']
        lastName = cur['lastName']
        email = cur['email']
        oldStatus = getStatusString(cur['oldStatus'])
        newStatus = getStatusString(cur['newStatus'])

        unsub = {'email': email, 'token': token}
        collectionT.insert_one({'email': email, 'token': token})
        url = 'http://cgds.me:5000/notifique?token='
        course = 'CS299'
        if cur['course'] == 1:
            course = 'CS399'

        html = replaceHtmlParams(html_template, course, firstName, lastName, oldStatus, newStatus, url + token)
        sendMail(sg, email, 'Your {0} report status changed!'.format(course), 'Hello {0} {1},\nYour {2} report status changed from {3} to {4}'.format(firstName, lastName, course, oldStatus, newStatus), html)
        print "Sent mail to {0} {1} at {2}. Status changed from {3} to {4}".format(firstName, lastName, email, cur['oldStatus'], cur['newStatus'])
