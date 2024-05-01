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
        console.log("Complete height:", pricelist.offsetHeight);
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

// var particlesDiv = document.getElementById("particles");
// var particlesPool = [];
// var poolSize = 20; // Reduced pool size

// // Create a pool of particles
// for (var i = 0; i < poolSize; i++) {
//     var particle = document.createElement("div");
//     particle.style.position = "absolute";
//     particle.style.bottom = "0px";
//     particle.style.width = "13px";
//     particle.style.height = "13px";
//     particle.style.backgroundColor = "#debd90";
//     particle.style.borderRadius = "50%";
//     particle.style.boxShadow = "0 0 10px #debd90";
//     particle.style.opacity = "1";
//     particlesPool.push(particle);
// }

// var activeParticles = []; // Array to store active particles

// // Function to generate a particle
// function generateParticle() {
//     var particle = particlesPool.pop();
//     if (!particle) return;

//     particle.style.bottom = "0px";
//     particle.style.opacity = "1";

//     // Determine the initial position of the particle
//     var position;
//     var horizontalMovement;
//     var spawnerMiddle;
//     if (Math.random() < 0.5) {
//         // Generate the particle on the left side of the screen
//         position =
//             window.innerWidth * 0.2 +
//             Math.random(-1, 1) * window.innerWidth * 0.02;
//         spawnerMiddle = window.innerWidth * 0.21;
//         // Adjust the horizontal movement based on the initial position relative to the middle of the spawner
//         horizontalMovement = (position - spawnerMiddle) / 30;
//     } else {
//         // Generate the particle on the right side of the screen
//         position =
//             window.innerWidth * 0.8 +
//             Math.random(-1, 1) * window.innerWidth * 0.02;
//         spawnerMiddle = window.innerWidth * 0.81;
//         // Adjust the horizontal movement based on the initial position relative to the middle of the spawner
//         horizontalMovement = (position - spawnerMiddle) / 30;
//     }
//     particle.style.left = position + "px";

//     particlesDiv.appendChild(particle);

//     var speed = Math.random() * 8 + 2;
//     var direction = "up";
//     var hoverTime = 0;

//     activeParticles.push({
//         particle,
//         speed,
//         direction,
//         hoverTime,
//         horizontalMovement,
//     }); // Add the particle to the active particles array
// }

// // Function to update all active particles
// function updateParticles() {
//     for (var i = activeParticles.length - 1; i >= 0; i--) {
//         var { particle, speed, direction, hoverTime, horizontalMovement } =
//             activeParticles[i];

//         var bottom = parseFloat(particle.style.bottom);
//         var left = parseFloat(particle.style.left);

//         if (direction === "up") {
//             speed -= 0.05;
//             particle.style.bottom = bottom + speed + "px";
//             particle.style.left = left + horizontalMovement + "px";
//             if (speed <= 0) {
//                 hoverTime++;
//                 if (hoverTime >= 3) {
//                     direction = "down";
//                     speed = 0;
//                 }
//             }
//         } else {
//             speed += 0.05;
//             particle.style.bottom = bottom - speed + "px";
//             particle.style.opacity = parseFloat(particle.style.opacity) - 0.01;
//             if (parseFloat(particle.style.opacity) <= 0) {
//                 particlesDiv.removeChild(particle);
//                 particlesPool.push(particle);
//                 activeParticles.splice(i, 1); // Remove the particle from the active particles array
//                 continue;
//             }
//         }

//         // Update the particle's properties in the active particles array
//         activeParticles[i] = {
//             particle,
//             speed,
//             direction,
//             hoverTime,
//             horizontalMovement,
//         };
//     }

//     requestAnimationFrame(updateParticles); // Continue the animation
// }

// // Generate new particles continuously
// setInterval(function () {
//     for (var i = 0; i < 6; i++) {
//         // Reduced number of particles generated
//         generateParticle();
//     }
// }, 30);

// requestAnimationFrame(updateParticles); // Start the animation
