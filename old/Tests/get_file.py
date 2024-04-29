import requests

def get_file(filename):
    
    file_url = f'http://localhost:5000/{filename}'
    local_filename = filename

    response = requests.get(file_url, stream=True)

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def upload_file(filename):
    url = 'http://localhost:5000/upload_file'
    file_path = filename

    with open(file_path, 'rb') as f:
        response = requests.post(url, files={'file': f})
        print(response.text)

upload_file("queue.txt")