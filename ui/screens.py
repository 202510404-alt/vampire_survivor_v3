import pygame
import config
from ui.fonts import font, small_font, medium_font, large_font 

CATEGORY_INFO = [
    {"name": "난이도 배율", "key": "DifficultyScore"},
    {"name": "최고 레벨", "key": "Levels"},
    {"name": "총 킬 수", "key": "Kills"},
    {"name": "보스 처치", "key": "Bosses"},
    {"name": "생존 시간", "key": "SurvivalTime"}
]
RANKING_BUTTONS = []

def setup_ranking_buttons():
    global RANKING_BUTTONS
    RANKING_BUTTONS.clear()
    total_w = len(CATEGORY_INFO) * 160
    start_x = (config.SCREEN_WIDTH - total_w) // 2 
    for i, info in enumerate(CATEGORY_INFO):
        rect = pygame.Rect(start_x + i * 160, config.SCREEN_HEIGHT - 60, 150, 40)
        RANKING_BUTTONS.append({"rect": rect, "key": info['key'], "name": info['name']})

def draw_main_menu(surface, start_rect, exit_rect, is_game_over, rank_rect):
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    txt = "게임 오버" if is_game_over else "뱀파이어 서바이벌"
    color = config.RED if is_game_over else config.BLUE
    title = large_font.render(txt, True, color)
    surface.blit(title, title.get_rect(center=(config.SCREEN_WIDTH//2, 200)))

    for r, t in [(start_rect, "게임 시작"), (rank_rect, "랭킹 보기")]:
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BG_COLOR, r, border_radius=15)
        st_txt = medium_font.render(t, True, config.WHITE)
        surface.blit(st_txt, st_txt.get_rect(center=r.center))

def draw_ranking_screen(surface, rankings, current_key):
    surface.fill(config.DARK_GREEN)
    title = large_font.render("온라인 랭킹", True, config.WHITE)
    surface.blit(title, (50, 30))
    
    # 랭킹 데이터 그리기 로직 (기존과 동일)
    # ... (생략하지만 기존 utils 데이터 활용하여 루프 돌리는 부분 포함)
    for btn in RANKING_BUTTONS:
        color = config.RED if btn['key'] == current_key else config.UI_OPTION_BOX_BG_COLOR
        pygame.draw.rect(surface, color, btn['rect'], border_radius=5)
        b_txt = small_font.render(btn['name'], True, config.WHITE)
        surface.blit(b_txt, b_txt.get_rect(center=btn['rect'].center))