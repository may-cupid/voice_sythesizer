import sys
sys.dont_write_bytecode = True
import pygame
from ui_elements import Button, Dropdown
from player import PlayerManager
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

player_manager = PlayerManager()

class GameState:
    
    def __init__(self, assets, info_panel, character):
        self.state = "start"
        self.assets = assets
        self.info_panel = info_panel
        self.character = character
        self.active_dropdown = None
        self.dropdowns = []
        
        # Create buttons
        
        # Create top-right buttons
        self.info_button = Button(SCREEN_WIDTH - 60, 20, 40, 40, "i", self.info_panel.toggle)
        self.mute_button = Button(SCREEN_WIDTH - 60, 120, 40, 40, "m", player_manager.toggle_mute)
        
        # Background management
        self.backgrounds = []
        self.current_background_index = 0
        self.current_background = pygame.Rect(0, 0, 0, SCREEN_HEIGHT)
        
 
    def set_state(self, new_state):
        
        self.state = new_state
        self.active_dropdown = None
        
        # Initialize dropdowns when entering config state
        
            # Clear previous dropdowns
        self.dropdowns = []
        
        # Create dropdowns for each category
        categories = [
            ("Select Vowel", "vowels"),
            ("Select Traits", "traits"),
            ("Set Pitch", "pitch"),
            ("Other Effects", "effects")
        ]
        
        y_pos = 70
        for display_name, category in categories:
            if self.assets[category]:  # Only create dropdown if there are assets
                options = list(self.assets[category].keys())
                self.dropdowns.append(Dropdown(30, y_pos, 190, 30, display_name, options, category))
                y_pos += 50
                    
    def is_position_over_any_dropdown(self, pos):
        
        if self.active_dropdown and self.active_dropdown.is_open:
            dropdown_rect = self.active_dropdown.get_dropdown_rect()
            if dropdown_rect and dropdown_rect.collidepoint(pos):
                return True
        return False