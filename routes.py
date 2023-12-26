from flask import Flask
from spotipy_auth import SPAuth


app = Flask(__name__)

@app.route("/")
def home():
    return "<p>Home</p>"

@app.route("/get_song")
def get_song():
    sp_auth = SPAuth()
    return sp_auth.get_results()