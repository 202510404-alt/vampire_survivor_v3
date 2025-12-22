import pygame
import asyncio
import random
import config
import utils
import ui.ui as ui
import core.state as state
import core.physics as physics
import core.logic as logic
from enemies.boss_minion_slime import BossMinionSlime
from entities.exp_orb import ExpOrb
from entities.bat_minion import BatMinion

async def load_rankings_data():
    state.online_rankings = None
    state.online_rankings = utils.load_rankings_online()
    print(f"랭킹 데이터 로드 완료.")

async def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("뱀파이어 서바이벌 v.2 (Modular)")
    clock = pygame.time.Clock()

    # UI 초기화
    state.input_box = ui.InputBox((config.SCREEN_WIDTH // 2) - 150, (config.SCREEN_HEIGHT // 2) + 100, 300, 50)
    ui.setup_ranking_buttons()

    # 배경 이미지 로드
    background_image = None
    try:
        background_image = pygame.image.load("image/background/background.png").convert()
        bg_width, bg_height = background_image.get_size()
    except:
        print("배경 로드 실패")

    running = True
    start_btn = pygame.Rect(0, 0, 200, 80)
    exit_btn = pygame.Rect(config.SCREEN_WIDTH - 50, 10, 40, 40)
    rank_btn = pygame.Rect(0, 0, 150, 60)

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            # --- 메뉴 이벤트 ---
            if state.game_state == state.GAME_STATE_MENU:
                if not state.is_name_entered:
                    if state.input_box.handle_event(event): state.is_name_entered = True
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_btn.collidepoint(mouse_pos) and state.is_name_entered:
                        state.reset_game_state(); state.game_state = state.GAME_STATE_PLAYING
                    elif rank_btn.collidepoint(mouse_pos):
                        state.game_state = state.GAME_STATE_RANKING; await load_rankings_data()
            
            # --- 랭킹 이벤트 ---
            elif state.game_state == state.GAME_STATE_RANKING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in ui.RANKING_BUTTONS:
                        if btn['rect'].collidepoint(mouse_pos):
                            state.current_rank_category_index = state.RANK_CATEGORIES.index(btn['key'])
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state.game_state = state.GAME_STATE_MENU

            # --- 게임 플레이 이벤트 ---
            elif state.game_state == state.GAME_STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: state.game_state = state.GAME_STATE_MENU
                    # 업그레이드 선택
                    elif state.player.is_selecting_upgrade or state.player.is_selecting_boss_reward:
                        choice = -1
                        if event.key == pygame.K_1: choice = 0
                        elif event.key == pygame.K_2: choice = 1
                        elif event.key == pygame.K_3: choice = 2
                        if choice != -1:
                            removed = state.player.apply_chosen_upgrade(choice)
                            if removed: # 박쥐 컨트롤러 삭제 시 박쥐들도 삭제
                                state.bats[:] = [b for b in state.bats if not (isinstance(b, BatMinion) and b.controller == removed)]
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # 우클릭 특수기
                    if state.player.special_skill:
                        wx, wy = state.camera_obj.world_x + event.pos[0], state.camera_obj.world_y + event.pos[1]
                        state.player.special_skill.activate(wx, wy, {'storm_projectiles': state.storm_projectiles})

        # --- 게임 업데이트 로직 ---
        if state.game_state == state.GAME_STATE_PLAYING and state.player:
            if not (state.player.is_selecting_upgrade or state.player.is_selecting_boss_reward):
                state.player.update(state.slimes, state.get_entities_dict())
                
                if state.player.hp <= 0: # 사망 처리
                    score = {
                        "levels": state.player.level, "kills": state.player.total_enemies_killed,
                        "bosses": state.player.total_bosses_killed, "difficulty_score": state.current_slime_max_hp / config.SLIME_INITIAL_BASE_HP,
                        "survival_time": state.slime_hp_increase_timer / config.FPS
                    }
                    utils.save_new_ranking_online(state.player.name, score)
                    state.game_state = state.GAME_STATE_MENU; state.is_game_over_for_menu = True
                
                if state.game_state == state.GAME_STATE_PLAYING:
                    state.camera_obj.update(state.player)
                    logic.update_game_logic(state)
                    logic.handle_boss_logic(state)
                    
                    # 일반 적 업데이트 및 사망 처리
                    slimes_to_rem = [s for s in state.slimes if not s.update(state.player.world_x, state.player.world_y, state.get_entities_dict())]
                    for s in slimes_to_rem:
                        if s.hp <= 0 and not isinstance(s, BossMinionSlime):
                            state.player.total_enemies_killed += 1
                            state.exp_orbs.append(ExpOrb(s.world_x, s.world_y))
                    state.slimes[:] = [s for s in state.slimes if s not in slimes_to_rem]
                    
                    # 물리 및 충돌
                    physics.handle_collisions(state)
                    # 발사체 수명 업데이트
                    state.daggers[:] = [d for d in state.daggers if d.update(state.get_entities_dict())]

        # --- 그리기 ---
        if state.game_state == state.GAME_STATE_PLAYING and state.player:
            if background_image:
                sx, sy = -(state.camera_obj.world_x % bg_width), -(state.camera_obj.world_y % bg_height)
                for y in range((config.SCREEN_HEIGHT // bg_height) + 2):
                    for x in range((config.SCREEN_WIDTH // bg_width) + 2):
                        screen.blit(background_image, (sx + x * bg_width, sy + y * bg_height))
            else: screen.fill(config.GREEN)

            for wpn in state.player.active_weapons: wpn.draw(screen, state.camera_obj.world_x, state.camera_obj.world_y)
            if not (state.player.invincible_timer > 0 and state.player.invincible_timer % 10 < 5): screen.blit(state.player.image, state.player.rect)
            for e in state.exp_orbs + state.daggers + state.bats + state.slime_bullets + state.storm_projectiles + state.slimes + state.boss_slimes:
                e.draw(screen, state.camera_obj.world_x, state.camera_obj.world_y)
            ui.draw_game_ui(screen, state.player, state.get_entities_dict(), state.current_slime_max_hp, state.player.total_bosses_killed, state.player.total_enemies_killed, config.BOSS_SLIME_SPAWN_KILL_THRESHOLD)

        elif state.game_state == state.GAME_STATE_MENU:
            screen.fill(config.GREEN)
            start_btn.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
            rank_btn.bottomleft = (10, config.SCREEN_HEIGHT - 10)
            ui.draw_main_menu(screen, start_btn, exit_btn, state.is_game_over_for_menu, rank_btn)
            if not state.is_name_entered: state.input_box.draw(screen)

        elif state.game_state == state.GAME_STATE_RANKING:
            cat = state.RANK_CATEGORIES[state.current_rank_category_index]
            filtered = [r for r in (state.online_rankings or []) if r.get('RankCategory') == cat]
            ui.draw_ranking_screen(screen, filtered, cat)

        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())