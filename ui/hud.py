import pygame
import config
from ui.fonts import font, small_font, medium_font, large_font

def draw_game_ui(surface, player_obj, game_entities, current_slime_max_hp_val, boss_defeat_count_val, slime_kill_count_val, boss_spawn_threshold_val):
    """게임 플레이 중의 UI를 그립니다."""
    
    # 1. 닉네임 표시
    name_text = font.render(f"ID: {player_obj.name}", True, config.WHITE)
    surface.blit(name_text, (config.SCREEN_WIDTH - name_text.get_width() - 10, 10))

    # 2. HP 게이지 바
    hp_x, hp_y, hp_w, hp_h = 10, 10, 150, 20
    hp_ratio = player_obj.hp / player_obj.max_hp if player_obj.max_hp > 0 else 0
    pygame.draw.rect(surface, config.DARK_RED, (hp_x, hp_y, hp_w, hp_h), border_radius=3) 
    if hp_ratio > 0:
        pygame.draw.rect(surface, config.HP_BAR_GREEN, (hp_x, hp_y, int(hp_w * hp_ratio), hp_h), border_radius=3)
    hp_text = small_font.render(f"HP: {int(player_obj.hp)}/{int(player_obj.max_hp)}", True, config.WHITE)
    surface.blit(hp_text, hp_text.get_rect(center=(hp_x + hp_w//2, hp_y + hp_h//2)))

    # 3. 레벨 표시
    level_text = font.render(f"레벨: {player_obj.level}", True, config.WHITE)
    surface.blit(level_text, (hp_x, hp_y + hp_h + 5))

    # 4. 경험치 바
    exp_x, exp_y, exp_w, exp_h = hp_x, hp_y + hp_h + 35, 150, 15
    exp_ratio = player_obj.exp / player_obj.exp_to_level_up if player_obj.exp_to_level_up > 0 else 0
    pygame.draw.rect(surface, config.DARK_RED, (exp_x, exp_y, exp_w, exp_h), border_radius=3)
    if exp_ratio > 0:
        pygame.draw.rect(surface, config.EXP_BAR_COLOR, (exp_x, exp_y, int(exp_w * exp_ratio), exp_h), border_radius=3)
    exp_text = small_font.render(f"EXP: {player_obj.exp}/{player_obj.exp_to_level_up}", True, config.WHITE)
    surface.blit(exp_text, exp_text.get_rect(center=(exp_x + exp_w//2, exp_y + exp_h//2)))

    # 5. 🚩 태풍 스킬 쿨타임 표시 (복구 완료)
    if player_obj.special_skill:
        s = player_obj.special_skill
        # 화면 우측 하단 넉넉한 위치
        skill_x, skill_y, skill_w, skill_h = config.SCREEN_WIDTH - 160, config.SCREEN_HEIGHT - 40, 150, 20
        cooldown_ratio = s.cooldown_timer / s.cooldown
        
        # 쿨타임 바 배경
        pygame.draw.rect(surface, (50, 50, 50), (skill_x, skill_y, skill_w, skill_h), border_radius=3)
        # 쿨타임 게이지 (차오르는 느낌)
        color = config.STORM_COLOR[:3] if cooldown_ratio >= 1.0 else (100, 100, 100)
        pygame.draw.rect(surface, color, (skill_x, skill_y, int(skill_w * min(1.0, cooldown_ratio)), skill_h), border_radius=3)
        
        txt = "태풍 READY (Z)" if cooldown_ratio >= 1.0 else f"태풍 로딩... {int(cooldown_ratio*100)}%"
        skill_text = small_font.render(txt, True, config.WHITE)
        surface.blit(skill_text, (skill_x, skill_y - 25))

    # 6. 난이도 및 보스 처치 수
    info_y = config.SCREEN_HEIGHT - 90
    diff_val = current_slime_max_hp_val / config.SLIME_INITIAL_BASE_HP
    surface.blit(font.render(f"난이도: {diff_val:.1f}x", True, config.WHITE), (10, info_y))
    surface.blit(font.render(f"보스 처치: {boss_defeat_count_val}", True, config.YELLOW), (10, info_y + 30))

    # 7. 보스 소환 게이지
    bg_w, bg_h = 400, 25
    bg_x, bg_y = (config.SCREEN_WIDTH - bg_w) // 2, 10
    progress = slime_kill_count_val % boss_spawn_threshold_val
    bg_ratio = progress / boss_spawn_threshold_val
    pygame.draw.rect(surface, (100, 50, 0), (bg_x, bg_y, bg_w, bg_h), border_radius=5) 
    if bg_ratio > 0:
        pygame.draw.rect(surface, (255, 140, 0), (bg_x, bg_y, int(bg_w * bg_ratio), bg_h), border_radius=5)
    surface.blit(medium_font.render(f"다음 보스: {progress}/{boss_spawn_threshold_val}", True, config.WHITE), (bg_x + 100, bg_y))

    # 8. 오버레이 (생략 방지용 이름 유지)
    # 실제 그리기는 ui.screens의 draw_upgrade_overlay 호출