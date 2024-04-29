import requests
import base64
import json
import webbrowser
import tkinter as tk
import tkinter.messagebox
import time
import unicodedata
import os

global queue_txt
global queuecopy_txt
global has_been_played_txt
global blocklist_txt
global blacklist_txt
global block_txt

queuecopy_txt = "queuecopy.txt"
queue_txt = "queue.txt"
has_been_played_txt = "has_been_played.txt"
blocklist_txt = "blocklist.txt"
blacklist_txt = "blacklist.txt"
block_txt = "block.txt"

global searching

searching = 0


def get_file(filename):
    file_url = f'http://127.0.0.1:5000/downloadfileusmaximus/{filename}'
    local_filename = filename
    
    try:
        with requests.Session() as session:
            response = session.get(file_url, stream=True)
            response.raise_for_status()

            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
    except:
        print("Connection Error")

def upload_file(filename):
    url = 'http://127.0.0.1:5000/upload_file'
    file_path = filename
    try:
        with requests.Session() as session:
            with open(file_path, 'rb') as f:
                response = session.post(url, files={'file': f})
                response.raise_for_status()
    except:
        print("Connection Error")

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

window_blocked = False

block_window = None

def block_screen():
    global block_window
    
    # create the blocking window
    block_window = tk.Toplevel()
    block_window.attributes('-fullscreen', True)
    block_window.configure(bg='red')
    block_window.grab_set()  # make the window modal
    
    # create the blocking label
    block_label = tk.Label(block_window, text="BILDSCHIRM GESPERRT", font=('Arial', 72), bg='red', fg='white')
    block_label.pack(expand=True)
    block_window.bind('<Control-F9>', lambda event: toggle_window_block())


def unblock_screen():
    global block_window
    
    if block_window:
        # destroy the blocking window
        block_window.destroy()
        block_window = None
        
        # enable all other windows
        root.grab_release()


def real_refresh_the_token():
    global timeleft
    global token
    global refresh_token
    #print("try to refresh")

    if time.time() >= timeleft:
        print("renewed token")

        headers = {
            "Authorization": f"Basic {base64Message}"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        try:
            r = requests.post(token_url, headers=headers, data=data)
            r.raise_for_status()  # Raise exception for non-successful response

            # Parse response for new access token and expiration time
            new_token = r.json()['access_token']
            expires_in = r.json()['expires_in']
            #print(r)

            # Replace old access token with new token
            token = new_token
            timeleft = time.time() + expires_in

        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
    
    #else:
        #print("Token still valid")






def refresh_the_token(refresh_token):
    
    try:
        global window_blocked
        sblock = False

        get_file("block.txt")
        with open('block.txt') as f:
            blacklist = [line.strip() for line in f.readlines()]
            for item in blacklist:
                if "This is a block file.".replace("\n","") in item.replace("\n",""):
                    sblock = True


        
        if sblock == True:
            if window_blocked == False:
            
                block_screen()
                window_blocked = True
        else:
            if window_blocked == True:
                unblock_screen()
                window_blocked = False
    except:
        print(" Connection Error")




    root.after(1000, refresh_the_token, search_results.get(tk.ACTIVE))



# Client credentials
client_id = "dcea901047da4251b0437c3666eae991"
client_secret = "d97ac3aacc2c4dd1a13f498667626e40"
redirect_uri = "http://www.google.com/"
scopes = "user-modify-playback-state"

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
#print(authorization_code)

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

global timeleft

print("get rtoken")

headers = {
    "Authorization": f"Basic {base64Message}"
}
data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}

r = requests.post(token_url, headers=headers, data=data)
r.raise_for_status()  # Raise exception for non-successful response

# Parse response for new access token and expiration time
expires_in = r.json()['expires_in']

timeleft = time.time() + expires_in

# Search function
# Search function
def search(query):
    real_refresh_the_token()
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "market": "DE", "limit": 20}
    while True:
        try:
            response = requests.get(search_url, headers=headers, params=params).json()
            break
        except:
            print("Conection Error")
    
    # Try to find an exact match for the track name
    track_name = query.lower()
    for track in response['tracks']['items']:
        if track_name == track['name'].lower():
            # sanitize track name
            track['name'] = replace_non_ascii(track['name'])
            return [track]
    
    # If no exact match was found, return the original search results
    sanitized_results = []
    for track in response['tracks']['items']:
        # sanitize track name
        track['name'] = replace_non_ascii(track['name'])
        sanitized_results.append(track)
    return sanitized_results


