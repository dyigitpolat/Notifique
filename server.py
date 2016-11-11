import sys
from flask import render_template
from flask import Flask
from flask import request
from pymongo import MongoClient

app = Flask(__name__)

html_template = open('./unsubscribed.html', 'r').read()
html_404 = open('./404.html', 'r').read()
html_mistoken = open('./mistoken.html', 'r').read()

host = 'localhost'
port = 27017
client = MongoClient(host, port)
db = client.notifique
collection = db['n20161'] # Application data
collectionU = db['u20161'] # List of people who unsubscribed
collectionT = db['t20161'] # List of email tokens

@app.route("/", methods=['GET'])
def index():
    # print "hola"
    # print request.args.get('token')
    return html_404

@app.route("/notifique", methods=['GET'])
def unsubscribe():
    token = request.args.get('token')
    tok = collectionT.find_one({'token': token})
    try:
	print tok
        collectionU.insert_one({'email': tok['email']})
        return html_template
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return html_mistoken

@app.errorhandler(404)
def page_not_found(e):
    return html_404

if __name__ == '__main__':
    app.run(host='0.0.0.0')
