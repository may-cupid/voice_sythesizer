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



clock = pygame.time.Clock()
#music_manager = MusicManager()


# Create info panel
#info_panel = InfoPanel(INFO_CONTENT["title"], INFO_CONTENT["text"])

FONT = pygame.font.SysFont("cambria", 50)
SMALL_FONT = pygame.font.SysFont("cambria", 25)

from ui_elements import Button, InfoPanel

VOWEL_BUTTON = Button(0,0,100,50, "Select Vowel")
TRAIT_BUTTON = Button(0,0,100,50, "Trait")
PITCH_BUTTON = Button(0,0,100,50, "Set Pitch")
EFFECTS_BUTTON = Button(0,0,100,50, "Effects")
ADVANCED_BUTTON = Button(0,0,100,50, "Advanced Options")
PLAYER_BUTTON = Button(0,0,100,50, "Play")
INFO_BUTTON = Button(0,0,100,50, "Info")

BACK_BUTTON = Button(0,0,100,50, "Back")


f0 = 200


def player():
    while True:
        pygame.display.set_caption("Player")

        screen.fill("black")
        BACK_BUTTON.draw(screen)

        if BACK_BUTTON.update == True:
            player == False

    

def vowel_selection():
    while True:
        pygame.display.set_caption("Vowel Selection")

        screen.fill("blue")
        BACK_BUTTON.draw(screen)

        if BACK_BUTTON.update == True:
            vowel_selection == False

def effects():
    while True:
        pygame.display.set_caption("Effects")

        screen.fill("green")
        BACK_BUTTON.draw(screen)

        if BACK_BUTTON.update == True:
            effects == False

def advanced():
    while True:
        pygame.display.set_caption("Advanced Options")

        screen.fill("red")
        BACK_BUTTON.draw(screen)

        if BACK_BUTTON.update == True:
            advanced == False

def info():
    while True:
        pygame.display.set_caption("Information")

        screen.fill("yellow")
        BACK_BUTTON.draw(screen)

        if BACK_BUTTON.update == True:
            player == False


def main():
    """Main game loop."""
    while True:
        pygame.display.set_caption("Main Menu")
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        #MENU_MOUSE_CLICKED = False
        MENU_MOUSE_WHEEL = 0

        TITLE_TEXT = pygame.Font.render(FONT, "Voice Synthesizer", True, "black")
        TITLE_RECT = TITLE_TEXT.get_rect(center=(640, 100))

        screen.fill("white")
        screen.blit(TITLE_TEXT,TITLE_RECT)

        VOWEL_BUTTON.draw(screen)
        TRAIT_BUTTON.draw(screen)
        PITCH_BUTTON.draw(screen)
        EFFECTS_BUTTON.draw(screen)
        ADVANCED_BUTTON.draw(screen)
        PLAYER_BUTTON.draw(screen)
        INFO_BUTTON.draw(screen)
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    MENU_MOUSE_CLICKED = True
                elif event.button == 4:  # Mouse wheel up
                    MENU_MOUSE_WHEEL = 1
                elif event.button == 5:  # Mouse wheel down
                    MENU_MOUSE_WHEEL = -1

                elif VOWEL_BUTTON.update():
                    """Open the vowel selector"""
                    vowel_selection()

                elif TRAIT_BUTTON.update():
                    """select male/female"""

                elif PITCH_BUTTON.update():
                    """Open the text input to input a pitch in Hz"""

                elif EFFECTS_BUTTON.update():
                    """Open the Effects window"""
                    effects()

                elif ADVANCED_BUTTON.update():
                    """open the advanced settings (keyboard input for F1-3 and Bandwidth)"""
                    advanced()

                elif PLAYER_BUTTON.update():
                    """open the player"""
                    player()

                elif INFO_BUTTON.update():
                    """open the info panel"""
                    info()
                    
                    
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
    FPS