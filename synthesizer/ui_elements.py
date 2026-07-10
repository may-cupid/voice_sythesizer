import sys
sys.dont_write_bytecode = True
import pygame
from constants import BUTTON_COLOUR, BUTTON_HOVER_COLOUR, BORDER_COLOUR, TEXT_COLOUR, UI_COLOUR, small_font

class Button:
    """Button class for creating interactive buttons."""
    def __init__(self, x, y, width, height, text, callback=None, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.icon = icon
        
    def draw(self, screen):
        """Draw the button on the screen."""
        color = BUTTON_HOVER_COLOUR if self.hovered else BUTTON_COLOUR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BORDER_COLOUR, self.rect, width=2, border_radius=5)
        
        # Render button text or icon
        if self.icon:
            screen.blit(self.icon, self.icon.get_rect(center=self.rect.center))
        else:
            text_surf = small_font.render(self.text, True, TEXT_COLOUR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
        
    def update(self, mouse_pos, mouse_clicked, blocked_by_dropdown=False):
        """Update button state and handle clicks."""
        # Don't update if a dropdown is blocking this button
        if blocked_by_dropdown:
            self.hovered = False
            return False
            
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_clicked and self.callback:
            self.callback()
            return True
        return False


class Dropdown:
    """Dropdown menu class for category selection."""
    def __init__(self, x, y, width, height, text, options, category):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.options = options
        self.category = category
        self.is_open = False
        self.option_height = 30
        self.hovered = False
        self.max_visible_options = 5
        self.scroll_offset = 0
        self.dropdown_area = None   # For scrolling through options
        
    def draw(self, screen):
        """Draw the dropdown on the screen."""
        # Draw main dropdown button
        color = BUTTON_HOVER_COLOUR if self.hovered else BUTTON_COLOUR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BORDER_COLOUR, self.rect, width=2, border_radius=5)
        
        # Render dropdown text
        text_surf = small_font.render(self.text, True, TEXT_COLOUR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        # Draw dropdown options if open
        if self.is_open:
            # Calculate how many options to show
            visible_options = min(len(self.options), self.max_visible_options)
            
            # Create a surface for the dropdown menu
            dropdown_height = visible_options * self.option_height
            dropdown_surface = pygame.Surface((self.rect.width, dropdown_height))
            dropdown_surface.fill(UI_COLOUR)
            
            # Determine options to display based on scroll offset
            display_options = self.options[self.scroll_offset:self.scroll_offset + visible_options]
            
            # Draw each option on the dropdown surface
            for i, option in enumerate(display_options):
                option_rect = pygame.Rect(
                    0, 
                    i * self.option_height, 
                    self.rect.width, 
                    self.option_height
                )
                
                # Check if mouse is hovering over this option
                screen_option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height + (i * self.option_height),
                    self.rect.width,
                    self.option_height
                )
                option_hovered = screen_option_rect.collidepoint(pygame.mouse.get_pos())
                
                color = BUTTON_HOVER_COLOUR if option_hovered else BUTTON_COLOUR
                pygame.draw.rect(dropdown_surface, color, option_rect)
                pygame.draw.rect(dropdown_surface, BORDER_COLOUR, option_rect, width=1)
                
                # Option text
                option_text = small_font.render(option, True, TEXT_COLOUR)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                dropdown_surface.blit(option_text, option_text_rect)
            
            # Draw scroll indicators if needed
            if len(self.options) > self.max_visible_options:
                if self.scroll_offset > 0:  # Can scroll up
                    pygame.draw.polygon(dropdown_surface, BORDER_COLOUR, 
                                      [(self.rect.width//2 - 10, 10), 
                                       (self.rect.width//2 + 10, 10), 
                                       (self.rect.width//2, 5)])
                
                if self.scroll_offset + visible_options < len(self.options):  # Can scroll down
                    pygame.draw.polygon(dropdown_surface, BORDER_COLOUR, 
                                      [(self.rect.width//2 - 10, dropdown_height - 10), 
                                       (self.rect.width//2 + 10, dropdown_height - 10), 
                                       (self.rect.width//2, dropdown_height - 5)])
            
            # Position the dropdown below or above the button depending on space
            dropdown_y = self.rect.y + self.rect.height
            if dropdown_y + dropdown_height > pygame.display.get_surface().get_height() - 20:
                dropdown_y = self.rect.y - dropdown_height  # Show above if not enough space below
            
            # Blit the dropdown surface to the screen
            screen.blit(dropdown_surface, (self.rect.x, dropdown_y))
    
    def get_dropdown_rect(self):
        """Returns the rectangle covering the dropdown options area for collision detection."""
        if not self.is_open:
            return None
            
        visible_options = min(len(self.options), self.max_visible_options)
        dropdown_height = visible_options * self.option_height
        
        dropdown_y = self.rect.y + self.rect.height
        if dropdown_y + dropdown_height > pygame.display.get_surface().get_height() - 20:
            dropdown_y = self.rect.y - dropdown_height
            
        return pygame.Rect(self.rect.x, dropdown_y, self.rect.width, dropdown_height)
                
    def update(self, mouse_pos, mouse_clicked, mouse_wheel=0, select_callback=None):
        """Update dropdown state and handle clicks and selection."""
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.dropdown_area = self.get_full_dropdown_area()

        if self.is_open:
            # Handle scrolling
            if mouse_wheel != 0:
                if self.is_mouse_over_dropdown(mouse_pos):
                    self.scroll_offset = max(0, min(
                        self.scroll_offset - mouse_wheel,
                        len(self.options) - self.max_visible_options
                    ))

            # Check for option selection
            if mouse_clicked:
                visible_options = min(len(self.options), self.max_visible_options)
                dropdown_rect = self.get_dropdown_rect()
                
                if dropdown_rect:
                    for i in range(visible_options):
                        option_rect = pygame.Rect(
                            self.rect.x,
                            dropdown_rect.y + (i * self.option_height),
                            self.rect.width,
                            self.option_height
                        )
                        
                        if option_rect.collidepoint(mouse_pos):
                            option_index = self.scroll_offset + i
                            if option_index < len(self.options) and select_callback:
                                select_callback(self.category, self.options[option_index])
                            return True  # Selection made but keep dropdown open

                    # Clicked outside dropdown options but still in dropdown area
                    if not dropdown_rect.collidepoint(mouse_pos):
                        self.is_open = False

        # Toggle dropdown on button click
        if mouse_clicked:
            if self.hovered:
                self.is_open = not self.is_open
                return True
            elif self.is_open and not self.is_mouse_over_dropdown(mouse_pos):
                self.is_open = False

        return False

    def get_full_dropdown_area(self):
        """Returns rect covering main button and dropdown area when open"""
        if not self.is_open:
            return self.rect
        
        dropdown_rect = self.get_dropdown_rect()
        if dropdown_rect:
            return self.rect.union(dropdown_rect)
        return self.rect

    def is_mouse_over_dropdown(self, mouse_pos):
        """Check if mouse is over main button or dropdown area"""
        if self.dropdown_area:
            return self.dropdown_area.collidepoint(mouse_pos)
        return self.rect.collidepoint(mouse_pos)