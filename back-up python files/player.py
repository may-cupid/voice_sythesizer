import sys
sys.dont_write_bytecode = True

import pygame

from synthesizer import speech


class PlayerManager:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Define music files
        self.played_speech = speech
        
        # Track current playing music and state
        self.current_music = None
        self.is_muted = False
        self.previous_state = None
    
    def update(self, game_state):
        """Update music based on game state"""
        # If state unchanged, no need to change music
        if game_state == self.previous_state:
            return
            
        self.previous_state = game_state
        
        # Change music based on game state
        if game_state == "start":
            self.is_muted = True
        elif game_state == "player_open":
            self.play_music(speech)
    
    def play_music(self, music_file):
        """Play a music file and loop it"""
        # First stop any currently playing music
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Set the current music track
        self.current_music = music_file
        
        # Load and play the new music, unless muted
        if not self.is_muted:
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(-1)  # -1 makes it loop indefinitely
            except pygame.error as e:
                print(f"Error loading music file {music_file}: {e}")
    
    def toggle_mute(self):
        """Toggle mute status"""
        self.is_muted = not self.is_muted
        
        if self.is_muted:
            # If muting, pause the music
            pygame.mixer.music.pause()
        else:
            # If unmuting, resume the music if there was music playing
            if pygame.mixer.music.get_pos() > 0:  # Music was paused
             pygame.mixer.music.unpause()
            else:
                if self.current_music:
                    pygame.mixer.music.load(self.current_music)
                    pygame.mixer.music.play(-1)
    
    def get_mute_status(self):
        """Return current mute status for UI display"""
        return self.is_muted