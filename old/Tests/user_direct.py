import requests
import base64
import json
import webbrowser
import tkinter as tk
import tkinter.messagebox

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

# Search function
def search(query):
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "market": "US", "limit": 10}
    response = requests.get(search_url, headers=headers, params=params).json()
    return response['tracks']['items']

# Function to add a track to the user's Spotify queue
def add_track_to_queue(uri):
    endpoint = "https://api.spotify.com/v1/me/player/queue"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"uri": uri}
    response = requests.post(endpoint, headers=headers, params=params)
    return response.ok

def search_button_click():
    query = search_entry.get()
    results = search(query)
    search_results.delete(0, tk.END)
    for track in results:
        search_results.insert(tk.END, f"{track['artists'][0]['name']} - {track['name']}")

# Create tkinter window
root = tk.Tk()
root.title("Spotify Search")
root.attributes('-fullscreen', True)
padding = 50
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = screen_width - (2*padding)
window_height = screen_height - (2*padding)
window_x = padding
window_y = padding
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

# Create search bar
search_frame = tk.Frame(root)
search_frame.pack(side=tk.TOP, padx=padding, pady=padding)
search_label = tk.Label(search_frame, text="Search:", font=('Arial', 28))
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, font=('Arial', 28))
search_entry.pack(side=tk.LEFT, padx=padding)
search_button = tk.Button(search_frame, text="Search", font=('Arial', 28), command=search_button_click)
search_button.pack(side=tk.LEFT, padx=padding)
    

def is_song_allowed(song_name):
    try:
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
        print(f"Error: {e}")
        return False



        
# Function to handle add button click
def add_button_click():
    selection = search_results.curselection()
    if len(selection) > 0:
        track = search_results.get(selection[0])
        artist_name, track_name = track.split(" - ")
        track_uri = [t['uri'] for t in search(track_name)][0]
        if is_song_allowed(f"{artist_name} - {track_name}"):
            add_track_to_queue(track_uri)
            tkinter.messagebox.showinfo("Success", f"Added '{artist_name} - {track_name}' to your Spotify queue.")
        else:
            tkinter.messagebox.showwarning("Warning", f"'{artist_name} - {track_name}' is not allowed to be played.")





# Create listbox
listbox_frame = tk.Frame(root)
listbox_frame.pack(side=tk.TOP, padx=padding, pady=padding, fill=tk.BOTH, expand=True)
search_results = tk.Listbox(listbox_frame, height=10, font=('Arial', 18))
search_results.pack(side=tk.LEFT, padx=padding, pady=padding, fill=tk.BOTH, expand=True)

# Create add to queue button
add_button = tk.Button(root, text="Add to Queue", font=('Arial', 28), command=add_button_click)
add_button.pack(side=tk.BOTTOM, pady=padding, padx=(window_width/4, window_width/4))

root.mainloop()