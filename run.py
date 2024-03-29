import sys
import os
from json import loads
from dotenv import load_dotenv
from flask import Flask, request
from Trakt import trakt
import logging
import datetime

#load_dotenv(".env")

date = datetime.date()
# main(sys.argv)
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

trakt = trakt.setup_trakt()
@app.route('/', methods=['POST', 'GET'])
def index():
    trakt.set_flask_app(app)
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
