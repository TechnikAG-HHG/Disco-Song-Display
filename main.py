from flask import Flask, request, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import webbrowser

class SpotifyServer:
    def __init__(self, StartServer=False):
        self.server = Flask(__name__)
        # Load data from JSON file
        with open('data.json') as json_file:
            spotify_data = json.load(json_file)

        self.spotify_auth = SpotifyOAuth(client_id=spotify_data['spotify_client_id'],
                          client_secret=spotify_data['spotify_client_secret'],
                          redirect_uri=spotify_data['redirect_uri'],
                          scope=spotify_data['spotify_scopes'])
        
        # Start the server
        self.init_endpoints()
        self.start_server()
    

    def start_server(self):
        self.server.run(debug=True, threaded=True, port=5000, host="0.0.0.0", use_reloader=True)
        webbrowser.open_new('http://127.0.0.1:5000/login')


    def init_endpoints(self):
        @self.server.route('/')
        def home():
            return render_template('tv.html')

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
        
        ##############################################################################################
        ##############################################################################################
        ##############################################################################################

        @self.server.route('/get_spotify')
        def get_spotify_data():
            token_info = self.spotify_auth.get_cached_token()
            if token_info:
                spotify_client = spotipy.Spotify(auth=token_info['access_token'])

                output = {}

                queue = spotify_client.queue()

                # look at the currently playing song
                current_track_info_json = queue['currently_playing']
                print(current_track_info_json)

                current_track_name = current_track_info_json['name']
                current_track_artist = current_track_info_json['artists'][0]['name']
                #current_track_album = current_track_info_json['album']['name']
                current_track_image = current_track_info_json['album']['images'][0]['url']
                #current_track_url = current_track_info_json['external_urls']['spotify']
                current_track_duration = current_track_info_json['duration_ms']

                current_track_info_json = spotify_client.current_user_playing_track()

                progress = current_track_info_json['progress_ms']

                # put it into a json in the format: {0: {"title": "xyz", "artists": "xyz", "progress": 123, "duration": 123, "image": "xyz"}, 1: {"title": "xyz", "artists": "xyz", "progress": 123, "duration": 123, "image": "xyz"}, 2: {"title": "xyz", "artists": "xyz", "progress": 123, "duration": 123, "image": "xyz"}}
                
                output[0] = {"title": current_track_name, "artists": current_track_artist, "progress": progress, "duration": current_track_duration, "image": current_track_image}

                for id in range(0,2):
                    # get the two next songs in the queue
                    next_track_info_json = queue['queue'][id]
                    next_track_name = next_track_info_json['name']
                    next_track_artist = next_track_info_json['artists'][0]['name']
                    #next_track_album = next_track_info_json['album']['name']
                    next_track_image = next_track_info_json['album']['images'][0]['url']
                    #next_track_url = next_track_info_json['external_urls']['spotify']
                    next_track_duration = next_track_info_json['duration_ms']

                    # put it into the json
                    output[id+1] = {"title": next_track_name, "artists": next_track_artist, "progress": 0, "duration": next_track_duration, "image": next_track_image}

                return output
            else:
                return "User is not authorized."
            
        
if __name__ == '__main__':
    spotify_server = SpotifyServer(StartServer=True)