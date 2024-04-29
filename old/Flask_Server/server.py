import requests
import base64
import json
import webbrowser
import time
import threading
import os

from flask import Flask, send_file, request, abort, render_template, make_response, session, redirect

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests



global blockusertime

blockusertime = 5*60



def refresh_the_token():
    
    global timeleft
    global token
    global refresh_token
    

    try:
        if time.time() >= timeleft:
            global token
            print(f"renewed token")

            headers = {
                "Authorization": f"Basic {base64Message}"
            }
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }

            r = requests.post(token_url, headers=headers, data=data)

            # Parse response for new access token and expiration time
            new_token = r.json()['access_token']
            expires_in = r.json()['expires_in']
            print(r)

            # Replace old access token with new token
            token = new_token
            timeleft = time.time() + expires_in
    except NameError:
        
        headers = {
            "Authorization": f"Basic {base64Message}"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        print("new expires time")
        
        r = requests.post(token_url, headers=headers, data=data)
        expires_in = r.json()['expires_in']
        #print(expires_in)
        timeleft = time.time() + expires_in




# Client credentials
client_id = "6f327ec6656f4701a85f38f785070b6b"
client_secret = "270b38800ee24ef18153d7681c098f18"
redirect_uri = "http://www.google.com/"
scopes = "user-modify-playback-state,user-read-playback-state"

# Get authorization code
auth_url = "https://accounts.spotify.com/authorize"
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scopes,
    "client_id": client_id
}
url_args = "&".join([f"{key}={value}" for key, value in auth_query_parameters.items()])
auth_url = f"{auth_url}?{url_args}"
webbrowser.open(auth_url)
authorization_code = input("Enter the authorization code: ")
authorization_code = authorization_code.replace("https://www.google.com/?code=","")

# Get access token
token_url = "https://accounts.spotify.com/api/token"
headers = {}
data = {}   
message = f"{client_id}:{client_secret}"
messageBytes = message.encode('ascii')
base64Bytes = base64.b64encode(messageBytes)
base64Message = base64Bytes.decode('ascii')
headers['Authorization'] = f"Basic {base64Message}"
data['grant_type'] = "authorization_code"
data['code'] = authorization_code
data['redirect_uri'] = redirect_uri
r = requests.post(token_url, headers=headers, data=data)
token = r.json()['access_token']

global refresh_token
refresh_token = r.json()['refresh_token']

print("RE: "+refresh_token)
print("TO: "+token)

app = Flask(__name__)
app.secret_key = "CodeSpecialist.com"


lock = threading.Lock()


@app.route('/downloadfileusmaximus/<filename>')
def download_file(filename):

    if not filename.endswith('.txt') or not os.path.isfile(filename):
        abort(404)

    with lock:
        with open(filename, "rb") as f:
            data = f.read()
    return send_file(filename, as_attachment=True)


@app.route('/upload_file', methods=['POST'])
def upload_file():
    with lock:
        file = request.files['file']
        file_path = file.filename
        file.save(file_path)
        return 'File uploaded successfully'


global duration_ms
global progress_ms
global last_time
global progress_ms_new

progress_ms_new = 0
duration_ms = 0
progress_ms = 0
last_time = 0

global song_name
global artists_names
global upcoming
global img

img = ""
upcoming = ""
artists_names = ""
song_name = ""

global execute_tv
global exetry
execute_tv = 0
exetry = 15

global first
first = 0

@app.route("/")
def tv():
    global execute_tv
    global resp
    global exetry
    global first
    

    if execute_tv == 0 or exetry == 0 or first == 0:
        exetry = 10
        execute_tv = 1
        progress_percent = 0
        
        global duration_ms
        global progress_ms
        global last_time
        global progress_ms_new
        global song_name
        global artists_names
        global upcoming
        global img

        search_url = "https://api.spotify.com/v1/me/player/queue"
        headers = {"Authorization": f"Bearer {token}"}
        newsearch_url = "https://api.spotify.com/v1/me/player"
        newheaders = {"Authorization": f"Bearer {token}"}


        if progress_ms_new - duration_ms >= 0 or img == "" or upcoming == "" or song_name == "" or artists_names == "" or time.time() - last_time >= 10 or first == 0:
                
            try:
                first = 1
                refresh_the_token()
                response = requests.get(search_url, headers=headers).json()
                #print(response)
                #print(requests.get(newsearch_url, headers=newheaders).json())
                
            
                img = response["currently_playing"]["album"]["images"][0]["url"]
                song_name = response["currently_playing"]["name"]
                artists = response["currently_playing"]["artists"]
                artists_names = ", ".join([artist["name"] for artist in artists])
            except NameError:
                first = 0
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!NAME ERROR")
            except:
                first = 0
                return(make_response(render_template("spotnotava.html")))


            next1artists = response["queue"][0]["artists"]
            
            next2artists = response["queue"][1]["artists"]
            
            upcoming_songs = [response["queue"][0]["name"],response["queue"][1]["name"]]
            upcoming = []
            
            upcoming.append({
                "name": response["queue"][0]["name"],
                "artists": ", ".join([next1artist["name"] for next1artist in next1artists])
            })
            upcoming.append({
                "name": response["queue"][1]["name"],
                "artists": ", ".join([next2artist["name"] for next2artist in next2artists])
            })

        #print(time.time() - last_time >= 1)
        # Check if it's time to refresh the progress
        if progress_ms_new - duration_ms >= 0 or duration_ms == 0 or progress_ms_new == 0 or time.time() - last_time >= 10 or first == 0:
            last_time = time.time()  # Update last_time before making the request
            newresponse = requests.get(newsearch_url, headers=headers).json()
            #print(newresponse)
            progress_ms = int(newresponse["progress_ms"]) + 8
            duration_ms = newresponse["item"]["duration_ms"]

        # Calculate the progress based on the value returned by Spotify
        progress_ms_new = progress_ms + (time.time() - last_time) * 1000


        #print((time.time() - last_time) * 1000)
        progress_percent = (progress_ms_new / duration_ms) * 100

        listing = []
        count = 0
        with open("realqueue.txt", "r") as file:
            for line in file:
                
                line = line.strip("\n")
                line,votes = line.rsplit(" - ",1)
                
                listing.append(line)
                listing.append("Stimmen: " + votes)
                count += 1
                if count >= 6:
                    break
        if listing == []:
            listing.append("Keine Songwünsche")

        resp = make_response(render_template("tv.html", img=img, songname=song_name, artists=artists_names, upcoming=upcoming, progress_percent=progress_percent, progress_ms_new=progress_ms_new, duration_ms=duration_ms, listing=listing))

        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        execute_tv = 0
        return resp
    else :
        exetry = exetry - 1
        return resp



if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=8000, host="0.0.0.0", use_reloader=False)