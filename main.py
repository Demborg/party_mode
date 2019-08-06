from base64 import b64encode
from flask import Flask, redirect, request, url_for, jsonify
from requests import post, get, put
app = Flask(__name__)
app.config.from_pyfile('settings_local.py')

@app.route('/')
def hello_world():
    me = get(
            'https://api.spotify.com/v1/me',
            headers={'Authorization': 'Bearer {}'.format(
                request.cookies.get('access_token'))}).json()
    devices = get(
            'https://api.spotify.com/v1/me/player/devices',
            headers={'Authorization': 'Bearer {}'.format(
                request.cookies.get('access_token'))}).json()
    res = put(
            "https://api.spotify.com/v1/me/player/volume?volume_percent=50",
            headers={'Authorization': 'Bearer {}'.format(
                request.cookies.get('access_token'))})


    return devices

@app.route('/login/')
def login():
    auth_url = 'https://accounts.spotify.com/authorize?client_id={}&response_type=code&redirect_uri={}&scope={}'
    return redirect(auth_url.format(app.config['CLIENT_ID'], 'http://localhost:5000/callback/', 'user-read-playback-state user-modify-playback-state'))

@app.route('/callback/')
def callback():
    code = request.args.get('code')
    res = post(
            'https://accounts.spotify.com/api/token', 
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'http://localhost:5000/callback/',
                'client_id': app.config['CLIENT_ID'],
                'client_secret': app.config['CLIENT_SECRET'],
            }
            
        )
    data = res.json()
    resp = redirect('http://localhost:5000/')
    resp.set_cookie('access_token', data['access_token']) 
    resp.set_cookie('refresh_token', data['refresh_token']) 
    return resp

if __name__ == '__main__':
    app.run()
