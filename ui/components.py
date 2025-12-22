import pygame
import config
from ui.fonts import medium_font

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = config.RED
        self.text = text
        self.font = medium_font 
        self.active = True
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = config.RED if self.active else config.UI_OPTION_BOX_BORDER_COLOR
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN: self.active = False
                elif event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
                elif event.unicode and len(self.text) < 15: self.text += event.unicode
                self.color = config.RED if self.active else config.UI_OPTION_BOX_BORDER_COLOR
        return not self.active and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN

    def draw(self, screen):
        pygame.draw.rect(screen, config.UI_OPTION_BOX_BG_COLOR, self.rect, border_radius=5)
        pygame.draw.rect(screen, self.color, self.rect, 3, border_radius=5)
        if self.font:
            display_text = self.text if self.text else "닉네임을 입력하세요"
            txt_s = self.font.render(display_text, True, config.WHITE)
            screen.blit(txt_s, txt_s.get_rect(center=self.rect.center))