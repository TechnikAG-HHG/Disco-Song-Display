var oldProgress = 0;

function setBackgroundCoverImage(url) {
    let currentSongCol = document.getElementById('currentSongCol');
    let coverImage = document.getElementById('album-art');

    currentSongCol.style.background = "url('" + url + "')";
    coverImage.src = url;
}

function setSongData(number, title, artist) {
    if (number == 0) {
        var songName = document.getElementById('songname');
        var songArtist = document.getElementById('song-artists');
    } else {
        var songName = document.getElementById(
            'upcoming' + number + 'songname'
        );
        var songArtist = document.getElementById(
            'upcoming' + number + 'artists'
        );
    }

    songName.textContent = title;
    songArtist.textContent = artist;
}

function setProgress(progress, duration) {
    var progressBar = document.getElementById('progressbar');

    progressBar.setAttribute('max', duration);
    progressBar.setAttribute('value', progress);
    oldProgress = progress;
}

function calculateProgress() {
    var progressBar = document.getElementById('progressbar');

    var newValue = oldProgress + 10;
    progressBar.setAttribute('value', newValue);
    oldProgress = newValue;
}

function updateData() {
    fetch('http://127.0.0.1/get_spotify').then((response) => {
        response
            .json()
            .then((data) => {
                console.log(data);
                for (var i = 0; i < 3; i++) {
                    console.log(data[i]);
                    if (i == 0) {
                        setBackgroundCoverImage(data[i].image);
                        setProgress(data[i].progress, data[i].duration);
                    }
                    setSongData(i, data[i].title, data[i].artists);
                }
            })
            .catch((error) => {
                document.body.innerHTML = 'Error: ' + error;
                console.error('Error:', error);
            });
    });
}

updateData();
setInterval(updateData, 5000);
setInterval(calculateProgress, 10);
