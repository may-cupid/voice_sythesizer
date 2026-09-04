import sys
sys.dont_write_bytecode = True
import pygame
from sys import exit
import numpy as np
import sounddevice as sd
import time
from scipy import signal
import wave
import struct
import math
import pygame_gui
from constants import SCREEN_HEIGHT,SCREEN_WIDTH


#from game_state import GameState


import synthesizer as synth
import parameters as p


"""
def clip16( x ):    
    # Clipping for 16 bits
    if x > 32767:
        x = 32767

def vibrato(wf):
    #wf = wave.open( wavfile, 'rb')
    v0 = 2
    W = 0.2
    # W = 0 # for no effct

    RATE = wf.getframerate()            # Sampling rate (frames/second)
    LEN  = wf.getnframes()              # Signal length

    # Create a buffer (delay line) for past values
    buffer_MAX =  1024                          # Buffer length
    buffer = [0.0 for i in range(buffer_MAX)]   # Initialize to zero

    # Buffer (delay line) indices
    kr = 0  # read index
    kw = int(0.5 * buffer_MAX)  # write index (initialize to middle of buffer)
    #kw = int(buffer_MAX/2)

    for n in range(0, LEN):

        # Get sample from wave file
        input_string = wf.readframes(1)

        # Convert string to number
        input_value = struct.unpack(int(h), input_string)[0]

        # Get previous and next buffer values (since kr is fractional)
        kr_prev = int(math.floor(kr))               
        kr_next = kr_prev + 1
        frac = kr - kr_prev    # 0 <= frac < 1
        if kr_next >= buffer_MAX:
            kr_next = kr_next - buffer_MAX

        # Compute output value using interpolation
        output_value = (1-frac) * buffer[kr_prev] + frac * buffer[kr_next]

        # Update buffer (pure delay)
        buffer[kw] = input_value

        # Increment read index
        kr = kr + 1 + W * math.sin( 2 * math.pi * v0 * n / RATE )
            # Note: kr is fractional (not integer!)

        # Ensure that 0 <= kr < buffer_MAX
        if kr >= buffer_MAX:
            # End of buffer. Circle back to front.
            kr = 0

        # Increment write index    
        kw = kw + 1
        if kw == buffer_MAX:
            # End of buffer. Circle back to front.
            kw = 0

        # Clip and convert output value to binary string
        output_string = struct.pack("h", clip16(int(output_value)))

        # Write output to audio stream
        #stream.write(output_string)

        output_all = output_all + output_string     # append new to total
"""



#hello hello
# Import custom modules


# Initialize pygame
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Voice Synthesizer")

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

clock = pygame.time.Clock()
#music_manager = MusicManager()

manager = pygame_gui.UIManager((SCREEN_WIDTH,SCREEN_HEIGHT))


# Create info panel
#info_panel = InfoPanel(INFO_CONTENT["title"], INFO_CONTENT["text"])
FONT = pygame.font.SysFont("cambria", 50)
SMALL_FONT = pygame.font.SysFont("cambria", 25)

button_layout_rect = pygame.Rect((30, 20), (100, 20))


VOWEL_button= pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Select Vowel',
          manager=manager)
TRAIT_button= pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Trait',
          manager=manager)
PITCH_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Pitch',
          manager=manager)
EFFECTS_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Effects',
          manager=manager)
ADVANCED_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Advanced Options',
          manager=manager)
PLAYER_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Play',
          manager=manager)
INFO_button= pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Info',
          manager=manager)
BACK_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
          text='Back',
          manager=manager)


#default pitch
f0 = 200


def player():
    time_delta = clock.tick(60)/1000.0
    while True:
        pygame.display.set_caption("Player")
        PLAYER_MOUSE_POS = pygame.mouse.get_pos()

        screen.fill("black")
        BACK_BUTTON.draw(screen)

        # Process events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == BACK_button:  # Left mouse button
                    player == False


                elif event.ui_element == 4:  # Mouse wheel up
                    MENU_MOUSE_WHEEL = 1
                elif event.ui_element == 5:  # Mouse wheel down
                    MENU_MOUSE_WHEEL = -1

            pygame.display.update()
            clock.tick(60)  

    

