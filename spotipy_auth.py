import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SPAuth():
    def __init__(self) -> None:
        self.scope = "user-read-currently-playing"

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope,
                                                            redirect_uri='http://127.0.0.1:5001'))

    def get_results(self):
        results = self.sp.currently_playing()
        song_name = results['item']['name'] 
        artist = results['item']['artists'][0]["name"]
        preview_url = results['item']['artists'][0]['external_urls']['spotify']
        image = results['item']['album']['images'][0]['url']
        return "\n".join([f"<img src={image}></img>", song_name, artist, preview_url])