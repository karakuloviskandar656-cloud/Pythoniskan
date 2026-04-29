import pygame
import os

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.playlist = []
        self.current_index = -1
        self.playing = False
        self.paused = False

        # Load tracks from 'music' folder
        music_dir = os.path.join(os.path.dirname(__file__), 'music')
        if os.path.exists(music_dir):
            for f in sorted(os.listdir(music_dir)):
                if f.lower().endswith(('.mp3', '.wav', '.ogg')):
                    self.playlist.append(os.path.join(music_dir, f))
        self.num_tracks = len(self.playlist)

    def play(self):
        if self.num_tracks == 0:
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        elif not self.playing or self.current_index == -1:
            if self.current_index == -1:
                self.current_index = 0
            self._load_and_play()
        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False

    def next_track(self):
        if self.num_tracks == 0:
            return
        self.current_index = (self.current_index + 1) % self.num_tracks
        self._load_and_play()

    def prev_track(self):
        if self.num_tracks == 0:
            return
        self.current_index = (self.current_index - 1) % self.num_tracks
        self._load_and_play()

    def _load_and_play(self):
        track = self.playlist[self.current_index]
        pygame.mixer.music.load(track)
        pygame.mixer.music.play()
        self.playing = True
        self.paused = False

    def get_current_track_name(self):
        if self.current_index >= 0:
            return os.path.basename(self.playlist[self.current_index])
        return "No track"

    def get_progress(self):
        """Return (position_seconds, length_seconds) or None."""
        if self.playing and pygame.mixer.music.get_busy():
            # pygame.mixer.music.get_pos() returns milliseconds
            pos = pygame.mixer.music.get_pos() / 1000.0
            # We don't have an easy way to get total length without loading metadata;
            # for simplicity, just return position and -1 for unknown length.
            return pos, -1
        return None