from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import paho.mqtt.publish as publish
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "LOr67KNASD"
CORS(app, supports_credentials=True)

oauth = OAuth(app)  # initialising the OAuth obj

github_oauth = oauth.register(
    name='github',
    client_id='Ov23li37GYkv6HoeSU7D',
    client_secret='c38ca45778a57f02cf800fadb79c17deac5781af',
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={'scope': 'user:email'}
)

MQTT_BROKER_ADDRESS = '10.25.35.130'
MQTT_TOPIC = 'flash_led'


@app.route('/')
def hello_world():
    if 'user_name' not in session:
        return "<h1>Hello, stranger </h1> <a href='/login'>Log In</a>"
    else:
        return f"Hello, {session['user_name']} <br> <a href='/logout'>Log Out</a>"


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return github_oauth.authorize_redirect(redirect_uri)


@app.route('/logout')
def logout():
    if 'user_name' in session:
        message = f"User {session['user_name']} is logged out"
        publish.single(MQTT_TOPIC, message, hostname=MQTT_BROKER_ADDRESS)
        session.pop('user_name')
        return redirect('/')


@app.route('/authorize')
def authorize():
    token = github_oauth.authorize_access_token()
    resp = github_oauth.get('https://api.github.com/user')
    resp.raise_for_status()
    profile = resp.json()
    session['user_name'] = profile['login']
    message = f"User {session['user_name']} is logged in"
    publish.single(MQTT_TOPIC, message, hostname=MQTT_BROKER_ADDRESS)
    return redirect('/')