# Search function
def search_user(query):
    real_refresh_the_token()
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "market": "DE", "limit": 20}
    while True:
        try:
            response = requests.get(search_url, headers=headers, params=params).json()
            break
        except:
            print("Conection Error")
    

    # If no exact match was found, return the original search results
    sanitized_results = []
    #print(response)
    for track in response['tracks']['items']:
        # sanitize track name
        track['name'] = replace_non_ascii(track['name'])
        sanitized_results.append(track)
    return sanitized_results

# Function to add a track to the user's Spotify queue




def add_track_to_queue(trackname):
    #print(trackname)
    trackname = replace_non_ascii(trackname)
    get_file(queue_txt)
    with open("queue.txt", "r") as f:
        queueitem = [line.strip() for line in f.readlines()]

        if not queueitem:
            with open("queue.txt", "a") as queue:
                queue.write(trackname)
                queue.write('\n')
                queue.write("1")
                queue.write('\n')
            upload_file(queue_txt)
        else:
            with open("queue.txt", "r") as queue:
                rl = queue.readlines()

            for index, item in enumerate(queueitem):
                if trackname == item:
                    gpt = index + 1  # Setze gpt Variable auf die aktuelle Zeilennummer
                    QueueNumber = rl[index+1]
                    nn = int(QueueNumber) + 1
                    rl[index+1] = str(nn) + "\n"
                    with open("queue.txt", "w") as queue:
                        queue.writelines(rl)
                    
                    upload_file(queue_txt)
                    break
                    
            else:   
                with open("queue.txt", "a") as queue:
                    #print("warn")
                    queue.write(trackname)
                    queue.write('\n')
                    queue.write("1")
                    queue.write('\n')
                upload_file(queue_txt)
                    






def search_button_click():
    global searching
    if searching == 0:
        global blockqueue 
        searching = 1
        blockqueue = 1
        query = search_entry.get()
        asonghasbeenadded = False
        
        #print(query)
        if not query == "":
            results = None
            while results == None:
                results = search_user(query)
            search_results.delete(0, tk.END)
            if not results == []:
                get_file(blacklist_txt)
                with open('blacklist.txt',"r") as f:
                    blacklist = [line.strip() for line in f.readlines()]
                    
                    for track in results:
                        song_name = f"{clean_name_from_breakin_things(track['artists'][0]['name'])} - {clean_name_from_breakin_things(track['name'])}"
                        allowed = True
                        for item in blacklist:
                            #print(item,replace_non_ascii(clean_name_from_breakin_things(song_name)) , replace_non_ascii(clean_name_from_breakin_things(item)))
                            if replace_non_ascii(clean_name_from_breakin_things(song_name)) == replace_non_ascii(clean_name_from_breakin_things(item)):
                                allowed = False

                        if allowed:
                            search_results.insert(tk.END, f"{clean_name_from_breakin_things(track['artists'][0]['name'])} - {clean_name_from_breakin_things(track['name'])}")
                            asonghasbeenadded = True
                    if not asonghasbeenadded:
                        search_results.insert(tk.END, f"Keine Ergebnisse gefunden")
                    #print("yes")
                    blockqueue = 0
            elif results == []:
                search_results.insert(tk.END, "Keine Ergebnisse gefunden")
                #print("No")
                blockqueue = 1
        else:
            search_results.delete(0, tk.END)
            search_results.insert(tk.END, "Du must den Song Titel in das Suchfeld eingeben")
            #print("No")
            blockqueue = 1
            #print("No2")
        searching = 0
     


    

def is_song_allowed(song_name):

        
    with open('blacklist.txt',"r") as f:
        blacklist = [line.strip() for line in f.readlines()]
        for item in blacklist:
            #print(item,replace_non_ascii(clean_name_from_breakin_things(song_name)) , replace_non_ascii(clean_name_from_breakin_things(item)))
            if replace_non_ascii(clean_name_from_breakin_things(song_name)) == replace_non_ascii(clean_name_from_breakin_things(item)):
                return False
        return True
    



