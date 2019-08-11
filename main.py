import json
from base64 import b64encode
from pathlib import Path

import requests
from flask import Flask, redirect, request, url_for, jsonify

AUTH_FILE = Path('.auth')

app = Flask(__name__)
app.config.from_pyfile('settings_local.py')


def authorized_request(**kwargs) -> requests.Response:
    if not AUTH_FILE.is_file():
        raise FileNotFoundError
    auth = json.loads(AUTH_FILE.read_text())
    headers = kwargs.get('headers', {})
    headers['Authorization'] = 'Bearer {}'.format(auth['access_token'])
    kwargs['headers'] = headers

    return requests.request(**kwargs)

@app.route('/')
def main():
    try:
        resp = authorized_request(
                url='https://api.spotify.com/v1/me',
                method='GET')
        resp.raise_for_status()
    except (FileNotFoundError, requests.HTTPError):
        return redirect(url_for('login'))
    me = resp.json()

    resp = authorized_request(
            url="https://api.spotify.com/v1/me/player/volume?volume_percent=50",
            method='PUT')
    
    resp = authorized_request(
            url='https://api.spotify.com/v1/me/player/devices',
            method='GET')
    devices = resp.json()

    return devices

@app.route('/login/')
def login():
    auth_url = 'https://accounts.spotify.com/authorize?client_id={}&response_type=code&redirect_uri={}&scope={}'
    callback_url = request.url_root + 'callback/'
    return redirect(auth_url.format(app.config['CLIENT_ID'], callback_url, 'user-read-playback-state user-modify-playback-state'))

@app.route('/callback/')
def callback():
    code = request.args.get('code')
    res = requests.post(
            'https://accounts.spotify.com/api/token', 
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': request.url_root + 'callback/',
                'client_id': app.config['CLIENT_ID'],
                'client_secret': app.config['CLIENT_SECRET'],
            }
            
        )
    data = res.json()
    AUTH_FILE.write_text(json.dumps(data))
    resp = redirect(url_for('main'))
    resp.set_cookie('access_token', data['access_token']) 
    resp.set_cookie('refresh_token', data['refresh_token']) 
    return resp

if __name__ == '__main__':
    app.run()
