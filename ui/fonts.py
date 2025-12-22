import pygame

pygame.font.init()
FONT_FILE_NAME = 'D2Coding.ttf'

font = None
small_font = None
large_font = None
medium_font = None

try:
    font = pygame.font.Font(FONT_FILE_NAME, 30)
    small_font = pygame.font.Font(FONT_FILE_NAME, 24)
    large_font = pygame.font.Font(FONT_FILE_NAME, 74)
    medium_font = pygame.font.Font(FONT_FILE_NAME, 36)
except:
    fallback = ["Malgun Gothic", "NanumGothic", "Arial"]
    for f in fallback:
        try:
            font = pygame.font.SysFont(f, 30)
            small_font = pygame.font.SysFont(f, 24)
            large_font = pygame.font.SysFont(f, 74)
            medium_font = pygame.font.SysFont(f, 36)
            break
        except: continue