def clean_trackname(trackname):
    # split the string into two parts at the first occurrence of '-'
    # if '-' doesn't exist in the string, the first part will be the entire string and the second part will be empty
    if " - " in trackname:
        artist, title = trackname.split(" - ",1)
    
    # remove all '-' characters in the title part except for the first one
    title = title.replace("-", "_")
    #print(title)
    
    # join the artist and cleaned title with a '-' separator
    return f"{artist} - {title}"

def reset_search():
    search_entry.delete(0,tk.END)
    search_results.delete(0,tk.END)
    return
        
# Function to handle add button click
def add_button_click():
    if blockqueue == 0:
        selection = search_results.curselection()
        if len(selection) > 0:
            track = search_results.get(selection[0])
            track = clean_trackname(track)
            split_track = track.split(" - ")
            #print(f"Split Track: {split_track}")
            if len(split_track) == 2:
                artist_name, track_name = split_track
                artist_name, track_name = replace_non_ascii(artist_name), replace_non_ascii(track_name)
                track_uri = f"{artist_name} - {track_name}"
                if is_song_allowed(track_uri):
                    add_track_to_queue(track_uri)
                    reset_search()
                    print(f"'{artist_name} - {track_name}' zu der Warteliste hinzugefügt.")
                    tkinter.messagebox.showinfo("Success", f"'{artist_name} - {track_name}' zu der Warteliste hinzugefügt.")
                else:
                    tkinter.messagebox.showwarning("Warning", f"'{artist_name} - {track_name}' darf nicht gespielt werden.")
            else:
                tkinter.messagebox.showwarning("Warning", f"'{track}' ist kein valieder Lied Name.")
                
    else: tkinter.messagebox.showwarning("Warning", f"Du kannst dieses Lied nicht hinzufügen")


def clean_name_from_breakin_things(tracknname):
    tracknname = str(tracknname)
    tracknname = tracknname.replace("-","_")
    tracknname = tracknname.replace("+","_")
    return tracknname


    
def toggle_window_block():
    
    get_file('block.txt')
    with open('block.txt', 'r') as f:
        first_line = f.readline()
    if first_line == 'This is a block file.':
            with open('block.txt', 'w') as f:
                f.write("\n")
    elif first_line == '' or first_line == "\n":
        with open('block.txt', 'w') as f:
            f.write('This is a block file.')
    upload_file(block_txt)
                    



# Create tkinter window
root = tk.Tk()
root.title("Spotify SR User")
root.attributes('-fullscreen', True)
padding = 10
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = screen_width - (2*padding)
window_height = screen_height - (2*padding)
window_x = padding
window_y = padding
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
root.configure(bg='#026873')

# Create search bar
coollabel = tk.Label(text="Song Request", font=('Helvetica', 48, 'bold'), bg='#026873', fg='white')
coollabel.pack(side=tk.TOP, pady=20)
search_frame = tk.Frame(root, bg='#026873')
search_frame.pack(side=tk.TOP, padx=padding, pady=padding)
search_label = tk.Label(search_frame, text="Suche:", font=('Arial', 32), bg='#026873', fg='white')
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, font=('Arial', 28),bg="#04BF8A")
search_entry.pack(side=tk.LEFT, padx=padding)
search_button = tk.Button(search_frame, text="Suchen", font=('Arial', 28), command=search_button_click)
search_button.pack(side=tk.LEFT, padx=padding)



# Create listbox
listbox_frame = tk.Frame(root, bg='#026873')
listbox_frame.pack(side=tk.TOP, padx=padding, pady=padding, fill=tk.BOTH, expand=True)
search_results = tk.Listbox(listbox_frame, height=10, font=('Arial', 23), bg='#04BF8A')
search_results.pack(side=tk.LEFT, padx=padding, pady=padding, fill=tk.BOTH, expand=True)

# Create add to queue button
add_button = tk.Button(root, text="Zur Warteliste hinzufügen", font=('Arial', 30), command=add_button_click)
add_button.pack(side=tk.BOTTOM, pady=padding, padx=(window_width/4, window_width/4))





root.bind('<Return>', lambda event: search_button_click())
root.bind('<Control-F9>', lambda event: toggle_window_block())

refresh_the_token(refresh_token)

root.mainloop()