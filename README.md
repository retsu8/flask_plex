# flask_plex
Plex webhook listener written in plex that updates trakt on watched shows and movies.

# Instructions
To run this application you will need:
1. create a trakt api app https://trakt.tv/oauth/applications/new
2. setup a plex webhook https://support.plex.tv/articles/115002267687-webhooks/

# Next
1. Clone the git repo
2. cd flask_plex
3. ```touch creds.json```
4. Create uwsgi.ini
```
[uwsgi]
http = :51120
wsgi-file = path to git
single-interpreter = true
enable-threads = true
master = true
processes = 4
threads = 2
env = JSON_URL=path to json to save login token
env = URL=https://api.trakt.tv
env = CLIENT_ID=client_id
env = CLIENT_SECRET=client_secret
logto = path to logs
safe-pidfile = path to pid file to keep track of running instance```

5. Set env variables.
6. run uwsgi:
```uwsgi --ini .config/trakt_sync/uwsgi.ini```
