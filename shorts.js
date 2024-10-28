// Placeholder for videos
const videos = [
    "Video 1: Learn Math",
    "Video 2: How to Add",
    "Video 3: Subtracting Basics"
];

let currentVideoIndex = 0;

function loadNextVideo() {
    const videoDisplay = document.getElementById("video-display");
    
    // Load next video from array
    currentVideoIndex = (currentVideoIndex + 1) % videos.length;
    
    // Replace content inside video display with the next video
    videoDisplay.innerHTML = `<p>${videos[currentVideoIndex]}</p>`;
}


// Sign up page JS

function checkUsername() {
    const usernameInput = document.getElementById('username').value;
    const messageElement = document.getElementById('message');
    
    // Simulated username check (replace this with your actual check)
    const existingUsernames = ["user1", "user2", "user3"]; // Example list of existing usernames

    if (existingUsernames.includes(usernameInput)) {
        messageElement.innerHTML = `Yes, it exists. <a class="link" href="">Click LOG IN instead!</a>`;
    } else {
        messageElement.innerHTML = `That username doesn't exist. <a class="link" href="">Click SIGN UP instead!</a>`;
    }
}
