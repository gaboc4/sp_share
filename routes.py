import os
import requests
from dataclasses import dataclass
from fastapi import Depends, FastAPI, Form
import sqlite3


@dataclass
class SimpleModel:
    user_id: str = Form(...)

class SPAuth():
    def __init__(self) -> None:
        self.scope = "user-read-currently-playing"
        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.user_id = None
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
        with sqlite3.connect("sp_share.db") as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS token_info(user_id, refresh_token)")
            cur.execute(f"INSERT INTO token_info VALUES ('{self.user_id}', '{refresh_token}')")

    def use_refresh_token(self, user_id: str):
        with sqlite3.connect("sp_share.db") as conn:
            cur = conn.cursor()
            res = cur.execute(f"SELECT refresh_token FROM token_info WHERE user_id = '{user_id}'")
            refresh_token = res.fetchone()
            test = cur.execute("select * from token_info")
            print(test.fetchall())
        print(refresh_token)
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
sp_auth = SPAuth()

@app.post("/auth")
def auth_user(response: SimpleModel = Depends()):
    sp_auth.user_id = response.user_id
    return {
			"blocks": [
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": f"<{sp_auth.auth_url}|Go to Auth> :spotify:"
					}
				}
			]
            }

@app.get("/callback", include_in_schema=False)
@app.post("/callback", include_in_schema=False)
def callback(code: str):
    sp_auth.save_refresh_token(auth_code=code)

@app.post("/get_song", include_in_schema=False)
def get_song(response: SimpleModel = Depends()):
    headers = sp_auth.use_refresh_token(response.user_id)
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
