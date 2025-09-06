import sys
import os
from json import loads
import jwt
from flask import Flask, request, jsonify, make_response
import logging

app = Flask(__name__)
app.debug = True

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        print(request.values)
    if request.method == 'GET':
        args = request.args.get('argname')
        print("args")
    

@app.route("/ombi", methods=["POST", "GET"])
def ombi():
    print("ombi")
    if request.method == 'POST':
        print("POST")
        print(request.values)
        if request.values.get('TV Show'):
            title = request.values.get('title')
            provider_id = request.values.get('providerId')
            
    if request.method == 'GET':
        print("GET")
        args = request.args.get('argname')
        print("args")
    return {}

app.run(host='10.11.88.101', port=9500)
#application = app
