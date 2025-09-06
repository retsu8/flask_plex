import sys
import os
from json import loads
from flask import Flask, request
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route('/', methods=['POST', 'GET'])
def index():
    data = loads(request.values['payload'])
    print(data);
    

@app.route("/ombi", methods=["POST", "GET"])
def ombi():
    data = loads(request.values['payload'])
    print(data);

app.run(host='0.0.0.0', port=9500)
#application = app
