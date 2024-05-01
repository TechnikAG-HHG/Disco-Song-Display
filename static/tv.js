var oldProgress = 0;
var spotifyEnabled = true;

function setBackgroundCoverImage(url) {
    let currentSongCol = document.getElementById("currentSongCol");
    let coverImage = document.getElementById("album-art");

    if (currentSongCol && coverImage) {
        currentSongCol.style.background = "url('" + url + "')";
        coverImage.src = url;
    }
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

    if (!songName || !songArtist) {
        return;
    }
    songName.textContent = title;
    songArtist.textContent = artist;
}

function scrollText() {}

function setProgress(progress, duration) {
    try {
        var progressBar = document.getElementById("progressbar");

        if (progressBar) {
            progressBar.setAttribute("max", duration);
            progressBar.setAttribute("value", progress);
            oldProgress = progress;
        }
    } catch (error) {
        console.log("Error:", error);
    }
}

function calculateProgress() {
    try {
        var progressBar = document.getElementById("progressbar");

        if (progressBar) {
            var newValue = oldProgress + 30;
            progressBar.setAttribute("value", newValue);
            oldProgress = newValue;
        }
    } catch (error) {
        console.log("Error:", error);
    }
}

function setPriceList(data) {
    var table = document.getElementById("priceList");
    table.innerHTML = ""; // Clear the table first

    for (var i = 0; i < data.categories.length; i++) {
        var category = data.categories[i];
        var categoryRow = document.createElement("tr");
        var categoryHeader = document.createElement("th");
        categoryHeader.setAttribute("colspan", "3");
        categoryHeader.textContent = category.name;
        categoryRow.appendChild(categoryHeader);
        table.appendChild(categoryRow);

        for (var j = 0; j < category.entries.length; j++) {
            var entry = category.entries[j];
            var entryRow = document.createElement("tr");
            var entryName = document.createElement("td");
            var entryAmount = document.createElement("td");
            var entryPrice = document.createElement("td");

            entryName.textContent = entry.name;
            entryAmount.textContent = entry.amount;
            entryPrice.textContent = entry.price;

            entryRow.appendChild(entryName);
            entryRow.appendChild(entryAmount);
            entryRow.appendChild(entryPrice);
            table.appendChild(entryRow);
        }
    }
}

function turnSpotifyOff() {
    let spotifyDiv = document.getElementById("spotify");
    spotifyDiv.remove();
}

function turnSpotifyOn() {
    let mainContainer = document.getElementsByClassName("main-container")[0];
    let spotifyDiv = document.createElement("div");
    spotifyDiv.id = "spotify";
    mainContainer.appendChild(spotifyDiv);

    spotifyDiv.innerHTML = `
        <div id="currentSongCol" class="col-md pe-0"></div>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <div id="currentSongDiv" class="container-fluid text-center">
            <div id="gradient">
                <img id="album-art" src="../testimage.png" />
                <div id="currentSong" class="container songDiv">
                    <h2 id="songname" class="scrolling-text">Songname</h2>
                    <h3 id="song-artists" class="scrolling-text">Artist</h3>
                    <progress id="progressbar" value="0" max="0"></progress>
                </div>
                <div id="upcoming1" class="container songDiv upcoming">
                    <h2 id="upcoming1songname" class="scrolling-text">Upcoming Songname 1</h2>
                    <h3 id="upcoming1artists" class="scrolling-text">Upcoming Artist 1</h3>
                </div>
                <div id="upcoming2" class="container songDiv upcoming">
                    <h2 id="upcoming2songname" class="scrolling-text">Upcoming Songname 2</h2>
                    <h3 id="upcoming2artists" class="scrolling-text">Upcoming Artist 2</h3>
                </div>
            </div>
        </div>
    `;

    updateData();
}

function renderConfetti() {
    // Create a new instance of the ConfettiGenerator
    const confetti = new ConfettiGenerator({
        target: "confetti-canvas",
        clock: 10,
        max: 150,
    });

    // Configure the confetti animation
    confetti.render();
}

function checkForScroll() {
    try {
        var pricelist = document.getElementsByClassName("pricelist")[0];
        var canvas = document.getElementById("confetti-canvas");

        console.log("Visible height:", canvas.scrollHeight);
        console.log("Complete height:", pricelist.clientHeight);
        if (canvas.scrollHeight < pricelist.clientHeight) {
            var scrollAmount = pricelist.scrollHeight - canvas.scrollHeight;
            pricelist.style.setProperty("--scroll-amount", scrollAmount + "px");
            pricelist.classList.add("scroll");
        }
    } catch (error) {
        console.log("Error:", error);
    }
}

function updateData() {
    try {
        fetch("/get_spotify").then((response) => {
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
                    console.error("Error:", error);
                });
        });

        fetch("/get_price_list").then((response) => {
            response
                .json()
                .then((data) => {
                    console.log(data);
                    setPriceList(data);
                })
                .catch((error) => {
                    console.error("Error:", error);
                });
        });

        fetch("/get_show_spotify").then((response) => {
            response
                .json()
                .then((data) => {
                    console.log(data);
                    if (data.enable == true) {
                        if (!spotifyEnabled) {
                            turnSpotifyOn();
                            spotifyEnabled = true;
                        }
                    } else {
                        if (spotifyEnabled) {
                            turnSpotifyOff();
                            spotifyEnabled = false;
                        }
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                });
        });
    } catch (error) {
        console.log("Error:", error);
    }
}

renderConfetti();
setTimeout(checkForScroll, 1000);
window.addEventListener("resize", function () {
    checkForScroll();
    renderConfetti();
});

updateData();
setInterval(updateData, 5000);
setInterval(calculateProgress, 30);
