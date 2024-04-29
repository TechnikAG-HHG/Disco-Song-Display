function setBackgroundCoverImage(url) {
    let currentSongCol = document.getElementById("currentSongCol");
    let coverImage = document.getElementById("album-art");

    currentSongCol.style.backgroundImage = "url('" + url + "')";
    coverImage.src = url;
}

function setSongData(number, title, artist) {
    if (number == 0) {
        var songName = document.getElementById("songname");
        var songArtist = document.getElementById("song-artists");
    } else {
        var songName = document.getElementById(
            "upcoming" + number + "songname"
        );
        var songArtist = document.getElementById(
            "upcoming" + number + "artists"
        );
    }

    songName.textContent = title;
    songArtist.textContent = artist;
}

setBackgroundCoverImage(
    "https://i.scdn.co/image/ab67616d0000b273e00f97607068f797b703559e"
);
setSongData(0, "Song Name", "Artist Name");
setSongData(1, "Upcoming Song Name", "Upcoming Artist Name");
setSongData(2, "Upcoming Song Name", "Upcoming Artist Name");
