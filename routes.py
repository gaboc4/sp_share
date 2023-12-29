import os
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

class SPAuth():
    def __init__(self) -> None:
        self.scope = "user-read-currently-playing"

        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    
    def get_access_token(self, auth_code: str):
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
            },
            auth=(self.client_id, self.client_secret),
        )
        access_token = response.json()["access_token"]
        return {"Authorization": "Bearer " + access_token}

app = FastAPI()

@app.route("/")
def home():
    sp_auth = SPAuth()
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={sp_auth.client_id}&redirect_uri={sp_auth.redirect_uri}&scope={sp_auth.scope}"
    return HTMLResponse(content=f'<a href="{auth_url}">Authorize</a>')

@app.route("/get_song")
def get_song(code):
    sp_auth = SPAuth()
    headers = sp_auth.get_access_token(code)
    url = f"https://api.spotify.com/v1/me/player/currently-playing"
    response = requests.post(url=url, headers=headers)
    print(response)
    return HTMLResponse(content=f'<p>bam</p>')
