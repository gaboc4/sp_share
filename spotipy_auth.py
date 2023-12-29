import os
import requests

import spotipy
from spotipy.oauth2 import SpotifyOAuth




    def get_results(self):
        results = self.sp.currently_playing()
        song_name = results['item']['name'] 
        artist = results['item']['artists'][0]["name"]
        preview_url = results['item']['artists'][0]['external_urls']['spotify']
        image = results['item']['album']['images'][0]['url']
        return "\n".join([f"<img src={image}></img>", song_name, artist, preview_url])
