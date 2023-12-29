import os
import requests
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

class SPAuth():
    def __init__(self) -> None:
        self.scope = "user-read-currently-playing"
        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scope}"
    
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
sp_auth = SPAuth()


@app.get("/", include_in_schema=False)
@app.post("/", include_in_schema=False)
def home():
    return RedirectResponse(sp_auth.auth_url)

@app.get("/get_song")
def get_song(code: Optional[str] = None):
    headers = sp_auth.get_access_token(code)
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
