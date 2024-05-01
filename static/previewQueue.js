let lastSongs = null;

const fetchSongData = async () => {
    document.getElementById('loading').style.display = 'block'; // Show loading message
    const response = await fetch('/get_queue/10');
    const data = await response.json();
    document.getElementById('loading').style.display = 'none'; // Hide loading message
    return data;
};

const createPlayer = (songData, index) => {
    if (songData.preview_url) {
        const title = document.getElementById(`song${index}-title`);
        title.textContent = songData.title;

        const audio = document.getElementById(`player${index}`);
        const source = document.getElementById(`song${index}-source`);
        source.src = songData.preview_url;
    }
};

const loadSongs = async () => {
    const songs = await fetchSongData();
    if (JSON.stringify(songs) !== JSON.stringify(lastSongs)) {
        Object.values(songs).forEach(createPlayer);
        lastSongs = songs;
    }
};

// Create table structure with 10 rows and 2 columns
for (let i = 0; i < 10; i++) {
    const row = document.createElement('div');
    row.className = 'row';

    const nameCol = document.createElement('div');
    nameCol.className = 'col';
    const title = document.createElement('h2');
    title.id = `song${i}-title`;
    title.textContent = 'Loading...';
    nameCol.appendChild(title);
    row.appendChild(nameCol);

    const playerCol = document.createElement('div');
    playerCol.className = 'col';
    const audio = document.createElement('audio');
    audio.id = `player${i}`;
    audio.controls = true;
    const source = document.createElement('source');
    source.id = `song${i}-source`;
    source.src = '';
    source.type = 'audio/mpeg';
    audio.appendChild(source);
    playerCol.appendChild(audio);
    row.appendChild(playerCol);

    document.body.appendChild(row);
}

document.body.innerHTML += '<div id="loading">Retrieving songs...</div>';
loadSongs();
setInterval(loadSongs, 5000);
