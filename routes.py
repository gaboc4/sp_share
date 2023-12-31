import os
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from token_db import TokenDB

class SPAuth():
    def __init__(self) -> None:
        self.scope = "user-read-currently-playing"
        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scope}"
    
    def get_access_token(self):
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": os.getenv('REFRESH_TOKEN'),
            },
            auth=(self.client_id, self.client_secret),
        )
        access_token = response.json()["access_token"]
        return {"Authorization": "Bearer " + access_token}

app = FastAPI()
sp_auth = SPAuth()
token_db = TokenDB()

@app.get("/", include_in_schema=False)
@app.post("/", include_in_schema=False)
def home():
    return HTMLResponse(content="<p>welcome</p>")

@app.get("/get_song", include_in_schema=False)
@app.post("/get_song", include_in_schema=False)
def get_song():
    headers = sp_auth.get_access_token()
    url = f"https://api.spotify.com/v1/me/player/currently-playing"
    results = requests.get(url=url, headers=headers)
    if results.status_code == 200:
        results = results.json()
        song_name = results['item']['name'] 
        artist = results['item']['artists'][0]["name"]
        preview_url = results['item']['artists'][0]['external_urls']['spotify']
        image = results['item']['album']['images'][0]['url']
        return HTMLResponse(content="\n".join([f"<img src={image}></img>", song_name, artist, preview_url]))
    return HTMLResponse(content="<p>No song playing</p>")