def vowel_selection():
    time_delta = clock.tick(60)/1000.0
    while True:
        pygame.display.set_caption("Vowel Selection")

        screen.fill("blue")
        screen.blit()

        VOWEL_MOUSE_POS = pygame.mouse.get_pos

        BACK_button.draw(screen)

        if BACK_button.checkForInput == True:
            vowel_selection == False

        # Process events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == BACK_button:  # Left mouse button
                   vowel_selection == False 
                        

                elif event.ui_element == 4:  # Mouse wheel up
                    MENU_MOUSE_WHEEL = 1
                elif event.ui_element == 5:  # Mouse wheel down
                    MENU_MOUSE_WHEEL = -1

            pygame.display.update()
            clock.tick(60)  

def effects():
    time_delta = clock.tick(60)/1000.0
    while True:
        pygame.display.set_caption("Effects")
        FX_MOUSE_POS = pygame.mouse.get_pos

        screen.fill("green")
        BACK_button.draw(screen)


                # Process events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    
                    if event.ui_element == BACK_button:
                        effects == False

            pygame.display.update()
            clock.tick(60)  

def advanced():
    time_delta = clock.tick(60)/1000.0
    while True:
        pygame.display.set_caption("Advanced Options")
        ADVANCED_MOUSE_POS = pygame.mouse.get_pos

        screen.fill("red")
        BACK_button.draw(screen)

        if BACK_button.checkForInput == True:
            advanced == False

        # Process events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    
                    if event.ui_element == BACK_button:
                        advanced == False


            pygame.display.update()
            clock.tick(60)  

def info():
    pygame.display.set_caption("Information")
    while True:
        time_delta = clock.tick(60)/1000.0
        pygame.display.set_caption("Information")

        screen.fill("yellow")
        BACK_button.draw(screen)
        INFO_MOUSE_POS = pygame.mouse.get_pos()

        if BACK_button.checkForInput == True:
            player == False

        # Process events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                    if event.ui_element == BACK_button:
                        info == False

            pygame.display.update()
            clock.tick(60)  

def main():
    """Main game loop."""
    while True:
        pygame.display.set_caption("Main Menu")
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        time_delta = clock.tick(60)/1000.0
        
        # Process events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == VOWEL_button: 
                    """Open the vowel selector"""
                    vowel_selection is True

                elif event.ui_element ==TRAIT_button:
                        """select male/female"""
    
                elif event.ui_element ==PITCH_button:
                        """Open the text input to input a pitch in Hz"""
    
                elif event.ui_element ==EFFECTS_button:
                        """Open the Effects window"""
                        effects
    
                elif event.ui_element ==ADVANCED_button:
                    """open the advanced settings (keyboard input for F1-3 and Bandwidth)"""
                    advanced
    
                elif event.ui_element ==PLAYER_button:
                    """open the player"""
                    player
    
                elif event.ui_element ==INFO_button:
                    """open the info panel"""
                    info()

                elif event.ui_element == 4:  # Mouse wheel up
                    MENU_MOUSE_WHEEL = 1
                elif event.ui_element == 5:  # Mouse wheel down
                    MENU_MOUSE_WHEEL = -1

            manager.process_events(event)

        manager.update(time_delta)

        TITLE_TEXT = pygame.Font.render(FONT, "Voice Synthesizer", True, "black")
        TITLE_RECT = TITLE_TEXT.get_rect(center=(640, 100))

        screen.blit(background,(0,0))
        screen.blit(TITLE_TEXT,TITLE_RECT)
        manager.draw_ui(screen)

        pygame.display.update()
        clock.tick(60)  
    

if __name__ == "__main__":
    main()

