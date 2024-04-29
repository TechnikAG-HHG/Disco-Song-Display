from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class MyApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.sp_oauth = SpotifyOAuth(client_id='your_spotify_client_id',
                                      client_secret='your_spotify_client_secret',
                                      redirect_uri='your_redirect_uri',
                                      scope='user-read-private user-read-email')

    def start_server(self):
        @self.app.route('/')
        def hello():
            return 'Hello, World!'

        @self.app.route('/login')
        def login():
            auth_url = self.sp_oauth.get_authorize_url()d
            return redirect(auth_url)

        @self.app.route('/callback')
        def callback():
            code = request.args.get('code')
            token_info = self.sp_oauth.get_access_token(code)
            access_token = token_info['access_token']
            return "Access token: " + access_token

        self.app.run()

if __name__ == '__main__':
    my_app = MyApp()
    my_app.start_server()