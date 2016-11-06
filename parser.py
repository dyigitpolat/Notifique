import sys
import urllib2
import json
from bs4 import BeautifulSoup

url2 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS299.htm'
url3 = 'http://www.cs.bilkent.edu.tr/~sekreter/SummerTraining/2016G/CS399.htm'

page = urllib2.urlopen(url2).read()
soup = BeautifulSoup(page, 'html.parser')
# print soup

trs = soup.findAll('tr')

# for td in tds:
    # print td

count = 0

# print int('a')

# sys.exit()
for i in xrange(len(trs)):
    tds = trs[i].findAll('td')
    try:
        num = int(tds[0].text.encode('utf-8'))
        first_name = str(tds[1].text.encode('utf-8')).rstrip().replace('\n', '').replace('\r', '').replace('  ', ' ')
        last_name = str(tds[2].text.encode('utf-8')).rstrip().replace('\n', '')
        professor = str(tds[3].text.encode('utf-8'))
        status = str(tds[4].text.encode('utf-8'))
        print num, first_name, last_name, professor, status
    except:
        # print i, "Fail", tds[0].text.encode('utf-8')
        pass
