# ui/ui.py (이 파일이 모든 UI 기능을 연결하는 통로입니다)

# 1. 폰트와 공통 변수 가져오기
from ui.fonts import font, small_font, medium_font, large_font

# 2. 클래스 가져오기
from ui.components import InputBox

# 3. 게임 플레이 HUD 함수 가져오기
from ui.hud import draw_game_ui

# 4. 메뉴, 랭킹 및 🟢인벤토리 화면 함수 가져오기
from ui.screens import (
    draw_main_menu, 
    draw_ranking_screen, 
    setup_ranking_buttons, 
    draw_weapon_inventory, # 🚩 이게 빠져있어서 에러가 났던 겁니다!
    RANKING_BUTTONS, 
    CATEGORY_INFO
)