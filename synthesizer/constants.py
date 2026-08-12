import sys
sys.dont_write_bytecode = True

import pygame
pygame.font.init


#screen
SCREEN_HEIGHT = 1200
SCREEN_WIDTH = 900

#colours
HEADER_COLOUR = (255, 175, 204)
TEXT_COLOUR = (255, 255, 255)

BUTTON_COLOUR = (189, 224, 254)
BUTTON_HOVER_COLOUR = (162, 210, 255)

BORDER_COLOUR = (162, 210, 255)
UI_COLOUR = (255, 200, 221)

BG_COLOUR = (255, 255, 255)
"""
FONT = pygame.font.SysFont("cambria", 50)
SMALL_FONT = pygame.font.SysFont("cambria", 25)
"""

INFO = {  
        "MAIN_INFO" : {"info_title": "dfs", "info_content": ""},
        "EFFECT_INFO" : {"info_title": "dfs", "info_content": ""},
        "TRAIT_INFO" : {"info_title": "dfs", "info_content": ""}
        }