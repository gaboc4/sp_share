import os
import requests
from typing import Annotated
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from token_db import TokenDB

class SPAuth():
    def __init__(self, db_conn: TokenDB) -> None:
        self.scope = "user-read-currently-playing"
        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.user_id = None
        self.db_conn=db_conn
        self.auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scope}"
    
    def save_refresh_token(self, auth_code: str):
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
            },
            auth=(self.client_id, self.client_secret),
        )
        refresh_token = response.json()["refresh_token"]
        self.db_conn.set_token(user_id=self.user_id, refresh_token=refresh_token)

    def use_refresh_token(self):
        refresh_token = self.db_conn.get_token(user_id=self.user_id)
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            auth=(self.client_id, self.client_secret),
        )
        access_token = response.json()["access_token"]
        return {"Authorization": "Bearer " + access_token}

app = FastAPI()
token_db = TokenDB()
sp_auth = SPAuth(db_conn=token_db)

@app.post("/auth", include_in_schema=False)
def auth_user(content: Annotated[str, Form()],):
    print(content)
    sp_auth.user_id = content
    return RedirectResponse(url=sp_auth.auth_url, status_code=301)

@app.post("/callback", include_in_schema=False)
def callback(code: str):
    print(code)
    sp_auth.save_refresh_token(auth_code=code, user_id=sp_auth.user_id)

@app.post("/get_song", include_in_schema=False)
def get_song():
    headers = sp_auth.use_refresh_token()
    url = f"https://api.spotify.com/v1/me/player/currently-playing"
    results = requests.get(url=url, headers=headers)
    if results.status_code == 200:
        results = results.json()
        song_name = results['item']['name'] 
        artist = results['item']['artists'][0]["name"]
        preview_url = results['item']['external_urls']['spotify']
        image = results['item']['album']['images'][-1]['url']
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Currently Playing:"
                    }
                },
                {
                    "type": "section",
                    "block_id": "section567",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{preview_url}|{song_name}> \n {artist}"
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": image,
                        "alt_text": "Album art"
                    }
                }
            ]
        }
    return       {
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "No song playing"
            }
          }]}
