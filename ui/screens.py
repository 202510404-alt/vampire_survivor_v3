import pygame
import config
from ui.fonts import font, small_font, medium_font, large_font

# --- 랭킹 관련 설정 ---
CATEGORY_INFO = [
    {"name": "난이도 배율", "key": "DifficultyScore"},
    {"name": "최고 레벨", "key": "Levels"},
    {"name": "총 킬 수", "key": "Kills"},
    {"name": "보스 처치", "key": "Bosses"},
    {"name": "생존 시간", "key": "SurvivalTime"}
]
RANKING_BUTTONS = []

# --- 🚩 클릭 감지용 버튼 영역 정의 (위치 수정 완료) ---
# 캐릭터 정보 텍스트가 대략 y=350 부근에서 끝나므로, 버튼 시작 위치를 380으로 조정
CHAR_INV_BTN = pygame.Rect(config.SCREEN_WIDTH//2 - 120, 380, 240, 50)
CHAR_QUIT_BTN = pygame.Rect(config.SCREEN_WIDTH//2 - 120, 445, 240, 50)

# 종료 확인창 버튼 (기존 유지)
CONFIRM_YES_BTN = pygame.Rect(config.SCREEN_WIDTH//2 - 110, 350, 100, 40)
CONFIRM_NO_BTN = pygame.Rect(config.SCREEN_WIDTH//2 + 10, 350, 100, 40)


def setup_ranking_buttons():
    """화면 하단에 랭킹 카테고리 전환 버튼들을 배치합니다."""
    global RANKING_BUTTONS
    RANKING_BUTTONS.clear()
    
    button_w = 150
    button_h = 40
    spacing = 10
    total_w = len(CATEGORY_INFO) * button_w + (len(CATEGORY_INFO) - 1) * spacing
    
    start_x = (config.SCREEN_WIDTH - total_w) // 2
    start_y = config.SCREEN_HEIGHT - 60 
    
    for i, info in enumerate(CATEGORY_INFO):
        rect = pygame.Rect(start_x + i * (button_w + spacing), start_y, button_w, button_h)
        RANKING_BUTTONS.append({"rect": rect, "key": info['key'], "name": info['name']})


def draw_main_menu(surface, start_rect, exit_rect, is_game_over, rank_rect):
    """메인 메뉴 화면"""
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    txt = "게임 오버" if is_game_over else "뱀파이어 서바이벌"
    color = config.RED if is_game_over else config.BLUE
    title = large_font.render(txt, True, color)
    surface.blit(title, title.get_rect(center=(config.SCREEN_WIDTH//2, 200)))

    # 버튼들
    for r, t in [(start_rect, "게임 시작"), (rank_rect, "랭킹 보기")]:
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BG_COLOR, r, border_radius=15)
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BORDER_COLOR, r, 2, border_radius=15)
        st_txt = medium_font.render(t, True, config.WHITE)
        surface.blit(st_txt, st_txt.get_rect(center=r.center))


def draw_ranking_screen(surface, rankings, current_key):
    """랭킹 데이터를 표 형태로 그립니다."""
    surface.fill(config.DARK_GREEN)
    
    title = large_font.render("온라인 랭킹", True, config.WHITE)
    surface.blit(title, title.get_rect(center=(config.SCREEN_WIDTH // 2, 50)))
    
    esc_txt = small_font.render("ESC: 메뉴로 복귀", True, config.YELLOW)
    surface.blit(esc_txt, (config.SCREEN_WIDTH - 160, 20))

    current_name = next((c['name'] for c in CATEGORY_INFO if c['key'] == current_key), "")
    cat_txt = medium_font.render(f"< {current_name} >", True, config.YELLOW)
    surface.blit(cat_txt, cat_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 110)))

    start_y = 160
    header_y = start_y
    col_rank, col_id, col_val, col_lv, col_kills = 50, 150, 400, 550, 680
    
    headers = [("순위", col_rank), ("아이디", col_id), (current_name, col_val), ("LV", col_lv), ("Kills", col_kills)]
    for h_txt, h_x in headers:
        surface.blit(small_font.render(h_txt, True, config.YELLOW), (h_x, header_y))
    
    pygame.draw.line(surface, config.WHITE, (col_rank, header_y + 30), (750, header_y + 30), 2)

    if rankings is None:
        loading = font.render("데이터 수신 중...", True, config.WHITE)
        surface.blit(loading, loading.get_rect(center=(config.SCREEN_WIDTH//2, config.SCREEN_HEIGHT//2)))
    elif len(rankings) == 0:
        nodata = font.render("기록이 없습니다.", True, config.WHITE)
        surface.blit(nodata, nodata.get_rect(center=(config.SCREEN_WIDTH//2, config.SCREEN_HEIGHT//2)))
    else:
        for i, row in enumerate(rankings[:10]):
            draw_y = header_y + 45 + (i * 35)
            color = config.WHITE
            if i == 0: color = (255, 215, 0)
            elif i == 1: color = (192, 192, 192)
            elif i == 2: color = (205, 127, 50)
            
            val = row.get('RankValue', 0)
            val_str = f"{val:.2f}" if current_key in ["DifficultyScore", "SurvivalTime"] else str(int(val))

            surface.blit(small_font.render(f"#{i+1}", True, color), (col_rank, draw_y))
            surface.blit(small_font.render(str(row.get('ID', '익명')), True, color), (col_id, draw_y))
            surface.blit(small_font.render(val_str, True, color), (col_val, draw_y))
            surface.blit(small_font.render(str(int(row.get('Levels', 0))), True, color), (col_lv, draw_y))
            surface.blit(small_font.render(str(int(row.get('Kills', 0))), True, color), (col_kills, draw_y))

    for btn in RANKING_BUTTONS:
        is_active = (btn['key'] == current_key)
        bg_color = config.DARK_RED if is_active else config.UI_OPTION_BOX_BG_COLOR
        pygame.draw.rect(surface, bg_color, btn['rect'], border_radius=8)
        pygame.draw.rect(surface, config.WHITE if is_active else config.UI_OPTION_BOX_BORDER_COLOR, btn['rect'], 2, border_radius=8)
        btn_txt = small_font.render(btn['name'], True, config.WHITE)
        surface.blit(btn_txt, btn_txt.get_rect(center=btn['rect'].center))


def draw_weapon_inventory(surface, player_obj):
    """무기 인벤토리 화면"""
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220)) 
    surface.blit(overlay, (0, 0))
    
    title = large_font.render("INVENTORY", True, config.YELLOW)
    surface.blit(title, title.get_rect(center=(config.SCREEN_WIDTH // 2, 70)))
    instr = small_font.render("M / ESC: 캐릭터 메뉴로 돌아가기", True, config.WHITE)
    surface.blit(instr, instr.get_rect(center=(config.SCREEN_WIDTH // 2, 120)))

    card_w, card_h = 140, 100
    start_x = (config.SCREEN_WIDTH - (5 * card_w + 4 * 10)) // 2
    start_y = 180
    for i, wpn in enumerate(player_obj.active_weapons):
        row, col = i // 5, i % 5
        rect = pygame.Rect(start_x + col * (card_w + 10), start_y + row * (card_h + 10), card_w, card_h)
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BG_COLOR, rect, border_radius=10)
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BORDER_COLOR, rect, 2, border_radius=10)
        name_s = small_font.render(wpn.name, True, config.WHITE)
        lvl_s = small_font.render(f"Lv.{wpn.level}", True, config.YELLOW)
        surface.blit(name_s, name_s.get_rect(center=(rect.centerx, rect.y + 30)))
        surface.blit(lvl_s, lvl_s.get_rect(center=(rect.centerx, rect.y + 65)))


# --- 캐릭터 메뉴 및 확인창 (위치 수정 완료) ---

def draw_character_window(surface, player_obj):
    """플레이어 정보를 보여주는 캐릭터 창 (M키)"""
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    # 버튼이 내려갔으므로 패널 높이를 420에서 460으로 늘림 (100~560 영역)
    panel_rect = pygame.Rect(config.SCREEN_WIDTH//2 - 200, 100, 400, 460)
    pygame.draw.rect(surface, config.UI_OPTION_BOX_BG_COLOR, panel_rect, border_radius=15)
    pygame.draw.rect(surface, config.UI_OPTION_BOX_BORDER_COLOR, panel_rect, 3, border_radius=15)

    title = medium_font.render("캐릭터 정보", True, config.WHITE)
    surface.blit(title, title.get_rect(center=(config.SCREEN_WIDTH//2, 140)))

    # 스탯 목록 (y=190부터 시작)
    stats = [
        f"닉네임: {player_obj.name}",
        f"레벨: {player_obj.level}",
        f"체력: {int(player_obj.hp)} / {player_obj.max_hp}",
        f"경험치 배수: {player_obj.exp_multiplier:.2f}x",
        f"총 처치 수: {player_obj.total_enemies_killed}"
    ]
    for i, s in enumerate(stats):
        txt = small_font.render(s, True, config.YELLOW)
        surface.blit(txt, (panel_rect.x + 50, 190 + i * 35))

    # 🚩 인벤토리 버튼 (y=380)
    pygame.draw.rect(surface, (50, 80, 50), CHAR_INV_BTN, border_radius=10)
    pygame.draw.rect(surface, config.WHITE, CHAR_INV_BTN, 2, border_radius=10)
    inv_txt = small_font.render("무기 레벨 확인하기", True, config.WHITE)
    surface.blit(inv_txt, inv_txt.get_rect(center=CHAR_INV_BTN.center))

    # 🚩 게임 종료 버튼 (y=445)
    pygame.draw.rect(surface, (120, 40, 40), CHAR_QUIT_BTN, border_radius=10)
    pygame.draw.rect(surface, config.WHITE, CHAR_QUIT_BTN, 2, border_radius=10)
    quit_txt = small_font.render("게임 그만두기", True, config.WHITE)
    surface.blit(quit_txt, quit_txt.get_rect(center=CHAR_QUIT_BTN.center))


def draw_quit_confirmation(surface):
    """정말 종료할지 묻는 팝업창"""
    pop_rect = pygame.Rect(config.SCREEN_WIDTH//2 - 150, config.SCREEN_HEIGHT//2 - 75, 300, 150)
    pygame.draw.rect(surface, (20, 20, 20), pop_rect, border_radius=12)
    pygame.draw.rect(surface, config.RED, pop_rect, 3, border_radius=12)

    msg = small_font.render("정말 그만둘까요? (결과 저장)", True, config.WHITE)
    surface.blit(msg, (pop_rect.centerx - msg.get_width()//2, pop_rect.y + 30))

    pygame.draw.rect(surface, config.DARK_RED, CONFIRM_YES_BTN, border_radius=8)
    y_txt = small_font.render("예", True, config.WHITE)
    surface.blit(y_txt, y_txt.get_rect(center=CONFIRM_YES_BTN.center))
    
    pygame.draw.rect(surface, (80, 80, 80), CONFIRM_NO_BTN, border_radius=8)
    n_txt = small_font.render("아니오", True, config.WHITE)
    surface.blit(n_txt, n_txt.get_rect(center=CONFIRM_NO_BTN.center))