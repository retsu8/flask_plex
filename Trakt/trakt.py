import requests
import sys
import os
import json
import urllib3
from json.decoder import JSONDecodeError
from datetime import datetime
from time import sleep

if 'JSON_URL' in os.environ:
    json_url = os.environ['JSON_URL']
else:
    json_url = './db.json'

class Trakt:
    url = os.environ['URL']
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    redirect_uri = "google.com"
    headers = {
        'Content-Type': 'application/json'
    }
    if "SECRET_CODE" not in os.environ:
        user_code = os.environ['SECRET_CODE']
    else:
        user_code = "mysecretcodehere"

    expires_in = 0

    def get_code(self):
        data = {
            "client_id": self.client_id
        }
        req_json = self.build_request(
            '/oauth/device/code', data=data, method="POST")
        self.user_code = req_json['user_code']
        self.device_code = req_json['device_code']
        self.expires_in = req_json["expires_in"]
        print(
            "Please input {user_code} into {verification_url}".format(**req_json))
        return req_json

    def authorize(self):
        data = {
            "code": self.device_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        now = datetime.now().timestamp()
        expires = now + self.expires_in
        req = None
        sleep(10)
        while expires > datetime.now().timestamp():
            req = self.build_request(
                "/oauth/device/token", data=data, method="POST")
            if "access_token" in req:
                self.access_token = req["access_token"]
                self.expires_in = req["expires_in"]
                self.refresh_token = req["refresh_token"]
                self.created_at = req["created_at"]
                self.headers.update({
                    'Authorization': 'Bearer {access_token}'.format(**req),
                    'trakt-api-version': '2',
                    'trakt-api-key': self.client_id
                })
                return req
            sleep(10)
        return False

    def refresh_token(self):
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "refresh_token"
        }
        self.build_request('/oauth/token', data=values, method="PUST")

    def build_request(self, url, headers={}, data={}, method="GET"):
        if not headers:
            headers = self.headers
        print("These are the headers")
        print(headers)
        print("this is the body")
        print(data)
        url = f'{self.url}{url}'
        try:
            req = None
            if "GET" in method:
                req = requests.get(url, headers=headers)
            elif "POST" in method:
                req = requests.post(url, headers=headers, json=data)
            print(req.__dict__)
            try:
                return req.json()
            except:
                return {}
        except urllib3.exceptions.NewConnectionError:
            if self.refresh_token():
                self.build_request(url=url, headers=headers, data=data, method=method)
            else:
                print("Need to reauthorize")
                # TODO: build reauthorize part

    def reinstate_authorize(self, state):
        self.access_token = state["access_token"]
        self.expires_in = state["expires_in"]
        self.refresh_token = state["refresh_token"]
        self.created_at = state["created_at"]
        self.headers.update({
            'Authorization': 'Bearer {access_token}'.format(**state),
            'trakt-api-version': '2',
            'trakt-api-key': self.client_id
        })

    def get_watched_movies(self):
        url = f'/users/me/watched/movies'
        return self.build_request(url, headers=self.headers)

    def build_movie_meta(self, meta):
        movie = {"movie": {
            'year': meta['year'],
            'title': meta['title'],
            'ids': {}}}
        for id in meta['Guid']:
            name, id = id['id'].split(':', 2)
            movie['movie']['ids'][name] = id.replace('/', '')
        return movie

    def scrobble_movie(self, meta):
        movie = self.build_movie_meta(meta)
        movie['progress'] = 100
        self.build_request('/scrobble/stop', data=movie, method="POST")

    def start_movie(self, meta):
        movie = self.build_movie_meta(meta)
        self.build_request('/scrobble/start', data=movie, method="POST")

    def build_tv_meta(self, meta):
        episode = ''
        if 'tvdb' in meta['guid']:
            episode = meta['guid'].split('/')[2:]
            episode = int(episode[0])
        show = {
            "show": {
                "title": meta['grandparentTitle'],
                "year": meta['year'],
                "ids": {
                    "tvdb": episode
                }
            },
            "episode": {
                "season": meta['parentIndex'],
                "number": meta['index']
            }
        }
        return show

    def start_episode(self, meta):
        # 'com.plexapp.agents.thetvdb://294002/1/2?lang=en',
        show = self.build_tv_meta(meta)
        show['progress'] = 10
        self.build_request('/scrobble/start', data=show, method="POST")

    def scrobble_episode(self, meta):
        show = self.build_tv_meta(meta)
        show['progress'] = 100
        self.build_request('/scrobble/stop', data=show, method="POST")

def setup_trakt():
    trakt = Trakt()
    try:
        f = open(json_url, "r")
        db = json.load(f)
        if not db:
             raise FileNotFoundError
        print(f"Got the db {db}")
    except JSONDecodeError as e:
        pass
    except FileNotFoundError as e:
        print("db.json not found creating")
        req_json = trakt.get_code()
        print(req_json)
        db = trakt.authorize()
        with open(json_url, "w") as outfile:
            json.dump(db, outfile, indent=4)
    expires = db["created_at"] + db['expires_in']
    if 'access_token' in db and expires > datetime.now().timestamp():
        trakt.reinstate_authorize(db)

    else:
        trakt.get_code()
        trakt.authorize()
    print("returning")
    return trakt

    f = open(json_url, "w")
