// FreeCodeCamp - Music Player State Manager
// Teaches: Array methods (map, filter, sort, forEach), Object mutation, State handling

const allSongs = [
  { id: 0, title: "Scratching The Surface", artist: "Quincy Larson", duration: "4:25", src: "track1.mp3" },
  { id: 1, title: "Can't Stay Down", artist: "Quincy Larson", duration: "4:15", src: "track2.mp3" },
  { id: 2, title: "Still Learning", artist: "Quincy Larson", duration: "3:51", src: "track3.mp3" },
  { id: 3, title: "Cruising for a Musing", artist: "Quincy Larson", duration: "3:34", src: "track4.mp3" },
  { id: 4, title: "Never Not Coding", artist: "Quincy Larson", duration: "2:59", src: "track5.mp3" }
];

const userData = {
  songs: [...allSongs],
  currentSong: null,
  songCurrentTime: 0
};

function playSong(id) {
  const song = userData?.songs.find((s) => s.id === id);
  if (!song) return "Song not found.";
  userData.currentSong = song;
  userData.songCurrentTime = 0;
  return `Now playing: "${song.title}" by ${song.artist} (${song.duration})`;
}

function playNextSong() {
  if (userData?.currentSong === null) {
    return playSong(userData?.songs[0].id);
  }
  const currentSongIndex = userData?.songs.indexOf(userData?.currentSong);
  const nextSong = userData?.songs[currentSongIndex + 1];
  if (nextSong) {
    return playSong(nextSong.id);
  }
  return "Reached end of playlist.";
}

function playPreviousSong() {
  if (userData?.currentSong === null) return "No song currently playing.";
  const currentSongIndex = userData?.songs.indexOf(userData?.currentSong);
  const previousSong = userData?.songs[currentSongIndex - 1];
  if (previousSong) {
    return playSong(previousSong.id);
  }
  return "At the start of the playlist.";
}

function shufflePlaylist() {
  userData.songs.sort(() => Math.random() - 0.5);
  return userData.songs.map((s) => s.title);
}

function deleteSong(id) {
  if (userData?.currentSong?.id === id) {
    userData.currentSong = null;
    userData.songCurrentTime = 0;
  }
  userData.songs = userData?.songs.filter((song) => song.id !== id);
  return `Song ${id} removed. ${userData.songs.length} remaining in queue.`;
}

// Demo
console.log("=== Music Player Demo ===");
console.log(playSong(0));
console.log(playNextSong());
console.log(playNextSong());
console.log(playPreviousSong());
console.log("\nDeleted song id 1:", deleteSong(1));
console.log("Shuffled playlist:", shufflePlaylist());
