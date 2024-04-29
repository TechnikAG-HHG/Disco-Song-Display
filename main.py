from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import webbrowser

class SpotifyServer:
    def __init__(self):
        self.server = Flask(__name__)
        # Load data from JSON file
        with open('data.json') as json_file:
            spotify_data = json.load(json_file)

        self.spotify_auth = SpotifyOAuth(client_id=spotify_data['spotify_client_id'],
                          client_secret=spotify_data['spotify_client_secret'],
                          redirect_uri=spotify_data['redirect_uri'],
                          scope=spotify_data['spotify_scopes'])

    def run_server(self):
        @self.server.route('/')
        def home():
            return 'Hello, World!'

        @self.server.route('/login')
        def user_login():
            auth_url = self.spotify_auth.get_authorize_url()
            return redirect(auth_url)

        @self.server.route('/callback')
        def auth_callback():
            auth_code = request.args.get('code')
            token_info = self.spotify_auth.get_access_token(auth_code)
            access_token = token_info['access_token']
            print("Authorization was successful!")
            return "Access token: " + access_token

        @self.server.route('/currently_playing')
        def current_song():
            token_info = self.spotify_auth.get_cached_token()
            if token_info:
                spotify_client = spotipy.Spotify(auth=token_info['access_token'])
                current_track = spotify_client.current_user_playing_track()
                if current_track is not None:
                    return current_track
                else:
                    return "No track is currently playing."
            else:
                return "User is not authorized."

        @self.server.route('/user_playlists')
        def user_playlists():
            token_info = self.spotify_auth.get_cached_token()
            if token_info:
                spotify_client = spotipy.Spotify(auth=token_info['access_token'])
                playlists = spotify_client.current_user_playlists()
                return playlists
            else:
                return "User is not authorized."

        @self.server.route('/playlist_tracks/<playlist_id>')
        def playlist_tracks(playlist_id):
            token_info = self.spotify_auth.get_cached_token()
            if token_info:
                spotify_client = spotipy.Spotify(auth=token_info['access_token'])
                tracks = spotify_client.playlist_tracks(playlist_id)
                return tracks
            else:
                return "User is not authorized."

        @self.server.route('/search/<query>')
        def search(query):
            token_info = self.spotify_auth.get_cached_token()
            if token_info:
                spotify_client = spotipy.Spotify(auth=token_info['access_token'])
                results = spotify_client.search(q=query, limit=20)
                return results
            else:
                return "User is not authorized."

        self.server.run(debug=True, threaded=True, port=5000, host="0.0.0.0", use_reloader=False)
        webbrowser.open_new('http://127.0.0.1:5000/login')

if __name__ == '__main__':
    spotify_server = SpotifyServer()
    spotify_server.run_server()