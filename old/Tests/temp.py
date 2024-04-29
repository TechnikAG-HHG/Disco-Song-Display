import requests
import base64
import json
import webbrowser
import tkinter as tk
import tkinter.messagebox
import time
import threading
import unicodedata
import os
import pathlib

from flask import Flask, send_file, request, abort, render_template, make_response, session, redirect

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests



global blockusertime

blockusertime = 5*60



def refresh_the_token():
    
    global timeleft
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

        r = requests.post(token_url, headers=headers, data=data)
        expires_in = r.json()['expires_in']
        #print(expires_in)
        timeleft = time.time() + expires_in



# Client credentials
client_id = "dcea901047da4251b0437c3666eae991"
client_secret = "d97ac3aacc2c4dd1a13f498667626e40"
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


def pure_name(names):
    names = str(names)
    names = names.strip()
    names = names.replace("\n","")
    return names


def replace_non_ascii(text):
    # Normalize the text into NFKD form
    normalized = unicodedata.normalize('NFKD', text)

    # Replace any non-ASCII characters with underscores
    ascii_text = ''
    for c in normalized:
        if ord(c) < 128:
            ascii_text += c
        else:
            ascii_text += '_'
    return ascii_text


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




def check(ip_address, last_visit):
    writeback = []
    boolen = True
    if last_visit:
        last_visit_timestamp = float(last_visit)
        if  time.time() - last_visit_timestamp <=  blockusertime:
            print("Cookie failed")
            return False
    else:
        with lock:
            with open('addresses.txt', 'r') as f:
                addresses = f.readlines()
                for line in addresses:
                    part1,part2 = line.split(" - ",1)
                    if time.time() - float(pure_name(part2)) <=  blockusertime:
                        writeback.append(line)
                    if pure_name(ip_address) == pure_name(part1):
                        if time.time() - float(pure_name(part2)) <=  blockusertime:
                            if ip_address != "127.0.0.1":
                                print("IP failed")
                                boolen = False
                        else:
                            print(float(pure_name(part2)))
                            print(time.time())
                            
    writebackacc = []
    with lock:
        with open('accounts.txt', 'r') as f:
                accounts = f.readlines()
                for line in accounts:
                    part1,part2 = line.split(" - ",1)
                    if time.time() - float(pure_name(part2)) <=  blockusertime:
                        writebackacc.append(line)
                    if pure_name(session["google_id"]) == pure_name(part1):
                        if time.time() - float(pure_name(part2)) <=  blockusertime:
                            
                            print("ACC failed")
                            boolen = False
                        else:
                            print(float(pure_name(part2)))
                            print(time.time())

    with lock:
        with open('addresses.txt', 'w') as f:
            for entry in writeback:
                    f.write(entry.replace("\n","")+"\n")

    with lock:
        with open('accounts.txt', 'w') as f:
            for entry in writebackacc:
                    f.write(entry.replace("\n","")+"\n")

    if boolen == False:
        return False
    elif boolen == True:
        return True


