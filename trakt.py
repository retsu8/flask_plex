import requests
import sys
import os
import json
import urllib3
from json.decoder import JSONDecodeError
from flask import Flask, request, jsonify
from datetime import datetime
from time import sleep

json_url = os.environ['JSON_URL']

class Trakt:
    url = os.environ['URL']
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    redirect_uri = "google.com"
    headers = {
        'Content-Type': 'application/json'
    }
    user_code = "mysecretcodehere" if not 'SECRET_CODE' in os.environ else os.environ['SECRET_CODE']
    expires_in = 0

    def get_code(self):
        data = {
            "client_id": self.client_id
        }
        req_json = self.build_request(
            '/oauth/device/code', data, method="POST")
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
                "/oauth/device/token", data, method="POST")
            print(req)
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
                return True
            sleep(5)
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
        url = f'{self.url}{url}'
        try:
            req = None
            if "GET" in method:
                req = requests.get(url, headers=headers)
            elif "POST" in method:
                req = requests.post(url, headers=headers, json=data)
            print(req.status_code)
            print(req.__dict__)
            try:
                return req.json()
            except:
                return {}
        except urllib3.exceptions.NewConnectionError:
            if self.refresh_token():
                self.build_request(url, headers, data, method)
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
        return self.build_request(url, self.headers)

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
    f = open(json_url, "r")
    try:
        db = json.load(f)
        print(db)
    except JSONDecodeError as e:
        print(e)
        db = {}
        pass
    if not db:
        return {}
    expires = db["created_at"] + db['expires_in']
    if True: # 'access_token' in db and expires > datetime.now().timestamp():
        trakt.reinstate_authorize(db)

    else:
        trakt.get_code()
        trakt.authorize()
    return trakt

    f = open(json_url, "w")
