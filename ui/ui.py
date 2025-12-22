# ui/ui.py
from ui.fonts import font, small_font, medium_font, large_font # 🚩 수정
from ui.components import InputBox # 🚩 수정
from ui.hud import draw_game_ui # 🚩 수정
from ui.screens import ( # 🚩 수정
    draw_main_menu, 
    draw_ranking_screen, 
    setup_ranking_buttons, 
    RANKING_BUTTONS, 
    CATEGORY_INFO
)