def check_time():
    writeback = []
    if last_visit:
        last_visit_timestamp = float(last_visit)
        if time.time() - last_visit_timestamp <=  blockusertime:
            return int(blockusertime//60 - (time.time() - last_visit_timestamp)//60) 
    else:
        with lock:
            with open('addresses.txt', 'r') as f:
                addresses = f.readlines()
                for line in addresses:
                    part1,part2 = line.split(" - ",1)
                    if ip_address == part1:
                        if time.time() - float(pure_name(part2)) <=  blockusertime:
                            return int(blockusertime//60 - (time.time() - float(part2))//60) 
    
    writebackacc = []
    with lock:
        with open('accounts.txt', 'r') as f:
                accounts = f.readlines()
                for line in accounts:
                    part1,part2 = line.split(" - ",1)
                    if time.time() - float(pure_name(part2)) <=  blockusertime:
                        writebackacc.append(line)
                    if pure_name(session["google_id"]) == pure_name(part1):
                        if time.time() - float(pure_name(part2)) <=  blockusertime:
                            
                            return int(blockusertime//60 - (time.time() - float(pure_name(part2)))//60) 

                


def clean_trackname(trackname):
    # split the string into two parts at the first occurrence of '-'
    # if '-' doesn't exist in the string, the first part will be the entire string and the second part will be empty
    artist, title = trackname.split(" - ", maxsplit=1)
    
    # remove all '-' characters in the title part except for the first one
    title = title.replace("-", "_")
    print(title)
    
    # join the artist and cleaned title with a '-' separator
    return f"{artist} - {title}"



def is_song_allowed(song_name):
    try:
        with lock:
            with open('blacklist.txt') as f:
                blacklist = [line.strip() for line in f.readlines()]
                for item in blacklist:
                    if song_name in item:
                        return False
                return True
    except FileNotFoundError:
        print("Error: blacklist.txt file not found.")
        return False
    except Exception as e:
        #print(f"Error: {e}")
        return False


def add_track_to_queue(trackname):
    #print(trackname)

    with lock:
        with open("queue.txt", "r") as f:
            queueitem = [line.strip() for line in f.readlines()]

    if not queueitem:
        with lock:
            with open("queue.txt", "a") as queue:
                queue.write(trackname)
                queue.write('\n')
                queue.write("1")
                queue.write('\n')

    else:
        with lock:
            with open("queue.txt", "r") as queue:
                rl = queue.readlines()

        for index, item in enumerate(queueitem):
            if trackname == item:
                gpt = index + 1  # Setze gpt Variable auf die aktuelle Zeilennummer
                QueueNumber = rl[index+1]
                nn = int(QueueNumber) + 1
                rl[index+1] = str(nn) + "\n"
                with lock:
                    with open("queue.txt", "w") as queue:
                        queue.writelines(rl)
                        break

        else:   
            with lock:
                with open("queue.txt", "a") as queue:
                    #print("warn")
                    queue.write(trackname)
                    queue.write('\n')
                    queue.write("1")
                    queue.write('\n')

def save_cookie_and_ip_adress():
    global savecookies
    savecookies = 1
    ip_found = False
    with lock:
        with open('addresses.txt', 'r') as f:
            lines = f.readlines()
    
    for line in lines:
        part1, part2 = line.split(" - ",1)
        if ip_address in part1:
            ip_found = True

    if ip_found == False:
        with lock:
            with open('addresses.txt', 'a') as f:
                f.write(ip_address + " - " + str(time.time()) + '\n')

    line = f"{session['google_id']} - {time.time()}"
    with lock:
        with open('accounts.txt', 'a') as f:
            f.write(line)
        



def get_listbox_items():
    # Your code here, return a list of items
    global blockqueue
    blockqueue = 1
    return ['Gib deine Suche in das Suchfeld ein']

def search_user(query):
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "market": "DE", "limit": 20}
    response = requests.get(search_url, headers=headers, params=params).json()
    

    # If no exact match was found, return the original search results
    sanitized_results = []
    if response != []:

        for track in response['tracks']['items']:
            # sanitize track name
            track['name'] = replace_non_ascii(track['name'])
            sanitized_results.append(track)

    return sanitized_results


#Google shit


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "450306821477-t53clamc7s8u20adedj2fqhv0904aa8t.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://technikag.serveo.net/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    global session
    if "state" not in session or session["state"] != request.args.get("state"):
        abort(400)  # Bad request

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/user")
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    global sblock
    sblock = False


    with open('block_user.txt',"r") as f:
        blacklist = [line.strip() for line in f.readlines()]
        for item in blacklist:
            if "This is a block_user file.".replace("\n","") in item.replace("\n",""):
                sblock = True
    if sblock == False:
        resp = make_response(render_template("login.html"))
        return resp
    else:
        shitresp = make_response(render_template("blocked.html"))
        return shitresp
    #return "Hello World <a href='/login'><button>Login</button></a>"


@app.route("/user", methods=['GET', 'POST'])
@login_is_required
def user():
    refresh_the_token()
    
    global sblock
    sblock = False


    with open('block_user.txt',"r") as f:
        blacklist = [line.strip() for line in f.readlines()]
        for item in blacklist:
            if "This is a block_user file.".replace("\n","") in item.replace("\n",""):
                sblock = True

    if sblock == False:
        global savecookies
        global ip_address
        global last_visit
        global input_value
        global listbox_html
        global search_performed
        global blockqueue 
        
        global warning

        savecookies = 0
        ip_address = request.remote_addr
        last_visit = request.cookies.get('last_visit')

        # Reset variables at the beginning of each request
        input_value = ''
        listbox_html = ''
        default_message = '<option>' + "Gib deine Suche in das Suchfeld ein" + '</option>'
        search_performed = False
        warning = False
        message_info = ""
        blockqueue = 0
        print("changed")

        if request.method == 'POST':
            if 'submit' in request.form and request.form['submit'] == 'Search':
                
                blockqueue = 1
                input_value = request.form['input']
                if check(ip_address, last_visit):
                    search_results = search_user(input_value)
                    if search_results:
                        for item in search_results:
                            listbox_html += '<option>' + str(f"{item['artists'][0]['name']} - {item['name']}") + '</option>'
                        search_performed = True
                        print("search_performed")
                        blockqueue = 0
                    else:
                        message_info = "Gib deine Suche in das Suchfeld ein" 
                        blockqueue = 1
                        warning = True
                else:
                    message_info = "Versuche es in "+ str(check_time()) + " min wieder."
                    
                    
                    
            elif 'submit' in request.form and request.form['submit'] == 'Submit':
                if blockqueue == 0:
                    selection = request.form.get('selected_items')
                    if check(ip_address,last_visit):
                        if selection != None:
                            track = request.form.get('selected_items')
                            track = clean_trackname(track)
                            split_track = track.split(" - ")
                            #print(f"Split Track: {split_track}")
                            if len(split_track) == 2:
                                artist_name, track_name = split_track
                                artist_name, track_name = artist_name, track_name
                                track_uri = f"{artist_name} - {track_name}"
                                if is_song_allowed(track_uri):
                                    print("Hat geklappt")
                                    add_track_to_queue(track_uri)
                                    save_cookie_and_ip_adress()
                                    #reset_search()
                                    message_info = f"'{artist_name} - {track_name}' zu der Warteliste hinzugefügt."
                                else:
                                    print("Not1")
                                    message_info = f"'{artist_name} - {track_name}' darf nicht gespielt werden."
                            else:
                                print("Not3")
                                message_info = f"'{track}' ist kein valieder Lied Name."

                        else: 
                            message_info = f"Du kannst dieses Lied nicht hinzufügen"
                            print("Not2")
                    else:
                        message_info = "Versuche es in "+ str(check_time()) + " min wieder."



        resp = make_response(render_template("user.html", message_info=message_info, listbox_html=listbox_html, search_performed = search_performed, default_message=default_message))
        if savecookies == 1:
            resp.set_cookie('last_visit', str(time.time()))
        return resp
    else:
        shitresp = make_response(render_template("blocked.html"))
        return shitresp


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


@app.route("/tv")
def tv():
    global execute_tv
    global resp
    global exetry
    global first
    

    if execute_tv == 0 or exetry == 0 or first ==  0:
        exetry = 15
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
            
            first = 1
            refresh_the_token()
            response = requests.get(search_url, headers=headers).json()
            #print(requests.get(newsearch_url, headers=newheaders).json())
            
            try:
                img = response["currently_playing"]["album"]["images"][0]["url"]
                song_name = response["currently_playing"]["name"]
                artists = response["currently_playing"]["artists"]
                artists_names = ", ".join([artist["name"] for artist in artists])
            except NameError:
                first = 0
            except TypeError:
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

        print(time.time() - last_time >= 1)
        # Check if it's time to refresh the progress
        if progress_ms_new - duration_ms >= 0 or duration_ms == 0 or progress_ms_new == 0 or time.time() - last_time >= 10 or first == 0:
            last_time = time.time()  # Update last_time before making the request
            newresponse = requests.get(newsearch_url, headers=newheaders).json()
            progress_ms = int(newresponse["progress_ms"]) + 8
            duration_ms = newresponse["item"]["duration_ms"]

        # Calculate the progress based on the value returned by Spotify
        progress_ms_new = progress_ms + (time.time() - last_time) * 1000


        #print((time.time() - last_time) * 1000)
        progress_percent = (progress_ms_new / duration_ms) * 100
        #print("PP: " + str(progress_percent))
        #print("Pnew: " + str(progress_ms_new))
        #print("duration: " + str(duration_ms))
        #print("lasttime: " + str(last_time))

        # Rest of your code...

        resp = make_response(render_template("tv.html", img=img, songname=song_name, artists=artists_names, upcoming=upcoming, progress_percent=progress_percent))

        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        execute_tv = 0
        return resp
    else :
        exetry = exetry - 1
        return resp












if __name__ == '__main__':
    app.run(debug=True, threaded = True, port=5000, host="0.0.0.0",use_reloader=False)
