# ui/ui.py

from ui.fonts import font, small_font, medium_font, large_font
from ui.components import InputBox
from ui.hud import draw_game_ui
from ui.screens import (
    draw_main_menu, 
    draw_ranking_screen, 
    setup_ranking_buttons, 
    draw_weapon_inventory,
    draw_character_window,  # 추가
    draw_quit_confirmation, # 추가
    CHAR_INV_BTN,           # 추가 (클릭 감지용)
    CHAR_QUIT_BTN,          # 추가
    CONFIRM_YES_BTN,        # 추가
    CONFIRM_NO_BTN,         # 추가
    RANKING_BUTTONS, 
    CATEGORY_INFO
)