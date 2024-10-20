// Placeholder for videos
const videos = [
    "Video 1: Learn Math!",
    "Video 2: How to Add!",
    "Video 3: Subtracting Basics!"
];

let currentVideoIndex = 0;

function loadNextVideo() {
    const videoDisplay = document.getElementById("video-display");
    
    // Load next video from array
    currentVideoIndex = (currentVideoIndex + 1) % videos.length;
    
    // Replace content inside video display with the next video
    videoDisplay.innerHTML = `<p>${videos[currentVideoIndex]}</p>`;
}
