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
from constants import SCREEN_HEIGHT,SCREEN_WIDTH, HEADER_COLOUR,TEXT_COLOUR, BUTTON_COLOUR, BUTTON_HOVER_COLOUR, BORDER_COLOUR, UI_COLOUR, BG_COLOUR, INFO

from ui_elements import Button, InfoPanel
from game_state import GameState


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
pygame.display.set_caption("Dress-Up")

clock = pygame.time.Clock()
#music_manager = MusicManager()


# Create info panel
#info_panel = InfoPanel(INFO_CONTENT["title"], INFO_CONTENT["text"])

# Create game state manager
game_state = GameState(p.PRESETS, info_panel, character)
game_state.set_backgrounds()


def main():
    """Main game loop."""
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_wheel = 0
        
        music_manager.update(game_state.state)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
                elif event.button == 4:  # Mouse wheel up
                    mouse_wheel = 1
                elif event.button == 5:  # Mouse wheel down
                    mouse_wheel = -1
        
        # Draw background
        if game_state.current_background:
            
            screen.blit(game_state.current_background, (0, 0))
            pygame.draw.rect(screen, BG_COLOUR,)
        

        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()