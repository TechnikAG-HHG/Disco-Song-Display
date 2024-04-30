from flask import Flask, request, redirect, render_template, session, make_response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import webbrowser
import os
import pathlib
import functools
import requests
import cachecontrol
import google.auth.transport.requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import requests
import subprocess

    
global server_ip
SERVER_IP = "https://technikag.serveo.net"


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "450306821477-t53clamc7s8u20adedj2fqhv0904aa8t.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "Flask Server/client_secret.json")
admins_file = os.path.join(pathlib.Path(__file__).parent, "Flask Server/admins.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://technikag.serveo.net/google/callback"
)


def login_is_required(function):
    @functools.wraps(function)
    def decorator(*args, **kwargs):
        if "google_id" not in session:
            session["next"] = request.url
            print("Google ID not in session and the next is: " + session["next"])
            return redirect("/google/login")
        else:
            return function(*args, **kwargs)
    return decorator


def read_admins(admins_file):
    try:
        with open(admins_file, 'r') as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                return []
    except FileNotFoundError:
        return []

def admin_is_required(function):
    @functools.wraps(function)
    def decorator(*args, **kwargs):
        if "google_id" not in session:
            print("session: " + str(session))
            print("Google ID not in session")
            session["next"] = request.url
            return redirect("/google/login")
        else:
            admins = read_admins(admins_file)
            print(admins)
            if session["google_id"] in admins.values():  # Change this line
                print("User is an admin.")
                return function(*args, **kwargs)
            else:
                print("User is not an admin.")
                return make_response("You are not an admin.", 403)
    return decorator


class SpotifyServer:
    def __init__(self, StartServer=False):
        self.server = Flask(__name__)
        # Load data from JSON file
        with open('Flask Server/data.json') as json_file:
            spotify_data = json.load(json_file)

        self.spotify_auth = SpotifyOAuth(client_id=spotify_data['spotify_client_id'],
                          client_secret=spotify_data['spotify_client_secret'],
                          redirect_uri=spotify_data['redirect_uri'],
                          scope=spotify_data['spotify_scopes'])
        
        #set the secret key. keep this really secret:
        self.server.secret_key = os.urandom(24)
        
        # Start the server
        self.init_endpoints()
        self.start_server()
    
        
    # Modify the start_server method
    def start_server(self):
        self.server.run(debug=True, threaded=True, port=5000, host="0.0.0.0", use_reloader=True)
        #server_ip = get_server_ip()
        print(f"Server IP: {SERVER_IP}")
        webbrowser.open_new(f'{SERVER_IP}/login')


    def init_endpoints(self):

        @self.server.route('/')
        def home():
            return render_template('tv.html', ip=SERVER_IP)
        

        @self.server.route('/administrate')
        @admin_is_required
        def admin():
            return render_template('admin.html')


        @self.server.route('/login')
        @admin_is_required
        def user_login():
            auth_url = self.spotify_auth.get_authorize_url()
            return redirect(auth_url)


        @self.server.route('/callback')
        @admin_is_required
        def auth_callback():
            auth_code = request.args.get('code')
            token_info = self.spotify_auth.get_access_token(auth_code)
            access_token = token_info['access_token']
            print("Authorization was successful!")
            return "Access token: " + access_token
        

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
        
        
        @self.server.route("/google/login")
        def login():
            authorization_url, state = flow.authorization_url()
            session["state"] = state
            return redirect(authorization_url)
        

        @self.server.route("/google/callback")
        def callback():
            try:
                global session
                state = session.pop("state", None)  # Use pop to get and remove state from session
                if state is None or state != request.args.get("state"):
                    return redirect("/google/login")
        
                flow.fetch_token(authorization_response=request.url)
        
                credentials = flow.credentials
                request_session = requests.session()
                cached_session = cachecontrol.CacheControl(request_session)
                token_request = google.auth.transport.requests.Request(session=cached_session)
                id_info = id_token.verify_oauth2_token(
        
        
                    id_token=credentials._id_token,
                    request=token_request,
                    audience=GOOGLE_CLIENT_ID, 
                    clock_skew_in_seconds=10
                )
        
                session["google_id"] = id_info.get("sub")
                session["name"] = id_info.get("name")
                session["email"] = id_info.get("email")

                print("NExt: " + session.get("next"))
                return redirect(session.pop("next", "/loginsuccess"))
            except:
                return redirect("/google/login")
         

        @self.server.route("/google/logout")
        def logout():
            session.clear()
            return redirect("/")
        

        @self.server.route("/loginsuccess")
        @login_is_required
        def loginsuccess():
            #return the loginSuccsessful page
            return render_template('loginSuccessful.html')
        

        @self.server.route('/administrate/set_price_list', methods=['POST'])
        @admin_is_required
        def set_price_list():
            # use the sent data to write savePriceList.json
            data = request.get_json()
            with open('Flask Server/savePriceList.json', 'w') as json_file:
                json.dump(data, json_file)
        
            return "Price list has been updated."
        

        @self.server.route('/get_price_list', methods=['GET'])
        def get_price_list():
            with open('Flask Server/savePriceList.json') as json_file:
                price_list = json.load(json_file)
        
            return price_list
        

        @self.server.route('/administrate/get_user_data', methods=['GET'])
        @login_is_required
        def print_user_data():
            print("USER DATA PRINT REQUESTED")
            print("User Name: " + session["name"])
            print("User Email: " + session["email"])
            print("User Google ID: " + session["google_id"])
            return "User data has been printed in the console."
            
        
if __name__ == '__main__':
    
    start_server_and_ssh = True

    if start_server_and_ssh:
        subprocess.Popen(["python", "serveo_shh_connect.py"])
    
    spotify_server = SpotifyServer(StartServer=True)