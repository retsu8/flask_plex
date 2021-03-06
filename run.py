import sys
import os
from json import loads
from dotenv import load_dotenv

load_dotenv(".env")

from flask import Flask, request
from Trakt.trakt import setup_trakt


print(os.environ.__dict__)
trakt = setup_trakt()
# main(sys.argv)
app = Flask(__name__)

@ app.route('/', methods=['POST', 'GET'])
def index():
    data = loads(request.values['payload'])
    if 'Metadata' not in data:
        return {}
    if 'movie' in data['Metadata']['type']:
        if data['event'] == 'media.play':
            trakt.start_movie(data['Metadata'])
        if data['event'] == 'media.scrobble':
            trakt.scrobble_movie(data['Metadata'])
    elif 'episode' in data['Metadata']['type']:
        if data['event'] == 'media.play':
            trakt.start_episode(data['Metadata'])
        if data['event'] == 'media.scrobble':
            trakt.scrobble_episode(data['Metadata'])
    return {}

#app.run(host='0.0.0.0', port=51120)
application = app
