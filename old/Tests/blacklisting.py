import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import base64
import json
import os
import webbrowser



# Step 1 - Authorization 
def authorize():
    global refresh_token
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

    refresh_token = r.json()['refresh_token']

    return token

access_token = authorize()

# Step 2 - Search
def search_track(track_name):
    url = f"https://api.spotify.com/v1/search?q={track_name}&type=track"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(url=url, headers=headers)

    results = []
    for track in res.json()["tracks"]["items"]:
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        results.append((track_name, artist_name))
        
    return results

def add_to_blacklist(track_name):
    selection = search_results.curselection()
    if len(selection) > 0:
        track = search_results.get(selection[0])
        track_name = track.split(" - ")[1]
        _, artist_name = search_track(track_name)[0]
        
        with open('blacklist.txt', 'a', encoding='utf-8') as f:
            f.write(f'{artist_name} - {track_name}\n')
    else:
        artist_name = ''
        
def search_button_click():
    query = search_entry.get()
    results = search_track(query)

    search_results.delete(0, tk.END)

    for result in results:
        track_name, artist_name = result
        search_results.insert(tk.END, f"{artist_name} - {track_name}")

def blacklist_button_click():
    selection = search_results.curselection()
    if len(selection) > 0:
        track = search_results.get(selection[0])
        track_name = track.split(" - ")[1]
        _, artist_name = search_track(track_name)[0]
        add_to_blacklist(track_name)
        messagebox.showinfo("Success", f"Added '{artist_name} - {track_name}' to the blacklist.")
    else:
        messagebox.showwarning("Warning", "Please select a track from the search results.")



# GUI setup
root = tk.Tk()
root.title("Spotify SR Blacklisting")
root.attributes('-fullscreen', True)
padding = 10
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = screen_width - (2*padding)
window_height = screen_height - (2*padding)
window_x = padding
window_y = padding
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

coollabel = tk.Label( text="Blacklist", font=('Arial', 34))
coollabel.pack(side=tk.TOP)
search_frame = tk.Frame(root)
search_frame.pack(side=tk.TOP, padx=padding, pady=padding)
search_label = tk.Label(search_frame, text="Search:", font=('Arial', 28))
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, font=('Arial', 28))
search_entry.pack(side=tk.LEFT, padx=padding)
search_button = tk.Button(search_frame, text="Search", font=('Arial', 28), command=search_button_click)
search_button.pack(side=tk.LEFT, padx=padding)

listbox_frame = tk.Frame(root)
listbox_frame.pack(side=tk.TOP, padx=padding, pady=padding, fill=tk.BOTH, expand=True)

search_results = tk.Listbox(listbox_frame, height=10, font=('Arial', 24))
search_results.pack(side=tk.LEFT, padx=padding, pady=padding, fill=tk.BOTH, expand=True)




blacklist_button = tk.Button(root, text="Add to blacklist", font=('Arial', 28), command=blacklist_button_click)
blacklist_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER, y=-padding)
blacklist_button.pack(side=tk.BOTTOM, pady=padding, padx=(window_width//4, window_width//4))


root.mainloop()
