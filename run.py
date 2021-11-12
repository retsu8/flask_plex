import sys
import os
from json import loads
from dotenv import load_dotenv
import logging
import datetime

#load_dotenv(".env")

from flask import Flask, request
from Trakt import trakt

date = datetime.date()

trakt = trakt.setup_trakt()
# main(sys.argv)
app = Flask(__name__)

logging.basicConfig(filename=f'logs/flask_plex/{date}.log', level=logging.debug, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route('/', methods=['POST', 'GET'])
def index():
    data = loads(request.values['payload'])
    if 'Metadata' not in data:
        app.logger.info('Failed there is no Metadata')
        return {}
    if 'movie' in data['Metadata']['type']:
        if data['event'] == 'media.play':
            app.logger.info('Got the event movie play')
            trakt.start_movie(data['Metadata'])
        if data['event'] == 'media.scrobble':
            app.logger.info('Got the event movie scrobble')
            trakt.scrobble_movie(data['Metadata'])
    elif 'episode' in data['Metadata']['type']:
        if data['event'] == 'media.play':
            app.logger.info('Got the event episode play')
            trakt.start_episode(data['Metadata'])
        if data['event'] == 'media.scrobble':
            app.logger.info('Got the event episode scrobble')
            trakt.scrobble_episode(data['Metadata'])
    return {}

#app.run(host='0.0.0.0', port=51120)
application = app
