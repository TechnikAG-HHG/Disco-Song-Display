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



global queue_txt
global queuecopy_txt
global has_been_played_txt
global blocklist_txt
global blacklist_txt
global block_txt
global AMode
global new_song_has_to_be_added_AM
global ini
global should_time 
global automatic_mode_tracks
global AMPause
global AMPSave




queuecopy_txt = "queuecopy.txt"
queue_txt = "queue.txt"
has_been_played_txt = "has_been_played.txt"
blocklist_txt = "blocklist.txt"
blacklist_txt = "blacklist.txt"
block_txt = "block.txt"
automatic_mode_tracks = ["","","",""]
new_song_has_to_be_added_AM = 0
AMode = 0
ini = -1
should_time = 0
AMPause = 0
AMPSave = 0


#def download_file():
    #get_file(queue_txt)
    #get_file(queuecopy_txt)
    #get_file(block_txt)
    #get_file(blocklist_txt)
    #get_file(blacklist_txt)
    #get_file(has_been_played_txt)
    #root.after(6000, download_file)


lock = threading.Lock()

global server_unavalible
server_unavalible = 0

def get_file(filename):
    global server_unavalible
    #print("Getting File")
    file_url = f'http://127.0.0.1:5000/downloadfileusmaximus/{filename}'
    local_filename = filename

    try:
        server_unavalible = 0
        with requests.Session() as session:
            response = session.get(file_url, stream=True)
            response.raise_for_status()

            with lock:    
                with open(local_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            f.write(chunk)
    except:
        if server_unavalible == 0:
            tkinter.messagebox.showwarning("Warning", "Server unreachable")
        server_unavalible = 1
        print("Server not avalible")

def upload_file(filename):
    global server_unavalible
    server_unavalible = 0
    
    #print("Uploading File")
    url = 'http://127.0.0.1:5000/upload_file'
    file_path = filename

    try:
        with requests.Session() as session:
            
            with lock:
                with open(file_path, 'rb') as f:
                    response = session.post(url, files={'file': f})
                    response.raise_for_status()
    except:
        if server_unavalible == 0:
            tkinter.messagebox.showwarning("Warning", "Server unreachable")
        
        server_unavalible = 1
        print("Server not avalible")


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

def clean_name_from_breakin_things(tracknname):
    tracknname = str(tracknname)
    tracknname = tracknname.replace("-","_")
    tracknname = tracknname.replace("+","_")
    return tracknname

def get_selected():
        
    try:
        selection = search_results.curselection()
        track = search_results.get(selection[0])
        ss,track = track.split("# ",1)
        if len(selection) > 0:
            

            parts = track.rsplit(" - ", 1)  # Trennen des Strings anhand des Trennzeichens und des letzten Elements
            track = " - ".join(parts[:-1])  # Entfernen des letzten Elements und Zusammenfügen des Strings

            artist_name, track_name = track.split(" - ")
            #print(track_name, artist_name)
            
            return True, f'{artist_name} - {track_name}'
        else:
            print("Error")
    except IndexError:
        tkinter.messagebox.showwarning("Warning", "Please select a track from the search results.")
        return False,0


def pure_name(names):
    names = str(names)
    names = names.strip()
    names = names.replace("\n","")
    return names

global new_name
new_name = ""

global not_playing
not_playing = 0

def if_the_next_song_must_be_moved_into_queue_AM():
    global AMode
    global automatic_mode_tracks
    global new_song_has_to_be_added_AM
    global new_name
    global not_playing
    

    if AMode == 1:
        if automatic_mode_tracks[2] != "":
            refresh_the_token()
            try:
                global errorresponse
                not_playing = 0
                search_url = "https://api.spotify.com/v1/me/player/queue"
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(search_url, headers=headers).json()
                #print("s request")
                errorresponse = response
                
                queue_name = clean_name_from_breakin_things(replace_non_ascii(response["currently_playing"]["name"]))
                artist_name = clean_name_from_breakin_things(replace_non_ascii(response["currently_playing"]["artists"][0]["name"]))
                next_queue_item_name = clean_name_from_breakin_things(replace_non_ascii(response["queue"][0]["name"]))
                next_queue_item_artist = clean_name_from_breakin_things(replace_non_ascii(response["queue"][0]["artists"][0]["name"])) 
                next_queue_item = f"{next_queue_item_artist} - {next_queue_item_name}"
                new_name = f"{artist_name} - {queue_name}"
                new_name = pure_name(new_name)
                next_queue_item = pure_name(next_queue_item)
            except Exception as e:
                print(f"Error: {e}")
                
                print(errorresponse)

                if not_playing == 0 :
                    return
                    
                not_playing = 1
                
            #print(new_name)
            #print(automatic_mode_tracks[2])
            #print(automatic_mode_tracks)
            if new_name == automatic_mode_tracks[2]:
                
                #print("new song has to be added = true")
                new_song_has_to_be_added_AM = 1

            
            elif new_name == automatic_mode_tracks[1]:
                automatic_mode_tracks = ["",automatic_mode_tracks[0],automatic_mode_tracks[1],automatic_mode_tracks[2]]
                print("Automatic Mode Tracks has been moved one forward")
            
            elif new_name == automatic_mode_tracks[0]:
                automatic_mode_tracks = ["","",automatic_mode_tracks[0],automatic_mode_tracks[1]]
                print("Automatic Mode Tracks has been moved one forward 2x")

            
            elif new_name != automatic_mode_tracks[3] and new_name != automatic_mode_tracks[2] and new_name != automatic_mode_tracks[1] and automatic_mode_tracks[3] != "" and automatic_mode_tracks[2] != "":
                print("go")
                print(f"1{new_name}")
                print(f"2{automatic_mode_tracks[2]}")
                print(f"3{automatic_mode_tracks[3]}")
                print(f"4{automatic_mode_tracks[1]}")
                automatic_mode_tracks = ["","","",""]
                print("AM has been reseted")
            

                    
            
        else:
            new_song_has_to_be_added_AM = 1
            #print("needs to be added")
            
        writetolabel = ""

        writetolabel = f'''
        [0]{automatic_mode_tracks[0]}
        [1]{automatic_mode_tracks[1]}
        [2]{automatic_mode_tracks[2]}
        [3]{automatic_mode_tracks[3]}
        [CP]{new_name}
        '''
        
        queuelistlabel.config(text=str(writetolabel))
    else:
        writetolabel = ""

        queuelistlabel.config(text=str(writetolabel))

    





def save_track_name_for_AM(tracknamee):
    global automatic_mode_tracks
    part1,part2 = tracknamee.split(" - ",1)
    part1,part2 = clean_name_from_breakin_things(part1),clean_name_from_breakin_things(part2)
    tracknamee = f"{part1} - {part2}"
    tracknamee = pure_name(replace_non_ascii(tracknamee))
    automatic_mode_tracks.insert(0,tracknamee)
    automatic_mode_tracks.pop(4)



def add_song_after_countdown_AM(track,indexs,savee):

    if len(track) > 0:
    

    
        track = str(track)
        part1,part2,part3 = track.split(" - ", 2)  # Trennen des Strings anhand des Trennzeichens und des letzten Elements
        track = f"{part1} - {part2}"
        #part1, part2 = track.rsplit(" Adding",1)
        #track = part1

        artist_name, track_name = track.split(" - ",1)
        artist_name, track_name = artist_name.replace("-","_"), track_name.replace("-","_")
        #print(track)
        #print(track_uri)
        if is_song_allowed(f"{clean_name_from_breakin_things(replace_non_ascii(artist_name))} - {clean_name_from_breakin_things(replace_non_ascii(track_name))}"):
            try:
                track_uri = [t['uri'] for t in search(f"{artist_name} - {track_name}")][0]
                add_track_to_queue(track_uri)
                #print(track_name,track,track_uri)
                delete_line_and_following("queue.txt",track)
                track_has_been_played(track)
                save_track_name_for_AM(track)
                download_track_on_spotify(f"{artist_name} - {track_name}")
                if "Adding" in part3:
                    part3,a = part3.rsplit("Adding",1)
                if "Added" in part3:
                    part3,a = part3.rsplit("Added",1)
                search_results.delete(indexs)
                print(f"Added {track}")
                
            except:
                delete_line_and_following("queue.txt",track)
                search_results.delete(indexs)
                print("Search Error")
                print(search(f"{artist_name} - {track_name}"))
                print(track)
           
        else:
            delete_line_and_following("queue.txt",track)
            search_results.delete(indexs)
            
            



def update_listbox(selected_item=None):

    global should_time
    global new_song_has_to_be_added_AM
    global realresult
    global indexs
    global AMPause
    global AMode
    global AMPSave
    global wait_time_Sek 
    global listing
    global indexs
    global nindex
    wait_time_Sek = 60


    get_file(queuecopy_txt)
    get_file(queue_txt)
    get_file(has_been_played_txt)
    get_file(blocklist_txt)


    refresh_the_token()
    decide_block_window(window_block_button)
    if_the_next_song_must_be_moved_into_queue_AM()

    
    if AMode == 1 and new_song_has_to_be_added_AM == 0:
        add_button["bg"] = "#772a19"
    else:
        add_button["bg"] = "#FF5733"
    

    scroll_position = search_results.yview()[0]

    lied = None
    ##print("")
    selection = search_results.curselection()
    if len(selection) > 0:
        lied = search_results.get(selection[0])
        ss,lied = lied.split("# ",1)


    # clear the listbox
    sort_queue()
    search_results.delete(0, tk.END)
    
    #print("")

    #search_results.insert(tk.END, "-----------------------------------------")
    #search_results.itemconfig(tk.END, {'bg' : 'white'})

    readed = []
    final = []
    
    with open('queuecopy.txt', 'r', encoding='latin-1') as f:
        data = [line.strip() for line in f]
    #print("")
    
    with open('queue.txt', 'r', encoding='latin-1') as f:
        data2 = [line.strip() for line in f]

    listing = []
    #print("")
    for line in data:
        try:
            final.append(data2[data2.index(line.replace("\n",""))-1] + " - " + data2[data2.index(line)])
            listing.append(data2[data2.index(line.replace("\n",""))-1] + " - " + data2[data2.index(line)])
            data2.remove(data2[data2.index(line)-1])
            data2.remove(data2[data2.index(line)])
        except ValueError:
            print("Value Error: " + line)

    #print("")
    # add each item in the array to the listbox
    #print(final)
    for item in final:
        has, timee = has_track_been_played(item)
        #print(has_track_been_blocked(item))
        #print(has)
        if not has_track_been_blocked(item):
            #print(item)
            if has == False:

                search_results.insert(tk.END,f"{listing.index(item)}# {item}")
                search_results.itemconfig(tk.END, {'bg' : '#03A64A'})
                
                
            elif has == True:
                timeee = str(int((float(timee) - float(time.time()))//60+1))
                search_results.insert(tk.END,f"{listing.index(item)}# {item} + added {timeee} min ago" )
                search_results.itemconfig(tk.END, {'bg' : 'yellow'})
                #print("")
            
            

        else:
            listing.remove(item)

    #print("does a song need to be added?" + str(new_song_has_to_be_added_AM))
    if AMode == 1:
        nindex = -1
        while True:
            nindex = nindex + 1
            if len(listing) - 1 >= nindex:
                nresult = listing[nindex]
                if nresult != "" and nresult != None:
                    #print(nresult)
                    #ss,nresult = nresult.split("# ",1)
                    if nresult != "":
                        nhas, ntimee = has_track_been_played(nresult)
                        if nhas == False:
                            notrealresult = nresult
                            
                            break
                        
                        #else:
                            #print("Has been played")    
                    else: 
                        notrealresult = ""
                        break
                else:
                    notrealresult = ""
                    break
            else:
                    notrealresult = ""
                    break
        #print("1",nindex,notrealresult)
                
            
        
        
        if new_song_has_to_be_added_AM == 1:

            
            if should_time == 0:
                indexs = -1
                #print("set")
                now_time = time.time()
                
                should_time = now_time + wait_time_Sek
                while True:
                    indexs = indexs + 1
                    #print("reoeted")
                    if len(listing) - 1 >= indexs:
                        result = listing[indexs]
                        if result != "" and result != None:
                            #print(nresult)
                            #ss,result = result.split("# ",1)
                            if result != "":
                                #print("now")
                                has, timee = has_track_been_played(result)
                                if has == False:
                                    realresult = result
                                    #print("Acc " + realresult)
                                    break
                                #else:
                                    #print("Has been played")
                            else: 
                                realresult = ""
                                break
                        else:
                            realresult = ""
                            break
                    else:
                        realresult = ""
                        break
                
            #print("2",indexs,realresult)

        
            if AMPause == 1 and AMPSave == 0:
                AMPSave = should_time - time.time()
                
            if AMPause == 0 and AMPSave != 0:
                AMPSave = 0

            
            if notrealresult == "":
                should_time = wait_time_Sek + time.time()
            
            #print(realresult)
            #print(notrealresult)
            #print(indexs)
            
            try:

                if realresult != notrealresult or indexs != nindex:
                    if should_time - time.time() > 40:
                        should_time = 0
                    else:
                        if realresult != "":
                            indexs = listing.index(realresult)
            except:
                print("AMODE Error")


            if should_time - time.time() >= 0:
                #print("working")

                
                if notrealresult != "":
                    if should_time - time.time() >= 0:

                        if AMPause == 0:
                            search_results.delete(indexs)
                            search_results.insert(indexs, f"{indexs}# {listing[indexs]} Adding in {int(((should_time - time.time())//5)*5+5)} sek.")
                            global savee
                            savee = f"{indexs}# {listing[indexs]} Adding in {int(((should_time - time.time())//5)*5+5)} sek."
                            search_results.itemconfig(indexs, {'bg' : '#00b0ee'})
    
                        else:
                            search_results.delete(indexs)
                            search_results.insert(indexs, f"{indexs}# {listing[indexs]} Adding in {int(((AMPSave)//5)*5+5)} sek. --Paused ")
                            search_results.itemconfig(indexs, {'bg' : 'green'})
            
            
    

            if notrealresult != "":
                if listing != []:
                    if should_time - time.time() < 0 and should_time != 0 and AMPause == 0:
                        #print("reseted")
                        should_time = 0
                        new_song_has_to_be_added_AM = 0
                        add_song_after_countdown_AM(listing[indexs],indexs,savee)
                    elif AMPause == 1:
                        should_time = AMPSave + time.time()
        else:
            should_time = 0
    else:
        should_time = 0


    #print("")

    if lied != "" and lied != None:
        if " + " in lied:
            part1, part2 = lied.rsplit(" + ",1)
            lied = part1
        if "Adding" in lied:
            part1, part2 = lied.rsplit(" Adding",1)
            lied = part1


    if lied != "" and lied != None:
        #print(listing)
        #print(lied)
        if lied in listing:
            search_results.selection_set(listing.index(lied))
            #print(lied)
            #print(listing)

    with lock:
        with open("realqueue.txt", "w") as file:
            for element in listing:
                file.write(element + "\n")


    search_results.yview_moveto(scroll_position)


    upload_file(has_been_played_txt)
    upload_file(blocklist_txt)         
    upload_file("realqueue.txt")  



    refresh_the_token()

    # store the time when the last item was selected
  
    # schedule the next update in 1000ms (1 second)
    root.after(1200, update_listbox, search_results.get(tk.ACTIVE))






def sort_queue():
    ##print("")
    block = 1
    aline = -1
    realdata = []
    block = 1
    realdata = []
    # Read the data from the text file into a list
    
    ##print("")
    get_file(queue_txt)
    with open('queue.txt', 'r', encoding='latin-1') as f:
        data = [line.strip() for line in f]
        for line in data:
            aline = aline + 1
            if block == 1:
                block = 0
            elif block == 0:
                #print(aline)
                #print(line.replace("\n",""))
                realdata.append(int(line.replace("\n","")))
                #print(realdata)
                
                block = 1
    ##print("")
    realdata.sort(reverse=True)

    # Write the sorted data back to the text file
    get_file(queuecopy_txt)
    with open('queuecopy.txt', 'w') as f:
        for item in realdata:
            f.write(str(item) + '\n')
    upload_file(queuecopy_txt)
    #print("")


def refresh_the_token():
    
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







# Client credentials
client_id = "dcea901047da4251b0437c3666eae991"
client_secret = "d97ac3aacc2c4dd1a13f498667626e40"
redirect_uri = "http://www.google.com/"
scopes = "user-modify-playback-state,user-read-playback-state,playlist-modify-public,playlist-modify-private"

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



def download_track_on_spotify(trackname):
    try:
        #print("executed")
        playlist_id = "2viCh2UqOxhbO8OsIpAv3S"
        track_uri = [t['uri'] for t in search(trackname)][0]
        #print(track_uri)
        refresh_the_token()

        add_track_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        data = {
            "uris": [track_uri],
            "position": 0
        }
        #print(data)

        response = requests.post(add_track_url, headers=headers, json=data)
                    
        #print("s request")
        

        #print(response)

        #if response.status_code == 201:
            #print("Track added to the playlist successfully!")
        #else:
            #print("Failed to add the track to the playlist.")
    except:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Couldnotdowload")


# Search function
def search(query):
    query = query.replace("_","")
    refresh_the_token()
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "market": "DE", "limit": 20}
    while True:
        try:
            response = requests.get(search_url, headers=headers, params=params).json()
            break
        except:
            print("Conection Error")
    #print("s request")
    
    # Try to find an exact match for the track name
    track_name = query.lower()

    for track in response['tracks']['items']:
        
        result_name = replace_non_ascii(track['name'].lower())
        result_name = result_name.replace("_","")
        shit,better_track_name = track_name.split(" - ",1)
        #print("TESTSTSTSTSTST: ")
        #print(result_name)
        #print(better_track_name)
        if better_track_name.replace("-","") == result_name.replace("-",""):
            # sanitize track name
            track['name'] = replace_non_ascii(track['name'])
            return [track]
    

# Function to add a track to the user's Spotify queue
def add_track_to_queue(uri):
    refresh_the_token()
    global not_playing
    try:
        not_playing = 0
        endpoint = "https://api.spotify.com/v1/me/player/queue"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"uri": uri}
        response = requests.post(endpoint, headers=headers, params=params)
        #print("s request1")
        ##print("")
        return response.ok
    except:
        if not_playing == 0 :
            return
        not_playing = 1




    
def track_has_been_played(track):
    get_file(has_been_played_txt)
    time.sleep(0.01)
    writeback = []
    filename = "has_been_played.txt"
    #global timetowait
    
    get_file(has_been_played_txt)


    with open(filename, 'r') as file:
        lines = file.readlines()

    
        with open(filename, 'w') as file:
            
            for i, line in enumerate(lines):
                if line != "" and line != "\n":
                    line2, shit = line.rsplit(" + ",1)
                    if track in line2:
                        
                        continue  # skip this line (i.e., delete it)
                        
                    else:
                        writeback.append(line)
                
            timetowait = str(time.time()+60*10*3)
            writeback.append(track.replace("\n","") + " + " + timetowait)

            for entry in writeback:
                file.write(entry.replace("\n","")+"\n")
    
    upload_file(has_been_played_txt)

    

def has_track_been_played(track):
        
    #print(track)
    if track != "":
        writeback = []
        filename = "has_been_played.txt"
        found = False
        
        
        with open(filename, 'r') as file:
            lines = file.readlines()

        
            track, shit2 = track.rsplit(" - ",1)
            #print("check if has  been played input after split= " + track)
            for i, line in enumerate(lines):
                line = line.replace("\n","")
                #print(line)
                if line != "" and line != "\n":
                    line2, shit = line.rsplit(" + ",1)
                    #print(line,track)
                    
                    if track in line2:
                        #print("truee")
                        found = True
                        realshit = shit
                        #print(shit.replace("\n", ""))

                    if (float(shit.replace("\n", "")) - time.time()) > 0:
                        #print(float(shit.replace("\n", "")) - time.time())
                        writeback.append(line)
        with lock:
            with open(filename, 'w') as file:
                if writeback != []:
                    for entry in writeback:
                        if entry != "" or entry != "\n":
                            file.write(entry.replace("\n","") + "\n")
                else:
                    file.write("")
        if found == True:
            return True,realshit
        else: return False, 0            
    else:
        return False,0

                




def track_has_been_blocked(track):
    time.sleep(0.1)
    writeback = []
    filename = "blocklist.txt"
    #global timetowait
    
    get_file(has_been_played_txt)


    with open(filename, 'r') as file:
        lines = file.readlines()

    
        with open(filename, 'w') as file:
            
            for i, line in enumerate(lines):
                if line != "" and line != "\n":
                    line2, shit = line.rsplit(" + ",1)
                    if track in line2:
                        
                        continue  # skip this line (i.e., delete it)
                        
                    else:
                        writeback.append(line)
                
            timetowait = str(time.time()+60*10*1)
            writeback.append(track.replace("\n","") + " + " + timetowait)

            for entry in writeback:
                file.write(entry.replace("\n","")+"\n")
        upload_file(blocklist_txt)
    
    
    

def has_track_been_blocked(track):
    writeback = []
    filename = "blocklist.txt"
    found = False
    
    
    
    if track != "":
        writeback = []
        filename = "blocklist.txt"
        
        found = False
        
        
        with open(filename, 'r') as file:
            lines = file.readlines()

        
            track, shit2 = track.rsplit(" - ",1)
            for i, line in enumerate(lines):
                line = line.replace("\n","")
                #print(line)
                if line != "" and line != "\n":
                    line2, shit = line.rsplit(" + ",1)
                    #print(line,track)
                    
                    if track in line2:
                        #print("truee")
                        found = True
                        realshit = shit
                        #print(shit.replace("\n", ""))

                    if (float(shit.replace("\n", "")) - time.time()) > 0:
                        #print(float(shit.replace("\n", "")) - time.time())
                        writeback.append(line)
        with lock:
            with open(filename, 'w') as file:
                if writeback != []:
                    for entry in writeback:
                        if entry != "" or entry != "\n":
                            file.write(entry.replace("\n","") + "\n")
                else:
                    file.write("")
        if found == True:
            return True
        else: return False         
    else:
        return False



def button_block_pressed():
    w,n=get_selected()
    if w == True:
        track_has_been_blocked(n)



def is_song_allowed(song_name):
    try:
        get_file(blacklist_txt)
        
        with open('blacklist.txt') as f:
            blacklist = [line.strip() for line in f.readlines()]
            for item in blacklist:
                #print(item,replace_non_ascii(clean_name_from_breakin_things(song_name)) , replace_non_ascii(clean_name_from_breakin_things(item)))
                if replace_non_ascii(clean_name_from_breakin_things(song_name)) == replace_non_ascii(clean_name_from_breakin_things(item)):
                    return False
            return True
    except FileNotFoundError:
        #print("Error: blacklist.txt file not found.")
        return False
    except Exception as e:
        #print(f"Error: {e}")
        return False


def delete_line_and_following(filename, text):
    get_file(filename)
    
    with open(filename, 'r') as file:
        lines = file.readlines()

    
        with open(filename, 'w') as file:
            found_text = False
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:  # skip empty lines
                    continue
                if " - " not in text:  # skip lines that do not contain " - "
                    continue
                split1, split2 = text.split(" - ", 1)
                split2 = split2.replace("-", "_")
                split2 = split2.replace("\n", "")
                text = " - ".join([split1, split2])
                line = line.replace("\n", "")
                if text == line:
                    found_text = True
                    continue  # skip this line (i.e., delete it)
                elif found_text:
                    found_text = False
                    continue  # skip the following line (i.e., delete it too)
                file.write(line + "\n")  # write all other lines to the file
    upload_file(filename)
    return



def add_to_blacklist(track_name):
    selection = search_results.curselection()
    if len(selection) > 0:
        track = search_results.get(selection[0])
        ss,track = track.split("# ",1)

        parts = track.rsplit(" - ", 1)  # Trennen des Strings anhand des Trennzeichens und des letzten Elements
        track = " - ".join(parts[:-1])  # Entfernen des letzten Elements und Zusammenfügen des Strings

        artist_name, track_name = track.split(" - ")
        #print(track_name, artist_name)
        get_file(blacklist_txt)
        with open('blacklist.txt', 'a', encoding='utf-8') as f:
            f.write(f'{artist_name} - {track_name}\n')
        upload_file(blacklist_txt)
    else:
        artist_name = ''


def blacklist_button_click():
    selection = search_results.curselection()
    if len(selection) > 0:
        track = search_results.get(selection[0])
        ss,track = track.split("# ",1)

        parts = track.rsplit(" - ", 1)  # Trennen des Strings anhand des Trennzeichens und des letzten Elements
        track = " - ".join(parts[:-1])  # Entfernen des letzten Elements und Zusammenfügen des Strings

        artist_name, track_name = track.split(" - ",1)
        add_to_blacklist(track_name)
        delete_line_and_following("queue.txt",track)
        tkinter.messagebox.showinfo("Success", f"Added '{artist_name} - {track_name}' to the blacklist.")
    else:
        tkinter.messagebox.showwarning("Warning", "Please select a track from the search results.")




# Function to handle add button click
def add_button_click():
    global new_song_has_to_be_added_AM
    
    if AMode == 0 or new_song_has_to_be_added_AM == 1:
        selection = search_results.curselection()
        if len(selection) > 0:
            
            
            
            track = search_results.get(selection[0])
            ss,track = track.split("# ",1)
            rtrack = track
            track = str(track)
            part1,part2,part3 = track.split(" - ", 2)  # Trennen des Strings anhand des Trennzeichens und des letzten Elements
            track = f"{part1} - {part2}"

            artist_name, track_name = track.split(" - ",1)
            artist_name, track_name = artist_name.replace("-","_"), track_name.replace("-","_")
            #print(track)
            #print(track_uri)
            if is_song_allowed(f"{clean_name_from_breakin_things(replace_non_ascii(artist_name))} - {clean_name_from_breakin_things(replace_non_ascii(track_name))}"):
                global should_time
                try:
                    track_uri = [t['uri'] for t in search(f"{artist_name} - {track_name}")][0]
                
                except:
                    delete_line_and_following("queue.txt",track)
                    search_results.delete(indexs)
                    
                    print("Search Error")
                    print(search(f"{artist_name} - {track_name}"))
                should_time = 0
                new_song_has_to_be_added_AM = 0
                add_track_to_queue(track_uri)
                #print(track_name,track,track_uri)
                delete_line_and_following("queue.txt",track)
                track_has_been_played(track)
                save_track_name_for_AM(track)
                download_track_on_spotify(f"{artist_name} - {track_name}")
                search_results.delete(selection)
                print(f"Added {artist_name} - {track_name}")
                tkinter.messagebox.showinfo("Success", f"Added '{artist_name} - {track_name}' to your Spotify queue.")
            else:

                delete_line_and_following("queue.txt",track)
                search_results.delete(indexs)
                tkinter.messagebox.showwarning("Warning", f"'{artist_name} - {track_name}' is not allowed to be played.")



def create_user_window_block():
    
    
    with open('block_user.txt', 'w') as f:
        f.write('This is a block_user file.')
    #print('File created successfully.')
    upload_file("block_user.txt")

def delete_user_window_block():
    
    with open('block_user.txt', 'w') as f:
        f.write("\n")
    upload_file("block_user.txt")


def decide_block_window(button):
   


    
    get_file('block.txt')
    with open('block.txt', 'r') as f:
        first_line = f.readline()
    if first_line == 'This is a block file.':
        with open('block.txt', 'w') as f:
            button['text'] = 'Unblock Window'
    elif first_line == '' or first_line == "\n":
        with open('block.txt', 'w') as f:
            button['text'] = 'Block Window'
            
        
        

def decide_user_block_window(button):
   
    sblock = False
    get_file("block_user.txt")
    
    
    with open('block_user.txt') as f:
        blacklist = [line.strip() for line in f.readlines()]
        for item in blacklist:
            if "This is a block_user file.".replace("\n","") in item.replace("\n",""):
                sblock = True



    if sblock == True:
       
        
        button['text'] = 'Unblock User Window'
           
    else:
        
        button['text'] = 'Block User Window'
          

def toggle_button(button):


    get_file('block.txt')
    with open('block.txt', 'r') as f:
        first_line = f.readline()
    if first_line == 'This is a block file.':
            with open('block.txt', 'w') as f:
                f.write("\n")
                button['text'] = 'Block Window'
    elif first_line == '' or first_line == "\n":
        with open('block.txt', 'w') as f:
            f.write('This is a block file.')
            button['text'] = 'Unblock Window'
    upload_file(block_txt)


def toggle_user_block_button(button):
    if button['text'] == 'Block User Window':
        create_user_window_block()
        button['text'] = 'Unblock User Window'
    else:
        delete_user_window_block()
        button['text'] = 'Block User Window'


def toggle_amode_button(button):
    global AMode
    if AMode == 1:
        AMode = 0
        button['text'] = 'AMode Off'
        button["bg"] = "#305924"
    else:
        AMode = 1
        button['text'] = 'AMode On'
        button["bg"] = "#76FC64"

def toggle_amode_pause_button(button):
    global AMPause
    if AMPause == 1:
        AMPause = 0
        button['text'] = 'AM Pause off'
        button["bg"] = "#305924"
    elif AMode == 1:
        AMPause = 1
        button['text'] = 'AM Pause on'
        button["bg"] = "#76FC64"


def returnclicked():
    settedtme = SetTimeEntry.get()
    if settedtme != None and settedtme != "" and settedtme.isnumeric():
        global server_unavalible

        try:
            server_unavalible = 0
            payload = {'number': settedtme}  # Create a payload with the number value
            file_url = 'http://127.0.0.1:5000/filiaminima_set_user_block_time'

            response = requests.post(file_url, data=payload)
            SetTimeEntry.delete(0,tk.END)
            if response.status_code == 200:
                print(response.text)
            else:
                print("Server returned an error:", response.text)
        except :
            if server_unavalible == 0:
                tkinter.messagebox.showwarning("Warning", "Server unreachable")
            server_unavalible = 1
            print("Server not available")
    else:
        add_button_click()



blocklist =[]


# Create tkinter window
root = tk.Tk()
root.title("Spotify SR Admin")
root.attributes('-fullscreen', True)
padding = 10
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = screen_width - (2*padding)
window_height = screen_height - (2*padding)
window_x = padding
window_y = padding
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
root.configure(bg='#0047AB')

coollabel = tk.Label(text="Admin", font=('Helvetica', 48, 'bold'), bg='#0047AB', fg='white')
coollabel.pack(side=tk.TOP, pady=20)



listbox_frame = tk.Frame(root,bg='#0047AB')
listbox_frame.pack(side=tk.BOTTOM, padx=padding, pady=padding, fill=tk.BOTH, expand=True)

search_results = tk.Listbox(listbox_frame, height=10, font=('Arial', 24),bg="#04BF8A")
search_results.pack(side=tk.LEFT, padx=padding, pady=padding, fill=tk.BOTH, expand=True)

# Create a Scrollbar widget and attach it to the Listbox
scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Attach the Scrollbar to the Listbox
scrollbar.config(command=search_results.yview)




# Create the button_frame within the listbox_frame to contain the buttons
button_frame = tk.Frame(listbox_frame, bg='#0047AB')
button_frame.pack(side=tk.LEFT, padx=padding-5, pady=padding)

global add_button
# Create the add_button with the specified properties and assign its command to the add_button_click function
add_button = tk.Button(button_frame, text="Add to Queue", font=('Arial', 28), command=add_button_click,bg='#FF5733')
add_button.pack(side=tk.BOTTOM, pady=padding)

# Create the blacklist_button with the same size and font as the add_button, and assign its command to the blacklist_button_click function
blacklist_button = tk.Button(button_frame, text="Blacklist", font=add_button['font'], command=blacklist_button_click)
blacklist_button.pack(side=tk.BOTTOM, pady=padding)

# Create the block_button with the same size and font as the add_button, and assign its command to the make_block_button_click function
block_button = tk.Button(button_frame, text="Block for 10min", font=add_button['font'], command=button_block_pressed)
block_button.pack(side=tk.BOTTOM, pady=padding)

amode_button = tk.Button(button_frame, text="AMode off", font=add_button['font'],bg="#305924", command=lambda: toggle_amode_button(amode_button))
amode_button.pack(side=tk.TOP, anchor=tk.NE, pady=padding, padx=padding)

amode_pause_button = tk.Button(button_frame, text="AM Pause off", font=add_button['font'],bg="#305924", command=lambda: toggle_amode_pause_button(amode_pause_button))
amode_pause_button.pack(side=tk.TOP, anchor=tk.NE, pady=padding, padx=padding)




# Specify the coordinates of the button
button_width = 200
button_height = 50
button_x = screen_width - button_width - padding
button_y = padding

# Create the button

global queuelistlabel
queuelistlabel = tk.Label(root, text='[]', font=('Arial', 24),bg='#0047AB')
queuelistlabel.pack(side=tk.LEFT, anchor=tk.N, pady=0, padx=0)

global window_block_button
window_block_button = tk.Button(root, text='Block Window', font=('Arial', 28), command=lambda: toggle_button(window_block_button))
window_block_button.pack(side=tk.TOP, anchor=tk.NE, pady=padding, padx=padding)

window_user_block_button = tk.Button(root, text='Block User Window', font=('Arial', 28), command=lambda: toggle_user_block_button(window_user_block_button))
window_user_block_button.pack(side=tk.TOP, anchor=tk.NE, pady=padding, padx=padding)


global SetTimeEntry
SetTimeEntry = tk.Entry(root, font=('Arial', 28),bg="#04BF8A")
SetTimeEntry.pack(side=tk.TOP, anchor=tk.NE, pady=padding, padx=padding)

root.bind('<Return>', lambda event: returnclicked())
root.bind('<Control-F9>', lambda event: toggle_button(window_block_button))


decide_block_window(window_block_button)
decide_user_block_window(window_user_block_button)





update_listbox()
#download_file()

root.mainloop()